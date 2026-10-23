#!/usr/bin/env bash
# One-command setup for the daily carousel run. Usage: bash setup.sh <workdir>   (safe to re-run in the same workdir)
set -e
KIT="$(cd "$(dirname "$0")" && pwd)"; WD="${1:-$HOME/work}"
mkdir -p "$WD/assets" "$WD/shots" && cd "$WD"
[ "$(pwd -P)" = "$(cd "$KIT" && pwd -P)" ] || cp "$KIT"/*.py .
[ -d node_modules/geist ] && [ -d node_modules/lucide-static ] && [ -d node_modules/simple-icons ] || {
  [ -f package.json ] || npm init -y >/dev/null; npm i geist@1 lucide-static@0 simple-icons@16 >/dev/null 2>&1; }   # simple-icons@16: the version MANIFEST in get_logos.py is checked against
cp node_modules/geist/dist/fonts/geist-sans/Geist-Variable.ttf assets/
cp "$KIT"/assets/*.png assets/ 2>/dev/null || true   # brand logos kept in the repo (e.g. logo-google.png, four-colour)
for n in lake-pine stone-arch mountain-valley mountain-water lake-waterfall faq-bridge; do
  [ -s assets/$n.png ] && continue
  curl -sSfL --retry 2 -o assets/$n.webp.part https://www.benjobuilds.com/landscapes/$n.webp && mv assets/$n.webp.part assets/$n.webp || { rm -f assets/$n.webp.part; echo "ENGRAVING MISSING $n"; }; done
KIT="$KIT" python3 get_logos.py 2>&1 | grep -E "MISSING|FAIL|Error" || true   # cached brand marks -> assets/logo-<slug>.png
python3 -c "
from PIL import Image;import glob,os
for f in glob.glob('assets/*.webp'):
    try: Image.open(f).convert('RGB').save(f[:-5]+'.png')
    except Exception as e: os.remove(f); print('ENGRAVING MISSING', os.path.basename(f)[:-5], str(e)[:60])"
python3 -m pip install -q pyoxipng --break-system-packages 2>/dev/null || python3 -m pip install -q pyoxipng 2>/dev/null || echo "pyoxipng not installed (optional)"
echo "READY in $WD"
