import sys, urllib.request
from PIL import Image
cmd = sys.argv[1]
if cmd in ("list", "shot"):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        br = p.chromium.launch()
        w = int(sys.argv[4]) if cmd == "shot" and len(sys.argv) > 4 else (1200 if cmd == "list" else 560)
        pg = br.new_page(viewport={"width": w, "height": 1400}, device_scale_factor=3 if cmd == "shot" else 1)
        r = pg.goto(sys.argv[2], wait_until="networkidle", timeout=45000); pg.wait_for_timeout(1200)
        print("status", r.status if r else None, "|", pg.title())
        if cmd == "list":
            for i in pg.evaluate("Array.from(document.images).filter(i=>i.naturalWidth>600).map(i=>[i.currentSrc,i.naturalWidth,i.naturalHeight,i.alt])"): print(i)
        else:
            pg.screenshot(path=sys.argv[3], full_page=True); print(Image.open(sys.argv[3]).size)
        br.close()
elif cmd == "get":
    req = urllib.request.Request(sys.argv[2], headers={"User-Agent": "Mozilla/5.0"})
    open(sys.argv[3], "wb").write(urllib.request.urlopen(req, timeout=60).read()); print(Image.open(sys.argv[3]).size)
elif cmd == "crop":
    Image.open(sys.argv[2]).convert("RGB").crop(tuple(int(v) for v in sys.argv[4:8])).save(sys.argv[3]); print(Image.open(sys.argv[3]).size)
