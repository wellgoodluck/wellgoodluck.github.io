#!/usr/bin/env python3
"""
Build the articles section: articles/src/*.md -> <out>/articles/<slug>.html plus
<out>/articles/index.html. Standard library only.

Usage:  python3 tools/build_articles.py [output-root]     (default: public)

Each source file starts with a front-matter block:

    ---
    title: Why Everything Costs 30% More Than It Did in 2019
    dek: One sentence under the title.
    date: 2026-10-24
    updated: 2026-10-28          (optional)
    kind: concept                (optional: concept = Plain words; path = household path;
                                  page = built and in the sitemap but not listed on the index)
    order: 1                     (optional: sort key within the household paths, and within
                                  the Plain words ideas)
    tile: cpi, core_cpi          (optional, Plain words only: the almanac indicators this page
                                  explains. Puts it under "The numbers" in the almanac's own
                                  grouping and order, and links each of those tiles and chart
                                  pages to it. A Plain words page without one is an "idea".)
    label: Inflation             (optional: the short name used in the Plain words lists)
    hook: why prices never go back   (optional: the phrase after the label in those lists,
                                  and after "In plain words:" on the tiles)
    ---

then Markdown. Supported: # ## ### headings, paragraphs, **bold**, *italic*,
[links](url), - bullet lists, 1. numbered lists, > quotes, --- rules, and raw
HTML lines (left as they are). Plus one directive for a live chart from the
site's own detail page:

    {{chart id=cpi range=10y ov=fed_target,pce caption="Inflation and the Fed's target."}}

Anything under `## Sources`, up to the next heading, is rendered as a sources list.

Live figures in the text ({{v …}}, {{fig …}}) and invisible review markers ({{check …}},
{{due …}}) are filled in from data/ by tools/figures.py before the Markdown is rendered; see
that file. The build prints a one-line summary plus any failing check, passed due date or
warning, and writes them to build-report.json (or $FIGURES_REPORT), outside the published folder.
"""

import html
import json
import os
import re
import shlex
import sys
from datetime import date

SRC_DIR = os.path.join("articles", "src")
SITE = "https://economyincontext.org"

# ---------------------------------------------------------------------------
# Minimal Markdown
# ---------------------------------------------------------------------------
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|[^)\s]+)\)",
               lambda m: f'<a href="{m.group(2).replace(chr(34), "&quot;")}"'    # text is already HTML-escaped above
                         + (' rel="noopener"' if m.group(2).startswith("http") else "") + f">{m.group(1)}</a>", s)
    s = s.replace("&#91;", "[")   # the doc export writes a literal bracket this way
    return s


def chart_directive(line):
    m = re.match(r"^\{\{\s*chart\s+(.*?)\s*\}\}$", line.strip())
    if not m:
        return None
    attrs = {}
    for tok in shlex.split(m.group(1)):
        if "=" in tok:
            k, v = tok.split("=", 1)
            attrs[k] = v
    if "id" not in attrs:
        return None
    q = ["id=" + attrs["id"], "embed=1"]
    for k in ("range", "ov", "from", "to"):
        if k in attrs:
            q.append(f"{k}={attrs[k]}")
    query = "&".join(q)
    full = query.replace("embed=1&", "").replace("&embed=1", "")
    cap = attrs.get("caption", "")
    height = attrs.get("height", "600")
    return (f'<figure class="chart-embed">'
            f'<iframe src="../chart.html?{html.escape(query, quote=True)}" title="Chart: {html.escape(attrs["id"])}" '
            f'loading="lazy" height="{html.escape(height)}"></iframe>'
            f'<figcaption>{inline(cap) + " " if cap else ""}'
            f'<a href="../chart.html?{html.escape(full, quote=True)}">Full chart and context →</a></figcaption></figure>')


