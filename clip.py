"""python3 clip.py <url> <out.png> <start text> <end text> [width] [bottom_pad] : screenshot from the block holding start text to the block holding end text. Rejects cookie banners, expands collapsed sections (GOV.UK accordions), hides fixed overlays."""
import sys
from playwright.sync_api import sync_playwright
url,out,st,en=sys.argv[1:5]; w=int(sys.argv[5]) if len(sys.argv)>5 else 420; pad=int(sys.argv[6]) if len(sys.argv)>6 else 14
JS="""([st,en])=>{
 const blocks=Array.from(document.querySelectorAll('h1,h2,h3,h4,p,li,td,th,tr,table,blockquote,div.section,dd,dt,span')).filter(e=>e.getClientRects().length&&e.getBoundingClientRect().height>0);
 const top=e=>e.getBoundingClientRect().top;
 const find=(t,below)=>{const c=blocks.filter(e=>e.innerText&&e.innerText.includes(t)&&(below==null||top(e)>=below));
   // innermost match; the end anchor is the first one at or below the start anchor, not the shortest anywhere on the page
   return below==null?c.sort((a,b)=>a.innerText.length-b.innerText.length)[0]:c.filter(e=>!c.some(x=>x!==e&&e.contains(x))).sort((a,b)=>top(a)-top(b))[0];};
 const a=find(st); if(!a) return 'start'; const b=find(en,top(a)); if(!b) return 'end';
 const ra=a.getBoundingClientRect(), rb=b.getBoundingClientRect();
 return [ra.top+scrollY, rb.bottom+scrollY];}"""
with sync_playwright() as p:
    br=p.chromium.launch(); pg=br.new_page(viewport={"width":w,"height":900},device_scale_factor=3)
    pg.goto(url,wait_until="networkidle",timeout=60000); pg.wait_for_timeout(1500)
    for sel in ["button:has-text('Reject')","button:has-text('Accept all')","button:has-text('Accept')","button:has-text('Necessary cookies only')","button:text-is('OK')"]:
        try:
            b=pg.locator(sel).first
            if b.is_visible(timeout=500): b.click(); pg.wait_for_timeout(800); print('clicked',sel); break
        except Exception: pass
    # expand collapsed sections (GOV.UK accordions): re-check each button when it is reached, so "Show all" is not undone, and leave header/nav menus shut
    pg.evaluate("""()=>{document.querySelectorAll('details').forEach(d=>d.open=true);document.querySelectorAll('button[aria-expanded="false"]').forEach(x=>{if(x.getAttribute('aria-expanded')=='false'&&!x.closest('header,nav'))try{x.click()}catch(e){}})}"""); pg.wait_for_timeout(500)
    pg.evaluate("()=>{for(const e of document.querySelectorAll('body *')){const c=getComputedStyle(e);if(c.position=='fixed'||c.position=='sticky')e.style.display='none'}}")
    hgt=min(30000,pg.evaluate('document.documentElement.scrollHeight')); pg.set_viewport_size({'width':w,'height':hgt}); pg.wait_for_timeout(1200)
    r=pg.evaluate(JS,[st,en]); print(r)
    if not isinstance(r,list):
        br.close(); sys.exit('NOT FOUND: %s text %r (not on the page, or only in a hidden element)' % (r, st if r=='start' else en))
    y0=max(0,r[0]-14); y1=min(hgt,r[1]+pad)
    pg.screenshot(path=out,clip={"x":0,"y":y0,"width":w,"height":y1-y0}); print('saved',out,w*3,'x',int((y1-y0)*3))
    br.close()
