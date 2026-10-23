#!/usr/bin/env bash
# Smoke test: bash tests/smoke.sh   (needs npm, python3 + playwright chromium, and network for setup; the GOV.UK clip test skips if offline)
set -uo pipefail
KIT="$(cd "$(dirname "$0")/.." && pwd)"; T="$(mktemp -d)"; WD="$T/work"; FAILS=0
ok() { echo "PASS  $*"; }
bad() { echo "FAIL  $*"; FAILS=$((FAILS+1)); }
trap 'rm -rf "$T"' EXIT

echo "== setup (from another folder, then re-run from the kit folder)"
(cd "$T" && bash "$KIT/setup.sh" "$WD") > "$T/setup1.log" 2>&1 && grep -q READY "$T/setup1.log" && ok "setup.sh first run" || { cat "$T/setup1.log"; bad "setup.sh first run"; }
(cd "$KIT" && bash setup.sh "$WD") > "$T/setup2.log" 2>&1 && grep -q READY "$T/setup2.log" && ok "setup.sh re-run (idempotent)" || { cat "$T/setup2.log"; bad "setup.sh re-run"; }
grep -hE "MISSING|FAIL|Error" "$T/setup1.log" "$T/setup2.log" | sed 's/^/      /'
for f in logo-google.png logo-xero.png logo-ico.png logo-linkedin.png Geist-Variable.ttf \
         lake-pine.png stone-arch.png mountain-valley.png mountain-water.png lake-waterfall.png faq-bridge.png; do
  [ -s "$WD/assets/$f" ] && ok "assets/$f" || bad "assets/$f missing"
done

echo "== render"
cd "$WD"
python3 "$KIT/tests/story_smoke.py" > "$T/render.log" 2>&1; rc=$?; sed 's/^/      /' "$T/render.log"
[ $rc -eq 0 ] && ok "render exit 0" || bad "render exited $rc"
grep -q "SMALL IMAGE source" "$T/render.log" && ok "SMALL IMAGE warning on the tall source image" || bad "no SMALL IMAGE warning"
grep -q "MISSING IMAGE" "$T/render.log" && bad "a logo or image failed to load" || ok "every image loaded"
grep -qE "OVERFLOW|UNDERFILL|SHORT LAST LINE" "$T/render.log" && bad "layout warnings on a story that should be clean" || ok "no OVERFLOW / UNDERFILL / SHORT LAST LINE"
python3 - "$WD/out/smoke" <<'EOF' && ok "7 PNGs 01-..07-.., all 1080x1440" || bad "slide PNGs wrong (see above)"
import os, sys, re
from PIL import Image
fs = sorted(f for f in os.listdir(sys.argv[1]) if f.endswith(".png"))
print("      ", fs)
assert [f[:3] for f in fs] == ["%02d-" % i for i in range(1, 8)], "expected 01-..07-"
for f in fs:
    s = Image.open(os.path.join(sys.argv[1], f)).size
    assert s == (1080, 1440), (f, s)
EOF
python3 contact_sheet.py smoke > /dev/null && [ -s contact_smoke.png ] && ok "contact_sheet.py" || bad "contact_sheet.py"

echo "== clip (local page: cookie banner, collapsed section, end text also above the start)"
cat > "$T/page.html" <<'EOF'
<html><body style="margin:0;font:16px sans-serif">
<div style="position:fixed;bottom:0;left:0;right:0;height:300px;background:#000;color:#fff">We use cookies <button onclick="this.parentNode.remove()">Accept all</button></div>
<p>7 May</p><div style="height:2000px"></div>
<details><summary>Update periods</summary><table><tr><th>Standard update period</th><th>Deadline</th></tr>
<tr><td>6 April to 5 July</td><td>7 August</td></tr><tr><td>6 April to 5 April</td><td>7 May (the following tax year)</td></tr></table></details>
<div style="height:3000px"></div><p>7 May.</p></body></html>
EOF
python3 clip.py "file://$T/page.html" "$T/local.png" "Standard update period" "7 May" > "$T/clip0.log" 2>&1; rc=$?; sed 's/^/      /' "$T/clip0.log"
H=$(python3 -c "from PIL import Image;print(Image.open('$T/local.png').size[1])" 2>/dev/null || echo 0)
[ $rc -eq 0 ] && [ "$H" -ge 150 ] && [ "$H" -le 600 ] && ok "local clip height $H px" || bad "local clip (exit $rc, height $H, want 150-600)"

echo "== clip (GOV.UK, network)"
URL=https://www.gov.uk/guidance/use-making-tax-digital-for-income-tax/send-quarterly-updates
if curl -sfI --max-time 10 "$URL" > /dev/null; then
  python3 clip.py "$URL" shots/smoke-mtd.png "Standard update period" "7 May" > "$T/clip.log" 2>&1; rc=$?; sed 's/^/      /' "$T/clip.log"
  H=$(python3 -c "from PIL import Image;print(Image.open('shots/smoke-mtd.png').size[1])" 2>/dev/null || echo 0)
  [ $rc -eq 0 ] && [ "$H" -ge 500 ] && [ "$H" -le 3000 ] && ok "GOV.UK clip height $H px" || bad "GOV.UK clip (exit $rc, height $H, want 500-3000)"
else
  echo "SKIP  GOV.UK clip: offline"
fi

echo
[ $FAILS -eq 0 ] && { echo "SMOKE TEST PASSED"; exit 0; } || { echo "SMOKE TEST FAILED: $FAILS check(s)"; exit 1; }
