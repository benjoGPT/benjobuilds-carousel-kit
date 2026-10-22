"""python3 logo.py <simple-icons slug>  -> assets/logo-<slug>.png in the brand's own colour (Simple Icons)."""
import sys, json, re
from playwright.sync_api import sync_playwright
slug=sys.argv[1]
svg=open('node_modules/simple-icons/icons/%s.svg'%slug).read()
data=json.load(open('node_modules/simple-icons/data/simple-icons.json'))
data=data.get('icons',data) if isinstance(data,dict) else data
hexc=[i for i in data if i.get('slug')==slug or i['title'].lower()==slug][0]['hex']
svg=svg.replace('<svg ','<svg fill="#%s" width="600" height="600" '%hexc,1)
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':600,'height':600})
    pg.set_content("<html><body style='margin:0;background:transparent'>%s</body></html>"%svg)
    pg.locator('svg').screenshot(path='assets/logo-%s.png'%slug, omit_background=True); b.close()
print('saved assets/logo-%s.png #%s'%(slug,hexc))
