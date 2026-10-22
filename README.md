# Benjo Builds carousel kit

Public, read-only kit for the daily @benjobuilds carousel run. Scripts and brand logos only: no business data, prices or client details.

1. `git clone --depth 1 https://github.com/benjoGPT/benjobuilds-carousel-kit kit && bash kit/setup.sh ~/work`
2. Write `story.py` (a STORY dict, see `carousel_kit.py` and the examples in the Benjobuilds Project), then `python3 story.py`.
3. Screenshots: `python3 clip.py <url> shots/x.png "<start text>" "<end text>" [width] [bottom_pad]` (rejects cookie banners, hides fixed overlays, crops from the start text block to the end text block).
4. Logos: real brand marks in `assets/` (`logo-google.png` is Google's official four-colour G). `logo.py` (Simple Icons) is single-colour only: fallback.
5. QA: `python3 contact_sheet.py <slug>`.

Rules and the covered-topics list live in the Benjobuilds Claude Project.