def md_to_html(text):
    out, para, lst, in_sources = [], [], None, False

    def flush_para():
        nonlocal para
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []

    def close_list():
        nonlocal lst
        if lst:
            out.append(f"</{lst}>")
            lst = None

    for raw in text.split("\n"):
        line = raw.rstrip()
        if not line.strip():
            flush_para(); close_list(); continue
        d = chart_directive(line)
        if d:
            flush_para(); close_list(); out.append(d); continue
        if line.startswith("<") and not line.startswith("<a "):     # raw HTML block line
            flush_para(); close_list()
            if line.startswith("<table"):                             # tables scroll inside a wrapper on narrow screens
                line = '<div class="table-scroll">' + line + "</div>"
            out.append(line); continue
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            flush_para(); close_list()
            level = len(m.group(1))                                # ## is h2 under the page's h1 (the title); sources use no # or ###
            title = m.group(2).strip()
            in_sources = level == 2 and title.lower() == "sources"     # a later section (Corrections) ends the sources list
            hid = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
            out.append(f'<h{level} id="{hid}">{inline(title)}</h{level}>')
            continue
        if re.match(r"^(-{3,}|\*{3,})$", line):
            flush_para(); close_list(); out.append("<hr>"); continue
        m = re.match(r"^[-*]\s+(.*)$", line)
        if m:
            flush_para()
            if lst != "ul":
                close_list(); lst = "ul"; out.append('<ul class="sources">' if in_sources else "<ul>")
            out.append("<li>" + inline(m.group(1)) + "</li>"); continue
        m = re.match(r"^\d+[.)]\s+(.*)$", line)
        if m:
            flush_para()
            if lst != "ol":
                close_list(); lst = "ol"; out.append("<ol>")
            out.append("<li>" + inline(m.group(1)) + "</li>"); continue
        m = re.match(r"^>\s?(.*)$", line)
        if m:
            flush_para(); close_list(); out.append("<blockquote><p>" + inline(m.group(1)) + "</p></blockquote>"); continue
        if lst and line.startswith("  "):                              # continuation of a list item
            out[-1] = out[-1][:-5] + " " + inline(line.strip()) + "</li>"; continue
        close_list()
        para.append(line.strip())
    flush_para(); close_list()
    return "\n".join(out)


# ---------------------------------------------------------------------------
def parse(path):
    text = open(path, encoding="utf-8").read()
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", text, re.S)
    if not m:
        raise SystemExit(f"{path}: missing front matter")
    meta = {}
    for ln in m.group(1).split("\n"):
        if ":" in ln:
            k, v = ln.split(":", 1)
            meta[k.strip()] = v.strip()
    for k in ("title", "date"):
        if k not in meta:
            raise SystemExit(f"{path}: front matter needs '{k}'")
    meta["slug"] = os.path.splitext(os.path.basename(path))[0]
    meta["body"] = m.group(2)
    meta["draft"] = meta.get("draft", "").lower() in ("true", "yes", "1")
    return meta


def fmt_date(s):
    y, mo, d = (int(x) for x in s.split("-"))
    return date(y, mo, d).strftime("%B %-d, %Y")


HEAD = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title} — Economy in Context</title>
<meta name="description" content="{desc}">
<link rel="license" href="https://creativecommons.org/licenses/by/4.0/">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Economy in Context">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<link rel="icon" href="/assets/icon.svg" type="image/svg+xml">
<link rel="icon" href="/assets/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta property="og:image" content="https://economyincontext.org/assets/og-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Economy in Context: the main numbers on the U.S. economy, each shown against its own history.">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="../assets/site.css">
</head>
<body>
<header class="masthead">
  <div class="wrap">
    <p class="crumb"><a href="../">Economy in Context</a> <span class="sep">/</span> <a href="./">Articles</a></p>
  </div>
