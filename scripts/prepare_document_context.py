#!/usr/bin/env python3
"""Prepare structured context for end-to-end document understanding."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from extract_docx import extract_docx_document
from extract_pdf import extract_pdf_document

SKILL_VERSION = "1.0.0"


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _normalize_whitespace(text: str) -> str:
    text = text.replace("\r\n", "\n")
    text = re.sub(r"[\t\f\v]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_text_into_chunks(text: str, chunk_chars: int, overlap_chars: int) -> list[dict[str, Any]]:
    clean_text = _normalize_whitespace(text)
    if not clean_text:
        return []

    paragraphs = [p.strip() for p in clean_text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""

    for para in paragraphs:
        if not current:
            current = para
            continue

        candidate = f"{current}\n\n{para}"
        if len(candidate) <= chunk_chars:
            current = candidate
            continue

        chunks.append(current.strip())
        if overlap_chars > 0 and len(current) > overlap_chars:
            tail = current[-overlap_chars:].strip()
            current = f"{tail}\n\n{para}".strip()
        else:
            current = para

    if current.strip():
        chunks.append(current.strip())

    output: list[dict[str, Any]] = []
    for idx, chunk in enumerate(chunks, start=1):
        output.append(
            {
                "chunk_id": f"C{idx:03d}",
                "char_count": len(chunk),
                "estimated_tokens": max(1, len(chunk) // 4),
                "text": chunk,
            }
        )
    return output


def _collect_headings(data: dict[str, Any], limit: int = 12) -> list[str]:
    headings: list[str] = []
    if data.get("file_type") == "docx":
        for p in data.get("paragraphs", []):
            style = (p.get("style") or "").lower()
            text = (p.get("text") or "").strip()
            if text and "heading" in style:
                headings.append(text)
            if len(headings) >= limit:
                break
    return headings


def _extract_key_lines(text: str, limit: int = 8) -> list[str]:
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    candidates: list[str] = []
    for line in lines:
        if len(line) >= 20:
            candidates.append(line)
        if len(candidates) >= limit:
            break
    return candidates


def build_understanding_report(data: dict[str, Any], chunks: list[dict[str, Any]], source_path: Path) -> str:
    headings = _collect_headings(data)
    key_lines = _extract_key_lines(data.get("full_text", ""))

    file_type = data.get("file_type", "unknown")
    page_count = data.get("page_count", "n/a")
    para_count = data.get("paragraph_count", "n/a")
    table_count = data.get("table_count", "n/a")

    lines: list[str] = []
    lines.append(f"# Understanding Report: {source_path.name}")
    lines.append("")
    lines.append("## 1) Document Profile")
    lines.append(f"- File: `{source_path}`")
    lines.append(f"- Type: `{file_type}`")
    lines.append(f"- Pages: `{page_count}`")
    lines.append(f"- Paragraphs: `{para_count}`")
    lines.append(f"- Tables: `{table_count}`")
    lines.append(f"- Chunks prepared: `{len(chunks)}`")
    conversion_note = data.get("conversion_note")
    if conversion_note:
        lines.append(f"- Conversion: `{conversion_note}`")
    pipeline = data.get("pipeline", {})
    lines.append(f"- Generated at (UTC): `{pipeline.get('generated_at_utc', 'n/a')}`")
    lines.append(f"- Skill version: `{pipeline.get('skill_version', SKILL_VERSION)}`")
    lines.append("")

    warnings = data.get("warnings", [])
    lines.append("## 2) Runtime Warnings")
    if warnings:
        for w in warnings:
            lines.append(f"- {w}")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## 3) Candidate Headings")
    if headings:
        for h in headings:
            lines.append(f"- {h}")
    else:
        lines.append("- No explicit headings detected.")
    lines.append("")

    lines.append("## 4) Key Lines (Fast Read)")
    if key_lines:
        for item in key_lines:
            lines.append(f"- {item}")
    else:
        lines.append("- No key lines detected from extracted text.")
    lines.append("")

    lines.append("## 5) Chunk Evidence Index")
    for chunk in chunks:
        preview = chunk["text"].replace("\n", " ")[:120]
        lines.append(
            f"- {chunk['chunk_id']} ({chunk['estimated_tokens']} tokens est.): {preview}{'...' if len(chunk['text']) > 120 else ''}"
        )
    lines.append("")

    lines.append("## 6) Analyst Instructions")
    lines.append("- Read all chunks before final conclusions.")
    lines.append("- Every claim must cite chunk IDs, for example: `[C003][C007]`.")
    lines.append("- Distinguish facts from assumptions and list missing evidence.")
    lines.append("- Summarize by: purpose, structure, key data points, risks, and next actions.")
    lines.append("")

    lines.append("## 7) Deliverable Template")
    lines.append("1. One-paragraph executive summary")
    lines.append("2. Full outline of document sections")
    lines.append("3. Key facts and numbers with citations")
    lines.append("4. Open questions and uncertainty")
    lines.append("5. Action recommendations")

    return "\n".join(lines)


def _convert_pptx_with_soffice(pptx_path: Path, temp_dir: Path) -> tuple[Path | None, str | None]:
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        return None, "LibreOffice not found."

    cmd = [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(temp_dir), str(pptx_path)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        return None, f"LibreOffice conversion failed: {proc.stderr.strip() or proc.stdout.strip() or 'unknown error'}"

    pdf_path = temp_dir / f"{pptx_path.stem}.pdf"
    if pdf_path.exists():
        return pdf_path, None
    return None, "LibreOffice finished but output PDF not found."


def _convert_pptx_with_powerpoint(pptx_path: Path, temp_dir: Path) -> tuple[Path | None, str | None]:
    try:
        import win32com.client  # type: ignore
    except Exception:
        return None, "pywin32 not available for PowerPoint COM conversion."

    output_pdf = temp_dir / f"{pptx_path.stem}.pdf"
    app = None
    deck = None
    try:
        app = win32com.client.Dispatch("PowerPoint.Application")
        app.Visible = 1
        deck = app.Presentations.Open(str(pptx_path), False, False, False)
        pp_save_as_pdf = 32
        deck.SaveAs(str(output_pdf), pp_save_as_pdf)
    except Exception as exc:
        return None, f"PowerPoint COM conversion failed: {exc}"
    finally:
        if deck is not None:
            try:
                deck.Close()
            except Exception:
                pass
        if app is not None:
            try:
                app.Quit()
            except Exception:
                pass

    if output_pdf.exists():
        return output_pdf, None
    return None, "PowerPoint COM finished but output PDF not found."


def convert_pptx_to_pdf(pptx_path: Path, output_dir: Path) -> tuple[Path, str]:
    temp_dir = output_dir / "_converted"
    temp_dir.mkdir(parents=True, exist_ok=True)

    pdf_path, err = _convert_pptx_with_soffice(pptx_path, temp_dir)
    if pdf_path:
        return pdf_path, "libreoffice"

    pdf_path, err2 = _convert_pptx_with_powerpoint(pptx_path, temp_dir)
    if pdf_path:
        return pdf_path, "powerpoint-com"

    details = " | ".join(x for x in [err, err2] if x)
    raise SystemExit(
        "Failed to convert .pptx to .pdf. Install LibreOffice (`soffice`) or pywin32 + Microsoft PowerPoint. "
        f"Details: {details}"
    )


def load_document(input_path: Path, output_dir: Path, args: argparse.Namespace) -> tuple[dict[str, Any], Path]:
    suffix = input_path.suffix.lower()

    if suffix == ".pdf":
        extracted = extract_pdf_document(
            input_path,
            enable_ocr=not args.disable_ocr,
            ocr_lang=args.ocr_lang,
            ocr_dpi=args.ocr_dpi,
            min_chars_for_native=args.min_chars_for_native,
            max_pages=args.max_pages,
        )
        return extracted, input_path

    if suffix == ".docx":
        return extract_docx_document(input_path), input_path

    if suffix == ".pptx":
        converted_pdf, converter = convert_pptx_to_pdf(input_path, output_dir)
        extracted = extract_pdf_document(
            converted_pdf,
            enable_ocr=not args.disable_ocr,
            ocr_lang=args.ocr_lang,
            ocr_dpi=args.ocr_dpi,
            min_chars_for_native=args.min_chars_for_native,
            max_pages=args.max_pages,
        )
        extracted["conversion_note"] = f"pptx->pdf via {converter} ({converted_pdf})"
        extracted["original_source_file"] = str(input_path)
        extracted["file_type"] = "pptx-via-pdf"
        return extracted, input_path

    if suffix == ".doc":
        raise SystemExit(".doc is not directly supported. Convert to .docx first, then rerun.")

    raise SystemExit(f"Unsupported file type: {suffix}. Supported: .pdf, .docx, .pptx")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prepare extraction + chunks + report for PDF/DOCX/PPTX understanding."
    )
    parser.add_argument("input", help="Path to input file (.pdf, .docx, or .pptx)")
    parser.add_argument("--output-dir", default="output/document-understanding", help="Output directory")

    parser.add_argument("--chunk-chars", type=int, default=3200, help="Target chunk size in characters")
    parser.add_argument("--overlap-chars", type=int, default=240, help="Chunk overlap in characters")

    parser.add_argument("--disable-ocr", action="store_true", help="Disable OCR fallback for PDF/PPTX-derived PDF")
    parser.add_argument("--ocr-lang", default="eng+chi_sim", help="Tesseract OCR language pack")
    parser.add_argument("--ocr-dpi", type=int, default=300, help="DPI used for OCR rendering")
    parser.add_argument("--min-chars-for-native", type=int, default=80, help="Use OCR when a page has too little text")
    parser.add_argument("--max-pages", type=int, default=None, help="Extract only first N pages for fast check")
    parser.add_argument("--fail-on-empty", action="store_true", help="Fail if no text is extracted")

    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    extracted, source_for_report = load_document(input_path, output_dir, args)
    extracted.setdefault("warnings", [])
    extracted["pipeline"] = {
        "skill_name": "pdf-word-reader-zh",
        "skill_version": SKILL_VERSION,
        "generated_at_utc": _utc_now_iso(),
        "input_file": str(input_path),
    }

    extracted_path = output_dir / "01_extracted.json"
    chunks_path = output_dir / "02_chunks.json"
    report_path = output_dir / "03_understanding_report.md"

    full_text = extracted.get("full_text", "")
    if args.fail_on_empty and not full_text.strip():
        raise SystemExit("No text extracted. Use OCR dependencies or verify the input file.")

    extracted_path.write_text(json.dumps(extracted, ensure_ascii=False, indent=2), encoding="utf-8")

    chunks = split_text_into_chunks(
        full_text,
        chunk_chars=args.chunk_chars,
        overlap_chars=args.overlap_chars,
    )

    chunks_payload = {
        "source_file": str(input_path),
        "processed_file": str(extracted.get("source_file", input_path)),
        "chunk_chars": args.chunk_chars,
        "overlap_chars": args.overlap_chars,
        "chunk_count": len(chunks),
        "total_chunk_chars": sum(chunk["char_count"] for chunk in chunks),
        "chunks": chunks,
        "pipeline": extracted.get("pipeline", {}),
    }
    chunks_path.write_text(json.dumps(chunks_payload, ensure_ascii=False, indent=2), encoding="utf-8")

    report = build_understanding_report(extracted, chunks, source_for_report)
    report_path.write_text(report, encoding="utf-8")

    print(f"Wrote: {extracted_path}")
    print(f"Wrote: {chunks_path}")
    print(f"Wrote: {report_path}")


if __name__ == "__main__":
    main()