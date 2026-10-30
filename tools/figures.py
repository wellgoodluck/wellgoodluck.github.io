#!/usr/bin/env python3
"""
Live figures for article text. Standard library only. Used by tools/build_articles.py,
which runs after the data is in place in both workflows, so these update with every refresh.

Four inline directives, written anywhere in an article's body:

    {{v claims}}                    the latest value, formatted   -> 196,750
    {{v claims period}}             the period it describes       -> the week ending October 24, 2026
    {{v claims.baseline fmt=thousands}}  a field of the series    -> 245,000
    {{fig claims_low}}              a named figure or phrase from FIGS below
    {{check claims.percentile <= 15 "claims near record lows"}}
                                    invisible; evaluated on every build, listed when it fails
    {{due 2026-11-14 "CMS announces the 2027 Part B premium"}}
                                    invisible; listed once the date has passed

Series ids are the almanac's tile ids, companion ids (data/companions.json) and extras
(series.json "extras"). Fields: value (default), previous, year_ago, baseline, percentile,
lowest_since, highest_since, min, max, since. Add "period" to get the period of a value field
instead of the value. Formats (fmt=): int, num0, num1, num2, pct0, pct1, pct2, thousands,
millions1, millions2, usd0, usd2, usd10. Any directive can carry else="..." (the text to print
if the figure can't be computed; default is the empty string plus a build warning).

Rules that keep live text honest (see claude/automation-plan.md in the project):
  - A sentence is either fully live or fully dated. A live value never sits next to a
    hand-written judgment about it; judgments come from FIGS, with every branch written.
  - Live values print their period somewhere in the sentence.
  - Never live: Arguments sections, first-print comparisons, Corrections lines, quotes.
  - A live value changing is not a correction and does not set `updated:`.

Command line:
    python3 tools/figures.py report              every article's checks and due dates
    python3 tools/figures.py backtest FIG [FROM] the distinct outputs of FIG as of each
                                                 month since FROM (YYYY-MM, default 2000-01)
"""

import json
import os
import re
import shlex
import sys
from datetime import date, datetime, timezone

MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December"]
ORD_Q = ["first", "second", "third", "fourth"]
BASELINE_START, BASELINE_END = "2015-01-01", "2019-12-31"
DIRECTIVE = re.compile(r"(\s*)\{\{\s*(v|fig|check|due)\s+(.*?)\s*\}\}")


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
class Data:
    """The committed data/ files, optionally truncated to an as-of date for backtests."""

    def __init__(self, root="data", asof=None):
        self.asof = asof
        self.series = {}
        s = json.load(open(os.path.join(root, "series.json"), encoding="utf-8"))
        for t in s.get("tiles", []):
            self.series[t["id"]] = {"kind": "tile", "obs": t.get("observations", []), "freq": t.get("freq", "m"),
                                    "ctx": t.get("context"),
                                    "url": (t.get("source") or {}).get("url"), "units": (t.get("source") or {}).get("fred_units", ""),
                                    "transform": (t.get("source") or {}).get("transform", "")}
        for k, e in (s.get("extras") or {}).items():
            obs = []
            if e.get("previous"):
                obs.append([e["previous"]["date"], e["previous"]["value"]])
            obs.append([e["date"], e["value"]])
            self.series[k] = {"kind": "extra", "obs": obs, "freq": None, "url": e.get("url"), "units": e.get("label", ""), "transform": ""}
        try:
            comps = json.load(open(os.path.join(root, "companions.json"), encoding="utf-8")).get("companions", [])
        except (OSError, ValueError):
            comps = []
        for c in comps:
            src = c.get("source") or {}
            self.series.setdefault(c["id"], {"kind": "companion", "obs": c.get("observations", []), "freq": c.get("freq", "m"),
                                             "url": src.get("url"), "units": src.get("fred_units", c.get("label", "")),
                                             "transform": src.get("transform", "")})
        if asof:
            for v in self.series.values():
                v["obs"] = [o for o in v["obs"] if o[0] <= asof]

    def get(self, sid):
        if sid not in self.series:
            raise KeyError(f"unknown series '{sid}'")
        s = self.series[sid]
        if not s["obs"]:
            raise KeyError(f"series '{sid}' has no observations")
        return s

    def context(self, sid):
        """The same numbers fetch_fred.py writes to a tile's context, computed from the observations
        so that backtests can ask for them as of any date."""
        s = self.get(sid)
        if s.get("ctx") and not self.asof:
            return self._tile_context(s["ctx"])     # the tile's own numbers, so text and tile agree
        obs = [o for o in s["obs"] if o[1] is not None]
        cur_d, cur = obs[-1]
        hist = [v for _, v in obs[:-1]]
        ctx = {"value": (cur_d, cur), "previous": tuple(obs[-2]) if len(obs) > 1 else None,
               "since": obs[0][0], "percentile": None, "baseline": None,
               "lowest_since": None, "highest_since": None, "min": min(obs, key=lambda o: o[1]),
               "max": max(obs, key=lambda o: o[1]), "year_ago": None}
        if hist:
            below = sum(1 for v in hist if v < cur)
            equal = sum(1 for v in hist if v == cur)
            ctx["percentile"] = round(100.0 * (below + 0.5 * equal) / len(hist), 1)
        base = [v for d, v in obs if BASELINE_START <= d <= BASELINE_END]
        if base:
            ctx["baseline"] = (None, sum(base) / len(base))
        for d, v in reversed(obs[:-1]):
            if ctx["highest_since"] is None and v >= cur:
                ctx["highest_since"] = d
            if ctx["lowest_since"] is None and v <= cur:
                ctx["lowest_since"] = d
            if ctx["highest_since"] and ctx["lowest_since"]:
                break
        cd = _d(cur_d)
        try:
            target = cd.replace(year=cd.year - 1)
        except ValueError:
            target = cd.replace(year=cd.year - 1, day=28)
        if len(obs) > 1:
            ya = min(obs[:-1], key=lambda o: abs((_d(o[0]) - target).days))
            if abs((_d(ya[0]) - target).days) <= 45:
                ctx["year_ago"] = tuple(ya)
        return ctx


    @staticmethod
    def _tile_context(c):
        pair = lambda x: (x["date"], x["value"]) if x else None
        return {"value": pair(c["current"]), "previous": pair(c.get("previous")), "since": c.get("since"),
                "percentile": c.get("percentile_below"),
                "baseline": (None, c["baseline_2015_19"]) if c.get("baseline_2015_19") is not None else None,
                "lowest_since": c.get("lowest_since"), "highest_since": c.get("highest_since"),
                "min": pair(c.get("min")), "max": pair(c.get("max")), "year_ago": pair(c.get("year_ago"))}