</header>
"""

FOOT = """
<footer class="about">
  <div class="wrap">
    <p>Articles on this site aim to lay out what the figures show, what is settled, what is argued about and by whom. Every number links to its source where one exists, and corrections are noted on the article. The charts are live from the almanac and update as agencies publish.</p>
    <p class="reuse">Free to reuse with credit: Economy in Context (economyincontext.org). The charts and writing here are licensed <a href="https://creativecommons.org/licenses/by/4.0/" rel="license noopener">CC BY 4.0</a>. Credit the data to its source, named on each chart.</p>
    <p>This site has no ads and no agenda beyond putting the numbers in context. It sets no cookies and keeps nothing that identifies you; it does count page views. It is paid for by one reader; <a href="how-this-site-is-paid-for.html">here is how</a>, how visits are counted, and how to chip in if you want to. Questions and corrections: <a href="mailto:hello@economyincontext.org">hello@economyincontext.org</a>.</p>
  </div>
</footer>
<script data-goatcounter="https://economyincontext.goatcounter.com/count" async src="/assets/count.js"></script>
</body>
</html>
"""


def render_article(a):
    desc = html.escape(a.get("dek", a["title"]), quote=True)
    page = HEAD.format(title=html.escape(a["title"]), desc=desc, canonical=f"{SITE}/articles/{a['slug']}.html")
    page += '<main class="wrap article">\n<article>\n'
    page += f'<h1>{inline(a["title"])}</h1>\n'
    if a.get("dek"):
        page += f'<p class="dek">{inline(a["dek"])}</p>\n'
    dates = fmt_date(a["date"])
    if a.get("updated") and a["updated"] != a["date"]:
        dates += f' <span class="sep">·</span> updated {fmt_date(a["updated"])}'
    page += f'<p class="dateline">{dates}</p>\n'
    page += md_to_html(a["body"])
    page += "\n</article>\n</main>\n" + FOOT
    return page


# ---------------------------------------------------------------------------
# The map on the Plain words index: the main loop, with lags on the arrows.
# Styled by .map rules in assets/site.css so it follows the light and dark themes.
# ---------------------------------------------------------------------------
MAP_NODES = [   # (label, href) in loop order; the loop closes back on the first
    ("Fed funds rate", "what-is-the-fed-funds-rate.html"),
    ("10-year yield", "what-is-the-10-year-yield.html"),
    ("Mortgage rate", "what-is-the-mortgage-rate.html"),
    ("Housing starts", "what-are-housing-starts.html"),
    ("Construction jobs", "what-is-the-jobs-report.html"),
    ("Jobs added", "what-is-the-jobs-report.html"),
    ("Wages", "what-is-hourly-pay.html"),
    ("Inflation", "what-is-inflation.html"),
]
MAP_LAGS = ["moves first, on expectations", "days", "3\u20136 months", "months",
            "same month", "6\u201312 months", "6\u201318 months", "next meeting, or sooner"]


def render_map():
    W, H = 480, 520
    bw, bh = 180, 44                       # node box
    lx, rx = 100, 380                      # column centers (left goes down, right comes up)
    ys = [60, 200, 340, 480]               # row centers
    pos = [(lx, ys[0]), (lx, ys[1]), (lx, ys[2]), (lx, ys[3]),
           (rx, ys[3]), (rx, ys[2]), (rx, ys[1]), (rx, ys[0])]
    out = [f'<svg viewBox="0 0 {W} {H}" role="img" aria-labelledby="map-title">',
           '<title id="map-title">How the indicators push on each other: Fed funds to the 10-year yield, '
           'to mortgage rates, to housing starts, to construction jobs, to jobs added, to wages, to inflation, '
           'and back to the Fed.</title>',
           '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           '<path d="M0,0 L10,5 L0,10 z"/></marker></defs>']
    n = len(pos)
    for i in range(n):
        (x1, y1), (x2, y2) = pos[i], pos[(i + 1) % n]
        lag = MAP_LAGS[i]
        if x1 == x2:                                           # vertical, within a column
            d = 1 if y2 > y1 else -1
            ya, yb = y1 + d * bh / 2 + 4, y2 - d * bh / 2 - 4
            out.append(f'<path class="edge" d="M{x1},{ya} L{x2},{yb}" marker-end="url(#arr)"/>')
            tx = x1 + (10 if x1 == lx else -10)                 # beside the arrow, inside the column
            anchor = "start" if x1 == lx else "end"
            words = lag.split(", ")
            for k, w in enumerate(words):
                out.append(f'<text class="lag" x="{tx}" y="{(y1 + y2) / 2 + 4 + (k - (len(words) - 1) / 2) * 14}" text-anchor="{anchor}">{html.escape(w)}</text>')
        else:                                                  # horizontal, across the gap
            d = 1 if x2 > x1 else -1
            xa, xb = x1 + d * bw / 2 + 4, x2 - d * bw / 2 - 4
            out.append(f'<path class="edge" d="M{xa},{y1} L{xb},{y2}" marker-end="url(#arr)"/>')
            words = lag.split(", ")
            for k, w in enumerate(words):                      # one or two short lines above the arrow
                out.append(f'<text class="lag" x="{(x1 + x2) / 2}" y="{y1 - 10 - (len(words) - 1 - k) * 14}" text-anchor="middle">{html.escape(w)}</text>')
    for (label, href), (x, y) in zip(MAP_NODES, pos):
        out.append(f'<a class="node" href="{href}"><rect x="{x - bw / 2}" y="{y - bh / 2}" width="{bw}" height="{bh}" rx="6"/>'
                   f'<text x="{x}" y="{y + 5}" text-anchor="middle">{html.escape(label)}</text></a>')
    out.append('</svg>')
    return ('<figure class="map">' + "".join(out) +
            '<figcaption>The main loop, in the order the effects travel. The lags are typical ranges, not rules, and every link '
            'is argued about on its page. Unemployment and jobless claims are other readings of the jobs stop; GDP is the whole '
            'loop\u2019s output.</figcaption></figure>')


LATEST_SHOWN = 6     # timely pieces listed in full; older ones fold under "Earlier"


def tile_ids(a):
    """The almanac indicator ids a Plain words page explains (its tile: line), in order."""
    return [x.strip() for x in a.get("tile", "").split(",") if x.strip()]


def sort_order(a, default=99):
    try:
        return int(a.get("order", default))
    except ValueError:
        return default


def load_tiles():
    """[(indicator id, section)] in almanac order, from data/series.json; empty if it can't be read."""
    import json
    try:
        with open(os.path.join("data", "series.json"), encoding="utf-8") as f:
            return [(t["id"], t["section"]) for t in json.load(f).get("tiles", [])]
    except Exception as e:                                       # a bad data file must not break the build
        print(f"index: no almanac order ({e}); The numbers listed alphabetically")
        return []


