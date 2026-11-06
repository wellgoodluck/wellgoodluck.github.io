#!/usr/bin/env python3
"""
One page per chart: <out>/chart/<id>/index.html for every tile in data/series.json, plus the charts
index at <out>/chart/index.html. Standard library only. Called by tools/build_articles.py, which runs
in both workflows after chart.html has been copied into the output folder.

Each page is chart.html with its head filled in: a title carrying the latest reading, the meta and
preview descriptions, and its own canonical address. Link previews (iMessage, Slack, Bluesky, Reddit)
and search engines read those without running the page's script. chart.html's script finds the id in
the address and draws the chart as before.

The output copy of chart.html also gets the list of ids that have a page, which its first script uses
to send an old chart.html?id=<id> link to /chart/<id>/ (embeds, with &embed=1, stay on chart.html).

fmt_value, fmt_period and context_sentence are ports of fmtValue, fmtPeriod and contextSentence in
chart.html and index.html. The test harness checks they print what the pages print, on every tile.
"""

import html
import json
import os
import re
from datetime import date, datetime, timezone
from decimal import Decimal, ROUND_HALF_UP

SITE = "https://economyincontext.org"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
MONTHS_LONG = ["January", "February", "March", "April", "May", "June", "July", "August",
               "September", "October", "November", "December"]
IDS_PLACEHOLDER = "null /*CHART_IDS*/"
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]          # date.weekday(): Monday is 0

# The headline releases worth a date on the masthead, by FRED release id (the same table as RELEASES in index.html,
# which draws the line for readers with scripts; keep the two in step). Daily and weekly releases and the derived
# Debt to GDP Ratios stay out, as does Average Price Data (454), which always comes out with the CPI. Order breaks ties on a day.
RELEASES = [
    (50, "Jobs report", "https://www.bls.gov/news.release/empsit.toc.htm"),
    (10, "Consumer prices", "https://www.bls.gov/news.release/cpi.toc.htm"),
    (53, "GDP", "https://www.bea.gov/data/gdp/gross-domestic-product"),
    (54, "PCE inflation and spending", "https://www.bea.gov/data/income-saving/personal-income"),
    (192, "Job openings", "https://www.bls.gov/news.release/jolts.toc.htm"),
    (27, "Housing starts", "https://www.census.gov/construction/nrc/index.html"),
    (46, "Producer prices", "https://www.bls.gov/news.release/ppi.toc.htm"),
    (51, "Trade balance", "https://www.bea.gov/data/intl-trade-investment/international-trade-goods-and-services"),
]
COMING_MAX = 4        # releases shown
COMING_GAP = 10       # days: a date this close to the release's previous date is a revision or supplement, not a release


# ---------------------------------------------------------------------------
# Ports of the pages' formatting (keep in step with chart.html)
# ---------------------------------------------------------------------------
def _fixed(x, decimals):
    """x to a fixed number of decimals with thousands commas, rounding as the browser does (half away from zero,
    on the shortest decimal form of the number)."""
    q = Decimal(repr(abs(x))).quantize(Decimal(1).scaleb(-decimals), rounding=ROUND_HALF_UP)
    return f"{q:,.{decimals}f}"


def fmt_value(v, d, decimals=None, nosign=False):
    decimals = d.get("decimals", 0) if decimals is None else decimals
    x = v / (d.get("scale") or 1)
    sign = "+" if d.get("signed") and x > 0 and not nosign else ""
    return ("−" if x < 0 else sign) + d.get("prefix", "") + _fixed(x, decimals) + d.get("suffix", "")


def _d(s):
    return date.fromisoformat(s[:10])


def fmt_period(s, freq, long=False):
    x = _d(s)
    if freq == "a":
        return f"FY {x.year}"
    if freq == "y":
        return str(x.year)
    if freq == "q":
        return f"Q{(x.month - 1) // 3 + 1} {x.year}"
    names = MONTHS_LONG if long else MONTHS
    if freq == "m":
        return f"{names[x.month - 1]} {x.year}"
    return f"{names[x.month - 1]} {x.day}, {x.year}"


def _years_between(a, b):
    return (_d(b) - _d(a)).days / 365.25


def _pf(t):
    """A yearly tile reads "FY 2025" (fiscal years) unless display.year is "calendar"; as pf() in the pages."""
    return "y" if t.get("freq") == "a" and (t.get("display") or {}).get("year") == "calendar" else t["freq"]


def _period_noun(freq):
    return {"a": "years", "q": "quarters", "w": "weeks"}.get(freq, "months")


def _adjusted(t):
    return bool(t["display"].get("adjust") and t.get("context_real"))


