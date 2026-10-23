"""Benjo Builds carousel kit v2 (copied from project doc carousel-kit-site-down-fallback.py, 13 Oct 2026 run).
Only change: matrix/bars no longer print a "My read:" label (design notes v3 forbid opinion labels); 'read' renamed 'note', optional."""
import os, re, sys
from playwright.sync_api import sync_playwright
from PIL import Image

W = os.path.dirname(os.path.abspath(__file__))
A = "file://" + W + "/assets/"
ICONS = W + "/node_modules/lucide-static/icons/"
M = 72


def ic(name, size=64, sw=1.5):
    if name.endswith(".png"):  # a real brand mark from assets/ (e.g. "logo-xero.png") instead of a Lucide icon, true colour
        return "<img src='%s%s' style='flex:none;display:block;height:%dpx;width:auto;max-width:%dpx;object-fit:contain'>" % (A, name, size, int(size * 1.6))
    s = re.sub(r"<!--.*?-->", "", open(ICONS + name + ".svg").read(), flags=re.S)
    s = re.sub(r'width="24"', 'width="%d"' % size, s, count=1)
    s = re.sub(r'height="24"', 'height="%d"' % size, s, count=1)
    return s.replace('stroke-width="2"', 'stroke-width="%s"' % sw).replace("<svg", "<svg style='flex:none;display:block'", 1)


def has_art(name):
    return bool(name) and os.path.exists(os.path.join(W, "assets", name + ".png"))


CSS = """
@font-face{font-family:'Geist';src:url('%sGeist-Variable.ttf') format('truetype');font-weight:100 900}
*{box-sizing:border-box;margin:0;padding:0}
:root{--paper:#F7F4EC;--blue:#1756A9;--line:rgba(23,86,169,.38)}
html,body{width:1080px;height:1440px;background:var(--paper)}
.s{width:1080px;height:1440px;position:relative;overflow:hidden;background:var(--paper);color:var(--blue);--fg:var(--blue);--bg:var(--paper);
   font-family:'Geist',sans-serif;font-weight:400;font-size:40px;line-height:1.38;-webkit-font-smoothing:antialiased}
.s.inv{background:var(--blue);color:var(--paper);--fg:var(--paper);--bg:var(--blue)}
.abs{position:absolute}
.h{font-weight:510;letter-spacing:-0.055em;line-height:.98}
.out{font-weight:400;letter-spacing:.01em;line-height:1.08;color:var(--bg);-webkit-text-stroke:4px var(--fg);paint-order:stroke fill;white-space:nowrap}
.eb{font-weight:720;font-size:23px;letter-spacing:.17em;text-transform:uppercase;line-height:1.25}
.t{font-weight:540;letter-spacing:-0.04em;line-height:1.06}
.b{font-size:40px;line-height:1.38}
.sm{font-size:34px;line-height:1.38}
.st{font-weight:650}
.rule{position:absolute;height:1px;background:var(--fg)}
.rule.q{background:var(--line)}
.vr{position:absolute;width:1px;background:var(--fg)}
.btn{display:inline-flex;align-items:center;gap:14px;background:var(--fg);color:var(--bg);font-weight:650;font-size:36px;padding:0 34px;height:88px;white-space:nowrap}
.art{position:absolute;background-size:cover;background-repeat:no-repeat}
.box{border:1px solid var(--fg)}
""" % A


def page(inner, n, total, section, inv=False, foot_chip=False):
    # design B: handle and page count sit on the header rule, top right; Instagram's tag avatars and dots cover the bottom-left corner
    chrome = ("<div class='abs eb' style='left:%dpx;top:78px'>%02d / %s</div><div class='rule' style='left:%dpx;right:%dpx;top:128px'></div>"
              "<div class='abs eb' style='right:%dpx;top:78px;font-weight:650;letter-spacing:.12em'>@benjobuilds · %02d / %02d</div>"
              % (M, n, section, M, M, M, n, total))
    if n == 1:  # swipe cue on the cover, a paper chip on the engraving band
        chrome += ("<div class='abs eb' style='right:%dpx;bottom:56px;display:flex;align-items:center;gap:10px;background:var(--paper);padding:12px 16px'>Swipe %s</div>"
                   % (M, ic("arrow-right", 28, 2)))
    return ("<!doctype html><html><head><meta charset='utf-8'><style>%s</style></head><body><div class='s%s'>%s%s</div></body></html>"
            % (CSS, " inv" if inv else "", inner, chrome))


