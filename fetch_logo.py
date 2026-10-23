"""Get a named company's real logo for the cover, in its own colours.

  python3 fetch_logo.py <name> <domain> [--url <image url> ...]
      Collects candidates: the company's own site icons (web app manifest, apple-touch-icon, SVG/PNG favicon),
      any --url images you found yourself (the company's press or brand page, best first), and the single-colour
      Simple Icons mark. Saves assets/cand-<name>-<n>.png and ONE small sheet, cand-<name>.png. Look at that
      sheet once and pick the cleanest full-colour mark (no app-tile background, not a wordmark if an icon exists).
  python3 fetch_logo.py <name> --pick <n>
      Trims and saves the chosen candidate as assets/logo-<name>.png (600px max, transparency kept).
Use in the cover dict: mark="logo-<name>.png", mark_h=170. Note the logo's source URL in the posting notes.
"""
import sys, os, io, json, re, glob, base64, subprocess, urllib.request, urllib.parse
from PIL import Image, ImageDraw

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
os.makedirs("assets", exist_ok=True)
name = sys.argv[1]

if "--pick" in sys.argv:
    n = sys.argv[sys.argv.index("--pick") + 1]
    im = Image.open("assets/cand-%s-%s.png" % (name, n)).convert("RGBA")
    if im.getbbox(): im = im.crop(im.getbbox())
    im.thumbnail((600, 600), Image.LANCZOS); im.save("assets/logo-%s.png" % name)
    src = open("assets/cand-%s-%s.txt" % (name, n)).read() if os.path.exists("assets/cand-%s-%s.txt" % (name, n)) else "?"
    print("saved assets/logo-%s.png" % name, im.size, "source:", src); sys.exit()

dom = sys.argv[2].replace("https://", "").replace("http://", "").strip("/") if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
extra = [sys.argv[i + 1] for i, a in enumerate(sys.argv) if a == "--url"]


def get(u, t=20):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t).read()


def render_svg(data):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 600, "height": 600})
        pg.set_content("<html><body style='margin:0;background:transparent'><img id=i src='data:image/svg+xml;base64,%s' style='width:600px;height:600px;object-fit:contain'></body></html>" % base64.b64encode(data).decode())
        pg.wait_for_timeout(300); ok = pg.evaluate("document.getElementById('i').naturalWidth > 0")
        png = pg.screenshot(omit_background=True); b.close()
    if not ok: raise ValueError("svg did not render")
    return Image.open(io.BytesIO(png))


def load(u):
    data = get(u)
    if u.split("?")[0].lower().endswith(".svg") or data[:300].lstrip()[:5] in (b"<?xml", b"<svg ", b"<svg>"):
        return render_svg(data)
    im = Image.open(io.BytesIO(data))
    if im.format == "ICO":
        im = im.ico.getimage(max(im.ico.sizes()))
    return im.convert("RGBA")


cands = [(u, 9999) for u in extra]
if dom:
    base = "https://" + dom + "/"
    try:
        html = get(base).decode("utf-8", "ignore")
        for tag in re.findall(r"<link[^>]+>", html, flags=re.I):
            rel = (re.search(r'rel=["\']([^"\']+)', tag, re.I) or [None, ""])[1].lower()
            href = (re.search(r'href=["\']([^"\']+)', tag, re.I) or [None, ""])[1]
            if not href: continue
            u = urllib.parse.urljoin(base, href)
            if "manifest" in rel:
                try:
                    for ic in json.loads(get(u)).get("icons", []):
                        s = max([int(x.split("x")[0]) for x in ic.get("sizes", "0x0").split() if "x" in x] or [0])
                        cands.append((urllib.parse.urljoin(u, ic["src"]), s))
                except Exception: pass
            elif "icon" in rel:
                sz = (re.search(r'sizes=["\']([^"\']+)', tag) or [None, "0x0"])[1]
                s = max([int(x.split("x")[0]) for x in sz.split() if "x" in x and x.split("x")[0].isdigit()] or [0])
                cands.append((u, 1000 if u.split("?")[0].endswith(".svg") else s or (180 if "apple" in rel else 32)))
    except Exception as e:
        print("homepage failed:", str(e)[:80])
    cands += [(base + "apple-touch-icon.png", 180), (base + "favicon.svg", 1000)]

for f in glob.glob("assets/cand-%s-*" % name): os.remove(f)
seen, got, prints = set(), [], set()
for u, s in sorted(cands, key=lambda c: -c[1]):
    if u in seen or len(got) >= 5: continue
    seen.add(u)
    try:
        im = load(u)
        fp = list(im.convert("L").resize((10, 10)).tobytes())
        dup = any(sum(abs(a - b) for a, b in zip(fp, q)) < 600 for q in prints)
        if im.getbbox() and im.size[0] >= 96 and not dup:
            prints.add(tuple(fp)); got.append((u, im))
    except Exception as e:
        print("skip", u[:80], str(e)[:50])
slug = name.lower()
if os.path.exists("node_modules/simple-icons/icons/%s.svg" % slug):
    si = "assets/cand-%s-si.png" % name  # not assets/logo-<slug>.png: that may be the true-colour mark get_logos.py built
    if subprocess.run([sys.executable, "logo.py", slug, si], capture_output=True).returncode == 0:
        got.append(("Simple Icons (single colour): " + slug, Image.open(si).convert("RGBA")))

if not got:
    print("NO CANDIDATES for", name, "- find the company's press/brand page and pass --url"); sys.exit(1)
T = 220; sheet = Image.new("RGB", (T * len(got), T + 40), (247, 244, 236)); d = ImageDraw.Draw(sheet)
for i, (u, im) in enumerate(got):
    im.save("assets/cand-%s-%d.png" % (name, i)); open("assets/cand-%s-%d.txt" % (name, i), "w").write(u)
    t = im.copy(); t.thumbnail((T - 30, T - 30)); sheet.paste(t, (i * T + 15, 15), t); d.text((i * T + 15, T + 10), str(i), fill=(23, 86, 169))
    print(i, im.size, u)
sheet.save("cand-%s.png" % name); print("sheet: cand-%s.png  then: python3 fetch_logo.py %s --pick <n>" % (name, name))
