#!/usr/bin/env python3
"""Extract text and tables from PDF, with optional OCR fallback."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class OCRSettings:
    enabled: bool
    language: str
    dpi: int


def _safe_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).replace("\r\n", "\n").strip()


def _extract_with_pdfplumber(pdf_path: Path, max_pages: int | None = None) -> list[dict[str, Any]]:
    try:
        import pdfplumber  # type: ignore
    except ImportError as exc:
        raise SystemExit("Missing dependency `pdfplumber`. Install with: pip install pdfplumber") from exc

    pages: list[dict[str, Any]] = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        total = len(pdf.pages)
        limit = total if max_pages is None else min(total, max_pages)
        for page_index in range(limit):
            page = pdf.pages[page_index]
            text = _safe_text(page.extract_text())
            raw_tables = page.extract_tables() or []
            tables: list[list[list[str]]] = []
            for raw_table in raw_tables:
                normalized_rows: list[list[str]] = []
                for row in raw_table or []:
                    normalized_rows.append([_safe_text(cell) for cell in (row or [])])
                if normalized_rows:
                    tables.append(normalized_rows)

            pages.append(
                {
                    "page": page_index + 1,
                    "text": text,
                    "text_source": "pdfplumber" if text else "none",
                    "tables": tables,
                }
            )

    return pages


def _run_ocr(pdf_path: Path, settings: OCRSettings, page_count: int) -> tuple[dict[int, str], str | None]:
    if not settings.enabled:
        return {}, None

    try:
        from pdf2image import convert_from_path  # type: ignore
        import pytesseract  # type: ignore
    except Exception:
        return {}, "OCR dependencies unavailable (`pdf2image` or `pytesseract`)."

    try:
        images = convert_from_path(str(pdf_path), dpi=settings.dpi, first_page=1, last_page=page_count)
    except Exception as exc:
        return {}, f"OCR image rendering failed: {exc}"

    ocr_by_page: dict[int, str] = {}
    for idx, image in enumerate(images, start=1):
        try:
            text = pytesseract.image_to_string(image, lang=settings.language)
            ocr_by_page[idx] = _safe_text(text)
        except Exception:
            ocr_by_page[idx] = ""
    return ocr_by_page, None


def extract_pdf_document(
    pdf_path: Path,
    *,
    enable_ocr: bool,
    ocr_lang: str,
    ocr_dpi: int,
    min_chars_for_native: int,
    max_pages: int | None,
) -> dict[str, Any]:
    warnings: list[str] = []
    pages = _extract_with_pdfplumber(pdf_path, max_pages=max_pages)
    page_count = len(pages)

    ocr_by_page, ocr_warning = _run_ocr(
        pdf_path,
        OCRSettings(enabled=enable_ocr, language=ocr_lang, dpi=ocr_dpi),
        page_count=page_count,
    )
    if ocr_warning:
        warnings.append(ocr_warning)

    replaced_by_ocr = 0
    for page in pages:
        native_text = _safe_text(page.get("text", ""))
        page_no = int(page["page"])
        if len(native_text) < min_chars_for_native and page_no in ocr_by_page:
            ocr_text = ocr_by_page[page_no]
            if len(ocr_text) > len(native_text):
                page["text"] = ocr_text
                page["text_source"] = "ocr"
                replaced_by_ocr += 1

    full_text_parts = [p.get("text", "") for p in pages if p.get("text")]
    full_text = "\n\n".join(full_text_parts).strip()
    source_counts = Counter(p.get("text_source", "none") for p in pages)

    return {
        "source_file": str(pdf_path),
        "file_type": "pdf",
        "page_count": page_count,
        "full_text": full_text,
        "pages": pages,
        "notes": {
            "ocr_enabled": enable_ocr,
            "ocr_language": ocr_lang,
            "ocr_dpi": ocr_dpi,
            "min_chars_for_native": min_chars_for_native,
        },
        "stats": {
            "text_source_counts": dict(source_counts),
            "ocr_replaced_pages": replaced_by_ocr,
            "full_text_chars": len(full_text),
        },
        "warnings": warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract text and tables from PDF with OCR fallback.")
    parser.add_argument("input", help="Path to input PDF file")
    parser.add_argument("output", help="Path to output JSON file")
    parser.add_argument("--disable-ocr", action="store_true", help="Disable OCR fallback")
    parser.add_argument("--ocr-lang", default="eng+chi_sim", help="Tesseract OCR language pack")
    parser.add_argument("--ocr-dpi", type=int, default=300, help="DPI used for OCR rendering")
    parser.add_argument(
        "--min-chars-for-native",
        type=int,
        default=80,
        help="If native extracted text on a page is below this size, try OCR",
    )
    parser.add_argument("--max-pages", type=int, default=None, help="Limit extraction to first N pages")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    result = extract_pdf_document(
        input_path,
        enable_ocr=not args.disable_ocr,
        ocr_lang=args.ocr_lang,
        ocr_dpi=args.ocr_dpi,
        min_chars_for_native=args.min_chars_for_native,
        max_pages=args.max_pages,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote: {output_path}")


if __name__ == "__main__":
    main()
