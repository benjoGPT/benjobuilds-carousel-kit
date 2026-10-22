#!/usr/bin/env bash
# One-command setup for the daily carousel run. Usage: bash setup.sh <workdir>
set -e
KIT="$(cd "$(dirname "$0")" && pwd)"; WD="${1:-$HOME/work}"
mkdir -p "$WD/assets" "$WD/shots" && cd "$WD"
cp "$KIT"/*.py .
[ -d node_modules/geist ] || { npm init -y >/dev/null; npm i geist lucide-static simple-icons >/dev/null 2>&1; }
cp node_modules/geist/dist/fonts/geist-sans/Geist-Variable.ttf assets/
cp "$KIT"/assets/*.png assets/ 2>/dev/null || true   # brand logos kept in the repo (e.g. logo-google.png, four-colour)
for n in lake-pine stone-arch mountain-valley mountain-water lake-waterfall faq-bridge; do
  curl -sSfL -o assets/$n.webp https://www.benjobuilds.com/landscapes/$n.webp || echo "ENGRAVING MISSING $n"; done
python3 -c "from PIL import Image;import glob;[Image.open(f).convert('RGB').save(f[:-5]+'.png') for f in glob.glob('assets/*.webp')]"
pip install -q pyoxipng --break-system-packages 2>/dev/null || pip install -q pyoxipng
echo "READY in $WD"
