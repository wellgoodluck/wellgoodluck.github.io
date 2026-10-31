#!/usr/bin/env python3
"""
The two tables in Indexed to Inauguration (articles/src/indexed-to-inauguration.md), computed from
the committed data. Standard library only. Not run by the workflows: the article is timely, so its
tables stay as of their date until someone recomputes them on purpose (at the end of a term, say).

Usage, from the repo root:
    python3 tools/term_tables.py                  # the current term counted to the latest month
    python3 tools/term_tables.py --end 2029-01    # the current term closed at its last month
    python3 tools/term_tables.py --compare        # also list the cells that differ from the article

It prints each table as one line of HTML, ready to replace the matching <table> line in the article,
then (with --compare) every cell that differs from the article's current tables, which after a refresh
is mostly the agencies' revisions.

Method, as stated in the article:
  - A term runs from January of its first year to January of the year it ends (inauguration months).
  - "From inauguration": jobs added per month over the months after the start month through the end
    month (payrolls, change from the month before, in thousands); unemployment at the start and end
    months; CPI (cpi_index, CPIAUCSL) at an annual rate between the two months; real GDP growth at an
    annual rate, compounding the quarters after the start quarter through the end quarter.
  - "One year in": the same window shifted twelve months later, cut off at the latest month in the
    data for the current term (and GDP at its latest quarter).
Kept from the script that produced the tables on Oct 28, 2026, unchanged except for the options. Checked
Oct 31 against the article: all 80 cells match with the data as it stood then (GDP through Q2 2026);
with the Q3 advance in the data, the current term's two growth cells read 2.7% and 2.8% instead of
2.6% and 2.2%.
"""

import argparse
import json
import os
import re
import sys

TERMS = [  # (label, first January, January the term ends); the current term's end comes from --end or the data
    ("Reagan", "1981-01-01", "1989-01-01"),
    ("G.H.W. Bush", "1989-01-01", "1993-01-01"),
    ("Clinton", "1993-01-01", "2001-01-01"),
    ("G.W. Bush", "2001-01-01", "2009-01-01"),
    ("Obama", "2009-01-01", "2017-01-01"),
    ("Trump, first term", "2017-01-01", "2021-01-01"),
    ("Biden", "2021-01-01", "2025-01-01"),
    ("Trump, second term", "2025-01-01", None),
]
MONTH_ABBR = ["Jan.", "Feb.", "March", "April", "May", "June", "July", "Aug.", "Sept.", "Oct.", "Nov.", "Dec."]
ARTICLE = os.path.join("articles", "src", "indexed-to-inauguration.md")


def load(root="data"):
    s = json.load(open(os.path.join(root, "series.json"), encoding="utf-8"))
    t = {x["id"]: dict(map(tuple, x["observations"])) for x in s["tiles"]}
    c = {x["id"]: dict(map(tuple, x["observations"])) for x in json.load(open(os.path.join(root, "companions.json"), encoding="utf-8"))["companions"]}
    return t["payrolls"], t["unemployment"], t["gdp"], c["cpi_index"]


def addm(d, k):
    y, mm = int(d[:4]), int(d[5:7])
    mm += k
    y += (mm - 1) // 12
    mm = (mm - 1) % 12 + 1
    return f"{y:04d}-{mm:02d}-01"


def tables(end=None):
    pay, un, gdp, cpi_idx = load()
    months = sorted(pay)
    last = months[-1]
    if end and end > last:
        sys.exit(f"--end {end[:7]} is past the data, which ends at {last[:7]}; run it after that month's figures are in")

    def jobs(a, b):                       # sum of monthly changes for the months after a through b
        ms = [m for m in months if a < m <= b]
        return sum(pay[m] for m in ms), len(ms)

    def cpi_ann(a, b):
        n = (int(b[:4]) - int(a[:4])) * 12 + int(b[5:7]) - int(a[5:7])
        return ((cpi_idx[b] / cpi_idx[a]) ** (12 / n) - 1) * 100

    def gdp_ann(a, b):                    # quarters strictly after the quarter containing a, through b
        qs = sorted(q for q in gdp if a < q <= b)
        g = 1.0
        for q in qs:
            g *= (1 + gdp[q] / 100) ** 0.25
        return (g ** (4 / len(qs)) - 1) * 100

    rows1 = ['<table><thead><tr><th>President</th><th>Jobs added per month, from inauguration</th><th>Same, counted from one year in</th>'
             '<th>Unemployment, inauguration to end</th><th>Same, one year in to one year after</th></tr></thead><tbody>']
    rows2 = ['<table><thead><tr><th>President</th><th>Inflation per year, from inauguration</th><th>Same, one year in</th>'
             '<th>Real GDP growth per year, from inauguration</th><th>Same, one year in</th></tr></thead><tbody>']
    for name, a, b in TERMS:
        if b is None:                     # the current term: closed at --end, or counted to date
            b = end or last
            if not end:
                name += f" (to {MONTH_ABBR[int(b[5:7]) - 1]} {b[:4]})"
        j, n = jobs(a, b)
        a2, b2 = addm(a, 12), min(addm(b, 12), last)
        j2, n2 = jobs(a2, b2)
        k = lambda v: f"{round(v) * 1000:+,}"   # payrolls are in thousands: +168 -> +168,000
        rows1.append(f"<tr><td>{name}</td><td>{k(j / n)}</td><td>{k(j2 / n2)}</td>"
                     f"<td>{un[a]:.1f}% → {un[b]:.1f}%</td><td>{un[a2]:.1f}% → {un[b2]:.1f}%</td></tr>")
        g2 = gdp_ann(a2, min(b2, max(gdp)))
        rows2.append(f"<tr><td>{name}</td><td>{cpi_ann(a, b):.1f}%</td><td>{cpi_ann(a2, b2):.1f}%</td>"
                     f"<td>{gdp_ann(a, b):.1f}%</td><td>{g2:.1f}%</td></tr>")
    rows1.append("</tbody></table>")
    rows2.append("</tbody></table>")
    return "".join(rows1), "".join(rows2)


def cells(table_html):
    return [re.findall(r"<td>(.*?)</td>", tr) for tr in re.findall(r"<tr><td>.*?</tr>", table_html)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--end", help="close the current term at this month (YYYY-MM), e.g. 2029-01")
    ap.add_argument("--compare", action="store_true", help="list cells that differ from the article's tables")
    args = ap.parse_args()
    end = None
    if args.end:
        if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", args.end):
            sys.exit("--end takes YYYY-MM")
        end = args.end + "-01"
    t1, t2 = tables(end)
    print("TABLE 1 (jobs and unemployment)")
    print(t1)
    print("\nTABLE 2 (inflation and growth)")
    print(t2)
    if args.compare:
        old = [ln for ln in open(ARTICLE, encoding="utf-8").read().split("\n") if ln.startswith("<table")]
        if len(old) < 2:
            sys.exit(f"\n{ARTICLE}: expected two <table> lines, found {len(old)}")
        diffs = []
        for label, new_t, old_t in (("table 1", t1, old[0]), ("table 2", t2, old[1])):
            for rn, ro in zip(cells(new_t), cells(old_t)):
                for col, (cn, co) in enumerate(zip(rn, ro)):
                    if cn != co:
                        diffs.append(f"  {label}, {ro[0]}, column {col + 1}: {co} -> {cn}")
        print(f"\n{len(diffs)} cells differ from the article" + (":" if diffs else "."))
        print("\n".join(diffs))


if __name__ == "__main__":
    main()
