"""python3 text.py <url> [grep word] : a page's rendered text (main, else body), for pages WebFetch returns without their body. With a grep word, only matching lines and two lines either side."""
import sys, re
from playwright.sync_api import sync_playwright
url = sys.argv[1]; word = sys.argv[2] if len(sys.argv) > 2 else None
with sync_playwright() as p:
    br = p.chromium.launch(); pg = br.new_page()
    pg.goto(url, wait_until="load", timeout=60000)
    try: pg.wait_for_load_state("networkidle", timeout=15000)
    except Exception: pass
    t = pg.inner_text("main") if pg.locator("main").count() else pg.inner_text("body")
    br.close()
lines = [l for l in t.splitlines() if l.strip()]
if word:
    keep = sorted({j for i, l in enumerate(lines) if re.search(word, l, re.I) for j in range(max(0, i - 2), min(len(lines), i + 3))})
    lines = [lines[i] for i in keep]
print("\n".join(lines)[:8000])
