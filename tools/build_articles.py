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
    featured: 2026-11-04         (optional: from that date (UTC, at the next build) the article is
                                  the Featured line at the top of the almanac and the articles index.
                                  The newest date that has arrived wins, so featuring another article
                                  needs only a later date on it; a future date schedules it.)
    menu: articles               (optional, Nov 9: which menu item a page sits under, articles, about or situation;
                                 a kind: page sits under About otherwise)
    picture: health_jobs range=10y   (optional: the picture on the Featured card while this article is featured:
                                  a tile id and, optionally, the view's range and ov, as in a chart page's address;
                                  drawn like the Make your own chart picture. For a series, picture in series.json.)
    teaser: what a town gets from a new business   (optional, Nov 9: the few words after the title on the home page's
                                  one-line Featured strip, lower case, no closing period; without one the strip shows
                                  the title alone. For a series, teaser in series.json.)
    ---

then Markdown. Supported: # ## ### headings, paragraphs, **bold**, *italic*,
[links](url), - bullet lists, 1. numbered lists, > quotes, --- rules, and raw
HTML lines (left as they are). Plus one directive for a live chart from the
site's own detail page:

    {{chart id=cpi range=10y ov=fed_target,pce caption="Inflation and the Fed's target."}}

and one for a small static figure drawn from numbers in the article (plain HTML, styled by
assets/site.css, so it follows the light and dark themes and reads at phone width):

    {{figure kind=bars title="Lobbying by group, 2025" rows="Drugmakers=168.0;Insurers=76.4" fmt="${v} million" caption="…" source="…"}}
    {{figure kind=stack title="Where a restaurant dollar goes" rows="Food=33;Labor=33;Everything else=29;Left over=5" fmt="{v}¢" caption="…"}}
    {{figure kind=pairs title="Fires per 10,000 vehicles" series="EVs;Other cars" rows="Sweden=0.45,7.5;Norway=0.55,3.9" caption="…"}}

and one for a hand-drawn illustration kept as an SVG file in articles/illustrations/ (Nov 9), inlined so it
picks up the page's font and both color themes from assets/site.css (.illo):

    {{illustration name=overdraft-statement caption="One sentence that says what the picture shows."}}

The SVG carries its own role="img", <title> and <desc> (the full text of the picture), and uses only the
classes in site.css's illustration block, never colors of its own. A missing file prints a WARNING and draws nothing.

kind=bars: one bar per row, one color, the value printed at each bar's tip. kind=stack: one
whole split into its parts, up to six, each part's value printed on it, a legend of names.
kind=pairs: two values per row, two colors, with a legend. fmt writes each value ({v} is the
number as given). The figure's accessible name lists every value, so nothing is color-only.

Anything under `## Sources`, up to the next heading, is rendered as a sources list.

Series (articles/series.json, optional): a series lists its parts in reading order by slug, each with a short
label. Every part gets a series box under its dateline (the series title linking to its group on the index, then
the parts, the current one unlinked) and a "Next in this series" line before See also; the index groups the parts
under the series title where the first part would fall. A series with featured: YYYY-MM-DD becomes the Featured
line by the same rule as an article (the newest date that has arrived wins; a series wins a tie), shown as the
series title, its dek and the parts. Optional landing: <slug> (Nov 9) names a page (usually kind: page) that
introduces the series; the series box's title, the series' Latest entry, its group heading on the index and its
Featured card then link there instead of to the index or part 1, and the landing page sits under Articles in the menu.
A missing or unreadable file, or a part that isn't an article, only prints a
line; the build never fails on it.

The build also writes one page per chart (chart/<id>/index.html, from the copy of chart.html already in
the output folder; see tools/chart_pages.py), the articles feed (articles/feed.xml, Atom), and the sitemap.
Links in articles to chart.html?id=<id> are pointed at chart/<id>/; embeds stay on chart.html.

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
    view = "&".join(x for x in q if not x.startswith(("id=", "embed=")))
    cap = attrs.get("caption", "")
    height = attrs.get("height", "600")
    return (f'<figure class="chart-embed">'
            f'<iframe src="../chart.html?{html.escape(query, quote=True)}" title="Chart: {html.escape(attrs["id"])}" '
            f'loading="lazy" height="{html.escape(height)}"></iframe>'
            f'<figcaption>{inline(cap) + " " if cap else ""}'
            f'<a href="../chart/{html.escape(attrs["id"], quote=True)}/{"?" + html.escape(view, quote=True) if view else ""}">Full chart and context →</a></figcaption></figure>')


def figure_directive(line):
    """{{figure kind=bars|stack|pairs title=… rows="a=1;b=2" [series="x;y"] [fmt="{v}"] [caption=…] [source=…]}}
    → a <figure class="figure fig-<kind>"> in plain HTML. Numbers are the author's; nothing is fetched."""
    m = re.match(r"^\{\{\s*figure\s+(.*?)\s*\}\}$", line.strip())
    if not m:
        return None
    attrs = {}
    for tok in shlex.split(m.group(1)):
        if "=" in tok:
            k, v = tok.split("=", 1)
            attrs[k] = v
    kind = attrs.get("kind", "bars")
    if kind not in ("bars", "stack", "pairs") or not attrs.get("rows"):
        print(f"figure: WARNING skipped a {kind!r} figure without rows")
        return None
    fmt = attrs.get("fmt", "{v}")
    def num(x):
        return float(x.replace(",", "").replace("$", ""))
    shown = {}                                              # each value is printed as the author wrote it
    def show(v):
        return fmt.replace("{v}", shown.get(v, ("%g" % v)))
    rows = []
    for item in attrs["rows"].split(";"):
        if "=" not in item:
            continue
        name, vals = item.split("=", 1)
        nums = []
        for x in vals.split(","):
            if x.strip():
                nums.append(num(x)); shown.setdefault(nums[-1], x.strip().lstrip("$"))
        rows.append((name.strip(), nums))
    if not rows or any(not v for _, v in rows):
        print("figure: WARNING skipped a figure with an empty row")
        return None
    series = [x.strip() for x in attrs.get("series", "").split(";") if x.strip()]
    title = attrs.get("title", "")
    parts = []
    if kind == "stack":
        total = sum(v[0] for _, v in rows) or 1
        rows = rows[:6]
        said = "; ".join(f"{n} {show(v[0])}" for n, v in rows)
        # a block too narrow for its value (under 8% of the bar) prints none; that value goes on its legend entry
        narrow = {i for i, (n, v) in enumerate(rows) if v[0] / total < 0.08}
        blocks = "".join(
            f'<span class="seg s{i + 1}" style="width:{v[0] / total * 100:.2f}%">'
            + ("" if i in narrow else f'<span class="v">{html.escape(show(v[0]))}</span>') + "</span>"
            for i, (n, v) in enumerate(rows) if v[0] > 0)
        legend = "".join(f'<li><i class="s{i + 1}"></i>{html.escape(n)}' + (f' <span class="v">{html.escape(show(v[0]))}</span>' if i in narrow else "") + "</li>"
                         for i, (n, v) in enumerate(rows))
        parts.append(f'<div class="stack" role="img" aria-label="{html.escape(title + ": " + said, quote=True)}">{blocks}</div>')
        parts.append(f'<ul class="legend" aria-hidden="true">{legend}</ul>')
    else:
        n_series = 2 if kind == "pairs" else 1
        top = max(x for _, v in rows for x in v[:n_series]) or 1
        said = []
        body = []
        for n, v in rows:
            vals = v[:n_series] + [0.0] * (n_series - len(v[:n_series]))
            said.append(n + " " + (", ".join(f"{series[i] if i < len(series) else ''} {show(x)}".strip() for i, x in enumerate(vals)) if n_series > 1 else show(vals[0])))
            bars = "".join(
                f'<span class="bar"><i class="s{i + 1}" style="width:{x / top * 100:.2f}%"></i><span class="v">{html.escape(show(x))}</span></span>'
                for i, x in enumerate(vals))
            body.append(f'<div class="row"><span class="lab">{html.escape(n)}</span><span class="bars">{bars}</span></div>')
        parts.append(f'<div class="rows" role="img" aria-label="{html.escape(title + ": " + "; ".join(said), quote=True)}">{"".join(body)}</div>')
        if n_series > 1 and series:
            parts.append('<ul class="legend" aria-hidden="true">' + "".join(f'<li><i class="s{i + 1}"></i>{html.escape(x)}</li>' for i, x in enumerate(series[:2])) + "</ul>")
    cap = inline(attrs["caption"]) if attrs.get("caption") else ""
    src = attrs.get("source", "")
    if src:
        cap += (" " if cap else "") + f'<span class="src">Source: {inline(src)}</span>'
    head = f'<p class="ftitle">{inline(title)}</p>' if title else ""
    return (f'<figure class="figure fig-{kind}">{head}{"".join(parts)}'
            + (f"<figcaption>{cap}</figcaption>" if cap else "") + "</figure>")


