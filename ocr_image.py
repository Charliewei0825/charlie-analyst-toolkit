#!/usr/bin/env python3
"""
Cloud OCR —— 多模态图片/扫描件文字识别
============================================
对接阿里云 & 腾讯云 OCR API，用于 charlie-analyst-toolkit 各模式下
将图片嵌入的 PDF 页面、截图表格、扫描件转为可提取的结构化文本。

每月免费额度：
  阿里云：1000 次/月（通用文字识别）
  腾讯云：1000 次/月（每项服务独立计算）

安装依赖（二选一，按需）：
  # 阿里云
  pip3 install --break-system-packages alibabacloud_ocr_api20210707

  # 腾讯云
  pip3 install --break-system-packages tencentcloud-sdk-python

配置文件 ~/.ocr_config.json：
{
  "alibaba": {
    "access_key_id":     "LTAI5t...",
    "access_key_secret": "..."
  },
  "tencent": {
    "secret_id":  "AKID...",
    "secret_key": "..."
  },
  "default": "alibaba"
}

用法：
  python3 ocr_image.py image.png                          # 默认阿里云，输出纯文本
  python3 ocr_image.py image.png --provider tencent       # 腾讯云
  python3 ocr_image.py image.png --output json            # JSON 输出（含坐标）
  python3 ocr_image.py scan.pdf --pages 1,3,5             # PDF 指定页（需先 pdftoimage）
"""

import os
import sys
import json
import base64
import argparse
from pathlib import Path
from typing import Optional

CONFIG_PATH = Path.home() / ".ocr_config.json"


# ── helpers ──────────────────────────────────────────────────────────

def _b64(path: str) -> str:
    """Read any file → base64 string."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def _load_cfg(provider: str) -> dict:
    if not CONFIG_PATH.exists():
        _die(f"配置文件不存在: {CONFIG_PATH}\n"
             f"请创建并写入 {provider} 的 API keys。格式见脚本头部注释。")
    cfg = json.loads(CONFIG_PATH.read_text())
    p = cfg.get(provider)
    if not p:
        _die(f"配置中未找到 '{provider}' 段。可用 provider: {[k for k in cfg if k != 'default']}")
    return p


def _die(msg: str):
    print(msg, file=sys.stderr)
    sys.exit(1)


# ── 阿里云 ───────────────────────────────────────────────────────────

def ocr_alibaba(image_path: str, cfg: dict) -> str:
    """阿里云 · 通用文字识别（RecognizeGeneral）。"""
    try:
        from alibabacloud_ocr_api20210707.client import Client
        from alibabacloud_ocr_api20210707 import models as ocr_models
        from alibabacloud_tea_openapi import models as open_api_models
    except ImportError:
        _die("缺少阿里云 OCR SDK。运行:\n"
             "  pip3 install --break-system-packages alibabacloud_ocr_api20210707")

    config = open_api_models.Config(
        access_key_id=cfg["access_key_id"],
        access_key_secret=cfg["access_key_secret"],
        endpoint="ocr-api.cn-hangzhou.aliyuncs.com",
    )
    client = Client(config)

    # body 直接传 base64 字符串（非 dict）
    req = ocr_models.RecognizeGeneralRequest()
    req.body = _b64(image_path)
    resp = client.recognize_general(req)
    data = resp.body.data

    if not data or not data.content:
        return ""

    raw = data.content
    if isinstance(raw, str):
        raw = json.loads(raw)

    lines = []
    # 阿里云 OCR 返回块级结构：{"content": "...", "confidence": 0.99, ...}
    if isinstance(raw, list):
        for block in raw:
            text = block.get("content", block.get("text", ""))
            conf = block.get("confidence", block.get("rate", 0))
            if text.strip():
                prefix = f"[{conf:.0%}] " if conf else ""
                lines.append(f"{prefix}{text}")
    elif isinstance(raw, dict):
        text = raw.get("content", raw.get("text", str(raw)))
        lines.append(text)
    return "\n".join(lines)


# ── 腾讯云 ───────────────────────────────────────────────────────────

def ocr_tencent(image_path: str, cfg: dict) -> str:
    """腾讯云 · 通用印刷体识别（GeneralBasicOCR）。"""
    try:
        from tencentcloud.common import credential
        from tencentcloud.ocr.v20181119 import ocr_client, models
    except ImportError:
        _die("缺少腾讯云 OCR SDK。运行:\n"
             "  pip3 install --break-system-packages tencentcloud-sdk-python")

    cred = credential.Credential(cfg["secret_id"], cfg["secret_key"])
    client = ocr_client.OcrClient(cred, "ap-guangzhou")

    req = models.GeneralBasicOCRRequest()
    req.ImageBase64 = _b64(image_path)

    resp = client.GeneralBasicOCR(req)
    result = json.loads(resp.to_json_string())

    lines = []
    for item in result.get("TextDetections", []):
        text = item.get("DetectedText", "")
        conf = item.get("Confidence", 0)
        if text.strip():
            # 腾讯云置信度 0-100，阿里云 0-1
            conf_pct = conf / 100 if conf > 1 else conf
            lines.append(f"[{conf_pct:.0%}] {text}")
    return "\n".join(lines)


# ── 主入口 ───────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Cloud OCR —— 阿里云 / 腾讯云图片文字识别"
    )
    parser.add_argument("image", help="图片路径（支持 jpg/png/bmp/pdf）")
    # 从 config 读取默认 provider
    default_provider = "tencent"
    if CONFIG_PATH.exists():
        cfg_all = json.loads(CONFIG_PATH.read_text())
        default_provider = cfg_all.get("default", "tencent")

    parser.add_argument(
        "--provider", default=default_provider, choices=["alibaba", "tencent"],
        help=f"云服务商（默认 {default_provider}）",
    )
    parser.add_argument(
        "--output", default="text", choices=["text", "json"],
        help="输出格式：text=纯文本, json=结构化",
    )
    parser.add_argument(
        "--pages", default=None,
        help="PDF 指定页（逗号分隔，如 1,3,5）。需配合 pdftoppm 使用。",
    )
    args = parser.parse_args()

    cfg = _load_cfg(args.provider)

    # PDF → image 转换（如果输入是 PDF）
    image_path = args.image
    if args.pages:
        # 这里只做占位说明：实际先用 pdftoppm 拆页，再对每页调 OCR
        print("[ocr_image] PDF 多页模式：请先用 pdftoppm 拆页后再对每张图片调用本脚本。",
              file=sys.stderr)
        print("[ocr_image] 示例: pdftoppm -png -f 3 -l 5 report.pdf page",
              file=sys.stderr)
        sys.exit(1)

    if args.provider == "alibaba":
        text = ocr_alibaba(image_path, cfg)
    else:
        text = ocr_tencent(image_path, cfg)

    if args.output == "json":
        result = {
            "text": text,
            "provider": args.provider,
            "image": str(Path(image_path).resolve()),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(text)


if __name__ == "__main__":
    main()
