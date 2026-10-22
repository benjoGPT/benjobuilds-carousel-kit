"""python3 clip.py <url> <out.png> <start text> <end text> [width] : screenshot from the block holding start text to the block holding end text."""
import sys
from playwright.sync_api import sync_playwright
url,out,st,en=sys.argv[1:5]; w=int(sys.argv[5]) if len(sys.argv)>5 else 420
JS="""([st,en])=>{
 const blocks=Array.from(document.querySelectorAll('h1,h2,h3,h4,p,li,td,th,tr,table,blockquote,div.section,dd,dt,span'));
 const find=t=>blocks.filter(e=>e.innerText&&e.innerText.includes(t)).sort((a,b)=>a.innerText.length-b.innerText.length)[0];
 const a=find(st), b=find(en); if(!a||!b) return null;
 const ra=a.getBoundingClientRect(), rb=b.getBoundingClientRect();
 return [ra.top+scrollY, rb.bottom+scrollY];}"""
with sync_playwright() as p:
    br=p.chromium.launch(); pg=br.new_page(viewport={"width":w,"height":900},device_scale_factor=3)
    pg.goto(url,wait_until="networkidle",timeout=60000); pg.wait_for_timeout(1500)
    for sel in ["button:has-text('Reject')","button:has-text('Accept all')","button:has-text('Accept')","button:has-text('Necessary cookies only')","button:has-text('OK')"]:
        try:
            b=pg.locator(sel).first
            if b.is_visible(timeout=500): b.click(); pg.wait_for_timeout(800); print('clicked',sel); break
        except Exception: pass
    pg.evaluate("()=>{for(const e of document.querySelectorAll('body *')){const c=getComputedStyle(e);if(c.position=='fixed'||c.position=='sticky')e.style.display='none'}}")
    hgt=min(30000,pg.evaluate('document.documentElement.scrollHeight')); pg.set_viewport_size({'width':w,'height':hgt}); pg.wait_for_timeout(1200)
    r=pg.evaluate(JS,[st,en]); print(r)
    if r:
        y0=max(0,r[0]-14); y1=r[1]+int(sys.argv[6]) if len(sys.argv)>6 else r[1]+14
        pg.screenshot(path=out,clip={"x":0,"y":y0,"width":w,"height":y1-y0}); print('saved',out)
    br.close()