ILLO_DIR = os.path.join("articles", "illustrations")


def illustration_directive(line):
    """{{illustration name=<file> [caption=…]}} -> <figure class="illo"> holding articles/illustrations/<file>.svg,
    inlined. Fail-soft: a bad name or a missing file prints a WARNING and leaves an HTML comment."""
    m = re.match(r"^\{\{\s*illustration\s+(.*?)\s*\}\}$", line.strip())
    if not m:
        return None
    attrs, inner = {}, m.group(1)
    cm = re.search(r'\bcaption="(.*)"$', inner)            # the caption runs to the last quote, so it may quote words
    if cm:                                                 # inside it (Nov 9 fix: shlex cut those captions short)
        attrs["caption"], inner = cm.group(1), inner[:cm.start()]
    for tok in shlex.split(inner):
        if "=" in tok:
            k, v = tok.split("=", 1)
            attrs[k] = v
    name = attrs.get("name", "")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", name):
        print(f"illustration: WARNING skipped one with a bad name ({name!r})")
        return "<!-- illustration skipped -->"
    try:
        with open(os.path.join(ILLO_DIR, name + ".svg"), encoding="utf-8") as f:
            svg = f.read()
    except OSError as e:
        print(f"illustration: WARNING {name}.svg not drawn ({e})")
        return f"<!-- illustration {name} missing -->"
    svg = re.sub(r"<\?xml.*?\?>|<!--.*?-->", "", svg, flags=re.S)
    svg = re.sub(r">\s+<", "><", svg.strip())                    # one line: the Markdown pass never sees it
    cap = inline(attrs["caption"]) if attrs.get("caption") else ""
    return (f'<figure class="illo" id="fig-{name}">{svg}'
            + (f"<figcaption>{cap}</figcaption>" if cap else "") + "</figure>")


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
        d = chart_directive(line) or figure_directive(line) or illustration_directive(line)
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


def featured_pick(articles, today=None, series=None):
    """(current, next): the article or series whose featured: date is the newest one on or before today
    (UTC), and the soonest one still to come. Either can be None; malformed dates are ignored. A series
    (kind "series", from articles/series.json) wins a tie with an article on the same date."""
    from datetime import datetime, timezone
    today = today or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    items = list(articles) + list(SERIES if series is None else series)
    dated = [a for a in items if re.fullmatch(r"\d{4}-\d{2}-\d{2}", a.get("featured", ""))]
    past = [a for a in dated if a["featured"] <= today]
    future = [a for a in dated if a["featured"] > today]
    cur = max(past, key=lambda a: (a["featured"], a.get("kind") == "series", a["date"])) if past else None
    nxt = min(future, key=lambda a: a["featured"]) if future else None
    return cur, nxt


SERIES = []        # [{kind, slug, title, dek, featured, date, parts: [{slug, label, title}]}], from load_series()
SERIES_OF = {}     # article slug -> (series, index of the part)
LANDINGS = {}      # landing-page slug -> its series (Nov 9)
SERIES_FOLD = 8    # a series box with more parts than this folds them behind "Show all N parts" (Nov 9)
FEATURED_PARTS = 4  # a featured series with a landing page and more than SERIES_FOLD parts shows its first few parts and
                    # then "All N parts", linking to the landing page, so the Featured card stays short (Nov 9)


def load_series(articles, path=os.path.join("articles", "series.json")):
    """Read articles/series.json into SERIES and SERIES_OF. Fail-soft: a missing file means no series;
    a bad file, or a part that isn't a listed article, prints a line and is skipped."""
    global SERIES, SERIES_OF, LANDINGS
    SERIES, SERIES_OF, LANDINGS = [], {}, {}
    if not os.path.exists(path):
        return
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f).get("series", {})
    except Exception as e:                                  # noqa: BLE001
        print(f"series: could not read {path} ({e}); no series this build")
        return
    by_slug = {a["slug"]: a for a in articles}
    for sid, d in raw.items():
        parts = []
        for p in d.get("parts", []):
            a = by_slug.get(p.get("slug", ""))
            if not a or a.get("kind") == "page":
                print(f"series: {sid}: part {p.get('slug')!r} is not a listed article; left out")
                continue
            if a["slug"] in SERIES_OF:
                print(f"series: {sid}: {a['slug']} is already in another series; left out")
                continue
            parts.append({"slug": a["slug"], "label": p.get("label") or a.get("label") or a["title"], "title": a["title"]})
        if len(parts) < 2 or not d.get("title"):
            print(f"series: {sid}: needs a title and at least two parts; skipped")
            continue
        landing = d.get("landing", "")
        if landing and landing not in by_slug:
            print(f"series: {sid}: landing page {landing!r} is not an article; linking to the index instead")
            landing = ""
        s = {"kind": "series", "slug": sid, "title": d["title"], "dek": d.get("dek", ""), "featured": d.get("featured", ""),
             "picture": d.get("picture", ""), "teaser": d.get("teaser", ""),
             "date": max(by_slug[p["slug"]]["date"] for p in parts), "parts": parts, "landing": landing}
        if landing:
            LANDINGS[landing] = s
        SERIES.append(s)
        for i, p in enumerate(parts):
            SERIES_OF[p["slug"]] = (s, i)
    print(f"series: {len(SERIES)} ({', '.join(s['slug'] + ' ' + str(len(s['parts'])) + ' parts' for s in SERIES) or 'none'})")


def series_box(slug):
    """The box under an article's dateline: the series title (to its group on the index) and the parts, the current one unlinked."""
    if slug not in SERIES_OF:
        return ""
    s, i = SERIES_OF[slug]
    items = "".join(
        (f'<li aria-current="page"><span class="n">{k + 1}</span> {inline(p["label"])}</li>' if k == i else
         f'<li><a href="{p["slug"]}.html" title="{html.escape(p["title"], quote=True)}"><span class="n">{k + 1}</span> {inline(p["label"])}</a></li>')
        for k, p in enumerate(s["parts"]))
    parts = f'<ol class="series-parts" role="list">{items}</ol>'
    if len(s["parts"]) > SERIES_FOLD:              # a long series folds its parts, so the article starts on the first screen (Nov 9)
        parts = (f'<details class="series-all"><summary><span class="more">Show all {len(s["parts"])} parts</span>'
                 f'<span class="less">Hide the parts</span></summary>{parts}</details>')
    return (f'<nav class="series" aria-label="Series: {html.escape(s["title"], quote=True)}">'
            f'<p class="series-name"><span class="series-label">Series, part {i + 1} of {len(s["parts"])}</span> '
            f'<a href="{s["landing"] + ".html" if s.get("landing") else "./#series-" + s["slug"]}">{inline(s["title"])}</a></p>'
            f'{parts}</nav>\n')


