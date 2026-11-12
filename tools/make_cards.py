"""Preview cards for articles (Nov 11): the 1200 x 630 image a link shows when it is shared (og:image).

Run from the repository root, by hand, whenever articles are added or their titles change:

    python3 tools/make_cards.py            # draw every card that is missing or out of date, remove cards no article uses
    python3 tools/make_cards.py --check    # list what is missing or out of date; draw nothing
    python3 tools/make_cards.py --all      # redraw every card

Not run by the workflows (they use the standard library only): it needs Playwright for Python and Chrome or Chromium
(PLAYWRIGHT_CHROME=/path/to/chrome, else Playwright's own), plus Pillow to shrink the files. It writes
assets/cards/<slug>.<hash>.png and assets/cards/cards.json, which records the label and title each card was drawn
with. tools/build_articles.py uses a card only when that record matches the article as it is now (and CARD_V), and
otherwise keeps the site card (assets/og-card.png) and names the article in its build log. The hash in the file name
changes whenever the drawing would, so apps that cache a preview by image address pick up the new one.

The card: the paper ground with the site card's 10px teal rule along the top; the lockup; a label (card_label() in
build_articles.py: the series and part, "In plain words", "A household guide", or the date of a timely piece); the title
in Public Sans Bold, broken after a colon, as large as fits from 86px down (four lines at most); the footer of the site
card (domain, "Free to reuse with credit · CC BY 4.0").
"""
import asyncio
import base64
import hashlib
import io
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build_articles as B  # noqa: E402

OUT = os.path.join("assets", "cards")
FONTS = os.path.join("assets", "fonts")


def articles():
    out = []
    for name in sorted(os.listdir(B.SRC_DIR)):
        if name.endswith(".md"):
            a = B.parse(os.path.join(B.SRC_DIR, name))
            if not a["draft"] and a.get("kind") != "tool":
                out.append(a)
    out.sort(key=lambda a: a["date"], reverse=True)
    B.load_series(out)
    return out