def art(name, x, y, w, h, pos="50% 50%"):
    return "<div class='art' style='left:%dpx;top:%dpx;width:%dpx;height:%dpx;background-image:url(%s%s.png);background-position:%s'></div>" % (x, y, w, h, A, name, pos)


def head(text, size=96, top=178, width=936):
    return "<div class='abs h' style='left:%dpx;top:%dpx;font-size:%dpx;width:%dpx'>%s</div>" % (M - 3, top, size, width, text)


ARTS = ["lake-pine", "stone-arch", "mountain-valley", "mountain-water", "lake-waterfall", "faq-bridge"]


def cover(d):
    o = ("<div class='abs h' style='left:%dpx;top:176px;font-size:%dpx;white-space:nowrap'>%s</div>" % (M - 8, d.get("size", 164), d["line1"])
         + "<div class='abs h out' style='left:%dpx;top:%dpx;font-size:%dpx'>%s</div>" % (M - 2, 176 + d.get("size", 164) + 6, d.get("size2", 140), d["line2"])
         + "<div class='abs' style='left:%dpx;top:570px;width:%dpx'><div class='b' style='font-size:42px'>%s</div>%s</div>" % (M, d.get("sf_width", 800), d["standfirst"],
            ("<img src='%s%s' style='display:block;margin-top:34px;height:%dpx;width:auto'>" % (A, d["logo"], d.get("logo_h", 64))) if d.get("logo") else ""))
    if d.get("mark"):  # the subject's icon (e.g. Google's G) sits in the open space to the right of the second headline line
        s1 = d.get("size", 164); mh = d.get("mark_h", 190)
        o += "<img src='%s%s' style='position:absolute;right:%dpx;top:%dpx;height:%dpx;width:auto'>" % (A, d["mark"], M + 10, 176 + s1 + 6 + int(d.get("size2", 140) * 0.85) - mh // 2, mh)
    if has_art(d.get("art", "lake-pine")):
        return o + art(d.get("art", "lake-pine"), 0, 880, 1080, 560, d.get("art_pos", "50% 46%")) + "<div class='rule' style='left:0;right:0;top:880px'></div>"
    lab, l1, l2 = d["facts"]
    return (o + "<div class='rule' style='left:%dpx;right:%dpx;top:900px'></div>" % (M, M)
            + "<div class='abs' style='left:%dpx;top:968px'>%s</div>" % (M - 12, ic(d["icon"], 300, 0.8))
            + "<div class='abs' style='left:440px;top:990px;right:%dpx'><div class='eb'>%s</div><div class='t' style='font-size:58px;margin-top:22px'>%s</div>"
              "<div class='b' style='margin-top:16px;font-size:42px'>%s</div></div>" % (M, lab, l1, l2))


def bigfact(d):
    f = "".join("<div style='flex:1;%s'><div class='eb'>%s</div><div class='b' style='margin-top:14px'>%s</div></div>"
                % ("padding-right:28px" if i == 0 else "border-left:1px solid var(--fg);padding-left:28px", a, b) for i, (a, b) in enumerate(d["facts"]))
    size = d.get("size", 440)
    ctx = ("<div class='b' style='margin:30px 0 0 15px;font-size:44px;line-height:1.3;width:900px'>%s</div>" % d["context"]) if d.get("context") else ""
    return ("<div class='abs bigflow' style='left:%dpx;top:170px;width:960px'>" % (M - 18)
            + "<div class='h fig' style='font-size:%dpx;letter-spacing:-.075em;white-space:nowrap;line-height:.86'>%s</div>" % (size, d["figure"])
            + "<div class='h' style='margin:%dpx 0 0 15px;font-size:84px;width:920px'>%s</div>" % (d.get("gap", 56), d["statement"])
            + ctx + "</div>"
            + "<div class='rule' style='left:%dpx;right:%dpx;top:1040px'></div><div class='abs' style='left:%dpx;right:%dpx;top:1072px;display:flex'>%s</div>" % (M, M, M, M, f))


def process(d):
    n = len(d["steps"]); gap = d.get("gap") or (min(300, (1130 - 440) // (n - 1)) if n > 1 else 250)
    o = head(d["headline"]) + "<div class='vr' style='left:%dpx;top:440px;height:%dpx'></div>" % (M + 60, gap * (n - 1) + 120)
    for i, (icn, t, b) in enumerate(d["steps"]):
        y = 440 + i * gap
        o += ("<div class='abs box' style='left:%dpx;top:%dpx;width:120px;height:120px;background:var(--bg);display:flex;align-items:center;justify-content:center'>%s</div>"
              "<div class='abs' style='left:232px;top:%dpx;right:%dpx'><div class='t' style='font-size:46px'><span style='font-weight:400'>%02d /</span> %s</div><div class='sm' style='margin-top:12px;font-size:36px'>%s</div></div>"
              % (M, y, ic(icn, 76, 1.5), y - 2, M, i + 1, t, b))
        if i < n - 1:
            o += "<div class='rule q' style='left:232px;right:%dpx;top:%dpx'></div>" % (M, y + gap - 44)
    return o


def source(d):
    import math, re as _re
    im = Image.open(os.path.join(W, "assets", d["img"] + ".png")); ratio = im.size[1] / im.size[0]
    hl = d.get("headline"); top = d.get("top", (300 if d.get("one_line") else 390) if hl else 178)
    plain = lambda t: _re.sub(r"<[^>]+>|&nbsp;", " ", t)
    text_h = 34 + math.ceil(len(plain(d["body"])) / 44) * 56 + 22 + math.ceil(len(plain(d["credit"])) / 60) * 42
    text_h += sum(30 + 36 + math.ceil(len(plain(p)) / 46) * 50 for p in d.get("points", []))
    w = d.get("w") or int(max(560, min(936, (1300 - top - text_h) / ratio)))
    h = int((w - 2) * ratio)
    return ((head(hl, 84) if hl else "")
            + "<div class='abs flow' style='left:%dpx;top:%dpx;width:936px'>" % (M, top)
            + "<div class='box' style='width:%dpx;height:%dpx;overflow:hidden;background:#fff'><img src='%s%s.png' style='width:%dpx;display:block'></div>" % (w, h + 2, A, d["img"], w - 2)
            + "<div class='b' style='margin-top:34px;font-size:40px'>%s</div>" % d["body"]
            + "".join("<div class='b' style='font-size:38px;line-height:1.3;padding:18px 0;border-top:1px solid var(--line);%s'>%s</div>"
                      % ("margin-top:30px" if i == 0 else "", p) for i, p in enumerate(d.get("points", [])))
            + "<div class='sm' style='margin-top:22px;font-size:30px;opacity:.82'>%s</div></div>" % d["credit"])


def stats(d):
    n = len(d["rows"]); top = d.get("top", 400); gap = d.get("gap") or max(180, min(270, (1210 - top) // n))
    o = head(d["headline"], 84)
    for i, (fig, txt) in enumerate(d["rows"]):
        y = top + i * gap
        o += ("<div class='rule' style='left:%dpx;right:%dpx;top:%dpx'></div>"
              "<div class='abs h' style='left:%dpx;top:%dpx;height:%dpx;width:370px;display:flex;align-items:center;font-size:%dpx;letter-spacing:-.06em;white-space:nowrap'>%s</div>"
              "<div class='abs b' style='left:452px;right:%dpx;top:%dpx;height:%dpx;display:flex;align-items:center;font-size:38px;line-height:1.32'><div>%s</div></div>") % (
              M, M, y, M - 3, y, gap, d.get("fsize", 112), fig, M, y, gap, txt)
    yb = top + n * gap
    o += "<div class='rule' style='left:%dpx;right:%dpx;top:%dpx'></div>" % (M, M, yb)
    if d.get("note"): o += "<div class='abs sm' style='left:%dpx;top:%dpx;width:936px;font-size:30px;opacity:.82'>%s</div>" % (M, yb + 26, d["note"])
    return o


def recap(d):
    o = head(d.get("headline", "The short version."), 104, 170)
    n = len(d["items"]); top = 350; gap = min(300, (1180 - top) // n)  # design B: no empty band under the headline
    for i, (t, b) in enumerate(d["items"]):
        y = top + i * gap
        o += ("<div class='rule' style='left:%dpx;right:%dpx;top:%dpx'></div><div class='abs h out' style='left:%dpx;top:%dpx;font-size:170px;line-height:1;letter-spacing:-.03em'>%d</div>"
              "<div class='abs' style='left:236px;top:%dpx;right:%dpx'><div class='t' style='font-size:54px'>%s</div><div class='b' style='margin-top:14px;font-size:38px'>%s</div></div>") % (M, M, y, M, y + 34, i + 1, y + 40, M, t, b)
    yb = top + n * gap
    o += ("<div class='rule' style='left:%dpx;right:%dpx;top:%dpx'></div><div class='abs' style='left:%dpx;top:%dpx;display:flex;align-items:center;gap:16px'>%s"
          "<div class='t' style='font-size:42px'>%s</div></div>") % (M, M, yb, M, yb + 44, ic("bookmark", 48, 1.5), d.get("save", "Save this for later."))
    return o


def limits(d):
    o = head(d["headline"], d.get("size", 76)) + ("<div class='abs sm' style='left:%dpx;top:%dpx'>%s</div>" % (M, d["rows_top"] - 74, d["source"]) if d.get("source") else "")
    gap = d.get("gap") or max(200, min(290, (1290 - d["rows_top"]) // len(d["rows"])))
    for i, (icn, t, b) in enumerate(d["rows"]):
        y = d["rows_top"] + i * gap
        o += ("<div class='rule' style='left:%dpx;right:%dpx;top:%dpx'></div><div class='abs' style='left:%dpx;top:%dpx;right:%dpx'><div class='t' style='font-size:48px'>%s</div><div class='sm' style='margin-top:12px;font-size:36px'>%s</div></div>"
              "<div class='abs' style='right:%dpx;top:%dpx'>%s</div>") % (M, M, y, M, y + 34, 240 if icn.endswith(".png") else 210, t, b, M, y + 52, ic(icn, 88, 1.25))
    return o


def cta(d=None):
    d = d or {}
    s1 = d.get("size", 164); s2 = d.get("size2", 150)
    o = ("<div class='abs h' style='left:%dpx;top:176px;font-size:%dpx;white-space:nowrap'>%s</div><div class='abs h out' style='left:%dpx;top:%dpx;font-size:%dpx'>%s</div>" % (M - 8, s1, d.get("line1", "Need a"), M - 2, 176 + s1 + 6, s2, d.get("line2", "website?"))
         + "<div class='abs b' style='left:%dpx;top:560px;width:%dpx;font-size:42px'>%s</div>" % (M, d.get("body_width", 860), d.get("body", "I plan, design and build every website myself, for small businesses."))
         + "<div class='abs btn' style='left:%dpx;top:%dpx'>%s %s</div>" % (M, d.get("btn_top", 728), d.get("button", "Start a project"), ic("arrow-up-right", 34, 2))
         + "<div class='abs h' style='left:%dpx;top:%dpx;font-size:104px'>benjobuilds.com</div>" % (M - 4, d.get("btn_top", 728) + 128))
    if has_art(d.get("art", "stone-arch")):
        o += art(d.get("art", "stone-arch"), 0, 1020, 1080, 420, d.get("art_pos", "50% 58%"))
    else:
        o += "<div class='rule' style='left:%dpx;right:%dpx;top:1020px'></div>" % (M, M)
    return o


def bars(d):
    o = head(d["headline"], 84)
    mx = d.get("max") or max(v for _, _, v in d["rows"]); top = d.get("top", 440); gap = d.get("gap", 200)
    for i, (lab, txt, v) in enumerate(d["rows"]):
        y = top + i * gap
        w = max(10, int(936 * v / mx))
        o += ("<div class='abs' style='left:%dpx;right:%dpx;top:%dpx;display:flex;justify-content:space-between;align-items:baseline'>"
              "<div class='t' style='font-size:46px'>%s</div><div class='h' style='font-size:64px'>%s</div></div>"
              "<div class='abs' style='left:%dpx;top:%dpx;width:%dpx;height:48px;background:var(--fg)'></div>"
              "<div class='rule q' style='left:%dpx;right:%dpx;top:%dpx'></div>") % (M, M, y, lab, txt, M, y + 84, w, M, M, y + 164)
    yb = top + len(d["rows"]) * gap
    if d.get("note"): o += "<div class='abs sm' style='left:%dpx;top:%dpx;width:936px;font-size:30px;opacity:.82'>%s</div>" % (M, yb + 6, d["note"])
    return o


TYPES = {"cover": cover, "bigfact": bigfact, "process": process, "source": source, "stats": stats, "recap": recap, "limits": limits, "cta": cta, "bars": bars}
INVERTED = {"bigfact", "cta"}
RHYTHM = {"stats", "process", "limits", "recap", "bars"}; RHYTHM_GAP = 72; RHYTHM_END = 1330


def _nb(v):
    if isinstance(v, str):
        if "<" in v or " " not in v.strip(): return v
        a, b = v.rstrip().rsplit(" ", 1)
        return a + "&nbsp;" + b if len(b) < 14 else v
    if isinstance(v, (list, tuple)): return type(v)(_nb(x) for x in v)
    if isinstance(v, dict): return {k: (_nb(x) if k not in ("img", "art", "art_pos", "line1", "line2", "mark") else x) for k, x in v.items()}
    return v


def render(story):
    out = os.path.join(W, "out", story["slug"]); os.makedirs(out, exist_ok=True)
    for f in os.listdir(out): os.remove(os.path.join(out, f))
    total = len(story["slides"]); names = []
    with sync_playwright() as p:
        br = p.chromium.launch(args=["--allow-file-access-from-files"])
        for i, (name, kind, section, data) in enumerate(story["slides"]):
            if kind == "cover" and data is not None and "art" not in data:  # design B: vary the cover engraving post to post (stone-arch stays on the cta)
                pool = [a for a in ARTS if a != "stone-arch"]; data = dict(data, art=pool[sum(map(ord, story["slug"])) % len(pool)])
            chip = kind in ("cover", "cta") and has_art((data or {}).get("art", "lake-pine" if kind == "cover" else "stone-arch"))
            html = page(TYPES[kind](_nb(data) if data is not None else data), i + 1, total, section, inv=kind in INVERTED, foot_chip=chip)
            hp = os.path.join(W, "_tmp.html"); open(hp, "w").write(html)
            pg = br.new_page(viewport={"width": 1080, "height": 1440}); pg.goto("file://" + hp); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(300)
            assert pg.evaluate("document.fonts.check('510 40px Geist')"), "Geist did not load"
            for src in pg.evaluate("Array.from(document.images).filter(i=>!i.naturalWidth).map(i=>i.getAttribute('src').split('/').pop())"):
                print("  MISSING IMAGE", name, src, "(not in assets/: run get_logos.py or fetch_logo.py)")
            if kind == "source" and not (data or {}).get("w"):
                pg.evaluate("""()=>{const fl=document.querySelector('.flow'), bx=fl.querySelector('.box'), im=bx.querySelector('img');
                    for(let k=0;k<3;k++){const w=bx.getBoundingClientRect().width, h=bx.getBoundingClientRect().height, r=(h-2)/(w-2);
                    const spare=1290-fl.getBoundingClientRect().bottom; const nw=Math.max(480,Math.min(936,w+spare/r));
                    bx.style.width=nw+'px'; bx.style.height=((nw-2)*r+2)+'px'; im.style.width=(nw-2)+'px';}}""")
                sw = pg.evaluate("document.querySelector('.flow .box').getBoundingClientRect().width")
                if sw < 700: print("  SMALL IMAGE", name, int(sw), "px wide: crop the screenshot tighter or shorten the text so it can grow")
            if kind == "bigfact":
                pg.evaluate("""()=>{const f=document.querySelector('.bigflow'), fig=f.querySelector('.fig');
                    let fs=parseFloat(getComputedStyle(fig).fontSize);
                    const wide=()=>{const r=document.createRange(); r.selectNodeContents(fig); return r.getBoundingClientRect().right>1008;};  // long figures ("11,334") ran off the right edge
                    while((f.getBoundingClientRect().bottom>1000 || wide()) && fs>160){fs-=20; fig.style.fontSize=fs+'px';}
                    const g=980-f.getBoundingClientRect().bottom;
                    if(g>0){const st=f.children[1]; st.style.marginTop=(parseFloat(getComputedStyle(st).marginTop)+g*0.5)+'px';}}""")
            if kind in RHYTHM:  # design B: same gap under every headline, rows spread evenly down to the same bottom line
                pg.evaluate("""([gap,end])=>{const s=document.querySelector('.s'), kids=Array.from(s.children);
                    const hd=kids.find(e=>e.classList.contains('h')&&e.getBoundingClientRect().top<320); if(!hd) return;
                    const body=kids.filter(e=>e!==hd&&e.style.top&&!e.style.bottom&&parseFloat(e.style.top)>150);
                    if(!body.length) return;
                    const r=body.map(e=>e.getBoundingClientRect()), top0=Math.min(...r.map(x=>x.top));
                    // the process slide's vertical line spans every row, so it can't be the last row: measure without it, redraw it after
                    const li=r.reduce((a,x,i)=>!body[i].classList.contains('vr')&&(a<0||x.bottom>r[a].bottom)?i:a,-1), start=hd.getBoundingClientRect().bottom+gap;
                    const span=r[li].top-top0; let k=span>0?(end-start-r[li].height)/span:1; k=Math.max(1,Math.min(1.5,k));
                    body.forEach((e,i)=>{e.style.top=(start+(r[i].top-top0)*k)+'px';});
                    const vr=body.find(e=>e.classList.contains('vr')), bx=Array.from(s.querySelectorAll('.box'));
                    if(vr&&bx.length) vr.style.height=(Math.max(...bx.map(b=>b.getBoundingClientRect().bottom))-vr.getBoundingClientRect().top)+'px';}""", [RHYTHM_GAP, RHYTHM_END])
            if kind not in ("cover", "cta"):
                bot = pg.evaluate("Math.max(...Array.from(document.querySelectorAll('.s > *:not(.eb), .s > * *')).map(e=>e.getBoundingClientRect().bottom))")
                if bot > 1338: print("  OVERFLOW", name, int(bot))
                if kind == "bigfact":
                    fb = pg.evaluate("document.querySelector('.bigflow').getBoundingClientRect().bottom")
                    if fb > 1020: print("  OVERFLOW", name, "statement/context runs into the facts rule:", int(fb))
                    if 1040 - fb > 170: print("  UNDERFILL", name, "gap above facts", int(1040 - fb), "px: add context")
                elif bot < 1150: print("  UNDERFILL", name, "content ends at", int(bot), "px: add a row or fact, or enlarge the image")
            orph = pg.evaluate("""Array.from(document.querySelectorAll('.b,.sm,.t,.h')).filter(e=>!e.classList.contains('out')&&e.children.length==0).map(e=>{
                const r=document.createRange(); r.selectNodeContents(e); const rects=Array.from(r.getClientRects());
                if(rects.length<2) return null; const last=rects[rects.length-1];
                return [e.textContent.trim().slice(-40), Math.round(last.width)]}).filter(Boolean)""")
            for t, wdt in orph:
                if wdt < 170: print("  SHORT LAST LINE", name, wdt, repr(t))
            fn = "%02d-%s.png" % (i + 1, name); pg.screenshot(path=os.path.join(out, fn)); pg.close(); names.append(fn)
        br.close()
    os.remove(os.path.join(W, "_tmp.html"))
    cols = 4; rows = (total + cols - 1) // cols
    sh = Image.new("RGB", (cols * 380 + 20, rows * 500 + 20), (205, 203, 196))
    for i, fn in enumerate(names):
        im = Image.open(os.path.join(out, fn)); assert im.size == (1080, 1440)
        sh.paste(im.resize((360, 480), Image.LANCZOS), (20 + (i % cols) * 380, 20 + (i // cols) * 500))
    sh.save(os.path.join(W, "out", story["slug"] + "-contact-sheet.png"))
    print("Rendered", total, "slides to", out)
