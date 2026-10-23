"""Build the cached brand-mark library: python3 get_logos.py [slug ...] [--sheet]
Writes assets/logo-<slug>.png (true colour, transparent, 600px max). Mono brands use the official glyph from Simple Icons in the
brand's own hex; multi-colour and official-body marks come from Wikimedia Commons (first URL that works). Marks that cannot be fetched are skipped with MISSING; the run then uses fetch_logo.py. Run by setup.sh.
Look at logos-sheet.png once (--sheet) when adding a mark."""
import sys, os, io, json, time, base64, urllib.request, urllib.parse
from PIL import Image, ImageDraw
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/126 Safari/537.36"}
C = "https://commons.wikimedia.org/wiki/Special:FilePath/"
# slug -> ("si", simple-icons slug) or ("url", [candidate urls, best first])
MANIFEST = {
 "google": ("url", [C + "Google_%22G%22_logo.svg", C + "Google_Favicon_2025.svg", C + "Google_%22G%22_Logo.svg"]),
 "microsoft": ("url", [C + "Microsoft_logo.svg", C + "Microsoft_logo_(2012).svg"]),
 "instagram": ("url", [C + "Instagram_logo_2016.svg", C + "Instagram_icon.png"]),
 "meta": ("si", "meta"), "facebook": ("si", "facebook"), "whatsapp": ("si", "whatsapp"), "youtube": ("si", "youtube"),
 "linkedin": ("url", [C + "LinkedIn_icon.svg", C + "LinkedIn_icon_circle.svg"]), "tiktok": ("si", "tiktok"), "stripe": ("si", "stripe"), "paypal": ("si", "paypal"),
 "shopify": ("si", "shopify"), "wix": ("si", "wix"), "wordpress": ("si", "wordpress"), "squarespace": ("si", "squarespace"),
 "xero": ("si", "xero"), "quickbooks": ("si", "quickbooks"), "cloudflare": ("si", "cloudflare"), "godaddy": ("si", "godaddy"),
 "mailchimp": ("si", "mailchimp"), "trustpilot": ("si", "trustpilot"),
 "ico": ("url", [C + "Information_Commissioner%27s_Office_logo.svg"]),
 # HMRC, Companies House, Ofcom, OpenAI: no clean Commons file found (23 Oct 2026). Use fetch_logo.py <name> <domain> --url <press-page image>.
}
def get(u, tries=3):
    for k in range(tries):  # Wikimedia answers 429 when hit quickly: back off briefly, then give up (caller prints MISSING)
        try: return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=25).read()
        except Exception:
            if k == tries - 1: raise
            time.sleep(2 * (k + 1))
def render(pg, svg_or_png, kind):
    if kind == "svg":
        pg.set_content("<html><body style='margin:0;background:transparent'><img id=i src='data:image/svg+xml;base64,%s' style='width:600px;height:600px;object-fit:contain'></body></html>" % base64.b64encode(svg_or_png).decode())
        pg.wait_for_timeout(250)
        if not pg.evaluate("document.getElementById('i').naturalWidth > 0"): raise ValueError("svg did not render")
        return Image.open(io.BytesIO(pg.screenshot(omit_background=True))).convert("RGBA")
    return Image.open(io.BytesIO(svg_or_png)).convert("RGBA")
def si_svg(slug):
    svg = open("node_modules/simple-icons/icons/%s.svg" % slug).read()
    d = json.load(open("node_modules/simple-icons/data/simple-icons.json")); d = d.get("icons", d) if isinstance(d, dict) else d
    hexc = [i for i in d if i.get("slug") == slug or i["title"].lower() == slug][0]["hex"]
    return svg.replace("<svg ", '<svg fill="#%s" width="600" height="600" ' % hexc, 1).encode()
def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]; os.makedirs("assets", exist_ok=True)
    todo = args or list(MANIFEST); done = []
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 600, "height": 600})
        for s in todo:
            im = None; used = None
            if s not in MANIFEST: print("MISSING", s, "(not in MANIFEST)"); continue
            kind, src = MANIFEST[s]
            try:
                if kind == "si": im = render(pg, si_svg(src), "svg"); used = "simple-icons:" + src
                else:
                    loc = os.path.join(os.environ.get("KIT") or os.path.dirname(os.path.abspath(__file__)), "svg", s + ".svg")  # committed copy first (Wikimedia rate-limits)
                    if os.path.exists(loc):
                        try: im = render(pg, open(loc, "rb").read(), "svg"); used = loc
                        except Exception: im = None
                    for u in ([] if im is not None and im.getbbox() else src):
                        try:
                            data = get(u); k = "png" if data[:4] == b"\x89PNG" else "svg"
                            im = render(pg, data, k); used = u
                            if im.getbbox(): break
                        except Exception: im = None
            except Exception as e: print("FAIL", s, str(e)[:60])
            if im is None or not im.getbbox(): print("MISSING", s); continue
            im = im.crop(im.getbbox()); im.thumbnail((600, 600), Image.LANCZOS); im.save("assets/logo-%s.png" % s)
            done.append((s, im)); print("ok", s, im.size, used)
        b.close()
    if "--sheet" in sys.argv and done:
        T = 170; cols = 6; rows = (len(done) + cols - 1) // cols
        sh = Image.new("RGB", (T * cols, (T + 24) * rows), (247, 244, 236)); d = ImageDraw.Draw(sh)
        for i, (s, im) in enumerate(done):
            t = im.copy(); t.thumbnail((T - 24, T - 24)); x, y = (i % cols) * T, (i // cols) * (T + 24)
            sh.paste(t, (x + 12, y + 8), t); d.text((x + 12, y + T - 8), s, fill=(23, 86, 169))
        sh.save("logos-sheet.png"); print("sheet: logos-sheet.png")
main()