def _d(s):
    return date.fromisoformat(s[:10])


def years_between(a, b):
    return (_d(b) - _d(a)).days / 365.25


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------
def month_year(d):
    x = _d(d)
    return f"{MONTHS[x.month - 1]} {x.year}"


def period(d, freq):
    x = _d(d)
    if freq == "w":
        return f"the week ending {MONTHS[x.month - 1]} {x.day}, {x.year}"
    if freq == "d":
        return f"{MONTHS[x.month - 1]} {x.day}, {x.year}"
    if freq == "q":
        return f"the {ORD_Q[(x.month - 1) // 3]} quarter of {x.year}"
    if freq == "a":
        return str(x.year)
    return month_year(d)


def fmt(v, how):
    if how == "int":
        return f"{v:,.0f}"
    if how in ("num0", "num1", "num2"):
        return f"{v:,.{how[-1]}f}"
    if how in ("pct0", "pct1", "pct2"):
        return f"{v:.{how[-1]}f}%"
    if how == "thousands":
        return f"{round(v / 1000) * 1000:,.0f}"
    if how in ("millions1", "millions2"):
        return f"{v / 1e6:.{how[-1]}f} million"
    if how == "usd0":
        return f"${v:,.0f}"
    if how == "usd2":
        return f"${v:,.2f}"
    if how == "usd10":
        return f"${round(v / 10) * 10:,.0f}"
    raise ValueError(f"unknown format '{how}'")


def default_fmt(s):
    if s["transform"] in ("pc1", "pch", "pca") or "percent" in (s["units"] or "").lower():
        return "pct1"
    return "int"


# ---------------------------------------------------------------------------
# Named figures and phrases. Each takes Data and returns (text, [source urls]).
# Every branch is written out; a new branch is a new decision, shown to Tom before it ships.
# ---------------------------------------------------------------------------
def fig_claims_low(D):
    """The clause after the claims level on the jobless-claims page."""
    c = D.context("claims")
    cur_d = c["value"][0]
    ls = c["lowest_since"]
    if ls is None:
        return "the lowest on record", []
    if years_between(ls, cur_d) >= 1:
        txt = f"the lowest since {month_year(ls)}"
        # CLF16OV was 81.5 million in October 1969 and first passed half of September 2026's
        # 170.3 million in November 1971 (FRED, checked Oct 30, 2026). Before 1970 the clause
        # holds with room to spare even if the labor force shrinks a few percent.
        if ls < "1970-01-01":
            txt += ", when the workforce was less than half its present size"
        return txt, ["https://fred.stlouisfed.org/series/CLF16OV"]
    hs = c["highest_since"]
    if hs is None:
        return "the highest on record", []
    if years_between(hs, cur_d) >= 1:
        return f"the highest since {month_year(hs)}", []
    p, since = c["percentile"], _d(c["since"]).year
    share = lambda x: min(99, max(1, round(x)))          # as on the tiles: a record is said once, above
    if p < 50:
        return f"lower than {share(100 - p)}% of weeks since {since}", []
    return f"higher than {share(p)}% of weeks since {since}", []


