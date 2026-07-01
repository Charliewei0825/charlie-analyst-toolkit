#!/bin/bash
# Convert interview briefing MD → PDF
# Usage: ./pdf-pipeline.sh input.md [output.pdf]
# Requires: pandoc, Google Chrome

INPUT="${1:-template.md}"
OUTPUT="${2:-${INPUT%.md}.pdf}"
CSS_FILE="$(dirname "$0")/style.css"

if [ ! -f "$INPUT" ]; then
    echo "Usage: ./pdf-pipeline.sh <input.md> [output.pdf]"
    exit 1
fi

TMP_HTML="/tmp/interview_briefing_$$.html"

echo "=== MD → HTML ==="
pandoc "$INPUT" \
    -f markdown-tex_math_dollars \
    -t html5 \
    --standalone \
    -H <(cat "$CSS_FILE" | sed 's/^/<style>/;s/$/<\/style>/') \
    -o "$TMP_HTML"

echo "=== HTML → PDF (Chrome headless) ==="
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --headless --disable-gpu --no-sandbox \
    --print-to-pdf="$OUTPUT" \
    --no-pdf-header-footer \
    "file://$TMP_HTML"

rm -f "$TMP_HTML"
echo "=== Done: $OUTPUT ==="