def render_index(articles):
    page = HEAD.format(title="Articles", desc="Longer reads on the U.S. economy: what the figures show, what is settled and what is argued about.",
                       canonical=f"{SITE}/articles/")
    page = page.replace('<a href="./">Articles</a>', "Articles")
    page += '<main class="wrap article">\n<h1>Articles</h1>\n<p class="dek">Longer reads on what the figures show, what is settled, and what is argued about.</p>\n'

    def updated_note(a):
        return (f'<span class="when">Updated {fmt_date(a["updated"])}</span>'
                if a.get("updated") and a["updated"] != a["date"] else "")

    def listing(items, dated):
        # Full entries: title, dek, and the date for timely pieces. Evergreen pages show a
        # date only once they have been updated, so a list of identical launch dates never reads as stale.
        out = '<ul class="article-list">\n'
        for a in items:
            out += (f'<li><a href="{a["slug"]}.html"><span class="t">{inline(a["title"])}</span></a>'
                    + (f'<span class="d">{inline(a["dek"])}</span>' if a.get("dek") else "")
                    + (f'<span class="when">{fmt_date(a["date"])}</span>' if dated else updated_note(a)) + "</li>\n")
        return out + "</ul>\n"

    def compact(items):
        # One line each: the short name, then the hook. Page titles stay as they are for search.
        out = '<ul class="compact-list">\n'
        for a in items:
            label, hook = a.get("label") or a["title"], a.get("hook") or ("" if a.get("label") else a.get("dek", ""))
            out += (f'<li><a href="{a["slug"]}.html">{inline(label)}</a>'
                    + (f'<span class="h"><span class="sep" aria-hidden="true"> — </span>{inline(hook)}</span>' if hook else "")
                    + updated_note(a) + "</li>\n")
        return out + "</ul>\n"

    timely = [a for a in articles if a.get("kind") not in ("concept", "path", "page")]    # newest first (main() sorts)
    paths = sorted((a for a in articles if a.get("kind") == "path"), key=lambda a: (sort_order(a, 9), a["title"]))
    concepts = [a for a in articles if a.get("kind") == "concept"]
    numbers = [a for a in concepts if tile_ids(a)]
    ideas = sorted((a for a in concepts if not tile_ids(a)), key=lambda a: (sort_order(a), a["title"]))

    jump = [("#latest", "Latest", timely), ("#household-paths", "Your situation", paths),
            ("#the-numbers", "The numbers", numbers), ("#the-ideas", "The ideas", ideas)]
    page += ('<nav class="jump" aria-label="On this page">'
             + "".join(f'<a href="{h}">{t}</a>' for h, t, items in jump if items) + "</nav>\n")

    if timely:
        page += '<h2 id="latest">Latest</h2>\n' + listing(timely[:LATEST_SHOWN], dated=True)
        if len(timely) > LATEST_SHOWN:
            page += (f'<details class="earlier"><summary>Earlier pieces ({len(timely) - LATEST_SHOWN})</summary>\n'
                     + listing(timely[LATEST_SHOWN:], dated=True) + "</details>\n")
    if paths:
        page += '<h2 id="household-paths">Start from your situation</h2>\n<p class="dek">Which of the numbers reach you, in what order, and how long they take. One page per kind of household.</p>\n'
        page += listing(paths, dated=False)
    if concepts:
        page += '<h2 id="plain-words">Plain words</h2>\n<p class="dek">What each number is, how it reaches your household, and where the usual analogies break. Evergreen; updated when the facts change.</p>\n'
    if numbers:
        tiles = load_tiles()
        position = {tid: i for i, (tid, _) in enumerate(tiles)}
        section_of = dict(tiles)
        numbers.sort(key=lambda a: (position.get(tile_ids(a)[0], len(tiles)), a["title"]))
        groups = []                              # [(almanac section, [pages])], in the almanac's order
        for a in numbers:
            sec = section_of.get(tile_ids(a)[0], "More numbers" if tiles else "")
            if groups and groups[-1][0] == sec:
                groups[-1][1].append(a)
            else:
                groups.append((sec, [a]))
        page += '<h3 id="the-numbers">The numbers</h3>\n<p class="lede">Pages for the numbers on the almanac, grouped as they are there.</p>\n'
        page += render_map() + "\n"
        for sec, items in groups:
            page += '<section class="num-group">' + (f"<h4>{html.escape(sec)}</h4>" if sec else "") + compact(items) + "</section>\n"
    if ideas:
        page += '<h3 id="the-ideas">The ideas</h3>\n<p class="lede">The handful of ideas that untangle most arguments about the numbers.</p>\n'
        page += compact(ideas)
    page += "</main>\n" + FOOT
    return page