def fig_continuing_claims(D):
    """Continuing claims against their 2025 peak, on the jobless-claims page."""
    s = D.get("continuing_claims")
    cur = s["obs"][-1][1]
    y25 = [v for d, v in s["obs"] if d.startswith("2025")]
    txt = f"about {fmt(cur, 'millions2')}"
    if y25:
        peak = max(y25)
        if fmt(cur, "millions2") == fmt(peak, "millions2"):
            txt += ", the same as the 2025 peak"
        elif cur < peak:
            txt += f", down from {fmt(peak, 'millions2')} at the 2025 peak"
        else:
            txt += f", above the 2025 peak of {fmt(peak, 'millions2')}"
    return txt, [s["url"]]


def fig_pension_3000_2019(D):
    """What a $3,000 pension fixed in 2019 buys, in 2019 dollars (price level, 2019 = 100)."""
    s = D.get("price_level")
    pl = s["obs"][-1][1]
    return fmt(3000 * 100 / pl, "usd10"), ["https://fred.stlouisfed.org/series/CPIAUCSL"]


def val_claims_rule_last(D):
    """Start of the most recent episode in which the claims four-week average rose 50,000 or
    more above its low of the prior 52 weeks (episodes more than 13 weeks apart count separately).
    Used by the claims page's check on "most recently in June 2023"."""
    obs = D.get("claims")["obs"]
    last_start, last = None, None
    for i in range(52, len(obs)):
        d, v = obs[i]
        if v - min(o[1] for o in obs[i - 52:i]) >= 50000:
            if last is None or (_d(d) - last).days > 91:
                last_start = d
            last = _d(d)
    return last_start


FIGS = {
    "claims_low": fig_claims_low,
    "continuing_claims": fig_continuing_claims,
    "pension_3000_2019": fig_pension_3000_2019,
}
VALUES = {      # usable on the left of a check as fig:<name>
    "claims_rule_last": val_claims_rule_last,
}


# ---------------------------------------------------------------------------
# Directives
# ---------------------------------------------------------------------------
def _field(D, path):
    """id.field -> (value, date, series). Dates come back as YYYY-MM-DD strings."""
    sid, _, field = path.partition(".")
    field = field or "value"
    s = D.get(sid)
    if s["kind"] == "extra" and field not in ("value", "previous"):
        raise KeyError(f"extras have only value and previous ('{path}')")
    c = D.context(sid)
    if field in ("lowest_since", "highest_since", "since"):
        return c[field], c[field], s
    if field == "percentile":
        return c["percentile"], c["value"][0], s
    if field not in c or c[field] is None:
        raise KeyError(f"no '{field}' for '{sid}'")
    d, v = c[field]
    return v, d, s


def _parse(arg):
    toks = shlex.split(arg)
    iskw = lambda t: re.match(r"^[a-z_]+=", t) is not None      # fmt=…, else=…; not the <= of a check
    pos = [t for t in toks if not iskw(t)]
    kw = dict(t.split("=", 1) for t in toks if iskw(t))
    return pos, kw


def _literal(x):
    if re.match(r"^\d{4}-\d{2}-\d{2}$", x):
        return x
    return float(x)