def font_face(weight, fname):
    with open(os.path.join(FONTS, fname), "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f'@font-face {{ font-family: "PS"; font-weight: {weight}; src: url(data:font/woff2;base64,{data}) format("woff2"); }}'


def page(label, title):
    esc = B.html.escape
    if ": " in title:
        a, b = title.split(": ", 1)
        t = f"<span>{esc(a)}:</span><span>{esc(b)}</span>"
    else:
        t = f"<span>{esc(title)}</span>"
    lab = f'<p class="lab">{esc(label)}</p>' if label else ""
    faces = "\n".join([font_face(400, "PublicSans-Regular.woff2"), font_face(600, "PublicSans-SemiBold.woff2"),
                       font_face(700, "PublicSans-Bold.woff2")])
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{faces}
html, body {{ margin: 0; }}
.card {{ position: relative; display: flex; flex-direction: column; width: 1200px; height: 630px; box-sizing: border-box; padding: 58px 96px 0; background: #f6f6f3; color: #1b1b1a; font-family: "PS"; overflow: hidden; }}
.card::before {{ content: ""; position: absolute; left: 0; right: 0; top: 0; height: 10px; background: #0b7a75; }}
.lock {{ display: flex; align-items: center; gap: 14px; font-size: 34px; letter-spacing: -0.01em; }}
.lock svg {{ width: 44px; height: 44px; }}
.lock b {{ font-weight: 700; }} .lock span {{ font-weight: 400; color: #5a5955; }} .lock i {{ font-style: normal; font-weight: 700; }}
.mid {{ flex: 1; display: flex; flex-direction: column; justify-content: center; min-height: 0; padding: 18px 0 26px; }}
.lab {{ margin: 0 0 14px; font-size: 23px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: #5a5955; }}
.t {{ margin: 0; font-weight: 700; letter-spacing: -0.018em; line-height: 1.08; }}
.t > span {{ display: block; text-wrap: balance; }}
.foot {{ flex: none; height: 84px; border-top: 2px solid #e3e2dc; display: flex; align-items: center; justify-content: space-between; font-size: 24px; color: #5a5955; }}
</style></head><body><div class="card" id="card">
<div class="lock"><svg viewBox="0 0 64 64"><path d="M25 14H15V50H25" fill="none" stroke="#1b1b1a" stroke-width="6.5"/><path d="M39 14H49V50H39" fill="none" stroke="#1b1b1a" stroke-width="6.5"/><circle cx="32" cy="32" r="8.5" fill="#0b7a75"/></svg><div><b>Economy</b> <span>in Context</span><i>.</i></div></div>
<div class="mid" id="mid">{lab}<h1 class="t" id="t">{t}</h1></div>
<div class="foot"><span>economyincontext.org</span><span>Free to reuse with credit · CC BY 4.0</span></div>
</div></body></html>"""


FIT = """() => { const t = document.getElementById('t'), m = document.getElementById('mid'), lab = m.querySelector('.lab');
  let s = 86; for (; s >= 50; s -= 2) { t.style.fontSize = s + 'px';
    const lh = (lab ? lab.offsetHeight + 14 : 0) + t.offsetHeight;
    if (lh <= m.clientHeight - 76 && t.offsetHeight / (s * 1.08) < 4.5) break; }
  return s; }"""


def file_for(slug, label, title):
    h = hashlib.sha256(f"{B.CARD_V}\n{label}\n{title}".encode()).hexdigest()[:8]
    return f"{slug}.{h}.png"


async def draw(jobs):
    from playwright.async_api import async_playwright
    from PIL import Image
    chrome = os.environ.get("PLAYWRIGHT_CHROME") or ("/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(**({"executable_path": chrome} if chrome else {}))
        p = await (await b.new_context(viewport={"width": 1200, "height": 630}, device_scale_factor=1)).new_page()
        for slug, label, title, fname in jobs:
            await p.set_content(page(label, title), wait_until="load")
            await p.evaluate("document.fonts.ready")
            size = await p.evaluate(FIT)
            png = await p.locator("#card").screenshot()
            im = Image.open(io.BytesIO(png)).convert("RGB").quantize(colors=96, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
            im.save(os.path.join(OUT, fname), optimize=True)
            kb = os.path.getsize(os.path.join(OUT, fname)) / 1024
            print(f"drew {fname} ({size}px title, {kb:.0f} KB)" + ("  WARNING: title at the smallest size" if size <= 50 else ""))
        await b.close()


def main():
    args = sys.argv[1:]
    os.makedirs(OUT, exist_ok=True)
    man_path = os.path.join(OUT, "cards.json")
    try:
        with open(man_path, encoding="utf-8") as f:
            cards = json.load(f).get("cards", {})
    except (OSError, ValueError):
        cards = {}
    arts = articles()
    want, jobs = {}, []
    for a in arts:
        label, title = B.card_label(a), B.plain(a["title"])
        fname = file_for(a["slug"], label, title)
        want[a["slug"]] = {"file": fname, "label": label, "title": title, "v": B.CARD_V}
        if "--all" in args or cards.get(a["slug"]) != want[a["slug"]] or not os.path.exists(os.path.join(OUT, fname)):
            jobs.append((a["slug"], label, title, fname))
    if "--check" in args:
        print(f"cards: {len(arts) - len(jobs)} current, {len(jobs)} to draw" + (": " + ", ".join(j[0] for j in jobs) if jobs else ""))
        return
    if jobs:
        asyncio.run(draw(jobs))
    keep = {c["file"] for c in want.values()} | {"cards.json"}
    for name in sorted(os.listdir(OUT)):
        if name not in keep:
            os.remove(os.path.join(OUT, name))
            print(f"removed {name}")
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump({"note": "Written by tools/make_cards.py: the label and title each card was drawn with. "
                           "tools/build_articles.py uses a card only when they match the article.",
                   "cards": dict(sorted(want.items()))}, f, indent=1, ensure_ascii=False)
        f.write("\n")
    print(f"cards: {len(want)} in {man_path}; drew {len(jobs)}")


if __name__ == "__main__":
    main()