def series_next(slug):
    """Before See also: the next part, or, on the last part, links back to the others."""
    if slug not in SERIES_OF:
        return ""
    s, i = SERIES_OF[slug]
    if i + 1 < len(s["parts"]):
        p = s["parts"][i + 1]
        body = (f'<span class="series-label">Next in this series, part {i + 2} of {len(s["parts"])}</span> '
                f'<a href="{p["slug"]}.html">{inline(p["title"])}</a> →')
    else:
        others = " · ".join(f'<a href="{p["slug"]}.html">{k + 1}. {inline(p["label"])}</a>' for k, p in enumerate(s["parts"][:-1]))
        body = f'<span class="series-label">Earlier in this series</span> {others}'
    label = "Next in this series" if i + 1 < len(s["parts"]) else "Earlier in this series"
    return f'<nav class="series-next" aria-label="{label}"><p>{body}</p></nav>\n'


def featured_picture(feat):
    """The Featured card's picture: the item's `picture` field ("<tile id> [range=…] [ov=…]") drawn like the Make your own
    chart picture, as inline SVG, or "" (no field, or no data)."""
    spec = (feat.get("picture") or "").split()
    if not spec:
        return ""
    query = "&".join(x for x in spec[1:] if "=" in x)
    return chart_prompt_thumb(spec[0], query)


def featured_html(feat, link_prefix=""):
    """The Featured card on the articles index: an article (title, dek), or a series (title to part 1, dek, parts),
    with its picture at the foot when it has one."""
    dek = f'<p class="fdek">{inline(feat["dek"])}</p>' if feat.get("dek") else ""   # cut to two lines by site.css
    url = f'{link_prefix}{(feat.get("landing") or feat["parts"][0]["slug"]) if feat.get("kind") == "series" else feat["slug"]}.html'
    svg = featured_picture(feat)
    pic = f'<a class="cthumb" href="{url}" aria-hidden="true" tabindex="-1">{svg}</a>' if svg else ""
    if feat.get("kind") == "series":
        shown, more = feat["parts"], ""
        if feat.get("landing") and len(shown) > SERIES_FOLD:
            shown = shown[:FEATURED_PARTS]
            more = f'<p class="fmore"><a href="{url}">All {len(feat["parts"])} parts</a> →</p>'
        parts = "".join(f'<li><a href="{link_prefix}{p["slug"]}.html" title="{html.escape(p["title"], quote=True)}"><span class="n">{k + 1}</span> {inline(p["label"])}</a></li>'
                        for k, p in enumerate(shown))
        return (f'<aside class="featured featured-series" aria-label="Featured series"><div class="ctext"><span class="flabel">Featured series</span>'
                f'<a class="ftitle" href="{url}">{inline(feat["title"])}</a> →{dek}'
                f'<ol class="fparts" role="list">{parts}</ol>{more}</div>{pic}</aside>\n')
    return (f'<aside class="featured" aria-label="Featured article"><div class="ctext"><span class="flabel">Featured</span>'
            f'<a class="ftitle" href="{url}">{inline(feat["title"])}</a> →{dek}</div>{pic}</aside>\n')


def chart_prompt_pick(path=os.path.join("articles", "chart-prompts.json"), today=None):
    """The Make your own chart card (called Chart to try until Nov 6): the prompt with the newest date on or before today (UTC), as
    {text, link, url} with url relative to the site root, or None. Fail-soft: a missing or bad file, or a
    prompt whose chart has no page this build, means no line (with a log line)."""
    from datetime import datetime, timezone
    today = today or datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as f:
            prompts = json.load(f).get("prompts", [])
    except Exception as e:                                  # noqa: BLE001
        print(f"chart prompt: could not read {path} ({e}); none this build")
        return None
    live = sorted((p for p in prompts if isinstance(p, dict) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(p.get("date", "")))
                   and p["date"] <= today and p.get("text") and p.get("chart")), key=lambda p: p["date"])
    if not live:
        print("chart prompt: none")
        return None
    p = live[-1]
    if CHART_IDS and p["chart"] not in CHART_IDS:
        print(f"chart prompt: WARNING {p['chart']!r} has no chart page; none this build")
        return None
    url = f"chart/{p['chart']}/" + (f"?{p['query']}" if p.get("query") else "")
    print(f"chart prompt: {p['chart']} (since {p['date']})")
    cp = {"title": p.get("title") or p.get("link") or "See the chart", "text": p["text"], "url": url}
    svg = chart_prompt_thumb(p["chart"], p.get("query", ""))
    if svg:
        cp["svg"] = svg
    return cp


