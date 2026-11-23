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
    release: 2026-12-01          (optional, Nov 14: hold the page until that date (Pacific), then publish it at the
                                  first build on or after it (the refresh runs weekdays about 6:15 am and 1:15 pm PT).
                                  Until then it is built nowhere: not on the index, Latest, feed, sitemap, series
                                  boxes or Featured, and any link to it on another page shows as plain text. Its
                                  figures and due dates are still checked into the build report. Once released, its
                                  date: becomes the release date if that is later, so the dateline, Latest and the
                                  New chip count from the day it went live. A date that isn't YYYY-MM-DD holds the
                                  page until it is fixed. RELEASE_TODAY=YYYY-MM-DD in the environment tests a build
                                  as of another day. Works the same for tools and articles/src/es pages.
                                  Wording on other pages that should appear with it (a landing-page entry, a teaching
                                  entry, a cross-link sentence) goes between {{after 2026-12-01}} and {{/after}},
                                  either on lines of their own around whole lines, or inline within one line; it is
                                  left out of the build until that date.)
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

and one for the "Try it with your own numbers" box that hands a reader off to a tool (Nov 19), on its own line where
the article's worked example ends; the title comes from the tool page, k= opens the tool's named example, and
example= replaces "It opens with this article's example." when the tool opens with only part of it, and example=none
drops it when the tool opens with numbers of its own (text= last):

    {{tool payment-plan-cost k=bnpl example="It opens with the sneakers from this example." text="Shows whether …"}}

