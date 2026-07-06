#!/bin/bash
# Convert interview briefing MD → PDF
# Usage: ./pdf-pipeline.sh input.md [output.pdf]
# Requires: pandoc, Google Chrome / Chromium
# Cross-platform: macOS / Windows (Git Bash) / Linux

INPUT="${1:-template.md}"
OUTPUT="${2:-${INPUT%.md}.pdf}"
CSS_FILE="$(dirname "$0")/style.css"

if [ ! -f "$INPUT" ]; then
    echo "Usage: ./pdf-pipeline.sh <input.md> [output.pdf]"
    exit 1
fi

# Temp file — use $TMPDIR or /tmp
TMP_HTML="${TMPDIR:-/tmp}/interview_briefing_$$.html"

echo "=== MD → HTML ==="
# Inject CSS inline via style tag
if [ -f "$CSS_FILE" ]; then
    CSS_CONTENT=$(cat "$CSS_FILE")
else
    CSS_CONTENT=""
fi

pandoc "$INPUT" \
    -f markdown-tex_math_dollars \
    -t html5 \
    --standalone \
    --metadata title="Interview Briefing" \
    -H <(printf '<style>\n%s\n</style>\n' "$CSS_CONTENT") \
    -o "$TMP_HTML"

echo "=== HTML → PDF (Chrome headless) ==="

# Auto-detect Chrome path by OS
if [ "$(uname -s)" = "Darwin" ]; then
    CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif [ "$(uname -s)" = "Linux" ]; then
    CHROME="google-chrome"
elif [ "$(uname -o 2>/dev/null)" = "Msys" ] || command -v powershell &>/dev/null; then
    # Windows (Git Bash)
    CHROME="C:/Program Files/Google/Chrome/Application/chrome.exe"
else
    echo "WARNING: unknown OS, trying google-chrome"
    CHROME="google-chrome"
fi

"$CHROME" \
    --headless --disable-gpu --no-sandbox \
    --print-to-pdf="$OUTPUT" \
    --no-pdf-header-footer \
    "file://$TMP_HTML"

rm -f "$TMP_HTML"
echo "=== Done: $OUTPUT ==="