def context_sentence(t):
    c = t["context_real"] if _adjusted(t) else t["context"]
    noun, since = _period_noun(t["freq"]), _d(c["since"]).year
    pct, sense = c["percentile_below"], t["display"].get("sense")
    # "deficit": a balance, below zero is a deficit (trade). "deficit-up": the deficit shown positive (federal).
    words = {"deficit": ("A smaller deficit than ", "A larger deficit than ", "The smallest deficit on record.",
                         "Smallest deficit since ", "The largest deficit on record.", "Largest deficit since "),
             "deficit-up": ("A larger deficit than ", "A smaller deficit than ", "The largest deficit on record.",
                            "Largest deficit since ", "The smallest deficit on record.", "Smallest deficit since ")
             }.get(sense, ("Higher than ", "Lower than ", "The highest on record.", "Highest since ",
                           "The lowest on record.", "Lowest since "))
    hi_word, lo_word, hi_rec, hi_since, lo_rec, lo_since = words
    share = lambda v: min(99, max(1, int(Decimal(repr(v)).quantize(Decimal(1), rounding=ROUND_HALF_UP))))
    is_record = c.get("highest_since") is None if pct >= 50 else c.get("lowest_since") is None
    parts = []
    if not is_record:
        parts.append(f"{hi_word}{share(pct)}% of {noun} since {since}." if pct >= 50
                     else f"{lo_word}{share(100 - pct)}% of {noun} since {since}.")
    cur, prev = c["current"]["value"], c["previous"]["value"]
    since_ok = not _adjusted(t)
    if cur > prev:
        if c.get("highest_since") is None:
            parts.append(hi_rec)
        elif since_ok and _years_between(c["highest_since"], c["current"]["date"]) >= 1:
            parts.append(hi_since + fmt_period(c["highest_since"], _pf(t)) + ".")
    elif cur < prev:
        if c.get("lowest_since") is None:
            parts.append(lo_rec)
        elif since_ok and _years_between(c["lowest_since"], c["current"]["date"]) >= 1:
            parts.append(lo_since + fmt_period(c["lowest_since"], _pf(t)) + ".")
    if _adjusted(t) and parts:
        parts[0] = "Adjusted for inflation, " + parts[0][0].lower() + parts[0][1:]
    return " ".join(parts)


def headline(t):
    """(value, period) as the chart page's headline shows them."""
    d, c = t["display"], t["context"]
    if t.get("headline"):
        return fmt_value(t["headline"]["value"], d), fmt_period(t["headline"]["date"], "d", True)
    return fmt_value(c["current"]["value"], d), fmt_period(c["current"]["date"], _pf(t), True)


def page_text(t):
    """The text a chart's page carries before its script runs."""
    value, when = headline(t)
    sentence = context_sentence(t)
    line = f"{t['title']}: {value} ({when})"
    return {
        "title": line + " — Economy in Context",
        "og_title": line,
        "description": f"{t['title']}: {t['subtitle']}. {sentence} Full history with optional overlays.".replace("  ", " "),
        "og_description": (f"{t['subtitle']}. {sentence}").strip(),
        "status": (line + ". " + sentence).strip(),
    }


# ---------------------------------------------------------------------------
# Writing the pages
# ---------------------------------------------------------------------------
def chart_url(tid, query=""):
    """The address of a chart's page, relative to the site root, with an optional view query."""
    return f"chart/{tid}/" + (f"?{query}" if query else "")


def _sub(page, old, new, what, warn):
    if page.count(old) != 1:
        warn.append(f"{what}: expected one match in chart.html, found {page.count(old)}")
        return page
    return page.replace(old, new)


def _with_ids(page, ids):
    return page.replace(IDS_PLACEHOLDER, json.dumps(ids), 1)


def _set_head(page, url, title, og_title, desc, og_desc, warn):
    e = lambda s: html.escape(s, quote=True)
    page = _sub(page, "<title>Economy in Context</title>", f"<title>{html.escape(title)}</title>", "title", warn)
    page = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{e(url)}">', page, count=1)
    page = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{e(url)}">', page, count=1)
    page = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{e(og_title)}">', page, count=1)
    if desc:
        page = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{e(desc)}">', page, count=1)
    if og_desc:
        page = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{e(og_desc)}">', page, count=1)
    return page