def chart_prompt_thumb(tile_id, query, series_path=os.path.join("data", "series.json"),
                       companions_path=os.path.join("data", "companions.json")):
    """A small picture of the Make your own chart view, as inline SVG (220x64 viewBox, colors from CSS tokens, no
    axes): the indicator over the view's range, with the first companion series the view turns on that shares its
    scale. Fail-soft: anything missing means no picture (with a log line), and the line still shows."""
    from datetime import date as _date
    try:
        with open(series_path, encoding="utf-8") as f:
            tiles = json.load(f).get("tiles", [])
        tile = next((t for t in tiles if t.get("id") == tile_id), None)
        if not tile or not tile.get("observations"):
            print(f"chart prompt: no thumbnail (no data for {tile_id!r})")
            return ""
        q = dict(x.split("=", 1) for x in query.split("&") if "=" in x)
        years = {"1y": 1, "5y": 5, "10y": 10, "25y": 25, "50y": 50, "all": None}.get(q.get("range", "25y"), 25)
        last = tile["observations"][-1][0]
        ly, lm = int(last[:4]), int(last[5:7])
        start = f"{ly - years:04d}-{lm:02d}" if years else "0000-00"
        if re.fullmatch(r"\d{4}-\d{2}", q.get("from", "")):
            start = q["from"]
        end = q["to"] + "-99" if re.fullmatch(r"\d{4}-\d{2}", q.get("to", "")) else "9999"
        def window(obs):
            pts = [(d, v) for d, v in obs if v is not None and start <= d[:7] and d <= end]
            step = max(1, len(pts) // 260)                   # weekly series over long ranges: thin to about 260 points
            return pts[::step] if step > 1 else pts
        main = window(tile["observations"])
        if len(main) < 2:
            return ""
        comp = None
        wanted = [x for x in q.get("ov", "").split(",") if x]
        if wanted and os.path.exists(companions_path):
            with open(companions_path, encoding="utf-8") as f:
                comps = {c["id"]: c for c in json.load(f).get("companions", []) if c.get("id")}
            for cid in wanted:
                c = comps.get(cid)
                if c and tile_id in (c.get("for") or []) and not c.get("panel") and c.get("observations"):
                    w = window(c["observations"])
                    if len(w) >= 2:
                        comp = w
                        break
        W, H, pad = 220, 64, 3
        xs = [d for d, _ in main] + ([d for d, _ in comp] if comp else [])
        x0, x1 = min(xs), max(xs)
        def days(d):
            return _date(int(d[:4]), int(d[5:7]), int(d[8:10])).toordinal()
        d0, d1 = days(x0), max(days(x1), days(x0) + 1)
        vs = [v for _, v in main] + ([v for _, v in comp] if comp else [])
        lo, hi = min(vs), max(vs)
        if hi - lo < 1e-9:
            lo, hi = lo - 1, hi + 1
        span = hi - lo
        lo, hi = lo - span * 0.04, hi + span * 0.04
        def X(d):
            return pad + (days(d) - d0) / (d1 - d0) * (W - 2 * pad)
        def Y(v):
            return pad + (hi - v) / (hi - lo) * (H - 2 * pad)
        def path(pts):
            return "M" + " L".join(f"{X(d):.1f},{Y(v):.1f}" for d, v in pts)
        parts = []
        if lo < 0 < hi:
            parts.append(f'<line class="zero" x1="{pad}" x2="{W - pad}" y1="{Y(0):.1f}" y2="{Y(0):.1f}"/>')
        if comp:
            parts.append(f'<path class="comp" d="{path(comp)}"/>')
        parts.append(f'<path class="main" d="{path(main)}"/>')
        ld, lv = main[-1]
        # the end dot is a zero-length round-capped stroke, so it stays round however the picture is stretched
        parts.append(f'<path class="end-halo" d="M{X(ld):.1f},{Y(lv):.1f} h0.01"/><path class="end" d="M{X(ld):.1f},{Y(lv):.1f} h0.01"/>')
        return (f'<svg class="thumb" viewBox="0 0 {W} {H}" preserveAspectRatio="none" aria-hidden="true" focusable="false">'
                + "".join(parts) + "</svg>")
    except Exception as e:                                  # noqa: BLE001
        print(f"chart prompt: no thumbnail ({e})")
        return ""


# The fixed line under every prompt on the Make your own chart card (Nov 6; the same words in index.html)
MAKE_YOUR_OWN = "Add a recession, a president or another line, then copy it into a slide, a paper or a newsletter. Free to use with credit."


def chart_prompt_html(cp, link_prefix=""):
    if not cp:
        return ""
    href = f'{link_prefix}{html.escape(cp["url"], quote=True)}'
    thumb = (f'<a class="cthumb" href="{href}" aria-hidden="true" tabindex="-1">{cp["svg"]}</a>'
             if cp.get("svg") else "")                      # the picture repeats the title's link, so it is skipped by assistive tech
    return (f'<aside class="chart-try" aria-label="Make your own chart"><div class="ctext"><span class="flabel">Make your own chart</span>'
            f'<a class="ftitle" href="{href}">{inline(cp["title"])}</a> →'
            f'<p class="fdek">{inline(cp["text"])}</p><p class="fhow">{MAKE_YOUR_OWN}</p></div>{thumb}</aside>\n')


def fmt_date(s):
    y, mo, d = (int(x) for x in s.split("-"))
    return date(y, mo, d).strftime("%B %-d, %Y")


# New / Revised labels (Nov 8): an article dated within LABEL_DAYS gets a "New" chip in the Featured teal wash; one
# whose updated: date is, a quieter "Revised Nov 5". Nothing dated before LABEL_START is labeled. Written at build
# time with its end date in data-until; a line of script in FOOT removes it on that day, so it never outlives a
# weekend without a rebuild. Same rule as index.html (freshLabel) and chart.html.
LABEL_START, LABEL_DAYS = "2026-11-01", 14


def fresh_label(a):
    from datetime import timedelta
    today = date.today()
    def until(s):
        if not s or s < LABEL_START:
            return None
        y, mo, d = (int(x) for x in s.split("-"))
        return date(y, mo, d) + timedelta(days=LABEL_DAYS)
    new, rev = until(a.get("date")), until(a.get("updated") if a.get("updated") != a.get("date") else None)
    if new and today < new:
        return f' <span class="fresh" data-until="{new.isoformat()}">New</span>'
    if rev and today < rev:
        y, mo, d = (int(x) for x in a["updated"].split("-"))
        return f' <span class="fresh rev" data-until="{rev.isoformat()}">Revised {date(y, mo, d).strftime("%b %-d")}</span>'
    return ""


_STAMPS = {}
def asset_stamp(path):
    """A cache stamp for a stylesheet or script link: ?v= plus eight hex characters of the file's hash, so a
    changed file is fetched fresh while an unchanged one stays cached (GitHub Pages caches every file for ten
    minutes under its fixed name). An unreadable file gets no stamp."""
    if path not in _STAMPS:
        try:
            import hashlib
            with open(path, "rb") as f:
                _STAMPS[path] = "?v=" + hashlib.sha256(f.read()).hexdigest()[:8]
        except OSError:
            _STAMPS[path] = ""
    return _STAMPS[path]


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
<link rel="alternate" type="application/atom+xml" title="Economy in Context: new articles" href="/articles/feed.xml">
<meta property="og:image" content="https://economyincontext.org/assets/og-card.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Economy in Context: the main numbers on the U.S. economy, each shown against its own history.">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="../assets/site.css{css_v}">
</head>
<body>
<header class="masthead" id="top">
  <div class="wrap">
    <div class="title-row"><a class="brand" href="/"><svg class="mark" viewBox="0 0 64 64" aria-hidden="true" focusable="false"><path d="M25 14H15V50H25"/><path d="M39 14H49V50H39"/><circle cx="32" cy="32" r="8.5"/></svg><span class="nm">Economy <span class="bl">in Context</span><span aria-hidden="true">.</span></span></a>{menu}</div>
  </div>
</header>
"""

# The site menu (Batch B, Nov 6), the same as the home page's and the chart pages': The numbers, Your situation, Tools,
# Articles, About. `here` names the item for the page (aria-current="page") or the part of the site it belongs to
# (aria-current="true"). Tools (Nov 8) carries class m-wide: shown at 900px and wider only, where five items fit on one row
# in the home page's masthead; phones reach Tools from footers, the home page card, tiles and the household pages.
MENU = [("numbers", "/?view=all", "The numbers"), ("situation", "/#your-situation", "Your situation"),
        ("tools", "/tools/", "Tools"), ("articles", "/articles/", "Articles"), ("about", "/articles/about.html", "About")]


def site_menu(here=None, page=False):
    cur = ' aria-current="page"' if page else ' aria-current="true"'
    return ('<nav class="site-menu" aria-label="Site">'
            + "".join(f'<a href="{u}"{' class="m-wide"' if k == "tools" else ""}{cur if k == here else ""}>{t}</a>'
                      for k, u, t in MENU) + "</nav>")


def menu_for(a):
    """Which menu item an article belongs to: About (the About page itself is the page), Your situation for the
    household paths, Articles for the rest."""
    if a["slug"] == "about":
        return site_menu("about", page=True)
    if a.get("kind") == "tool":
        return site_menu("tools", page=a.get("out") == "index")
    if a["slug"] in LANDINGS:                       # a series' landing page sits under Articles (Nov 9)
        return site_menu("articles")
    if a.get("menu") in ("articles", "about", "situation"):   # front matter `menu:` places a page by hand (Nov 9: the teaching page)
        return site_menu(a["menu"])
    if a.get("kind") == "page":
        return site_menu("about")
    if a.get("kind") == "path":
        return site_menu("situation")
    return site_menu("articles")


DIGEST_NUDGE = ('<p class="digest-nudge">New articles and charts arrive in one short email on Monday mornings. '
                '<a href="#weekly">Get the weekly digest</a></p>\n')

FOOT = """
<div class="wrap signup-wrap">
  <section class="signup" id="weekly" aria-labelledby="weekly-h">
    <h2 id="weekly-h">The weekly digest</h2>
    <p class="stext">One email on Monday mornings: the week's new articles and charts, the numbers that moved most, and what comes out in the week ahead. No ads, and no tracking of opens or clicks.</p>
    <form action="https://buttondown.com/api/emails/embed-subscribe/EconomyInContext" method="post">
      <label for="weekly-email">Email address</label>
      <div class="srow"><input type="email" id="weekly-email" name="email" autocomplete="email" required><button type="submit">Subscribe</button></div>
      <input type="hidden" name="embed" value="1">
    </form>
    <p class="smeta"><a href="https://buttondown.com/EconomyInContext/archive/">Past issues</a><span class="sep" aria-hidden="true">·</span><a href="how-this-site-is-paid-for.html#the-weekly-email">How addresses are kept</a></p>
  </section>
</div>
<footer class="about">
  <div class="wrap">
    <p>Articles on this site aim to lay out what the figures show, what is settled, what is argued about and by whom. Every number links to its source where one exists, and corrections are noted on the article. The charts are live from the almanac and update as agencies publish.</p>
    <p class="reuse">Free to reuse with credit: Economy in Context (economyincontext.org). The charts and writing here are licensed <a href="https://creativecommons.org/licenses/by/4.0/" rel="license noopener">CC BY 4.0</a>. Credit the data to its source, named on each chart.</p>
    <p>This site has no ads and no agenda beyond putting the numbers in context. It sets no cookies and keeps nothing that identifies you; it does count page views, and clicks on a few links on the home page. The optional weekly email is sent through Buttondown, which keeps the addresses for that and nothing else. It is paid for by the person who runs it, out of pocket; <a href="how-this-site-is-paid-for.html">here is how</a>, how visits are counted, and how to chip in if you want to. Questions and corrections: <a href="mailto:hello@economyincontext.org">hello@economyincontext.org</a>.</p>
    <p class="about-link"><a href="/tools/">Tools: put your own figures next to the national numbers →</a></p>
    <p class="about-link"><a href="about.html">About this site, how it works, and every correction →</a></p>
  </div>
</footer>
<script>document.querySelectorAll('[data-until]').forEach(function (e) { if (new Date().toISOString().slice(0, 10) >= e.getAttribute('data-until')) e.remove(); });</script>
<script data-goatcounter="https://economyincontext.goatcounter.com/count" async src="/assets/count.js"></script>
</body>
</html>
"""


def render_article(a):
    desc = html.escape(a.get("dek", a["title"]), quote=True)
    page = HEAD.format(title=html.escape(a["title"]), desc=desc, canonical=f"{SITE}/articles/{a['slug']}.html", css_v=asset_stamp("assets/site.css"), menu=menu_for(a))
    page += '<main class="wrap article">\n<article>\n'
    page += f'<h1>{inline(a["title"])}</h1>\n'
    if a.get("dek"):
        page += f'<p class="dek">{inline(a["dek"])}</p>\n'
    dates = fmt_date(a["date"])
    if a.get("updated") and a["updated"] != a["date"]:
        dates += f' <span class="sep">·</span> updated {fmt_date(a["updated"])}'
    es = TRANSLATIONS.get(a["slug"])
    if es:                                         # Nov 9: a Spanish version exists
        dates += f' <span class="sep">·</span> <a href="../es/{es}.html" lang="es" hreflang="es">En español</a>'
        page = page.replace('<link rel="canonical"', hreflang_tags(a["slug"], es) + '<link rel="canonical"', 1)
    page += f'<p class="dateline">{dates}{fresh_label(a)}</p>\n'
    page += series_box(a["slug"])
    body = md_to_html(a["body"])
    if a.get("kind") != "page":                   # Nov 8: one line pointing to the digest box, after the opening section
        first = body.find("<h2")                  # (In one sentence / The short version / The question ...), since most
        second = body.find("<h2", first + 1) if first != -1 else -1   # phone readers never reach the box at the bottom.
        if second != -1:                          # Template only: no article's date, updated: line, feed or sitemap entry changes.
            body = body[:second] + DIGEST_NUDGE + body[second:]
    nxt = series_next(a["slug"])
    if nxt:
        for anchor in ('<h2 id="see-also">', '<h2 id="sources">'):
            if anchor in body:
                body = body.replace(anchor, nxt + anchor, 1)
                break
        else:
            body += "\n" + nxt
    page += body
    page += "\n</article>\n</main>\n"
    if 'class="table-scroll"' in page:            # a table may be wider than a phone: assets/tables.js marks the ones that are
        page += '<script src="../assets/tables.js' + asset_stamp("assets/tables.js") + '"></script>\n'
    page += FOOT
    return clean_chart_links(page, CHART_IDS) if clean_chart_links else page


# ---------------------------------------------------------------------------
# Tools (Nov 8): reader tools at /tools/, from articles/src files with `kind: tool` (`out: index` for the Tools page
# itself). Built like an article but with no dateline, digest line or series box, left out of the articles index, the
# feed and the series, and listed in the sitemap. A tool page sits one folder down like an article, so ../assets works;
# relative links meant for /articles/ (the footer's, and the body's) are pointed there. Links that must stay put are
# written root-relative (/tools/…, /chart/, /data/…). The repo's tools/ folder is these build scripts, never published.
# ---------------------------------------------------------------------------
_REL_HREF = re.compile(r'href="(?!(?:/|#|https?:|mailto:|\.\./))([^"]+)"')


def tool_name(a):
    return a.get("out") or a["slug"]


def render_tool(a):
    desc = html.escape(a.get("dek", a["title"]), quote=True)
    name = tool_name(a)
    canonical = f"{SITE}/tools/" if name == "index" else f"{SITE}/tools/{name}.html"
    page = HEAD.format(title=html.escape(a["title"]), desc=desc, canonical=canonical, css_v=asset_stamp("assets/site.css"), menu=menu_for(a))
    page += '<main class="wrap article tool-page">\n<article>\n'
    page += f'<h1>{inline(a["title"])}</h1>\n'
    if a.get("dek"):
        page += f'<p class="dek">{inline(a["dek"])}</p>\n'
    page += md_to_html(a["body"])
    page += "\n</article>\n</main>\n"
    if 'class="table-scroll"' in page:
        page += '<script src="../assets/tables.js' + asset_stamp("assets/tables.js") + '"></script>\n'
    page += FOOT
    page = _REL_HREF.sub(lambda m: f'href="../articles/{m.group(1)}"', page)
    return clean_chart_links(page, CHART_IDS) if clean_chart_links else page


# ---------------------------------------------------------------------------
# Spanish pages (Nov 9 pilot): articles/src/es/*.md with `kind: es`, built to /es/<slug>.html (`out: index` for /es/).
# `translation_of: <English slug>` pairs a page with its English original: each links to the other under its dateline
# and in hreflang tags. `reviewed: yes` once a bilingual person has read it (the page says which). The chrome is Spanish:
# the menu (Spanish home, English), the date, the footer. Illustrations come from <name>-es.svg
# (tools/make_money_traps_illustrations.py, ES). Not in the articles index, the feed or the series; in the sitemap.
# ---------------------------------------------------------------------------
TRANSLATIONS = {}          # English slug -> Spanish slug, filled by main() before any article is rendered
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre",
         "diciembre"]


def fecha(iso):
    y, m, d = (int(x) for x in iso.split("-"))
    return f"{d} de {MESES[m - 1]} de {y}"


def es_name(a):
    return a.get("out") or a["slug"]


def hreflang_tags(en_slug, es_slug):
    en = f"{SITE}/articles/{en_slug}.html"
    es = f"{SITE}/es/" if es_slug == "index" else f"{SITE}/es/{es_slug}.html"
    return (f'<link rel="alternate" hreflang="en" href="{en}">\n<link rel="alternate" hreflang="es" href="{es}">\n'
            f'<link rel="alternate" hreflang="x-default" href="{en}">\n')


FOOT_ES = """
<footer class="about" lang="es">
  <div class="wrap">
    <p>Economy in Context explica las cifras de la economía de Estados Unidos en palabras sencillas: qué muestran, qué está claro y qué se discute, y quién lo discute. Cada número lleva a su fuente.</p>
    <p class="reuse">Puede reutilizar estas páginas citando la fuente: Economy in Context (economyincontext.org). El texto y los dibujos tienen licencia <a href="https://creativecommons.org/licenses/by/4.0/deed.es" rel="license noopener">CC BY 4.0</a>.</p>
    <p>El sitio no tiene anuncios, no usa cookies y no guarda nada que lo identifique; sí cuenta las visitas. Preguntas y correcciones, en español o en inglés: <a href="mailto:hello@economyincontext.org">hello@economyincontext.org</a>.</p>
    <p class="about-link"><a href="/es/">Todas las páginas en español →</a></p>
    <p class="about-link"><a href="/" lang="en">Economy in Context, in English →</a></p>
  </div>
</footer>
<script>document.querySelectorAll('[data-until]').forEach(function (e) { if (new Date().toISOString().slice(0, 10) >= e.getAttribute('data-until')) e.remove(); });</script>
<script data-goatcounter="https://economyincontext.goatcounter.com/count" async src="/assets/count.js"></script>
</body>
</html>
"""


def render_es(a):
    desc = html.escape(a.get("dek", a["title"]), quote=True)
    name = es_name(a)
    canonical = f"{SITE}/es/" if name == "index" else f"{SITE}/es/{name}.html"
    en = a.get("translation_of", "")
    menu = ('<nav class="site-menu" aria-label="Sitio"><a href="/es/"' + (' aria-current="page"' if name == "index" else ' aria-current="true"')
            + '>En español</a><a href="/" lang="en" hreflang="en">English</a></nav>')
    page = HEAD.format(title=html.escape(a["title"]), desc=desc, canonical=canonical, css_v=asset_stamp("assets/site.css"), menu=menu)
    page = page.replace('<html lang="en">', '<html lang="es">', 1).replace('<meta property="og:type"', '<meta property="og:locale" content="es_US">\n<meta property="og:type"', 1)
    if en:
        page = page.replace('<link rel="canonical"', hreflang_tags(en, name) + '<link rel="canonical"', 1)
    page += '<main class="wrap article">\n<article>\n'
    page += f'<h1>{inline(a["title"])}</h1>\n'
    if a.get("dek"):
        page += f'<p class="dek">{inline(a["dek"])}</p>\n'
    if name != "index":
        other = f' <span class="sep">·</span> <a href="../articles/{en}.html" lang="en" hreflang="en">Read it in English</a>' if en else ""
        page += f'<p class="dateline">{fecha(a["date"])}{other}</p>\n'
    page += md_to_html(a["body"])
    if name != "index" and en:
        note = ("Esta página es una traducción de la versión en inglés, revisada por una persona bilingüe."
                if str(a.get("reviewed", "")).lower() == "yes" else
                "Esta página es una traducción de la versión en inglés. Todavía no la ha revisado una persona bilingüe.")
        page += f'<p class="es-note">{note} ¿Ve un error? Escríbanos a <a href="mailto:hello@economyincontext.org">hello@economyincontext.org</a>.</p>\n'
    page += "\n</article>\n</main>\n"
    if 'class="table-scroll"' in page:
        page += '<script src="../assets/tables.js' + asset_stamp("assets/tables.js") + '"></script>\n'
    page += FOOT_ES
    return page


# The figures "Has It Kept Up With Prices?" reads (assets/keptup.js), as one small file: each series a start month and one
# value per month (null for a month with no reading, such as October 2025 for most BLS series). The not seasonally
# adjusted series are the ones BLS's own CPI calculator uses (fetch_fred.py *_nsa companions, Nov 8); if one is missing the
# seasonally adjusted series stands in, labeled as such, and with neither the file isn't written (the tool says so).
TOOL_SERIES = {
    "cpi": [("cpi_nsa", "CPIAUCNS", "Consumer Price Index for All Urban Consumers, all items, U.S. city average, not seasonally adjusted"),
            ("cpi_index", "CPIAUCSL", "Consumer Price Index for All Urban Consumers, all items, U.S. city average, seasonally adjusted")],
    "pay": [("pay_nsa", "CEU0500000008", "Average hourly earnings, production and nonsupervisory workers, not seasonally adjusted"),
            ("pay_level", "AHETPI", "Average hourly earnings, production and nonsupervisory workers, seasonally adjusted")],
    "rent": [("rent_nsa", "CUUR0000SEHA", "Consumer Price Index, rent of primary residence, not seasonally adjusted"),
             ("rent_level", "CUSR0000SEHA", "Consumer Price Index, rent of primary residence, seasonally adjusted")],
}


def write_tool_prices(out_root):
    path = os.path.join("data", "companions.json")
    try:
        raw = json.load(open(path, encoding="utf-8"))
    except Exception as e:                                      # noqa: BLE001
        print(f"tools: WARNING data/tool-prices.json not written ({e})")
        return
    comp = raw.get("companions", raw)
    by_id = comp if isinstance(comp, dict) else {c.get("id"): c for c in comp}
    out = {"generated": raw.get("generated")}
    for key, choices in TOOL_SERIES.items():
        for cid, series, label in choices:
            obs = (by_id.get(cid) or {}).get("observations") or []
            if len(obs) < 24:
                continue
            vals = {o[0][:7]: o[1] for o in obs}
            y, m = map(int, obs[0][0][:7].split("-"))
            y1, m1 = map(int, obs[-1][0][:7].split("-"))
            v = []
            while (y, m) <= (y1, m1):
                v.append(vals.get(f"{y:04d}-{m:02d}"))
                m += 1
                if m == 13:
                    y, m = y + 1, 1
            out[key] = {"series": series, "label": label, "start": obs[0][0][:7], "v": v,
                        "url": f"https://fred.stlouisfed.org/series/{series}"}
            break
    if "cpi" not in out:
        print("tools: WARNING no price series; data/tool-prices.json not written")
        return
    os.makedirs(os.path.join(out_root, "data"), exist_ok=True)
    with open(os.path.join(out_root, "data", "tool-prices.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    print("tools: data/tool-prices.json (" + ", ".join(f"{k} {out[k]['series']} from {out[k]['start']}" for k in TOOL_SERIES if k in out) + ")")


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


LATEST_SHOWN = 6     # newest pieces listed in full; older ones fold under "Earlier"


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
                       canonical=f"{SITE}/articles/", css_v=asset_stamp("assets/site.css"), menu=site_menu("articles", page=True))
    page += '<div class="wrap article article-head">\n<h1>Articles</h1>\n<p class="dek">Longer reads on what the figures show, what is settled, and what is argued about.</p>\n</div>\n'
    # the section bar sits between the title and the lead items, as the almanac's does, and the rest is main
    page += "{SECNAV}"
    page += '<main class="wrap article" id="main">\n'
    feat, _ = featured_pick(articles)
    lead = (featured_html(feat) if feat else "") + chart_prompt_html(CHART_PROMPT, "../")
    if lead:                                                # the two lead cards side by side (stacked on phones)
        page += '<div class="lead">\n' + lead + '</div>\n'

    def updated_note(a):
        return (f'<span class="when">Updated {fmt_date(a["updated"])}</span>'
                if a.get("updated") and a["updated"] != a["date"] else "")

    def listing(items, dated):
        # Full entries: title, dek, and the date for timely pieces. Evergreen pages show a
        # date only once they have been updated, so a list of identical launch dates never reads as stale.
        out = '<ul class="article-list">\n'
        for a in items:
            out += (f'<li><a href="{a["slug"]}.html"><span class="t">{inline(a["title"])}</span>{fresh_label(a)}</a>'
                    + (f'<span class="d">{inline(a["dek"])}</span>' if a.get("dek") else "")
                    + (f'<span class="when">{fmt_date(a["date"])}</span>' if dated else updated_note(a)) + "</li>\n")
        return out + "</ul>\n"

    def compact(items):
        # One line each: the short name, then the hook. Page titles stay as they are for search.
        out = '<ul class="compact-list">\n'
        for a in items:
            label, hook = a.get("label") or a["title"], a.get("hook") or ("" if a.get("label") else a.get("dek", ""))
            out += (f'<li><a href="{a["slug"]}.html">{inline(label)}</a>{fresh_label(a)}'
                    + (f'<span class="h"><span class="sep" aria-hidden="true"> — </span>{inline(hook)}</span>' if hook else "")
                    + updated_note(a) + "</li>\n")
        return out + "</ul>\n"

    timely = [a for a in articles if a.get("kind") not in ("concept", "path", "page")]    # newest first (main() sorts)
    # Latest is everything new that isn't a reference page: timely pieces and the idea pages (Plain words with
    # no tile: line). A series shows once, as its first part. Indicator pages and paths stay in their sections.
    latest = [a for a in articles if a.get("kind") not in ("concept", "path", "page") or (a.get("kind") == "concept" and not tile_ids(a))]
    shown, merged = set(), []
    for a in latest:
        if a["slug"] in SERIES_OF:                  # one entry per series, dated by its newest part, linking to part 1
            sr = SERIES_OF[a["slug"]][0]
            if sr["slug"] in shown:
                continue
            shown.add(sr["slug"])
            a = {"slug": sr.get("landing") or sr["parts"][0]["slug"], "title": sr["title"], "date": sr["date"],
                 "dek": sr.get("dek") or f"A series in {len(sr['parts'])} parts."}
        merged.append(a)
    latest = merged
    latest.sort(key=lambda a: (a["date"], a["title"]), reverse=True)
    paths = sorted((a for a in articles if a.get("kind") == "path"), key=lambda a: (sort_order(a, 9), a["title"]))
    concepts = [a for a in articles if a.get("kind") == "concept"]
    numbers = [a for a in concepts if tile_ids(a)]
    ideas = sorted((a for a in concepts if not tile_ids(a)), key=lambda a: (sort_order(a), a["title"]))

    jump = [("#latest", "Latest", latest), ("#household-paths", "Your situation", paths),
            ("#the-numbers", "The numbers", numbers), ("#the-ideas", "The ideas", ideas)]
    secnav = ('<nav class="secnav" aria-label="On this page"><div class="wrap"><span class="secnav-label" aria-hidden="true">On this page</span><a class="to-top" href="#top" aria-label="Back to the top of the page">↑ Top</a>'
              '<ul class="sections-nav" id="nav">' + "".join(f'<li><a href="{h}">{t}</a></li>' for h, t, items in jump if items)
              + '</ul></div></nav>\n')
    page = page.replace("{SECNAV}", secnav, 1)
    page += '<p class="feed-link">New and updated articles by feed reader: <a href="feed.xml">the Atom feed</a>.</p>\n'

    if latest:
        page += '<h2 id="latest">Latest</h2>\n' + listing(latest[:LATEST_SHOWN], dated=True)
        if len(latest) > LATEST_SHOWN:
            page += (f'<details class="earlier"><summary><span class="more">Show {len(latest) - LATEST_SHOWN} earlier pieces ↓</span>'
                     f'<span class="less">Hide the earlier pieces ↑</span></summary>\n'
                     + listing(latest[LATEST_SHOWN:], dated=True) + "</details>\n")
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
        by_slug = {a["slug"]: a for a in articles}
        run, done = [], set()
        for a in ideas:                          # a series sits, in its own order, where its first part would fall
            if a["slug"] in done:
                continue
            if a["slug"] in SERIES_OF:
                s, _ = SERIES_OF[a["slug"]]
                if run:
                    page += compact(run); run = []
                parts = [by_slug[p["slug"]] for p in s["parts"]]
                done.update(p["slug"] for p in s["parts"])
                title = (f'<a href="{s["landing"]}.html">{inline(s["title"])}</a>' if s.get("landing") else inline(s["title"]))
                page += (f'<section class="num-group series-group" id="series-{s["slug"]}"><h4><span class="series-label">Series</span> '
                         f'{title}</h4>' + compact(parts) + "</section>\n")
            else:
                run.append(a)
        if run:
            page += compact(run)
    page += '</main>\n<script src="../assets/secnav.js' + asset_stamp("assets/secnav.js") + '"></script>\n' + FOOT
    return page


CORRECTION = re.compile(r"^(?:[-*]\s+)?((?:January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}):\s*(.+)$", re.S)


def collect_corrections(articles):
    """Every dated line under an article's ## Corrections heading, newest first: [(iso date, article, text)].
    Each entry is a paragraph or a list item that opens "Month D, YYYY:"; anything else in the section is skipped."""
    from datetime import datetime
    out = []
    for a in articles:
        m = re.search(r"^## Corrections[ \t]*\n(.*?)(?=^## |\Z)", a["body"], re.S | re.M)
        if not m:
            continue
        for block in re.split(r"\n\s*\n|\n(?=[-*]\s)", m.group(1).strip()):
            e = CORRECTION.match(" ".join(x.strip() for x in block.strip().split("\n")))
            if e:
                out.append((datetime.strptime(e.group(1), "%B %d, %Y").date().isoformat(), a, e.group(2).strip()))
    out.sort(key=lambda x: (x[0], x[1]["title"]), reverse=True)
    return out


def corrections_html(entries):
    """One line of HTML (raw HTML passes through md_to_html only line by line)."""
    if not entries:
        return '<p class="corrections-none">No corrections so far.</p>'
    items = "".join(f'<li><span class="when">{fmt_date(d)}</span> <a href="{a["slug"]}.html">{inline(a["title"])}</a>'
                    f'<span class="d">{inline(t)}</span></li>' for d, a, t in entries)
    return f'<ul class="article-list corrections-log">{items}</ul>'


def write_explainers(out_root, articles):
    """data/explainers.json: indicator id -> its Plain words page, from each page's tile: line.
    The almanac and the chart pages read it to link every number to its explainer."""
    import json
    ex = {}
    for a in articles:
        if a.get("kind") not in ("concept", "path"):       # a path with a tile: line (You Rent) explains that tile
            continue
        for tid in tile_ids(a):
            ex[tid] = {"url": f"articles/{a['slug']}.html", "title": a["title"], "hook": a.get("hook", "")}
    # explains: (Nov 9) links a tile to an article without a tile: line, so the article keeps its place on the index
    # (an idea page stays under The ideas, a timely piece under Latest). A tile: line elsewhere wins. explains_hook:
    # is the link text when the article's own hook doesn't fit the tile, or it has none.
    for a in articles:
        if a.get("kind") == "page":
            continue
        for tid in [x.strip() for x in a.get("explains", "").split(",") if x.strip()]:
            ex.setdefault(tid, {"url": f"articles/{a['slug']}.html", "title": a["title"],
                                "hook": a.get("explains_hook") or a.get("hook", "")})
    feat, nxt = featured_pick(articles)
    if feat and feat.get("kind") == "series":
        url = f"articles/{feat.get('landing') or feat['parts'][0]['slug']}.html"
        shown = feat["parts"][:FEATURED_PARTS] if feat.get("landing") and len(feat["parts"]) > SERIES_FOLD else feat["parts"]
        featured = {"url": url, "title": feat["title"], "dek": feat.get("dek", ""), "series": feat["slug"],
                    "parts": [{"url": f"articles/{p['slug']}.html", "label": p["label"], "title": p["title"]} for p in shown]}
        if len(shown) < len(feat["parts"]):        # the home card ends "All N parts →" (index.html reads `more`)
            featured["more"] = {"url": url, "label": f"All {len(feat['parts'])} parts"}
    else:
        featured = {"url": f"articles/{feat['slug']}.html", "title": feat["title"], "dek": feat.get("dek", "")} if feat else None
    if featured:
        svg = featured_picture(feat)
        if svg:
            featured["svg"] = svg
        if feat.get("teaser"):                    # the home page's Featured strip (Nov 9)
            featured["teaser"] = feat["teaser"].strip().rstrip(".")
    os.makedirs(os.path.join(out_root, "data"), exist_ok=True)
    with open(os.path.join(out_root, "data", "explainers.json"), "w", encoding="utf-8") as f:
        json.dump({"note": "Written by tools/build_articles.py from the tile: line of each Plain words page, "
                           "and the featured: line of the article or series (articles/series.json) featured now.",
                   "explainers": ex, "featured": featured, "chart_prompt": CHART_PROMPT}, f, ensure_ascii=False, separators=(",", ":"))
    print(f"built data/explainers.json ({len(ex)} indicators)")
    print("featured: " + (("series " if feat.get("kind") == "series" else "") + f"{feat['slug']} (since {feat['featured']})" if feat else "none")
          + (f"; next {nxt['slug']} on {nxt['featured']}" if nxt else ""))


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


CHART_IDS = []
CHART_PROMPT = None
clean_chart_links = None


def load_chart_pages():
    """tools/chart_pages.py, or None (then no chart pages and article links stay on chart.html)."""
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import chart_pages
        return chart_pages
    except Exception as e:                                  # noqa: BLE001
        print(f"chart pages: not available ({e})")
        return None


def main():
    global CHART_IDS, CHART_PROMPT, clean_chart_links
    out_root = sys.argv[1] if len(sys.argv) > 1 else "public"
    out_dir = os.path.join(out_root, "articles")
    os.makedirs(out_dir, exist_ok=True)
    cp = load_chart_pages()
    if cp:                                                  # before the articles, which link to these pages
        CHART_IDS = cp.write_chart_pages(out_root)
        clean_chart_links = cp.clean_chart_links if CHART_IDS else None
        try:                                                # the almanac's readings as plain HTML, for crawlers and no-script readers
            cp.write_home_static(out_root)
        except Exception as e:                              # noqa: BLE001
            print(f"home: WARNING static figures not written ({e})")
    CHART_PROMPT = chart_prompt_pick()                      # after the chart pages, so its chart is checked against them
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
    tools = [a for a in articles if a.get("kind") == "tool"]            # Nov 8: built to /tools/, listed nowhere else
    articles = [a for a in articles if a.get("kind") != "tool"]
    spanish = []                                            # Nov 9: articles/src/es/*.md, built to /es/
    es_dir = os.path.join(SRC_DIR, "es")
    if os.path.isdir(es_dir):
        en_slugs = {x["slug"] for x in articles}
        for name in sorted(os.listdir(es_dir)):
            if name.endswith(".md"):
                a = parse(os.path.join(es_dir, name))
                if a["draft"] or a.get("kind") != "es":
                    continue
                t = a.get("translation_of", "")
                if t and t not in en_slugs:
                    print(f"es: {name}: translation_of {t!r} is not an article; not paired")
                    a["translation_of"] = ""
                elif t and es_name(a) != "index":
                    TRANSLATIONS[t] = es_name(a)
                spanish.append(a)
    articles.sort(key=lambda a: a["date"], reverse=True)
    load_series(articles)
    fixes = collect_corrections(articles)                   # the About page's log: <!--corrections--> on a line of its own
    for a in articles:
        if "<!--corrections-->" in a["body"]:
            a["body"] = a["body"].replace("<!--corrections-->", corrections_html(fixes))
    print(f"corrections: {len(fixes)} across {len({a['slug'] for _, a, _ in fixes})} articles")
    for a in articles:
        with open(os.path.join(out_dir, a["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(render_article(a))
        print(f"built articles/{a['slug']}.html")
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_index(articles))
    print(f"built articles/index.html ({len(articles)} articles)")
    if tools:
        tools_dir = os.path.join(out_root, "tools")
        os.makedirs(tools_dir, exist_ok=True)
        for a in tools:
            with open(os.path.join(tools_dir, tool_name(a) + ".html"), "w", encoding="utf-8") as f:
                f.write(render_tool(a))
            print(f"built tools/{tool_name(a)}.html")
    if spanish:
        es_out = os.path.join(out_root, "es")
        os.makedirs(es_out, exist_ok=True)
        for a in spanish:
            with open(os.path.join(es_out, es_name(a) + ".html"), "w", encoding="utf-8") as f:
                f.write(render_es(a))
            print(f"built es/{es_name(a)}.html")
    write_tool_prices(out_root)
    write_explainers(out_root, articles)
    write_feed(out_dir, articles)
    write_sitemap(out_root, articles, tools, spanish)
    if report is not None:
        print(figures.summarize(report))
        try:                                                # outside the published folder; read by the weekly check
            with open(os.environ.get("FIGURES_REPORT", "build-report.json"), "w", encoding="utf-8") as f:
                json.dump(report, f, indent=1)
        except OSError as e:
            print(f"figures: could not write the report ({e})")


FEED_KINDS = {"concept": "Plain words", "path": "Household paths"}


def write_feed(out_dir, articles):
    """articles/feed.xml: an Atom feed of the listed articles, newest first by date or update. Dates come from
    the front matter only (date, updated), so a live figure changing never makes an entry look new; a
    correction or update that sets updated: does."""
    from xml.sax.saxutils import escape
    listed = [a for a in articles if a.get("kind") != "page"]
    stamp = lambda d: f"{d}T00:00:00Z"
    when = lambda a: max(a["date"], a.get("updated") or a["date"])
    listed.sort(key=lambda a: (when(a), a["date"]), reverse=True)
    x = lambda s: escape(s, {'"': "&quot;"})
    out = ['<?xml version="1.0" encoding="utf-8"?>', '<feed xmlns="http://www.w3.org/2005/Atom">',
           "  <title>Economy in Context: articles</title>",
           "  <subtitle>What the figures on the U.S. economy show, what is settled, and what is argued about.</subtitle>",
           f'  <link rel="self" type="application/atom+xml" href="{SITE}/articles/feed.xml"/>',
           f'  <link rel="alternate" type="text/html" href="{SITE}/articles/"/>',
           f"  <id>{SITE}/articles/</id>",
           f"  <updated>{stamp(when(listed[0])) if listed else stamp(date.today().isoformat())}</updated>",
           "  <author><name>Economy in Context</name></author>",
           f"  <icon>{SITE}/assets/icon-192.png</icon>",
           "  <rights>CC BY 4.0: free to reuse with credit to Economy in Context (economyincontext.org)</rights>"]
    for a in listed:
        url = f"{SITE}/articles/{a['slug']}.html"
        out += ["  <entry>", f"    <title>{x(a['title'])}</title>", f'    <link rel="alternate" type="text/html" href="{url}"/>',
                f"    <id>{url}</id>", f"    <published>{stamp(a['date'])}</published>", f"    <updated>{stamp(when(a))}</updated>",
                f'    <category term="{x(FEED_KINDS.get(a.get("kind"), "Latest"))}"/>']
        if a.get("dek"):
            out.append(f"    <summary>{x(a['dek'])}</summary>")
        out.append("  </entry>")
    out.append("</feed>")
    with open(os.path.join(out_dir, "feed.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")
    print(f"built articles/feed.xml ({len(listed)} entries)")


def write_sitemap(out_root, articles, tools=(), spanish=()):
    """sitemap.xml and robots.txt at the site root: the almanac, the chart index, one page per chart
    (those chart_pages wrote this build), the articles index and every article."""
    import json
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [(f"{SITE}/", today, "daily", "1.0")]
    if CHART_IDS:                                               # the pages written this build
        urls.append((f"{SITE}/chart/", today, "weekly", "0.6"))
        urls += [(f"{SITE}/chart/{tid}/", today, "daily", "0.8") for tid in CHART_IDS]
    else:                                                       # no chart pages: the old addresses, from the data
        urls.append((f"{SITE}/chart.html", today, "weekly", "0.6"))
        series_path = os.path.join("data", "series.json")
        if os.path.exists(series_path):
            try:
                for t in json.load(open(series_path, encoding="utf-8")).get("tiles", []):
                    urls.append((f"{SITE}/chart.html?id={t['id']}", today, "daily", "0.8"))
            except Exception as e:                              # a bad data file must not break the build
                print(f"sitemap: skipped chart pages ({e})")
    for a in tools:                                             # Nov 8: the Tools page and each tool
        name = tool_name(a)
        urls.append((f"{SITE}/tools/" if name == "index" else f"{SITE}/tools/{name}.html", a.get("updated") or a["date"], "monthly", "0.7"))
    urls.append((f"{SITE}/articles/", today, "weekly", "0.8"))
    for a in articles:
        urls.append((f"{SITE}/articles/{a['slug']}.html", a.get("updated") or a["date"], "monthly", "0.7"))
    for a in spanish:                                           # Nov 9: the Spanish pages
        name = es_name(a)
        urls.append((f"{SITE}/es/" if name == "index" else f"{SITE}/es/{name}.html", a.get("updated") or a["date"], "monthly", "0.6"))
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