def write_explainers(out_root, articles):
    """data/explainers.json: indicator id -> its Plain words page, from each page's tile: line.
    The almanac and the chart pages read it to link every number to its explainer."""
    import json
    ex = {}
    for a in articles:
        if a.get("kind") != "concept":
            continue
        for tid in tile_ids(a):
            ex[tid] = {"url": f"articles/{a['slug']}.html", "title": a["title"], "hook": a.get("hook", "")}
    os.makedirs(os.path.join(out_root, "data"), exist_ok=True)
    with open(os.path.join(out_root, "data", "explainers.json"), "w", encoding="utf-8") as f:
        json.dump({"note": "Written by tools/build_articles.py from the tile: line of each Plain words page.",
                   "explainers": ex}, f, ensure_ascii=False, separators=(",", ":"))
    print(f"built data/explainers.json ({len(ex)} indicators)")


def body_offset(path, body):
    """Lines before the body (the front matter), so directive warnings name the file's own line."""
    text = open(path, encoding="utf-8").read()
    return text[: len(text) - len(body)].count("\n")


def load_figures():
    """tools/figures.py and the committed data, or None. A missing module or unreadable data
    leaves every live figure at its else= text with a warning; the build itself never fails on it."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import figures
        return figures, figures.Data("data")
    except Exception as e:                                  # noqa: BLE001
        print(f"figures: not available ({e}); live figures print their fallback text")
        return None, None


def main():
    out_root = sys.argv[1] if len(sys.argv) > 1 else "public"
    out_dir = os.path.join(out_root, "articles")
    os.makedirs(out_dir, exist_ok=True)
    figures, data = load_figures()
    report = figures.new_report() if figures else None
    articles = []
    if os.path.isdir(SRC_DIR):
        for name in sorted(os.listdir(SRC_DIR)):
            if name.endswith(".md"):
                path = os.path.join(SRC_DIR, name)
                a = parse(path)
                if a["draft"]:
                    print(f"skip draft {name}")
                    continue
                if figures and data:
                    a["body"] = figures.render(a["body"], data, a["slug"], report, body_offset(path, a["body"]))
                elif "{{v " in a["body"] or "{{fig " in a["body"] or "{{check " in a["body"] or "{{due " in a["body"]:
                    a["body"] = re.sub(r"\s*\{\{\s*(?:check|due)\s+.*?\}\}", "", a["body"])
                    a["body"] = re.sub(r"\{\{\s*(?:v|fig)\s+.*?\}\}", "", a["body"])
                articles.append(a)
    articles.sort(key=lambda a: a["date"], reverse=True)
    for a in articles:
        with open(os.path.join(out_dir, a["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(render_article(a))
        print(f"built articles/{a['slug']}.html")
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_index(articles))
    print(f"built articles/index.html ({len(articles)} articles)")
    write_explainers(out_root, articles)
    write_sitemap(out_root, articles)
    if report is not None:
        print(figures.summarize(report))
        try:                                                # outside the published folder; read by the weekly check
            with open(os.environ.get("FIGURES_REPORT", "build-report.json"), "w", encoding="utf-8") as f:
                json.dump(report, f, indent=1)
        except OSError as e:
            print(f"figures: could not write the report ({e})")


def write_sitemap(out_root, articles):
    """sitemap.xml and robots.txt at the site root: the almanac, the chart index, one chart page per
    indicator (read from data/series.json when present), the articles index and every article."""
    import json
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [(f"{SITE}/", today, "daily", "1.0"), (f"{SITE}/chart.html", today, "weekly", "0.6")]
    series_path = os.path.join("data", "series.json")
    if os.path.exists(series_path):
        try:
            for t in json.load(open(series_path, encoding="utf-8")).get("tiles", []):
                urls.append((f"{SITE}/chart.html?id={t['id']}", today, "daily", "0.8"))
        except Exception as e:                                  # a bad data file must not break the build
            print(f"sitemap: skipped chart pages ({e})")
    urls.append((f"{SITE}/articles/", today, "weekly", "0.8"))
    for a in articles:
        urls.append((f"{SITE}/articles/{a['slug']}.html", a.get("updated") or a["date"], "monthly", "0.7"))
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod, freq, pri in urls:
        xml.append(f"  <url><loc>{html.escape(loc, quote=True)}</loc><lastmod>{mod}</lastmod><changefreq>{freq}</changefreq><priority>{pri}</priority></url>")
    xml.append("</urlset>")
    with open(os.path.join(out_root, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(xml) + "\n")
    with open(os.path.join(out_root, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n")
    print(f"built sitemap.xml ({len(urls)} urls) and robots.txt")


if __name__ == "__main__":
    main()