def write_chart_pages(out_root, series_path=os.path.join("data", "series.json")):
    """Write <out>/chart/<id>/index.html per tile and <out>/chart/index.html. Returns the ids written
    (empty when chart.html or the data can't be read; the build goes on either way)."""
    src = os.path.join(out_root, "chart.html")
    if not os.path.exists(src):
        print(f"chart pages: no {src}; skipped")
        return []
    try:
        tiles = json.load(open(series_path, encoding="utf-8")).get("tiles", [])
    except Exception as e:                                   # a bad data file must not break the build
        print(f"chart pages: skipped ({e})")
        return []
    base = open(src, encoding="utf-8").read()
    ids = [t["id"] for t in tiles if re.fullmatch(r"[A-Za-z0-9_-]+", t.get("id", ""))]
    warn = []
    if IDS_PLACEHOLDER not in base:
        warn.append("chart.html has no id-list placeholder; old chart.html links won't move")
    base_ids = _with_ids(base, ids)

    for t in tiles:
        if t["id"] not in ids:
            continue
        url = f"{SITE}/{chart_url(t['id'])}"
        try:
            txt = page_text(t)
        except Exception as e:                               # missing context: a plain title, the script does the rest
            warn.append(f"{t['id']}: no reading for the title ({e})")
            txt = {"title": f"{t['title']} — Economy in Context", "og_title": t["title"], "description": "",
                   "og_description": "", "status": "Loading the figures…"}
        page = _set_head(base_ids, url, txt["title"], txt["og_title"], txt["description"], txt["og_description"], warn)
        page = _sub(page, '<h1 id="title">Loading…</h1>', f'<h1 id="title">{html.escape(t["title"])}</h1>', "h1", warn)
        # the crumb: back to its row in the full view ("All N numbers", N the number of tiles), then this page's name
        page = _sub(page, '<p class="crumb"><a href="/">All the numbers</a>', f'<p class="crumb"><a href="/#i-{t["id"]}">All {len(ids)} numbers</a>', "crumb", warn)
        page = _sub(page, '<span id="crumb-here"></span>', f'<span id="crumb-here">{html.escape(t["title"])}</span>', "crumb page", warn)
        page = _sub(page, '<p class="sub" id="subtitle"></p>', f'<p class="sub" id="subtitle">{html.escape(t["subtitle"])}</p>', "subtitle", warn)
        # the status line carries the reading before the script runs (its attributes may change: match on the id)
        m = re.findall(r'<p class="status" id="status"[^>]*>Loading the figures…</p>', page)
        if len(m) == 1:
            page = page.replace(m[0], m[0].replace("Loading the figures…", html.escape(txt["status"])))
        else:
            warn.append(f"status: expected one match in chart.html, found {len(m)}")
        os.makedirs(os.path.join(out_root, "chart", t["id"]), exist_ok=True)
        with open(os.path.join(out_root, "chart", t["id"], "index.html"), "w", encoding="utf-8") as f:
            f.write(page)

    index = _set_head(base_ids, f"{SITE}/chart/", "Charts — Economy in Context", "Charts — Economy in Context", "", "", warn)
    with open(os.path.join(out_root, "chart", "index.html"), "w", encoding="utf-8") as f:
        f.write(index)
    with open(src, "w", encoding="utf-8") as f:              # the redirect list for old links
        f.write(base_ids)
    for w in sorted(set(warn)):
        print(f"chart pages: WARNING {w}")
    print(f"built chart/ ({len(ids)} chart pages and the index)")
    return ids