def render(body, D, slug, report, offset=0):
    """Replace the directives in one article body. Never raises: a figure that can't be computed
    prints its else= text and is reported, so an article can't stop a data refresh."""
    out, pos = [], 0
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for m in DIRECTIVE.finditer(body):
        lead, kind, arg = m.group(1), m.group(2), m.group(3)
        line = offset + body.count("\n", 0, m.start()) + 1 + lead.count("\n")
        where = f"{slug}.md:{line}"
        out.append(body[pos:m.start()])
        pos = m.end()
        try:
            args, kw = _parse(arg)
        except ValueError as e:
            report["warnings"].append(f"{where}: can't read directive ({e})")
            out.append(lead)
            continue
        if kind in ("check", "due"):
            out.append("" if not lead.count("\n") else lead[: lead.rfind("\n") + 1])
            if kind == "due":
                when, what = (args + ["", ""])[:2]
                item = {"where": where, "due": when, "what": what}
                report["due"].append(item)
                if when <= today:
                    report["overdue"].append(item)
                continue
            note = args[3] if len(args) > 3 else ""
            item = {"where": where, "check": " ".join(args[:3]), "note": note}
            try:
                lhs, op, rhs = args[0], args[1], _literal(args[2])
                if lhs.startswith("fig:"):
                    got = VALUES[lhs[4:]](D)
                else:
                    got = _field(D, lhs)[0]
                if got is None and isinstance(rhs, str):
                    got = "0000-01-01"                 # a None "since" means a record: earlier than any date
                ok = {"<": got < rhs, "<=": got <= rhs, ">": got > rhs, ">=": got >= rhs,
                      "==": got == rhs, "!=": got != rhs}[op]
                item["got"] = got
                report["checks"].append(item)
                if not ok:
                    report["failing"].append(item)
            except Exception as e:                      # noqa: BLE001 — a bad check is reported, never fatal
                item["error"] = str(e)
                report["checks"].append(item)
                report["failing"].append(item)
            continue
        try:
            if kind == "fig":
                text, srcs = FIGS[args[0]](D)
            else:
                path = args[0]
                v, d, s = _field(D, path)
                field = path.partition(".")[2] or "value"
                if "period" in args[1:]:
                    text = period(d, s["freq"]) if field not in ("lowest_since", "highest_since", "since") else month_year(v)
                elif field in ("lowest_since", "highest_since", "since"):
                    text = month_year(v) if v else "on record"
                else:
                    text = fmt(v, kw.get("fmt") or ("num1" if field == "percentile" else default_fmt(s)))
                srcs = [s["url"]]
            report["values"].append({"where": where, "directive": f"{kind} {arg}", "text": text})
            for u in srcs:
                if u and u not in body:
                    report["warnings"].append(f"{where}: {u} is not linked anywhere on the page")
            out.append(lead + text)
        except Exception as e:                          # noqa: BLE001
            report["warnings"].append(f"{where}: {kind} {arg}: {e}")
            out.append(lead + kw.get("else", ""))
    out.append(body[pos:])
    return "".join(out)


def new_report():
    return {"values": [], "checks": [], "failing": [], "due": [], "overdue": [], "warnings": []}


def summarize(report):
    lines = [f"figures: {len(report['values'])} live values, {len(report['checks'])} checks "
             f"({len(report['failing'])} failing), {len(report['due'])} due dates ({len(report['overdue'])} passed)"]
    for x in report["failing"]:
        lines.append(f"  CHECK FAILS {x['where']}: {x['check']}  (got {x.get('got', x.get('error'))})  {x['note']}")
    for x in report["overdue"]:
        lines.append(f"  DUE {x['where']}: {x['due']}  {x['what']}")
    for w in report["warnings"]:
        lines.append(f"  WARNING {w}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Command line
# ---------------------------------------------------------------------------
def _main(argv):
    if len(argv) >= 2 and argv[1] == "backtest":
        name = argv[2]
        start = (argv[3] if len(argv) > 3 else "2000-01") + "-01"
        full = Data()
        fn = FIGS.get(name) or VALUES.get(name)
        months, y, mth = [], int(start[:4]), int(start[5:7])
        end = datetime.now(timezone.utc).date()
        while date(y, mth, 1) <= end:
            nxt = date(y + (mth == 12), mth % 12 + 1, 1)
            months.append((nxt.fromordinal(nxt.toordinal() - 1)).isoformat())
            y, mth = nxt.year, nxt.month
        last = None
        for asof in months:
            D = Data(asof=asof)
            try:
                r = fn(D)
                text = r[0] if isinstance(r, tuple) else r
            except Exception as e:                      # noqa: BLE001
                text = f"[error: {e}]"
            shape = re.sub(r"\d", "#", str(text))
            if shape != last:
                print(f"{asof}  {text}")
                last = shape
        print(f"(full data) {(fn(full)[0] if name in FIGS else fn(full))}")
        return 0
    if len(argv) >= 2 and argv[1] == "report":
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        import build_articles as b                       # noqa: E402
        D = Data()
        rep = new_report()
        src = os.path.join("articles", "src")
        for name in sorted(os.listdir(src)):
            if name.endswith(".md"):
                a = b.parse(os.path.join(src, name))
                render(a["body"], D, a["slug"], rep, b.body_offset(os.path.join(src, name), a["body"]))
        print(summarize(rep))
        return 1 if rep["failing"] or rep["warnings"] else 0
    print(__doc__)
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv))
