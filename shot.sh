#!/bin/bash
# Render the figure to PNG at 2x. Usage: ./shot.sh
set -e
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=8742
python3 -m http.server $PORT --directory "$DIR" >/dev/null 2>&1 &
SRV=$!; trap 'kill $SRV 2>/dev/null || true' EXIT
sleep 1
"$CHROME" --headless --disable-gpu --hide-scrollbars --force-device-scale-factor=2 \
  --window-size=1172,853 --virtual-time-budget=6000 \
  --screenshot="$DIR/figure.png" "http://127.0.0.1:$PORT/index.html" 2>/dev/null
sips -c 1602 2240 "$DIR/figure.png" --out "$DIR/figure.png" >/dev/null
echo "figure.png"