def coming_up(calendar, today):
    """The next date of each headline release on or after `today` (a date), soonest first: [(label, url, date)].
    Port of comingUp() in index.html. Housing starts, for one, lists a 9 am supplement a week after each 8:30
    release; a date within COMING_GAP days of the date before it is skipped. Anything missing or malformed
    leaves that release out."""
    by_id = {}
    for r in (calendar or {}).get("releases") or []:
        if isinstance(r, dict) and r.get("id") is not None:
            by_id[r["id"]] = r
    out = []
    for rank, (rid, label, url) in enumerate(RELEASES):
        r = by_id.get(rid)
        if not r or not isinstance(r.get("next"), list):
            continue
        prev = r.get("last") if isinstance(r.get("last"), str) else None
        for d in r["next"]:
            if not isinstance(d, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
                continue
            try:
                gap = (_d(d) - _d(prev)).days if prev else None
                when = _d(d)
            except ValueError:
                continue
            prev = d
            if gap is not None and gap < COMING_GAP:
                continue
            if when < today:
                continue
            out.append((when, rank, label, url))
            break
    out.sort()
    return [(label, url, when) for when, rank, label, url in out[:COMING_MAX]]


def fmt_day(x):
    return f"{DAYS[x.weekday()]}, {MONTHS[x.month - 1]} {x.day}"


def coming_html(calendar, today):
    """The Coming up line's inner HTML, or "" when there is nothing upcoming."""
    items = coming_up(calendar, today)
    if not items:
        return ""
    return '<span class="rel-h">Next releases<span class="sep">: </span></span>' + '<span class="sep"> · </span>'.join(
        f'<span class="rel"><a href="{html.escape(url)}">{html.escape(label)}</a><span class="when"> {fmt_day(when)}</span></span>'
        for label, url, when in items)


def write_home_static(out_root, series_path=os.path.join("data", "series.json")):
    """Fill <out>/index.html with the latest readings as plain HTML, so search engines, link previews and
    readers without scripts get the numbers. The page's script clears <main> when it draws the tiles, and keeps
    this list if the figures fail to load. Returns True when written; the build goes on either way."""
    src = os.path.join(out_root, "index.html")
    if not os.path.exists(src):
        print(f"home: no {src}; skipped")
        return False
    try:
        data = json.load(open(series_path, encoding="utf-8"))
        tiles = data.get("tiles", [])
    except Exception as e:                                   # a bad data file must not break the build
        print(f"home: skipped ({e})")
        return False
    page = open(src, encoding="utf-8").read()
    status = '<p class="status" id="status" role="status">Loading the latest figures…</p>'
    if page.count(status) != 1:
        print("home: WARNING no loading line in index.html; static figures not written")
        return False
    sections, out = [], []
    for t in tiles:
        if t["section"] not in sections:
            sections.append(t["section"])
    for sec in sections:
        items = []
        for t in (x for x in tiles if x["section"] == sec):
            try:
                value, when = headline(t)
                sentence = context_sentence(t)
            except Exception as e:                           # no reading: leave the tile out of the static list
                print(f"home: WARNING {t.get('id')}: {e}")
                continue
            hh = (t.get("household") or {}).get("text", "")
            items.append(f'<li><a href="{chart_url(t["id"])}">{html.escape(t["title"])}</a>: <strong>{html.escape(value)}</strong> '
                         f'({html.escape(when)}). {html.escape(sentence)}' + (f' {html.escape(hh)}' if hh else "") + "</li>")
        if items:
            out.append(f'<h2>{html.escape(sec)}</h2><ul>' + "".join(items) + "</ul>")
    # The home page's In short (summaries.home, written by fetch_fred.py from Nov 6), as one plain paragraph above the
    # list, its figures in bold. A series.json from before then has none, and the list starts as it did.
    short = ""
    try:
        para = ((data.get("summaries") or {}).get("home") or {}).get("paragraph") or []
        if para:
            short = "".join(html.escape(x) if isinstance(x, str) else f"<strong>{html.escape(x.get('t', ''))}</strong>" for x in para
                            if isinstance(x, (str, dict)))
    except Exception as e:                                   # never the build's problem
        print(f"home: WARNING in short: {e}")
        short = ""
    gen = (data.get("generated") or "")[:10]
    asof = f"{MONTHS_LONG[int(gen[5:7]) - 1]} {int(gen[8:10])}, {gen[:4]}" if len(gen) == 10 else ""
    block = ('<p class="status" id="status" role="status">Loading the charts…</p>\n'
             '  <noscript><p class="status">The charts need JavaScript. The latest readings are listed below.</p></noscript>\n'
             '  <div class="static-figures" id="static-figures">'
             + (f'<p class="short-static"><b>In short:</b> {short}</p>' if short else "")
             + (f'<p class="asof">Latest readings, as of {asof}. Each links to its full chart.</p>' if asof else "")
             + "".join(out) + "</div>")
    page = page.replace(status, block, 1)
    if asof:
        page = page.replace('<p class="updated" id="updated"></p>',
                            f'<p class="updated" id="updated">New figures last checked {asof} · <span class="nw">data from FRED</span></p>', 1)
    # the Coming up line, as of the build's UTC date; the script redraws it for the reader's own date
    try:
        coming = coming_html(data.get("calendar"), datetime.now(timezone.utc).date())
    except Exception as e:                                   # never the build's problem
        print(f"home: WARNING coming up: {e}")
        coming = ""
    if coming:
        page = page.replace('<p class="coming" id="coming" hidden></p>', f'<p class="coming" id="coming">{coming}</p>', 1)
    with open(src, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"built index.html static figures ({sum(len(o.split('<li>')) - 1 for o in out)} readings)")
    return True


def clean_chart_links(page, ids, prefix="../"):
    """In built article HTML, point links to chart.html?id=<id>… at /chart/<id>/…; iframes (embeds) stay."""
    known = set(ids)

    def repl(m):
        tid, rest = m.group(1), m.group(2)
        if tid not in known:
            return m.group(0)
        return f'href="{prefix}{chart_url(tid, rest[5:] if rest.startswith("&amp;") else "")}"'
    return re.sub(r'href="' + re.escape(prefix) + r'chart\.html\?id=([A-Za-z0-9_-]+)((?:&amp;[^"]*)?)"', repl, page)


if __name__ == "__main__":                                   # print each page's text, for review
    for t in json.load(open(os.path.join("data", "series.json"), encoding="utf-8"))["tiles"]:
        txt = page_text(t)
        print(f"{t['id']}\n  title: {txt['title']}\n  preview: {txt['og_title']}\n           {txt['og_description']}\n")
