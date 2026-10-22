# Benjo Builds carousel kit

Public, read-only kit for the daily @benjobuilds carousel run. Scripts and brand logos only: no business data, prices or client details.

1. `git clone --depth 1 https://github.com/benjoGPT/benjobuilds-carousel-kit kit && bash kit/setup.sh ~/work`
2. Write `story.py` (a STORY dict, see `carousel_kit.py` and the examples in the Benjobuilds Project), then `python3 story.py`.
3. Screenshots: `python3 clip.py <url> shots/x.png "<start text>" "<end text>" [width] [bottom_pad]` (rejects cookie banners, hides fixed overlays, crops from the start text block to the end text block).
4. Logos (the company the story is about): `python3 fetch_logo.py <name> <domain> [--url <press-kit image>]` makes a candidate sheet from the company's own site icons, any URLs you pass, and the single-colour Simple Icons mark. Look at the sheet once, then `python3 fetch_logo.py <name> --pick <n>` saves `assets/logo-<name>.png`.
5. QA: `python3 contact_sheet.py <slug>`.

Rules and the covered-topics list live in the Benjobuilds Claude Project.