kind=bars: one bar per row, one color, the value printed at each bar's tip. kind=stack: one
whole split into its parts, up to six, each part's value printed on it, a legend of names.
kind=pairs: two values per row, two colors, with a legend. fmt writes each value ({v} is the
number as given; {v,} prints it with thousands separators, fmt="${v,}" giving $21,840). The figure's accessible name lists every value, so nothing is color-only.

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
import math
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
    """{{figure kind=bars|stack|pairs title=… rows="a=1;b=2" [series="x;y"] [fmt="{v}" or "{v,}"] [caption=…] [source=…]}}
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
        if "{v,}" in fmt:                                   # Nov 11: {v,} prints the value with thousands separators (21,840)
            return fmt.replace("{v,}", f"{v:,.0f}")
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
TOOL_TITLES = {}     # tool name -> title, filled in main() before any article is rendered (Nov 19, the tool box)


def tool_directive(line):
    """{{tool <name> [k=<example>] text="…"}} -> the "Try it with your own numbers" box (Nov 19): the tool's title as a
    link (to its #k= example when given), the text line, and a fixed line under it. On its own line, where the article
    hands off to the tool (the Money Traps pieces: the end of A worked example). Fail-soft: an unknown tool prints a
    WARNING and leaves an HTML comment."""
    m = re.match(r"^\{\{\s*tool\s+(.*?)\s*\}\}$", line.strip())
    if not m:
        return None
    attrs, inner = {}, m.group(1)
    tm = re.search(r'\btext="(.*)"$', inner)               # the text runs to the last quote, as an illustration's caption
    if tm:
        attrs["text"], inner = tm.group(1), inner[:tm.start()]
    toks = shlex.split(inner)
    name = toks[0] if toks else ""
    for tok in toks[1:]:
        if "=" in tok:
            k, v = tok.split("=", 1)
            attrs[k] = v
    if name not in TOOL_TITLES:
        print(f"tool box: WARNING no tool named {name!r}; box left out")
        return f"<!-- tool box {html.escape(name)} skipped -->"
    href = f"../tools/{name}.html" + (f"#k={attrs['k']}" if re.fullmatch(r"[a-z0-9-]+", attrs.get("k", "")) else "")
    text = f'<p class="fdek">{inline(attrs["text"])}</p>' if attrs.get("text") else ""
    ex = attrs.get("example") or TOOL_BOX_EXAMPLE                # example=none: the tool doesn't open with the article's numbers
    how = TOOL_BOX_PRIVATE if ex == "none" else inline(ex) + " " + TOOL_BOX_PRIVATE
    return (f'<aside class="tool-try" aria-label="Try it with your own numbers"><span class="flabel">Try it with your own numbers</span>'
            f'<a class="ftitle" href="{href}">{inline(TOOL_TITLES[name])}</a> →{text}'
            f'<p class="fhow">{how}</p></aside>')


# Tom, Nov 19: the box's label and fixed line. The second sentence is the Tools page's dek.
TOOL_BOX_EXAMPLE = "It opens with this article's example."
TOOL_BOX_PRIVATE = "Nothing you type is saved or sent anywhere."


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
        d = chart_directive(line) or figure_directive(line) or illustration_directive(line) or tool_directive(line)
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


HELD = {}   # slug -> release date of pages held back this build (Nov 14)


def release_today():
    """Today in Pacific time, the day a release: date is compared with (RELEASE_TODAY overrides it, for tests)."""
    t = os.environ.get("RELEASE_TODAY", "")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", t):
        return t
    from datetime import datetime
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
    except Exception:                                       # noqa: BLE001  no tz data: UTC minus 8 hours, never early
        from datetime import timezone, timedelta
        return (datetime.now(timezone.utc) - timedelta(hours=8)).strftime("%Y-%m-%d")


def held(a, name, today, key=None):
    """True if the page's release: date hasn't arrived (it is then recorded in HELD and left out of the build).
    On or after the date, a later release date replaces date: so the page counts as new from the day it went live."""
    rel = a.get("release", "")
    if not rel:
        return False
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", rel):
        print(f"hold {name}: WARNING release {rel!r} is not YYYY-MM-DD; held until it is fixed")
        HELD[key or a["slug"]] = rel
        return True
    if rel > today:
        print(f"hold {name} until {rel}")
        HELD[key or a["slug"]] = rel
        return True
    if rel > a["date"]:
        a["date"] = rel
    return False


_AFTER_BLOCK = re.compile(r"^\{\{after (\d{4}-\d{2}-\d{2})\}\}[ \t]*\n(.*?)^\{\{/after\}\}[ \t]*(?:\n|\Z)", re.M | re.S)
_AFTER_INLINE = re.compile(r"\{\{after (\d{4}-\d{2}-\d{2})\}\}(.*?)\{\{/after\}\}")


def apply_after(body, name, today):
    """{{after YYYY-MM-DD}} … {{/after}}: the wording inside appears from that date (Pacific) on, and not before."""
    if "{{after" not in body:
        return body
    keep = lambda m: m.group(2) if m.group(1) <= today else ""
    body = _AFTER_INLINE.sub(keep, _AFTER_BLOCK.sub(keep, body))
    if "{{after" in body or "{{/after}}" in body:
        print(f"after: WARNING {name} has an {{{{after}}}} marker that isn't closed, isn't YYYY-MM-DD, or spans lines "
              f"without standing on lines of its own; left as typed")
    return body


def unlink_held(out_root):
    """Links on built pages to a held page become their plain text, so nothing points at a page that isn't up yet."""
    slugs = [k for k in HELD if "/" not in k and k != "index"]   # es/ pages: English pages link to them only once paired
    if not slugs:
        return
    pat = re.compile(r'<a\b[^>]*?\bhref="(?:[^"]*/)?(?:' + "|".join(re.escape(s) for s in slugs) +
                     r')\.html(?:[?#][^"]*)?"[^>]*>(.*?)</a>', re.S)
    n_links = n_files = 0
    for root, _, files in os.walk(out_root):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(root, fn)
            with open(path, encoding="utf-8") as f:
                text = f.read()
            new, n = pat.subn(r"\1", text)
            if n:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(new)
                n_links += n
                n_files += 1
                print(f"held links: {n} in {os.path.relpath(path, out_root)}")
    print(f"held: {len(HELD)} page(s) ({', '.join(f'{k} {v}' for k, v in sorted(HELD.items(), key=lambda x: x[1]))}); "
          f"{n_links} link(s) to them shown as plain text in {n_files} file(s)")


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
SERIES_RELATED_MAX = 2   # "Also read" pages a series may show in its box (Nov 22)
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
        related = []                                       # Nov 22: "Also read" pages from outside the series, shown in each part's box
        own = {p["slug"] for p in parts}
        for r in d.get("related", []) or []:
            r = r if isinstance(r, dict) else {}
            a = by_slug.get(r.get("slug", ""))
            if not a or a.get("kind") == "page" or a["slug"] in own:
                print(f"series: {sid}: related page {r.get('slug')!r} is not a listed article outside the series; left out")
                continue
            related.append({"slug": a["slug"], "label": r.get("label") or a.get("label") or a["title"],
                            "title": a["title"], "tag": r.get("tag", "")})
        if len(related) > SERIES_RELATED_MAX:
            print(f"series: {sid}: {len(related)} related pages; showing the first {SERIES_RELATED_MAX}")
            related = related[:SERIES_RELATED_MAX]
        s = {"kind": "series", "slug": sid, "title": d["title"], "dek": d.get("dek", ""), "featured": d.get("featured", ""),
             "picture": d.get("picture", ""), "teaser": d.get("teaser", ""),
             "date": max(by_slug[p["slug"]]["date"] for p in parts), "parts": parts, "landing": landing,
             "related": related}
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
    rel = ""
    if s.get("related"):                            # Nov 22: unnumbered, on its own line, so "part k of n" stays true
        pills = " ".join(
            f'<a class="rel" href="{r["slug"]}.html" title="{html.escape(r["title"], quote=True)}">'
            + (f'<span class="tag">{html.escape(r["tag"])}</span> ' if r.get("tag") else "")
            + f'<span class="rl">{inline(r["label"].replace("-", chr(0x2011)))}</span></a>'   # no break at a hyphen ("seven-year")
            for r in s["related"])
        rel = f'<p class="series-related"><span class="series-label">Also read</span> {pills}</p>'
    return (f'<nav class="series" aria-label="Series: {html.escape(s["title"], quote=True)}">'
            f'<p class="series-name"><span class="series-label">Series, part {i + 1} of {len(s["parts"])}</span> '
            f'<a href="{s["landing"] + ".html" if s.get("landing") else "./#series-" + s["slug"]}">{inline(s["title"])}</a></p>'
            f'{parts}{rel}</nav>\n')


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
# Tools (Nov 19): each tool's title on its own page and its entry on the Tools page get the same chip, from the tool
# page's date: / updated:. The Tools page's first week (Nov 8-14) isn't labeled, so its first tools don't all read as new.
TOOL_LABEL_START = "2026-11-15"


def fresh_label(a, start=LABEL_START, attrs=""):
    from datetime import timedelta
    today = date.today()
    def until(s):
        if not s or s < start:
            return None
        y, mo, d = (int(x) for x in s.split("-"))
        return date(y, mo, d) + timedelta(days=LABEL_DAYS)
    new, rev = until(a.get("date")), until(a.get("updated") if a.get("updated") != a.get("date") else None)
    if new and today < new:
        return f' <span class="fresh" data-until="{new.isoformat()}"{attrs}>New</span>'
    if rev and today < rev:
        y, mo, d = (int(x) for x in a["updated"].split("-"))
        return f' <span class="fresh rev" data-until="{rev.isoformat()}"{attrs}>Revised {date(y, mo, d).strftime("%b %-d")}</span>'
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
    """Nov 14: Search comes twice, so the reading and Tab order always match what shows: .site-search beside the
    lockup (phones, and the home page at 761-939px) and .m-search as the menu's last item (desktop). site.css shows
    one at a time. here="search" marks both on the search page."""
    cur = ' aria-current="page"' if page else ' aria-current="true"'
    s_cur = ' aria-current="page"' if here == "search" else ""
    return (f'<a class="site-search" href="/search/"{s_cur}>Search</a><nav class="site-menu" aria-label="Site">'
            + "".join(f'<a href="{u}"{' class="m-wide"' if k == "tools" else ""}{cur if k == here else ""}>{t}</a>'
                      for k, u, t in MENU) + f'<a class="m-search" href="/search/"{s_cur}>Search</a></nav>')


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


# Nov 22 (batch o): a compact signup form high on every article and tool page, replacing the one-line link that jumped
# to the box at the bottom (most readers never got that far: 7 subscribers in four weeks). The bottom box stays. Presses
# of either Subscribe button are counted (signup-top, signup-bottom); the footer and How This Site Is Paid For say so.
DIGEST_FORM = ('<form class="dsub" action="https://buttondown.com/api/emails/embed-subscribe/EconomyInContext" method="post" '
               'aria-label="Weekly digest" data-pagefind-ignore>'
               '<p class="dsub-t"><b>Get the weekly digest.</b> One short email on Monday mornings: the week\'s new articles and charts, '
               'and what comes out next. No ads.</p>'
               '<div class="dsub-row"><label class="sr-only" for="dsub-email">Email address</label>'
               '<input type="email" id="dsub-email" name="email" autocomplete="email" placeholder="Email address" required>'
               '<button type="submit" data-goatcounter-click="signup-top" data-goatcounter-title="Weekly digest: Subscribe (top of page)">Subscribe</button></div>'
               '<input type="hidden" name="embed" value="1"></form>\n')

FOOT = """
<div class="wrap signup-wrap">
  <section class="signup" id="weekly" aria-labelledby="weekly-h">
    <h2 id="weekly-h">The weekly digest</h2>
    <p class="stext">One email on Monday mornings: the week's new articles and charts, the numbers that moved most, and what comes out in the week ahead. No ads, and no tracking of opens or clicks.</p>
    <form action="https://buttondown.com/api/emails/embed-subscribe/EconomyInContext" method="post">
      <label for="weekly-email">Email address</label>
      <div class="srow"><input type="email" id="weekly-email" name="email" autocomplete="email" required><button type="submit" data-goatcounter-click="signup-bottom" data-goatcounter-title="Weekly digest: Subscribe (bottom of page)">Subscribe</button></div>
      <input type="hidden" name="embed" value="1">
    </form>
    <p class="smeta"><a href="https://buttondown.com/EconomyInContext/archive/">Past issues</a><span class="sep" aria-hidden="true">·</span><a href="how-this-site-is-paid-for.html#the-weekly-email">How addresses are kept</a></p>
  </section>
</div>
<footer class="about">
  <div class="wrap">
    <p>Articles on this site aim to lay out what the figures show, what is settled, what is argued about and by whom. Every number links to its source where one exists, and corrections are noted on the article. The charts are live from the almanac and update as agencies publish.</p>
    <p class="reuse">Free to reuse with credit: Economy in Context (economyincontext.org). The charts and writing here are licensed <a href="https://creativecommons.org/licenses/by/4.0/" rel="license noopener">CC BY 4.0</a>. Credit the data to its source, named on each chart.</p>
    <p>This site has no ads and no agenda beyond putting the numbers in context. It explains how things work. It is not tax, legal or financial advice. It sets no cookies and keeps nothing that identifies you; it does count page views, clicks on a few links on the home page, presses of the Subscribe buttons (never the address typed), and uses of the share, copy and print buttons on articles. The optional weekly email is sent through Buttondown, which keeps the addresses for that and nothing else. It is paid for by the person who runs it, out of pocket; <a href="how-this-site-is-paid-for.html">here is how</a>, how visits are counted, and how to chip in if you want to. Questions and corrections: <a href="mailto:hello@economyincontext.org">hello@economyincontext.org</a>.</p>
    <p class="about-link"><a href="/search/">Search every article, chart and tool →</a></p>
    <p class="about-link"><a href="/tools/">Tools: put your own figures next to the national numbers →</a></p>
    <p class="about-link"><a href="for-teachers.html">For teachers: free lessons built on these numbers →</a></p>
    <p class="about-link"><a href="about.html">About this site, how it works, and every correction →</a></p>
  </div>
</footer>
<script>document.querySelectorAll('[data-until]').forEach(function (e) { if (new Date().toISOString().slice(0, 10) >= e.getAttribute('data-until')) e.remove(); });</script>
<script data-goatcounter="https://economyincontext.goatcounter.com/count" async src="/assets/count.js"></script>
</body>
</html>
"""



# ---------------------------------------------------------------------------
# Sharing (Nov 11): a text button at the end of every article's dateline, a "Share this article" row at the end, a
# copy-link control after each h2 on computers, and a preview card per article. assets/share.js does the work and
# chooses the buttons: computers (hover + fine pointer) get Copy link (top) and Copy link · Email the link · Print or
# save as PDF (end); phones and tablets get Share (the device's own menu) and Copy link, or Copy link · Email the link
# where the browser has no share menu. Without JavaScript the two rows stay hidden and the heading links are plain
# anchors ("Link to this section"). Every control counts its click under one name per article, share/<slug>, so
# GoatCounter shows which articles readers pass on (the How This Site Is Paid For page and every footer say so).
# One visually hidden live region (#share-live) announces each result; the visible messages are aria-hidden so
# nothing is read twice. Mock rounds and reviews: the project doc claude/sharing-mock-nov11.md.
# ---------------------------------------------------------------------------
LINK_SVG = ('<svg viewBox="0 0 20 20" aria-hidden="true" focusable="false"><path d="M8.6 11.4a3.2 3.2 0 0 0 4.5 0l3-3a3.2 3.2 0 0 0-4.5-4.5l-1.1 1.1"/>'
            '<path d="M11.4 8.6a3.2 3.2 0 0 0-4.5 0l-3 3a3.2 3.2 0 0 0 4.5 4.5l1.1-1.1"/></svg>')
NO_SECTION_LINK = {"see-also"}


def plain(s):
    """Plain text of a title written in the site's Markdown (no tags, entities decoded)."""
    return html.unescape(re.sub(r"<[^>]+>", "", inline(s)))


def share_attrs(a):
    return (f' data-goatcounter-click="share/{a["slug"]}"'
            f' data-goatcounter-title="{html.escape(plain(a["title"]), quote=True)}"')


def share_top(a):
    return (f'<span class="share-top" id="share-top" hidden> <span class="sep" aria-hidden="true">·</span> '
            f'<button type="button" class="tbtn"{share_attrs(a)}>Copy link</button><span class="done" aria-hidden="true"></span></span>')


def share_end(a):
    title, dek = plain(a["title"]), plain(a.get("dek", ""))
    url = f"{SITE}/articles/{a['slug']}.html"
    from urllib.parse import quote
    mail = "mailto:?subject=" + quote(title) + "&body=" + quote((dek + "\n\n" if dek else "") + url)
    at = share_attrs(a)
    return ('<section class="share-end" id="share-end" aria-labelledby="share-h" hidden>\n'
            '<p class="share-label" id="share-h">Share this article</p>\n<div class="share-btns">'
            f'<button type="button" class="act share-btn"{at}>Share</button>'
            f'<button type="button" class="act copy-btn"{at}>Copy link</button>'
            f'<a class="act email-btn" href="{html.escape(mail, quote=True)}"{at}>Email the link</a>'
            f'<button type="button" class="act print-btn"{at}>Print or save as PDF</button>'
            '</div>\n<p class="share-status" id="share-status" aria-hidden="true"></p>\n</section>\n')


def section_links(body, a):
    """A copy-link control after each h2's text (computers only, by CSS), the heading named by its own text."""
    at = share_attrs(a)
    def rep(m):
        hid, inner = m.group(1), m.group(2)
        if hid in NO_SECTION_LINK:
            return m.group(0)
        label = html.escape("Link to this section: " + html.unescape(re.sub(r"<[^>]+>", "", inner)), quote=True)
        k = inner.rfind(" ")
        if "<" in inner or k == -1:                 # markup in the heading: no last-word wrap
            text = inner
        else:
            text = f'{inner[:k + 1]}<span class="h-end">{inner[k + 1:]}</span>'
        return (f'<h2 id="{hid}" aria-labelledby="{hid}-t"><span id="{hid}-t">{text}</span>'
                f'<a class="h-link" href="#{hid}" aria-label="{label}"{at}>{LINK_SVG}</a></h2>')
    return re.sub(r'<h2 id="([^"]+)">(.*?)</h2>', rep, body)


# Preview cards: assets/cards/<slug>.<hash>.png, 1200 x 630, made offline by tools/make_cards.py (headless Chrome, not run
# by the workflows) and listed in assets/cards/cards.json with the label and title each was drawn with. An article whose
# card is missing or was drawn from an older title or label keeps the site card, and the build log names it.
CARDS = None
CARD_V = "1"                                       # bump to redraw every card (tools/make_cards.py hashes it in)


def card_label(a):
    """The small line above the title on a card: the series and part, else the kind of page in readers' words, else
    (timely pieces) the date. No "of N": a series grows."""
    if a["slug"] in SERIES_OF:
        s, i = SERIES_OF[a["slug"]]
        return f'{plain(s["title"])} · Part {i + 1}'
    if a["slug"] in LANDINGS:
        return "A series"
    kind = a.get("kind")
    if kind == "concept":
        return "In plain words"
    if kind == "path":
        return "A household guide"
    if kind == "page":
        return ""
    return fmt_date(a["date"])


def card_for(a):
    """The card's URL for this article, or None (the site card)."""
    global CARDS
    if CARDS is None:
        try:
            with open(os.path.join("assets", "cards", "cards.json"), encoding="utf-8") as f:
                CARDS = json.load(f).get("cards", {})
        except (OSError, ValueError) as e:
            print(f"cards: none ({e})")
            CARDS = {}
    c = CARDS.get(a["slug"])
    if not c or c.get("title") != plain(a["title"]) or c.get("label") != card_label(a) or c.get("v") != CARD_V \
            or not os.path.exists(os.path.join("assets", "cards", c.get("file", ""))):
        CARD_MISSING.append(a["slug"])
        return None
    return f"{SITE}/assets/cards/{c['file']}"


CARD_MISSING = []


# ---------------------------------------------------------------------------
# Site search (Nov 14). Pagefind indexes the built site in both workflows (publish.yml, refresh.yml) and writes
# /pagefind/; nothing it makes is committed. What it reads is marked here: an article's or tool's <article> is the body
# (data-pagefind-body), the parts that would repeat on every page are left out (data-pagefind-ignore), a short label
# goes into the kind meta, and the front matter's `also:` line (words readers type that the page doesn't, comma
# separated) goes into a hidden also meta that is searched, weighted in assets/search.js, and never shown. Handouts,
# index pages and Spanish pages carry no body and so are not indexed. Chart pages are marked in tools/chart_pages.py.
# ---------------------------------------------------------------------------
SEARCH_LOW = {"about", "how-this-site-is-paid-for", "for-teachers", "teaching-with-money-traps"}   # weight 0.5
_SEARCH_IGNORE = re.compile(r'<(p class="dateline"|nav class="series"|p class="digest-nudge"|nav class="series-next"|'
                            r'section class="share-end"|ul class="sources"|h2 id="sources"|nav class="more-tools"|figure(?=[\s>]))')


def search_label(a):
    """The small line over a search result, in readers' words; empty for a plain article."""
    if a["slug"] in SERIES_OF:
        s, i = SERIES_OF[a["slug"]]
        return f'{plain(s["title"]).split(":")[0].strip()} · Part {i + 1}'
    if a["slug"] in LANDINGS:
        return "Series"
    if a["slug"].startswith("lesson-") or a["slug"] in ("for-teachers", "teaching-with-money-traps"):
        return "For teachers"
    if a["slug"] in ("about", "how-this-site-is-paid-for"):
        return "About this site"
    kind = a.get("kind")
    if kind == "tool":
        return "Tool"
    if kind == "path":
        return "Your situation"
    if kind == "concept" and tile_ids(a):
        return "In plain words"
    return ""


def search_also_meta(words):
    """A hidden meta span for the synonyms (semicolons: a comma would start a new meta field)."""
    terms = [w.strip() for w in str(words).split(",") if w.strip()]
    if not terms:
        return ""
    return '<span hidden data-pagefind-meta="also:' + html.escape("; ".join(terms), quote=True) + '"></span>'


def search_open(a):
    """The <article> tag with its search marks, or a plain one for a page search leaves out."""
    if a["slug"].endswith("-handout"):
        return "<article>"
    lab = search_label(a)
    low = a["slug"] in SEARCH_LOW or a["slug"].startswith("lesson-")
    return ("<article data-pagefind-body" + (' data-pagefind-weight="0.5"' if low else "")
            + (f' data-pagefind-meta="kind:{html.escape(lab, quote=True)}"' if lab else "") + ">"
            + search_also_meta(a.get("also", "")))


def search_ignore(page):
    return _SEARCH_IGNORE.sub(lambda m: m.group(0) + " data-pagefind-ignore", page)


def search_form(fid, cls):
    """The search box: a plain GET form, so it works as a link even before the script loads."""
    return (f'<form class="sform {cls}" role="search" action="/search/" method="get" data-search-form>'
            f'<label for="{fid}">Search articles, charts and tools</label>'
            f'<div class="srow"><input type="search" id="{fid}" name="q" autocomplete="off" spellcheck="false" '
            f'enterkeyhint="search"><button type="submit">Search</button></div></form>\n')


def use_title_tag(page, a):
    """Nov 19 (SEO audit): front matter `title_tag:` replaces the title in the browser tab and in search results only.
    The h1, og:title (link previews), the feed, the JSON-LD headline and site search keep `title`."""
    tt = a.get("title_tag")
    if not tt:
        return page
    old = f"<title>{html.escape(a['title'])} — Economy in Context</title>"
    if page.count(old) != 1:
        print(f"WARNING {a['slug']}: title_tag not applied")
        return page
    return page.replace(old, f"<title>{html.escape(tt)} — Economy in Context</title>", 1)


def article_ld(a, card):
    """Nov 19 (SEO audit): schema.org Article markup for articles, Plain words and household paths (not pages, landing
    pages, lessons or tools), so search engines read the dates and the preview image the same way every time. No
    author or publisher: the site has no byline and no organization behind it. isPartOf names the WebSite that
    index.html describes."""
    if a.get("kind") not in (None, "", "concept", "path") or a["slug"] in LANDINGS:
        return ""
    url = f"{SITE}/articles/{a['slug']}.html"
    pub = a["date"]
    mod = max(pub, a.get("updated") or pub)
    ld = {"@context": "https://schema.org", "@type": "Article", "headline": plain(a["title"]),
          "description": plain(a.get("dek", a["title"])), "datePublished": pub, "dateModified": mod,
          "url": url, "mainEntityOfPage": url, "image": card or f"{SITE}/assets/og-card.png", "inLanguage": "en",
          "isAccessibleForFree": True, "license": "https://creativecommons.org/licenses/by/4.0/",
          "isPartOf": {"@type": "WebSite", "@id": f"{SITE}/#website", "name": "Economy in Context", "url": f"{SITE}/"}}
    return ('<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False).replace("</", "<\\/")
            + "</script>\n")


def render_article(a):
    desc = html.escape(a.get("dek", a["title"]), quote=True)
    page = HEAD.format(title=html.escape(a["title"]), desc=desc, canonical=f"{SITE}/articles/{a['slug']}.html", css_v=asset_stamp("assets/site.css"), menu=menu_for(a))
    page = use_title_tag(page, a)
    card = card_for(a)                             # Nov 11: the article's own preview card, when one is current
    ld = article_ld(a, card)
    if ld:
        page = page.replace("</head>", ld + "</head>", 1)
    if card:
        lab = card_label(a)
        alt = html.escape((lab + ": " if lab else "") + plain(a["title"]), quote=True)
        page = page.replace('content="https://economyincontext.org/assets/og-card.png"', f'content="{card}"', 1)
        page = re.sub(r'<meta property="og:image:alt" content="[^"]*">', lambda m: f'<meta property="og:image:alt" content="{alt}">', page, count=1)
    if not a.get("kind"):                          # timely pieces: the date in the preview's title, where it stays readable
        page = page.replace(f'<meta property="og:title" content="{html.escape(a["title"])}">',
                            f'<meta property="og:title" content="{html.escape(a["title"])} ({fmt_date(a["date"])})">', 1)
    page += '<main class="wrap article">\n' + search_open(a) + '\n'
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
    page += f'<p class="dateline">{dates}{fresh_label(a)}{share_top(a)}</p>\n'
    page += series_box(a["slug"])
    body = md_to_html(a["body"])
    if a.get("kind") != "page":                   # Nov 8: the digest, after the opening section (a compact form since Nov 22)
        first = body.find("<h2")                  # (In one sentence / The short version / The question ...), since most
        second = body.find("<h2", first + 1) if first != -1 else -1   # phone readers never reach the box at the bottom.
        if second != -1:                          # Template only: no article's date, updated: line, feed or sitemap entry changes.
            body = body[:second] + DIGEST_FORM + body[second:]
    nxt = series_next(a["slug"]) + share_end(a)  # Nov 11: the share row follows Next in this series
    for anchor in ('<h2 id="see-also">', '<h2 id="sources">'):
        if anchor in body:
            body = body.replace(anchor, nxt + anchor, 1)
            break
    else:
        body += "\n" + nxt
    body = section_links(body, a)
    body += '<p class="sr-only" id="share-live" role="status" aria-live="polite"></p>\n'
    page += body
    page += "\n</article>\n</main>\n"
    if 'class="table-scroll"' in page:            # a table may be wider than a phone: assets/tables.js marks the ones that are
        page += '<script src="../assets/tables.js' + asset_stamp("assets/tables.js") + '"></script>\n'
    page += '<script src="../assets/share.js' + asset_stamp("assets/share.js") + '"></script>\n'
    page = search_ignore(page)
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


def rate_tool_attrs():
    """Nov 11: the payment tool's starting rates, written onto its mount at every build: the latest 30-year weekly
    average and the one 52 weeks earlier (the mortgage tile, data/series.json), and the same pair for the 15-year
    average (companion mortgage_15yr, data/companions.json) when it is there and dated the same week. Fail-soft:
    whatever can't be read is left off, and assets/moneytools.js copes (no 15-year figure, no loan-length switch)."""
    from datetime import date as _d

    def pair(obs):
        obs = [o for o in obs if o[1] is not None]
        last = obs[-1]
        d0 = _d.fromisoformat(last[0][:10])
        ago = min(obs, key=lambda o: abs((d0 - _d.fromisoformat(o[0][:10])).days - 364))
        year = ago[1] if abs((d0 - _d.fromisoformat(ago[0][:10])).days - 364) <= 4 else None
        return d0, last[1], year

    out, note = "", []
    try:
        with open(os.path.join("data", "series.json"), encoding="utf-8") as f:
            tiles = json.load(f).get("tiles", [])
        d30, r30, y30 = pair(next(t for t in tiles if t.get("id") == "mortgage")["observations"])
    except Exception as e:                                      # noqa: BLE001
        print(f"tools: WARNING payment tool has no starting rate ({e})")
        return ""
    out += f' data-r30="{r30:g}" data-week="{d30:%B} {d30.day}, {d30.year}"' + (f' data-y30="{y30:g}"' if y30 else "")
    note.append(f"30-year {r30:g} ({d30.isoformat()}), a year ago {y30 if y30 else 'n/a'}")
    try:
        with open(os.path.join("data", "companions.json"), encoding="utf-8") as f:
            raw = json.load(f)
        comp = raw.get("companions", raw)
        c15 = comp.get("mortgage_15yr") if isinstance(comp, dict) else next((c for c in comp if c.get("id") == "mortgage_15yr"), None)
        if not c15:
            raise RuntimeError("mortgage_15yr isn't in data/companions.json yet")
        d15, r15, y15 = pair(c15["observations"])
        if abs((d15 - d30).days) > 1:
            raise RuntimeError(f"15-year figure is for {d15.isoformat()}, not {d30.isoformat()}")
        out += f' data-r15="{r15:g}"' + (f' data-y15="{y15:g}"' if y15 else "")
        note.append(f"15-year {r15:g}, a year ago {y15 if y15 else 'n/a'}")
    except Exception as e:                                      # noqa: BLE001
        note.append(f"no 15-year figure ({e}); the loan-length switch stays hidden")
    print("tools: payment tool rates: " + "; ".join(note))
    return out


_TOOL_FIG = []


def _tool_figures():
    """tools/figures.py and the committed data, for the starting figures written onto tool mounts (Nov 19). Loaded once."""
    if not _TOOL_FIG:
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import figures as fg
            _TOOL_FIG.extend([fg, fg.Data("data")])
        except Exception as e:                                  # noqa: BLE001
            print(f"tools: WARNING tool starting figures unavailable ({e})")
            _TOOL_FIG.extend([None, None])
    return _TOOL_FIG[0], _TOOL_FIG[1]


def save_tool_attrs():
    """Nov 19: the savings tool's buying-power line (the 12-month CPI change, as the page text prints it) and its
    Treasury bill button (the latest weekly 3-month yield). Fail-soft: without one, assets/moneytools.js leaves out the
    line or hides the button."""
    fg, D = _tool_figures()
    if not D:
        return ""
    out, note = "", []
    try:
        ym, p = fg.cpi12_nsa(D)
        out += f' data-cpi12="{fg.half_up(p, 1)}" data-cpim="{fg.month_year(ym + "-01")}"'
        note.append(f"prices {fg.half_up(p, 1)}% to {ym}")
    except Exception as e:                                      # noqa: BLE001
        note.append(f"no 12-month CPI change ({e}); the buying-power line is left out")
    try:
        d, v = fg._latest(D, "tbill_3mo")
        out += f' data-tb="{fg.half_up(v, 2)}"'
        note.append(f"Treasury bill {fg.half_up(v, 2)}% ({d})")
    except Exception as e:                                      # noqa: BLE001
        note.append(f"no Treasury bill rate ({e}); its button stays hidden")
    print("tools: savings tool: " + "; ".join(note))
    return out


def myrate_tool_attrs():
    """Nov 19: each line's 12-month change for What's My Own Inflation Rate? (figures.myrate_lines), as JSON. Fail-soft:
    a line left out asks for the reader's own year-ago amount; with no data at all the tool says the figures didn't load."""
    fg, D = _tool_figures()
    if not D:
        return ""
    try:
        ym, ch = fg.myrate_lines(D)
    except Exception as e:                                      # noqa: BLE001
        print(f"tools: WARNING inflation tool has no national figures ({e})")
        return ""
    missing = [k for k in fg.MYRATE_LINES if k not in ch]
    core = [k for k in ("all", "rent", "elec", "groc", "eat", "gas", "carins", "med") if k not in ch]
    if core:                                                    # the shown lines must all have a figure, or the tool says so
        print(f"tools: WARNING inflation tool left without figures (no {', '.join(core)} to {ym}); it says the figures didn't load")
        return ""
    print(f"tools: inflation tool: {len(ch)} lines to {ym}" + (f"; no figure for {', '.join(missing)}" if missing else ""))
    js = json.dumps({k: round(v, 4) for k, v in ch.items()}, separators=(",", ":"))
    return f' data-m="{fg.month_year(ym + "-01")}" data-p="{html.escape(js, quote=True)}"'


def car_tool_attrs():
    """Nov 19: the car tool's starting gas and electricity prices and loan rate (figures.car_tool_inputs). Fail-soft:
    assets/carcost.js falls back to AAA's own prices and the typed August 2026 loan rate."""
    fg, D = _tool_figures()
    if not D:
        return ""
    try:
        x = fg.car_tool_inputs(D)
    except Exception as e:                                      # noqa: BLE001
        print(f"tools: WARNING car tool has no starting prices ({e})")
        return ""
    out = (f' data-gas="{x["gas"]}" data-gasw="{x["gas_week"]}" data-el="{x["elec"]}" data-elm="{x["elec_month"]}"'
           + (f' data-apr="{x["apr"]}" data-aprm="{x["apr_month"]}"' if "apr" in x else ""))
    print(f"tools: car tool: gas ${x['gas']} ({x['gas_week']}), electricity {x['elec']}¢ ({x['elec_month']}), "
          + (f"loan {x['apr']}% ({x['apr_month']})" if "apr" in x else "no loan rate yet"))
    return out


def hour_tool_attrs():
    """Nov 19: the national hourly pay figure for What Do I Take Home per Hour? Fail-soft: the line is left out."""
    fg, D = _tool_figures()
    if not D:
        return ""
    try:
        x = fg.hour_tool_inputs(D)
    except Exception as e:                                      # noqa: BLE001
        print(f"tools: WARNING take-home tool has no national pay figure ({e})")
        return ""
    print(f"tools: take-home tool: pay ${x['pay']} ({x['pay_month']})")
    return f' data-pay="{x["pay"]}" data-paym="{x["pay_month"]}"'


TOOL_ATTRS = {"rate": rate_tool_attrs, "save": save_tool_attrs, "myrate": myrate_tool_attrs, "own": car_tool_attrs,
              "hour": hour_tool_attrs}


# Nov 22 (SEO follow-up): the state tool's first two lead sentences for every state, as plain HTML inside its mount, for
# crawlers that don't run scripts and readers without them. Python ports of sentences() and domClause() in
# assets/states.js: change both together. An inline script hides the list at once and states.js replaces the mount's
# contents when it draws, so readers with scripts see the tool as before. Site search skips it (data-pagefind-ignore).
STATES_JSON = "assets/states.json"


def _js_round1(x):                                  # Math.round(x * 10) / 10, then toFixed(1)
    return f"{math.floor(x * 10 + 0.5) / 10:.1f}"


def _sp_fmt(n):
    return ("−" if n < 0 else "") + f"{abs(n):,}"


def _sp_ord(n):
    return f"{n}" + ("th" if 11 <= n % 100 <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th"))


def _sp_the(name):
    return "the " + name if name == "District of Columbia" else name


def state_sentences(D, ab):
    """sentences() in assets/states.js, first two sentences (the third is about the chart)."""
    s = D["states"][ab]
    ys = D["comp_years"]
    i = len(ys) - 1
    y = ys[i]
    now, prev = s["est"][f"y{y}"], s["est"][f"y{y - 1}"]
    change = now - prev
    pct = abs(change) / prev * 100
    pct_txt = "less than 0.1%" if pct < 0.05 else _js_round1(pct) + "%"
    nm = _sp_the(s["name"])
    p1 = (nm[0].upper() + nm[1:] + " had " + _sp_fmt(now) + f" residents in July {y}: "
          + ("up " + _sp_fmt(change) if change >= 0 else "down " + _sp_fmt(-change)) + ", or " + pct_txt + ", over the year.")
    nat, intl, dom = s["natural"][i], s["intl"][i], s["dom"][i]
    if abs(dom) < 500:
        dc = "about as many people moved in from other states as moved out"
    else:
        r = 1 + sum(1 for t in D["states"].values() if (dom > 0 and t["dom"][i] > dom) or (dom < 0 and t["dom"][i] < dom))
        rank = "the largest" if r == 1 else "the " + _sp_ord(r) + "-largest"
        dc = (_sp_fmt(dom) + " more people moved in from other states than moved out — " + rank
              + " net gain from other states in the country") if dom > 0 else (
              _sp_fmt(-dom) + " more people moved out to other states than moved in — " + rank
              + " net loss to other states in the country")
    p2 = ("Where that came from: "
          + ("births outnumbered deaths by " + _sp_fmt(nat) if nat >= 0 else "deaths outnumbered births by " + _sp_fmt(-nat)) + "; "
          + (_sp_fmt(intl) + " more people arrived from other countries than left" if intl >= 0
             else _sp_fmt(-intl) + " more people left for other countries than arrived") + "; and " + dc + ".")
    return p1, p2


def state_static(body):
    """Insert the every-state list into the state tool's mount, after its no-script line. Fails soft."""
    noscript_end = '</p></div>'
    i = body.find('<div class="sp-mount"')
    j = body.find(noscript_end, i) if i >= 0 else -1
    if j < 0:
        print("tools: WARNING state tool: no mount to fill")
        return body
    try:
        with open(STATES_JSON, encoding="utf-8") as f:
            D = json.load(f)
        rows = "".join(f'<dt>{html.escape(D["states"][ab]["name"])}</dt><dd>{html.escape(" ".join(state_sentences(D, ab)))}</dd>'
                       for ab in sorted(D["states"], key=lambda k: D["states"][k]["name"]))
    except Exception as e:                                      # noqa: BLE001
        print(f"tools: WARNING state tool: no static list ({e})")
        return body
    block = ('<div class="sp-static" id="sp-static" data-pagefind-ignore><dl>' + rows + '</dl></div>'
             "<script>document.getElementById('sp-static').hidden = true;</script>")
    print(f"tools: state tool: static list of {len(D['states'])} states")
    return body[:j] + "</p>" + block + "</div>" + body[j + len(noscript_end):]


_TOOLS_LI = re.compile(r'(<li><a href="([^"#]+)(?:#[^"]*)?">)(.*?)(</a>)')
_TOOLS_GROUP = re.compile(r'^## (.+)$', re.M)
_TOOLS_ENTRY = re.compile(r'<li><a href="([^"]+)">(.*?)</a>')


def tools_groups(index):
    """The Tools page's groups, in order: [(heading, [(href, title), ...]), ...], read from its source."""
    if not index:
        return []
    parts = _TOOLS_GROUP.split(index["body"])
    return [(parts[i].strip(), _TOOLS_ENTRY.findall(parts[i + 1])) for i in range(1, len(parts) - 1, 2)]


def more_tools(tools, groups):
    """Nov 19: the More tools row on each tool page: up to three other tools, first those sharing a group with it on
    the Tools page (in the page's order), then any named in its `more_tools:` front matter (tool names, comma-separated),
    then All tools. Returns {tool name: html}."""
    titles = {h.split("#")[0]: (h, t) for _, items in groups for h, t in items}
    titles.update({f"/tools/{tool_name(x)}.html": (f"/tools/{tool_name(x)}.html", x["title"]) for x in tools if tool_name(x) != "index"})
    out = {}
    for x in tools:
        name = tool_name(x)
        if name == "index":
            continue
        me, picks = f"/tools/{name}.html", []
        for _, items in groups:
            if any(h == me for h, _ in items):
                picks += [h.split("#")[0] for h, _ in items]
        picks += [f"/tools/{n.strip()}.html" for n in x.get("more_tools", "").split(",") if n.strip()]
        seen, keep = {me, "/chart/"}, []
        for h in picks:
            if h in titles and h not in seen:
                seen.add(h); keep.append(titles[h])
        keep = keep[:3]
        if len(keep) < 2:
            print(f"tools: {name}: only {len(keep)} other tool(s) in More tools; add more_tools: to its front matter")
        links = "".join(f'<a href="{h}">{inline(t)}</a> · ' for h, t in keep)
        out[name] = (f'<nav class="more-tools" aria-label="More tools"><p><span class="series-label">More tools</span> '
                     f'{links}<a href="/tools/">All tools</a></p></nav>\n')
    return out


def render_tool(a, by_href=None, more=None, groups=None):
    desc = html.escape(a.get("dek", a["title"]), quote=True)
    name = tool_name(a)
    canonical = f"{SITE}/tools/" if name == "index" else f"{SITE}/tools/{name}.html"
    page = HEAD.format(title=html.escape(a["title"]), desc=desc, canonical=canonical, css_v=asset_stamp("assets/site.css"), menu=menu_for(a))
    page = use_title_tag(page, a)
    if name == "index" and groups:                              # Nov 19: the articles index's On this page bar, one link a group
        page += f'<div class="wrap article article-head">\n<h1>{inline(a["title"])}</h1>\n'
        if a.get("dek"):
            page += f'<p class="dek">{inline(a["dek"])}</p>\n'
        page += DIGEST_FORM                                      # Nov 22: the digest in the first screen
        page += ('</div>\n<nav class="secnav" aria-label="On this page"><div class="wrap"><span class="secnav-label" aria-hidden="true">On this page</span>'
                 '<a class="to-top" href="#top" aria-label="Back to the top of the page">↑ Top</a><ul class="sections-nav" id="nav">'
                 + "".join(f'<li><a href="#{re.sub(r"[^a-z0-9]+", "-", g.lower()).strip("-")}">{inline(g)}</a></li>' for g, _ in groups) + '</ul></div></nav>\n')
        page += '<main class="wrap article tool-page" id="main">\n<article>\n'
    else:
        page += '<main class="wrap article tool-page">\n' + ("<article>" if name == "index" else search_open(a)) + '\n'
        # Nov 19: a new tool's chip after its title, as on chart pages; kept out of the search index so results never say "New"
        chip = "" if name == "index" else fresh_label(a, TOOL_LABEL_START, " data-pagefind-ignore")
        page += f'<h1>{inline(a["title"])}{chip}</h1>\n'
        if a.get("dek"):
            page += f'<p class="dek">{inline(a["dek"])}</p>\n'
        page += DIGEST_FORM                                      # Nov 22: the digest above the tool (Tom's call)
    body = a["body"]
    if name == "index":                                         # Nov 19: the chip on each Tools page entry, inside its link;
        by_href = by_href or {}                                 # the title in span.t carries the underline, so it stops at the title
        body = _TOOLS_LI.sub(lambda m: m.group(1) + '<span class="t">' + m.group(3) + "</span>"
                             + (fresh_label(by_href[m.group(2)], TOOL_LABEL_START) if m.group(2) in by_href else "") + m.group(4), body)
    for key, attrs in TOOL_ATTRS.items():                       # Nov 11 (rate), Nov 19 (the rest): starting figures on the mount
        tag = f'data-tool="{key}"'
        if tag in body:
            body = body.replace(tag, tag + attrs(), 1)
    body = md_to_html(body)
    if '<div class="sp-mount"' in body:                         # Nov 22: the state tool's every-state list (state_static)
        body = state_static(body)
    if more and name in more:                                   # Nov 19: More tools, before Sources (where articles put Next in this series)
        anchor = '<h2 id="sources">'
        body = body.replace(anchor, more[name] + anchor, 1) if anchor in body else body + "\n" + more[name]
    page += body
    page += "\n</article>\n</main>\n"
    if 'class="table-scroll"' in page:
        page += '<script src="../assets/tables.js' + asset_stamp("assets/tables.js") + '"></script>\n'
    if 'class="secnav"' in page:
        page += '<script src="../assets/secnav.js' + asset_stamp("assets/secnav.js") + '"></script>\n'
    page = search_ignore(page)
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
    # Nov 11: role="group", not "img": an img role hides the eight links inside it from screen readers (axe
    # nested-interactive). The arrows and lag labels are drawing only, so they sit in an aria-hidden group;
    # the title still describes the loop, and each stop is a link read by its own name.
    out = [f'<svg viewBox="0 0 {W} {H}" role="group" aria-labelledby="map-title">',
           '<title id="map-title">How the indicators push on each other: Fed funds to the 10-year yield, '
           'to mortgage rates, to housing starts, to construction jobs, to jobs added, to wages, to inflation, '
           'and back to the Fed.</title>',
           '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
           '<path d="M0,0 L10,5 L0,10 z"/></marker></defs>']
    n = len(pos)
    out.append('<g aria-hidden="true">')
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
    out.append('</g>')
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
    page += '<div class="wrap article article-head">\n<h1>Articles</h1>\n<p class="dek">Longer reads on what the figures show, what is settled, and what is argued about.</p>\n'
    page += search_form("ix-q", "sform-ix") + '</div>\n'
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
    page += ('</main>\n<script src="../assets/secnav.js' + asset_stamp("assets/secnav.js") + '"></script>\n'
             '<script src="/assets/search.js' + asset_stamp("assets/search.js") + '" defer></script>\n' + FOOT)
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
    return ex                                      # Nov 19: main() hands it to the chart pages


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
    today = release_today()
    if os.path.isdir(SRC_DIR):
        for name in sorted(os.listdir(SRC_DIR)):
            if name.endswith(".md"):
                path = os.path.join(SRC_DIR, name)
                a = parse(path)
                if a["draft"]:
                    print(f"skip draft {name}")
                    continue
                a["body"] = apply_after(a["body"], name, today)
                if held(a, name, today):
                    if figures and data:                    # checked now, so a banked page's figures are right on its day
                        figures.render(a["body"], data, a["slug"], report, body_offset(path, a["body"]))
                    continue
                if figures and data:
                    a["body"] = figures.render(a["body"], data, a["slug"], report, body_offset(path, a["body"]))
                elif "{{v " in a["body"] or "{{fig " in a["body"] or "{{check " in a["body"] or "{{due " in a["body"]:
                    a["body"] = re.sub(r"\s*\{\{\s*(?:check|due)\s+.*?\}\}", "", a["body"])
                    a["body"] = re.sub(r"\{\{\s*(?:v|fig)\s+.*?\}\}", "", a["body"])
                articles.append(a)
    tools = [a for a in articles if a.get("kind") == "tool"]            # Nov 8: built to /tools/, listed nowhere else
    articles = [a for a in articles if a.get("kind") != "tool"]
    TOOL_TITLES.update({tool_name(x): x["title"] for x in tools if tool_name(x) != "index"})
    spanish = []                                            # Nov 9: articles/src/es/*.md, built to /es/
    es_dir = os.path.join(SRC_DIR, "es")
    if os.path.isdir(es_dir):
        en_slugs = {x["slug"] for x in articles}
        for name in sorted(os.listdir(es_dir)):
            if name.endswith(".md"):
                a = parse(os.path.join(es_dir, name))
                if a["draft"] or a.get("kind") != "es" or held(a, "es/" + name, today, "es/" + es_name(a)):
                    continue
                a["body"] = apply_after(a["body"], "es/" + name, today)
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
    n_cards = len(articles) - len(CARD_MISSING)
    print(f"cards: {n_cards} articles with their own card" + (f"; site card for {len(CARD_MISSING)} (no card, or drawn from an older title or label: "
          f"{', '.join(CARD_MISSING)}; run tools/make_cards.py)" if CARD_MISSING else ""))
    if tools:
        tools_dir = os.path.join(out_root, "tools")
        os.makedirs(tools_dir, exist_ok=True)
        by_href = {f"/articles/{x['slug']}.html": x for x in articles}
        by_href.update({f"/tools/{tool_name(x)}.html": x for x in tools if tool_name(x) != "index"})
        groups = tools_groups(next((x for x in tools if tool_name(x) == "index"), None))
        more = more_tools(tools, groups)
        for a in tools:
            with open(os.path.join(tools_dir, tool_name(a) + ".html"), "w", encoding="utf-8") as f:
                f.write(render_tool(a, by_href, more, groups))
            print(f"built tools/{tool_name(a)}.html")
    if spanish:
        es_out = os.path.join(out_root, "es")
        os.makedirs(es_out, exist_ok=True)
        for a in spanish:
            with open(os.path.join(es_out, es_name(a) + ".html"), "w", encoding="utf-8") as f:
                f.write(render_es(a))
            print(f"built es/{es_name(a)}.html")
    os.makedirs(os.path.join(out_root, "search"), exist_ok=True)       # Nov 14: site search
    with open(os.path.join(out_root, "search", "index.html"), "w", encoding="utf-8") as f:
        f.write(render_search_page())
    with open(os.path.join(out_root, "404.html"), "w", encoding="utf-8") as f:
        f.write(render_not_found())
    print("built search/index.html and 404.html")
    write_tool_prices(out_root)
    explainers = write_explainers(out_root, articles)
    if cp and CHART_IDS:                                    # Nov 19: each chart page's "In plain words" link, as plain HTML
        try:
            cp.write_chart_explainers(out_root, explainers, CHART_IDS)
        except Exception as e:                              # noqa: BLE001
            print(f"chart pages: WARNING explainer links not written ({e})")
    write_feed(out_dir, articles)
    write_sitemap(out_root, articles, tools, spanish)
    unlink_held(out_root)
    if report is not None:
        print(figures.summarize(report))
        try:                                                # outside the published folder; read by the weekly check
            with open(os.environ.get("FIGURES_REPORT", "build-report.json"), "w", encoding="utf-8") as f:
                json.dump(report, f, indent=1)
        except OSError as e:
            print(f"figures: could not write the report ({e})")


# ---------------------------------------------------------------------------
# The search page (/search/) and the not-found page (/404.html, which GitHub Pages serves for any missing address).
# Both are drawn by assets/search.js against the Pagefind index. The query lives after # (#q=…&n=…), never after ?,
# because the visit counter (assets/count.js) sends the ?part of every address it counts; a line in the search page's
# head moves an incoming ?q= behind # before the counter loads. The not-found page searches the words in the bad
# address, isn't counted (an address can hold anything) and isn't indexed. Links on both are root-relative, since the
# not-found page is served at whatever depth the missing address had.
# ---------------------------------------------------------------------------
_HASH_Q = ("<script>(function(){var m=location.search.match(/[?&]q=([^&]*)/);"
           "if(m){history.replaceState(null,'',location.pathname+'#q='+m[1]);}})();</script>\n")


def _rooted(page):
    page = page.replace('href="../assets/', 'href="/assets/')
    return re.sub(r'href="(?!(?:/|#|https?:|mailto:))([^"]+)"', r'href="/articles/\1"', page)


def render_search_page():
    page = HEAD.format(title="Search", desc="Search every article, chart and tool on Economy in Context.",
                       canonical=f"{SITE}/search/", css_v=asset_stamp("assets/site.css"), menu=site_menu("search"))
    page = page.replace('<meta property="og:type" content="article">', '<meta property="og:type" content="website">', 1)
    page = page.replace("</head>", _HASH_Q + "</head>", 1)
    page = page.replace("</head>", '<meta name="robots" content="noindex">\n</head>', 1)   # Nov 19: a shell, not a page to list
    page += ('<main class="wrap article search-page" id="main">\n<h1>Search</h1>\n' + search_form("q", "sform-page")
             + '<p class="s-privacy">The search runs in your browser: it downloads pieces of the site\'s index, the way it '
               'loads any page, and looks there. What you type isn\'t sent to anyone or counted.</p>\n'
               '<div id="s-out" data-search-out>\n<noscript><p class="s-msg">Search needs JavaScript. The '
               '<a href="/articles/">articles index</a> lists every article, and <a href="/?view=all">all the numbers</a> '
               'are on one page.</p></noscript>\n</div>\n'
               '<p class="sr-only" id="s-live" role="status" aria-live="polite"></p>\n</main>\n'
               '<script src="/assets/search.js' + asset_stamp("assets/search.js") + '" defer></script>\n')
    return _rooted(page + FOOT)


def render_not_found():
    page = HEAD.format(title="Page not found", desc="That page isn't on Economy in Context.",
                       canonical=f"{SITE}/404.html", css_v=asset_stamp("assets/site.css"), menu=site_menu())
    page = page.replace('<meta property="og:type" content="article">', '<meta property="og:type" content="website">', 1)
    page = page.replace("</head>", '<meta name="robots" content="noindex">\n</head>', 1)
    page += ('<main class="wrap article search-page notfound" id="main">\n<h1>That page isn\'t here</h1>\n'
             '<p class="dek" id="nf-dek">The address may be mistyped, or the page may have moved.</p>\n'
             + search_form("q", "sform-page")
             + '<div id="s-out" data-search-out data-from-path></div>\n'
               '<p class="sr-only" id="s-live" role="status" aria-live="polite"></p>\n'
               '<p class="nf-links">Or start from <a href="/">the home page</a>, <a href="/articles/">the articles index</a> '
               'or <a href="/?view=all">all the numbers</a>.</p>\n</main>\n'
               '<script src="/assets/search.js' + asset_stamp("assets/search.js") + '" defer></script>\n')
    foot = re.sub(r'<script data-goatcounter[^>]*></script>\n', "", FOOT)
    return _rooted(page + foot)


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
