# Benjo Builds carousel kit

Public, read-only kit for the daily @benjobuilds carousel run. Scripts and brand logos only: no business data, prices or client details.

1. `git clone --depth 1 https://github.com/benjoGPT/benjobuilds-carousel-kit kit && bash kit/setup.sh ~/work`
   If running setup.sh is blocked, clone alone, then: `cp kit/*.py ~/work/`, `npm i geist lucide-static simple-icons`, copy Geist-Variable.ttf into assets/, download the six engravings from benjobuilds.com/landscapes/ and convert to .png, then `KIT=kit python3 get_logos.py`. Never retype the kit.
2. Write `story.py` (a STORY dict: every slide type and field is in `KIT.md`, so there's no need to read `carousel_kit.py`), then `python3 story.py`. For a page WebFetch returns without its body: `python3 text.py <url> [grep word]`.
3. Screenshots: `python3 clip.py <url> shots/x.png "<start text>" "<end text>" [width] [bottom_pad]` (rejects cookie banners, expands collapsed sections such as GOV.UK accordions, hides fixed overlays, crops from the start text block to the end text block).
4. Brand marks: setup builds `assets/logo-<slug>.png` for google, microsoft, instagram, meta, facebook, whatsapp, youtube, linkedin, tiktok, stripe, paypal, shopify, wix, wordpress, squarespace, xero, quickbooks, cloudflare, godaddy, mailchimp, trustpilot and ico (the committed `svg/` copies are used first). Use them as `mark="logo-<slug>.png"` on a cover, or as the icon of a `process` or `limits` row (e.g. `"logo-xero.png"`). For any other company or regulator (HMRC, Companies House, CMA, Ofcom, OpenAI): `python3 fetch_logo.py <name> <domain> [--url <press-kit image>]`, look at the sheet once, then `--pick <n>`. `python3 get_logos.py --sheet` previews the library.
5. QA: `python3 contact_sheet.py <slug>`. The renderer prints OVERFLOW, UNDERFILL, SHORT LAST LINE and SMALL IMAGE (a screenshot under 700px wide, hard to read at 360px): fix all of them.
6. Changing the kit: run `bash tests/smoke.sh` before pushing (sets up a temp workdir, renders every slide type, checks the logos and both clip cases; needs network).

Rules and the covered-topics list live in the Benjobuilds Claude Project.
