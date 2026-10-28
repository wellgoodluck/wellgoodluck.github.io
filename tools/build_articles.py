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
    ---

then Markdown. Supported: # ## ### headings, paragraphs, **bold**, *italic*,
[links](url), - bullet lists, 1. numbered lists, > quotes, --- rules, and raw
HTML lines (left as they are). Plus one directive for a live chart from the
site's own detail page:

    {{chart id=cpi range=10y ov=fed_target,pce caption="Inflation and the Fed's target."}}

Anything after `## Sources` is rendered as a sources list.
"""

import html
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
            f'<a href="../chart.html?{html.escape(full, quote=True)}">Open the full chart with overlays →</a></figcaption></figure>')


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
            flush_para(); close_list(); out.append(line); continue
        m = re.match(r"^(#{1,3})\s+(.*)$", line)
        if m:
            flush_para(); close_list()
            level = len(m.group(1)) + 1                            # the page's h1 is the title
            title = m.group(2).strip()
            if level == 2 and title.lower() == "sources":
                in_sources = True
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
<link rel="canonical" href="{canonical}">
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
    <p>Questions and corrections: <a href="mailto:hello@economyincontext.org">hello@economyincontext.org</a>.</p>
  </div>
</footer>
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


def render_index(articles):
    page = HEAD.format(title="Articles", desc="Longer reads on the U.S. economy: what the figures show, what is settled and what is argued about.",
                       canonical=f"{SITE}/articles/")
    page = page.replace('<a href="./">Articles</a>', "Articles")
    page += '<main class="wrap article">\n<h1>Articles</h1>\n<p class="dek">Longer reads on what the figures show, what is settled, and what is argued about.</p>\n'
    def listing(items):
        out = '<ul class="article-list">\n'
        for a in items:
            out += (f'<li><a href="{a["slug"]}.html"><span class="t">{inline(a["title"])}</span></a>'
                    + (f'<span class="d">{inline(a["dek"])}</span>' if a.get("dek") else "")
                    + f'<span class="when">{fmt_date(a["date"])}</span></li>\n')
        return out + "</ul>\n"
    timely = [a for a in articles if a.get("kind") != "concept"]
    concepts = [a for a in articles if a.get("kind") == "concept"]
    if timely:
        page += listing(timely)
    if concepts:
        page += '<h2 id="plain-words">Plain words</h2>\n<p class="dek">What each number is, how it reaches your household, and where the usual analogies break. Evergreen; updated when the facts change.</p>\n'
        page += listing(sorted(concepts, key=lambda a: a["title"]))
    page += "</main>\n" + FOOT
    return page


def main():
    out_root = sys.argv[1] if len(sys.argv) > 1 else "public"
    out_dir = os.path.join(out_root, "articles")
    os.makedirs(out_dir, exist_ok=True)
    articles = []
    if os.path.isdir(SRC_DIR):
        for name in sorted(os.listdir(SRC_DIR)):
            if name.endswith(".md"):
                a = parse(os.path.join(SRC_DIR, name))
                if a["draft"]:
                    print(f"skip draft {name}")
                    continue
                articles.append(a)
    articles.sort(key=lambda a: a["date"], reverse=True)
    for a in articles:
        with open(os.path.join(out_dir, a["slug"] + ".html"), "w", encoding="utf-8") as f:
            f.write(render_article(a))
        print(f"built articles/{a['slug']}.html")
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(render_index(articles))
    print(f"built articles/index.html ({len(articles)} articles)")


if __name__ == "__main__":
    main()
