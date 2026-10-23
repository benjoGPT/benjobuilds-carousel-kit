# Kit reference (read this, not the .py files)

Everything the daily run needs to write `story.py`. Work in the workdir made by `setup.sh`.

## Story shape

```python
from carousel_kit import render
render({"slug": "my-slug", "slides": [
    # (file name, slide type, section label in the header, data dict)
    ("cover", "cover", "News / Search Console", {...}),
    ...
]})
```

Output: `out/<slug>/NN-<name>.png` (1080x1440) and `out/<slug>-contact-sheet.png`. Text strings can hold simple HTML (`<b>`, `<br>`). The last word is joined to the one before it automatically.

`bigfact` and `cta` render inverted (blue background).

## Slide types (required fields first, then optional with defaults)

| type | required | optional (default) |
|---|---|---|
| `cover` | `line1`, `line2`, `standfirst` | `size` (164), `size2` (140), `sf_width` (800), `mark` (a `logo-*.png`, sits right of line 2), `mark_h` (190), `logo` + `logo_h` (64, under the standfirst), `art` ("lake-pine"), `art_pos` ("50% 46%"). With no art file: `facts` = (label, line1, line2) and `icon` |
| `bigfact` | `figure`, `statement`, `facts` = [(label, text), (label, text)] | `context`, `size` (440, shrinks to fit), `gap` (56) |
| `process` | `headline`, `steps` = [(icon, title, body), ...] (2 to 4) | `gap` (auto) |
| `source` | `img` (name in `assets/`, no .png), `body`, `credit` | `headline`, `one_line` (headline fits one line), `points` = [text, ...], `top`, `w` (auto-fits) |
| `stats` | `headline`, `rows` = [(figure, text), ...] | `top` (400), `gap` (auto), `fsize` (112), `note` |
| `limits` | `headline`, `rows_top` (e.g. 420), `rows` = [(icon, title, body), ...] | `size` (76), `source` (line above the rows), `gap` (auto) |
| `bars` | `headline`, `rows` = [(label, value text, number), ...] | `max`, `top` (440), `gap` (200), `note` |
| `recap` | `items` = [(title, body), ...] (3) | `headline` ("The short version.") |
| `cta` | none (pass `None` for defaults) | `line1` ("Need a"), `line2` ("website?"), `body`, `body_width` (860), `button` ("Start a project"), `btn_top` (728), `size` (164), `size2` (150), `art` ("stone-arch"), `art_pos` |

**Icons:** a Lucide name (`"file-search"`, `"calendar"`, `"circle-alert"`; check one with `ls node_modules/lucide-static/icons/<name>.svg`) or a brand mark `"logo-<slug>.png"`.

**Art (engravings):** `lake-pine`, `stone-arch`, `mountain-valley`, `mountain-water`, `lake-waterfall`, `faq-bridge`.

**Logos in assets/ after setup:** google, microsoft, instagram, meta, facebook, whatsapp, youtube, linkedin, tiktok, stripe, paypal, shopify, wix, wordpress, squarespace, xero, quickbooks, cloudflare, godaddy, mailchimp, trustpilot, ico. Others: `python3 fetch_logo.py <name> <domain>`, view the sheet once, `--pick <n>`.

## Tools

- Screenshot: `python3 clip.py <url> shots/x.png "<start text>" "<end text>" [width 420] [bottom_pad 14]`, then **copy it into assets/** (`cp shots/x.png assets/x.png`); `source` only reads `assets/`. A narrower width (e.g. 640 to 1000 viewport px) gives bigger text. Crop with PIL if needed.
- Page text when WebFetch returns no body: `python3 text.py <url> [grep word]`.
- Thumbnail before viewing: `python3 -c "from PIL import Image;im=Image.open('shots/x.png');im.thumbnail((700,700));im.save('/tmp/x.png')"`.

## Warnings and the usual fix

| warning | fix |
|---|---|
| `OVERFLOW` | shorten text, drop a row, or lower `size` |
| `UNDERFILL` (content ends above 1150px) | add a row, point or `context`; on `source`, crop the screenshot tighter so it grows |
| `SHORT LAST LINE` | reword so the last line has 3+ words |
| `SMALL IMAGE` (under 700px) | crop the screenshot tighter, or shorten `body` / `points` |
| `MISSING IMAGE` | the file isn't in assets/ (copy it, or run fetch_logo.py) |

## Final checks (one command)

```bash
cd out/<slug> && python3 -c "
import glob;from PIL import Image
f=sorted(glob.glob('*.png'));assert all(Image.open(x).size==(1080,1440) for x in f);assert [int(x[:2]) for x in f]==list(range(1,len(f)+1));print(len(f),'ok')" \
&& cd .. && zip -qr <slug>.zip <slug> && unzip -tq <slug>.zip
```
