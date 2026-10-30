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
                                    "ctx": t.get("context"), "ctx_real": t.get("context_real"),
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
    if how == "k_millions2":                       # a series in thousands, as millions (housing starts)
        return f"{v / 1000:.2f} million"
    if how == "k_millions1":                       # a series in thousands, as millions to one decimal
        return f"{v / 1000:.1f} million"
    if how == "k_round10k":                        # a series in thousands, to the nearest 10,000
        return f"{round(v / 10) * 10000:,.0f}"
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


# --- helpers for the figures below ------------------------------------------------
def _aligned(D, *sids):
    """The latest date every series has, and each series' value on it."""
    maps = [dict((d, v) for d, v in D.get(s)["obs"]) for s in sids]
    common = set(maps[0]).intersection(*maps[1:])
    if not common:
        raise KeyError(f"no common date for {', '.join(sids)}")
    d = max(common)
    return d, [m[d] for m in maps]


def _pct_of_history(obs):
    cur = obs[-1][1]
    hist = [v for _, v in obs[:-1]]
    below = sum(1 for v in hist if v < cur)
    equal = sum(1 for v in hist if v == cur)
    return 100.0 * (below + 0.5 * equal) / len(hist)


def _share(x):
    return min(99, max(1, round(x)))                # as on the tiles: 1–99%, a record is said once


def _rank_phrase(D, sid, unit, own="its "):
    """'its highest since July 2007' / 'its highest on record' / 'higher than 63% of months since 1953'."""
    c = D.context(sid)
    cur_d = c["value"][0]
    for side in ("lowest", "highest"):
        since = c[f"{side}_since"]
        if since is None:
            return f"{own}{side} on record"
        if years_between(since, cur_d) >= 1:
            return f"{own}{side} since {month_year(since)}"
    p, first = c["percentile"], _d(c["since"]).year
    if p < 50:
        return f"lower than {_share(100 - p)}% of {unit} since {first}"
    return f"higher than {_share(p)}% of {unit} since {first}"


def _signed_pct(x, places=1):
    s = f"{abs(x):.{places}f}%"
    return ("−" + s) if round(x, places) < 0 else s


def _month(d, ref):
    """'April' when d is in the same year as ref, else 'April 2025'."""
    x = _d(d)
    return MONTHS[x.month - 1] if x.year == _d(ref).year else month_year(d)


def _payment(principal, rate_pct, years=30):
    r = rate_pct / 100 / 12
    n = years * 12
    return principal * r / (1 - (1 + r) ** -n)


# --- pay against prices (inflation page, hourly pay page) --------------------------
def fig_pay_cpi_month(D):
    d, _ = _aligned(D, "pay", "cpi")
    return month_year(d), []


def fig_pay_cpi_pay(D):
    _, (pay, cpi) = _aligned(D, "pay", "cpi")
    return fmt(pay, "pct1"), ["https://fred.stlouisfed.org/series/AHETPI"]


def fig_pay_cpi_cpi(D):
    _, (pay, cpi) = _aligned(D, "pay", "cpi")
    return fmt(cpi, "pct1"), ["https://fred.stlouisfed.org/series/CPIAUCSL"]


def _real_gap(D):
    _, (pay, cpi) = _aligned(D, "pay", "cpi")
    return round(pay, 1) - round(cpi, 1)            # from the two figures as printed, so the text adds up


def fig_pay_cpi_buys(D):
    g = _real_gap(D)
    if abs(g) < 0.05:
        return "so an hour of work bought about as much as it did a year before", []
    return f"so an hour of work bought about {abs(g):.1f}% {'less' if g < 0 else 'more'} than it did a year before", []


def fig_pay_cpi_verdict(D):
    g = _real_gap(D)
    if abs(g) < 0.05:
        return "so typical paychecks about kept pace over the year", []
    return f"so typical paychecks {'lost' if g < 0 else 'gained'} ground over the year", []


def fig_real_wage_run(D):
    """How long the gap between pay growth and inflation has been on its current side of zero."""
    obs = [o for o in D.get("real_wages")["obs"] if o[1] is not None]
    neg = obs[-1][1] < 0
    start = obs[-1][0]
    for d, v in reversed(obs[:-1]):
        if (v < 0) != neg:
            break
        start = d
    side = "below" if neg else "above"
    if start == obs[-1][0]:
        return f"That gap went {side} zero in {_month(start, start)}", []
    return f"That gap has been {side} zero every month since {_month(start, obs[-1][0])}", []


# --- prices ----------------------------------------------------------------------
def _cpi_mom(D):
    obs = D.get("cpi_index")["obs"]
    return (obs[-1][1] / obs[-2][1] - 1) * 100


def fig_cpi_mom(D):
    return _signed_pct(_cpi_mom(D)), ["https://fred.stlouisfed.org/series/CPIAUCSL"]


def fig_cpi_mom_annual(D):
    m = round(_cpi_mom(D), 1) / 100                # from the monthly figure as printed, so the text adds up
    return "about " + _signed_pct(((1 + m) ** 12 - 1) * 100, 0), []


def val_cpi_core_gap(D):
    _, (a, b) = _aligned(D, "cpi", "core_cpi")
    return round(a - b, 2)


# --- jobs --------------------------------------------------------------------------
def fig_epop_vs_record(D):
    obs = D.get("prime_age_epop")["obs"]
    cur = obs[-1][1]
    hist = obs[:-1]
    top = max(hist, key=lambda o: o[1])
    gap = round(top[1] - cur, 1)
    yr = _d(top[0]).year
    if gap <= 0:
        return "a record", []
    if gap < 0.5:
        return f"just below its {yr} record", []
    if gap < 1:
        return f"under a point below its {yr} record", []
    if gap < 1.5:
        return f"a little over a point below its {yr} record", []
    return f"{gap:.1f} points below its {yr} record", []


def val_u6_gap(D):
    _, (u6, u) = _aligned(D, "u6", "unemployment")
    return round(u6 - u, 1)


def fig_payrolls_vs_avg(D):
    """'September 2026's 29,000 sits in an average of about 51,000' and its negative forms."""
    d, (m, a) = _aligned(D, "payrolls", "payrolls_3mo")
    mm = f"{abs(round(m)) * 1000:,.0f}"
    aa = f"{abs(round(a)) * 1000:,.0f}"
    first = f"{month_year(d)}'s {mm}" if m >= 0 else f"{month_year(d)}'s loss of {mm}"
    second = f"an average of about {aa}" if a >= 0 else f"an average loss of about {aa}"
    return f"{first} sits in {second}", ["https://fred.stlouisfed.org/series/PAYEMS"]


# --- growth and rates ----------------------------------------------------------------
def fig_gdp_quarterly(D):
    a = D.get("gdp")["obs"][-1][1]
    return _signed_pct(((1 + a / 100) ** 0.25 - 1) * 100, 2), []


def fig_ten_year_rank(D):
    return _rank_phrase(D, "ten_year", "months"), []


def fig_pmt_now(D):
    return fmt(_payment(400000, D.get("mortgage")["obs"][-1][1]), "usd10"), []


def _pmt_diff(D):
    now = round(_payment(400000, D.get("mortgage")["obs"][-1][1]) / 10) * 10
    then = round(_payment(400000, 3.0) / 10) * 10
    return now - then


def fig_pmt_diff(D):
    return fmt(_pmt_diff(D), "usd0"), []


def fig_pmt_diff_year(D):
    y = _pmt_diff(D) * 12
    k = int(y // 1000) * 1000
    return (f"over ${k:,}" if y > k else f"${k:,}"), []


def fig_pay_rank_norm(D):
    c = D.context("pay")
    p, first = c["percentile"], _d(c["since"]).year
    rank = (f"lower than about {_share(100 - p)}% of months since {first}" if p < 50
            else f"higher than about {_share(p)}% of months since {first}")
    gap = c["value"][1] - c["baseline"][1]
    if abs(gap) < 0.3:
        norm = "close to the pre-pandemic norm"
    elif 0 < gap < 1:
        norm = "not far above the pre-pandemic norm"
    elif gap >= 1:
        norm = "well above the pre-pandemic norm"
    elif gap > -1:
        norm = "a little below the pre-pandemic norm"
    else:
        norm = "well below the pre-pandemic norm"
    return f"{rank} and {norm}", []


# --- housing and trade ------------------------------------------------------------
def fig_starts_month(D):
    d, _ = _aligned(D, "housing_starts", "single_family_starts")
    return month_year(d), []


def fig_starts_total(D):
    _, (tot, sf) = _aligned(D, "housing_starts", "single_family_starts")
    return fmt(tot, "k_millions2"), ["https://fred.stlouisfed.org/series/HOUST"]


def fig_starts_houses(D):
    _, (tot, sf) = _aligned(D, "housing_starts", "single_family_starts")
    return fmt(sf, "k_round10k"), ["https://fred.stlouisfed.org/series/HOUST1F"]


def fig_starts_apartments(D):
    _, (tot, sf) = _aligned(D, "housing_starts", "single_family_starts")
    return fmt(tot - sf, "k_round10k"), []


def _trade_3mo(D):
    obs = D.get("trade")["obs"][-3:]
    return obs[-1][0], -sum(v for _, v in obs) / 3            # $ millions a month, deficit positive


def fig_trade_3mo_month(D):
    return month_year(_trade_3mo(D)[0]), []


def fig_trade_3mo(D):
    d, m = _trade_3mo(D)
    word = "deficit" if m >= 0 else "surplus"
    return f"a {word} of about ${round(abs(m) / 5000) * 5} billion a month", ["https://fred.stlouisfed.org/series/BOPGSTB"]


def val_trade_share(D):
    _, m = _trade_3mo(D)
    gdp = D.get("nominal_gdp")["obs"][-1][1]                   # $ billions, annual rate
    return round(m * 12 / 1000 / gdp * 100, 1)


def fig_trade_3mo_share(D):
    return f"{abs(val_trade_share(D)):.1f}%", ["https://fred.stlouisfed.org/series/GDP"]


# --- gasoline ----------------------------------------------------------------------
def fig_gas_tank(D):
    return fmt(D.get("gas")["obs"][-1][1] * 15, "usd0"), []


def fig_gas_tank_year_ago(D):
    ya = D.context("gas")["year_ago"]
    return fmt(ya[1] * 15, "usd0"), []


def fig_gas_real_rank(D):
    """Where today's price sits in its history in today's dollars (the gas_real companion; ranks
    don't depend on which month's dollars the history is stated in)."""
    obs = D.get("gas_real")["obs"]
    p = _pct_of_history(obs)
    first = _d(obs[0][0]).year
    if p < 50:
        return f"lower than about {_share(100 - p)}% of weeks since {first}", []
    return f"higher than about {_share(p)}% of weeks since {first}", []


def _gas_2022_peak(D):
    nominal = [o for o in D.get("gas")["obs"] if o[0].startswith("2022")]
    d = max(nominal, key=lambda o: o[1])[0]
    real = dict((x, v) for x, v in D.get("gas_real")["obs"])
    return d, real[d]


def fig_gas_2022_today(D):
    return fmt(_gas_2022_peak(D)[1], "usd2"), []


def val_gas_vs_2022_real(D):
    return round(D.get("gas_real")["obs"][-1][1] - _gas_2022_peak(D)[1], 2)


def fig_gas_real_max(D):
    top = max(D.get("gas_real")["obs"], key=lambda o: o[1])
    return fmt(top[1], "usd2"), []


def val_gas_real_max_year(D):
    return float(_d(max(D.get("gas_real")["obs"], key=lambda o: o[1])[0]).year)


# --- phase 2b ------------------------------------------------------------------
_FRACTIONS = [(0.1, "about one month in ten"), (0.2, "about one month in five"), (0.25, "about one month in four"),
              (1 / 3, "about one month in three"), (0.5, "about half of all months"), (2 / 3, "about two months in three"),
              (0.75, "about three months out of four"), (0.8, "about four months in five"), (0.9, "about nine months in ten")]


def _frac_words(x):
    return min(_FRACTIONS, key=lambda f: abs(f[0] - x))[1]


def fig_hires_rank(D):
    """'lower than in about three months out of four since 2000' (share of earlier months strictly higher)."""
    obs = D.get("hires_rate")["obs"]
    cur, hist = obs[-1][1], [v for _, v in obs[:-1]]
    hi = sum(v > cur for v in hist) / len(hist)
    lo = sum(v < cur for v in hist) / len(hist)
    first = _d(obs[0][0]).year
    if hi >= lo:
        return (f"the lowest since the series began in {first}" if lo == 0 else f"lower than in {_frac_words(hi)} since {first}"), []
    return (f"the highest since the series began in {first}" if hi == 0 else f"higher than in {_frac_words(lo)} since {first}"), []


def fig_quits_vs_2019(D):
    obs = D.get("quits_rate")["obs"]
    base = [v for d, v in obs if d.startswith("2019")]
    r = obs[-1][1] / (sum(base) / len(base)) - 1
    if abs(r) < 0.05:
        return "about as many workers quit as in a typical month of 2019", []
    words = min([(0.1, "a tenth"), (0.2, "a fifth"), (0.25, "a quarter"), (1 / 3, "a third"), (0.5, "half")],
                key=lambda w: abs(w[0] - abs(r)))[1]
    return f"about {words} {'fewer' if r < 0 else 'more'} workers quit than in a typical month of 2019", []


def _cpi_avg(D, year):
    vals = [v for d, v in D.get("cpi_index")["obs"] if d.startswith(str(year))]
    return sum(vals) / len(vals)


def fig_pmt2000_2020(D):
    return fmt(2000 * _cpi_avg(D, 2020) / D.get("cpi_index")["obs"][-1][1], "usd10"), ["https://fred.stlouisfed.org/series/CPIAUCSL"]


def fig_pmt2000_2022(D):
    return fmt(2000 * _cpi_avg(D, 2022) / D.get("cpi_index")["obs"][-1][1], "usd10"), []


def fig_prices_since_2020(D):
    return f"{round((D.get('cpi_index')['obs'][-1][1] / _cpi_avg(D, 2020) - 1) * 100)}%", []


def fig_pmt_gap_100(D):
    return f"${round(_pmt_diff(D) / 100) * 100:,}", []


def fig_price_level_int(D):
    return f"{round(D.get('price_level')['obs'][-1][1])}", []


def fig_price_level_pct(D):
    return f"{round(D.get('price_level')['obs'][-1][1] - 100)}%", []


def fig_real_ff_words(D):
    v = D.get("real_fed_funds")["obs"][-1][1]
    if v < 0:
        return f"below zero, about {_signed_pct(v)}", []
    n, frac = int(v), v - int(v)
    if frac < 0.1:
        return f"about {n}%", []
    if frac < 0.45:
        return f"a little over {n}%", []
    if frac < 0.6:
        return f"about {n}.5%", []
    if frac < 0.9:
        return f"a little under {n + 1}%", []
    return f"about {n + 1}%", []


def fig_claims_history_pos(D):
    p = D.context("claims")["percentile"]
    if p <= 15:
        return "near the low end of its history", []
    if p <= 35:
        return "in the lower part of its history", []
    if p < 65:
        return "in the middle of its history", []
    if p < 85:
        return "in the upper part of its history", []
    return "near the high end of its history", []


# --- phase 3b: series added Oct 30 (pay level, rent level, unemployed, openings, search length, ECI) ---
def _avg_year(obs, year):
    vals = [v for d, v in obs if d.startswith(str(year))]
    return sum(vals) / len(vals)


def _since_2019(D, sid):
    obs = D.get(sid)["obs"]
    return obs[-1][0], obs[-1][1] / _avg_year(obs, 2019) - 1


def _pay_prices_rent(D):
    """Pay, prices and rent since the 2019 average, on the latest month all three have."""
    d, (pay, pl, rent) = _aligned(D, "pay_level", "price_level", "rent_level")
    p0 = _avg_year(D.get("pay_level")["obs"], 2019)
    r0 = _avg_year(D.get("rent_level")["obs"], 2019)
    return d, pay / p0 - 1, pl / 100 - 1, rent / r0 - 1           # price_level is already 2019 = 100


def _pay_prices(D):
    d, (pay, pl) = _aligned(D, "pay_level", "price_level")
    return d, pay / _avg_year(D.get("pay_level")["obs"], 2019) - 1, pl / 100 - 1


def _pct_round(x):
    return f"{round(x * 100)}%"


def fig_pp_month(D):
    return month_year(_pay_prices(D)[0]), []


def fig_pay_since_2019(D):
    return _pct_round(_pay_prices(D)[1]), ["https://fred.stlouisfed.org/series/AHETPI"]


def fig_prices_since_2019(D):
    return _pct_round(_pay_prices(D)[2]), ["https://fred.stlouisfed.org/series/CPIAUCSL"]


def _years_since_mid_2019(d):
    return (_d(d) - date(2019, 7, 1)).days / 365.25


_NUMBERS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve"]


def _years_words(yrs):
    n = int(round(yrs))
    w = _NUMBERS[n] if n < len(_NUMBERS) else str(n)
    return "one year" if n == 1 else f"{w} years"


def fig_real_gain_since_2019(D):
    """'a real gain of about 5% over seven years, less than 1% a year' and its other forms."""
    d, pay, prices = _pay_prices(D)
    pay_r, prices_r = round(pay * 100) / 100, round(prices * 100) / 100   # from the two figures as printed
    real = (1 + pay_r) / (1 + prices_r) - 1
    yrs = _years_since_mid_2019(d)
    n = _years_words(yrs)
    per = (1 + real) ** (1 / yrs) - 1
    if abs(real) < 0.005:
        return f"no real gain over {n}", []
    word = "gain" if real > 0 else "loss"
    pace = "less than 1% a year" if abs(per) < 0.01 else f"about {abs(per) * 100:.1f}% a year"
    return f"a real {word} of about {round(abs(real) * 100)}% over {n}, {pace}", []


def fig_rent_since_2019(D):
    return _pct_round(_pay_prices_rent(D)[3]), ["https://fred.stlouisfed.org/series/CUSR0000SEHA"]


def fig_rent_month(D):
    return month_year(_pay_prices_rent(D)[0]), []


def fig_rent3_pay(D):
    return _pct_round(_pay_prices_rent(D)[1]), ["https://fred.stlouisfed.org/series/AHETPI"]


def fig_rent3_prices(D):
    return _pct_round(_pay_prices_rent(D)[2]), ["https://fred.stlouisfed.org/series/CPIAUCSL"]


def val_rent_minus_prices(D):
    d, pay, prices, rent = _pay_prices_rent(D)
    return round(rent * 100) - round(prices * 100)


def fig_rent_verdict(D):
    d, pay, prices, rent = _pay_prices_rent(D)
    pay_r, prices_r, rent_r = (round(x * 100) for x in (pay, prices, rent))
    gained_prices = pay_r > prices_r
    gap = pay_r - rent_r
    first = "gained ground on prices overall" if gained_prices else "lost ground to prices overall"
    if gap > 5:
        second = "and on rent" if gained_prices else "but gained on rent"
    elif gap > 0:
        second = "and, narrowly, on rent" if gained_prices else "but, narrowly, gained on rent"
    elif gap == 0:
        second = "and kept even with rent" if gained_prices else "and only kept even with rent"
    elif gap >= -5:
        second = "but, narrowly, not on rent" if gained_prices else "and, narrowly, to rent"
    else:
        second = "but not on rent" if gained_prices else "and to rent"
    return f"So the average worker has {first} {second}", []


def _pay_prices_sep2019(D):
    pay = D.get("pay_level")["obs"]
    cpi = D.get("cpi_index")["obs"]
    p0 = dict(pay)["2019-09-01"]
    c0 = dict(cpi)["2019-09-01"]
    d, (p, c) = _aligned(D, "pay_level", "cpi_index")
    return d, p / p0 - 1, c / c0 - 1


def fig_pay_since_sep2019(D):
    return _pct_round(_pay_prices_sep2019(D)[1]), ["https://fred.stlouisfed.org/series/AHETPI"]


def fig_prices_since_sep2019(D):
    return _pct_round(_pay_prices_sep2019(D)[2]), []


def fig_sep2019_month(D):
    return month_year(_pay_prices_sep2019(D)[0]), []


def fig_real_raise_sep2019(D):
    """'The real raise over seven years is about 5%, less than 1% a year'."""
    d, p, c = _pay_prices_sep2019(D)
    p_r, c_r = round(p * 100) / 100, round(c * 100) / 100
    real = (1 + p_r) / (1 + c_r) - 1
    yrs = (_d(d) - date(2019, 9, 1)).days / 365.25
    n = _years_words(yrs)
    per = (1 + real) ** (1 / yrs) - 1
    pace = "less than 1% a year" if abs(per) < 0.01 else f"about {abs(per) * 100:.1f}% a year"
    if real < 0:
        return f"The real change over {n} is a loss of about {round(-real * 100)}%, {pace}", []
    return f"The real raise over {n} is about {round(real * 100)}%, {pace}", []


def val_real_raise_sep2019(D):
    d, p, c = _pay_prices_sep2019(D)
    return round(((1 + round(p, 2)) / (1 + round(c, 2)) - 1) * 100, 1)


def fig_search_median(D):
    obs = D.get("uempmed")["obs"]
    return f"{obs[-1][1]:.1f} weeks", ["https://fred.stlouisfed.org/series/UEMPMED"]


def fig_search_mean(D):
    return f"{D.get('uempmean')['obs'][-1][1]:.1f} weeks", ["https://fred.stlouisfed.org/series/UEMPMEAN"]


def fig_long_term_pct(D):
    return f"{D.get('long_term_share')['obs'][-1][1]:.1f}%", ["https://fred.stlouisfed.org/series/LNS13025703"]


def fig_search_median_vs_2019(D):
    obs = D.get("uempmed")["obs"]
    base = _avg_year(obs, 2019)
    cur = obs[-1][1]
    if abs(cur - base) < 0.3:
        return f"about the same as the 2019 average of {base:.1f}", []
    return f"{'up' if cur > base else 'down'} from an average of {base:.1f} in 2019", []


def fig_long_term_words(D):
    """'more than a quarter' of the unemployed looking six months or longer."""
    s = D.get("long_term_share")["obs"][-1][1] / 100
    for x, w in [(0.5, "half"), (1 / 3, "a third"), (0.25, "a quarter"), (0.2, "a fifth"), (0.1, "a tenth")]:
        if abs(s - x) < 0.012:
            return f"about {w}", []
        if s > x:
            return f"more than {w}", []
        if x - s < 0.03:
            return f"nearly {w}", []
    return "fewer than one in ten", []


def fig_long_term_count(D):
    d, (share, unemp) = _aligned(D, "long_term_share", "unemployed")
    return f"about {share / 100 * unemp / 1000:.1f} million", ["https://fred.stlouisfed.org/series/UNEMPLOY"]


def fig_long_term_2019(D):
    return f"{round(_avg_year(D.get('long_term_share')['obs'], 2019))}%", []


def _jolts_cps(D):
    d, (op, un) = _aligned(D, "openings", "unemployed")
    return d, op, un


def fig_openings_month(D):
    return month_year(_jolts_cps(D)[0]), []


def fig_openings(D):
    return f"{_jolts_cps(D)[1] / 1000:.1f} million", ["https://fred.stlouisfed.org/series/JTSJOL"]


def fig_openings_vs_2019(D):
    d, op, un = _jolts_cps(D)
    r = op / _avg_year(D.get("openings")["obs"], 2019) - 1
    if abs(r) < 0.05:
        return "about as many as in 2019", []
    return f"about {round(abs(r) * 100)}% {'more' if r > 0 else 'fewer'} than in 2019", []


def fig_unemployed_aligned(D):
    return f"{_jolts_cps(D)[2] / 1000:.1f} million", ["https://fred.stlouisfed.org/series/UNEMPLOY"]


def val_unemployed_vs_2019(D):
    """Percent change in the unemployed count from its 2019 average, on the JOLTS-aligned month."""
    return round((_jolts_cps(D)[2] / _avg_year(D.get("unemployed")["obs"], 2019) - 1) * 100, 1)


def val_openings_vs_2019(D):
    return round((_jolts_cps(D)[1] / _avg_year(D.get("openings")["obs"], 2019) - 1) * 100, 1)


def fig_unemployed_2019(D):
    return f"about {round(_avg_year(D.get('unemployed')['obs'], 2019) / 1000)} million", []


def fig_ratio_sentence(D):
    """'the ratio of openings to job seekers fell to about one to one, from 1.2 in 2019 and a record 2.0 in March 2022'."""
    d, op, un = _jolts_cps(D)
    o, u = dict(D.get("openings")["obs"]), dict(D.get("unemployed")["obs"])
    common = sorted(set(o) & set(u))
    ratios = [(x, o[x] / u[x]) for x in common]
    r = op / un
    r19 = sum(v for x, v in ratios if x.startswith("2019")) / len([1 for x, v in ratios if x.startswith("2019")])
    top = max(ratios, key=lambda t: t[1])
    now = "about one to one" if abs(r - 1) < 0.1 else f"{r:.1f}"
    if top[0] == d:
        return f"the ratio of openings to job seekers rose to a record {r:.1f}, from {r19:.1f} in 2019", []
    if round(r, 1) == round(r19, 1):
        return f"the ratio of openings to job seekers was {r:.1f}, the same as in 2019, against a record {top[1]:.1f} in {month_year(top[0])}", []
    verb = "fell to" if r < r19 else "rose to"
    if round(r, 1) == round(top[1], 1):
        return f"the ratio of openings to job seekers {verb} {r:.1f}, from {r19:.1f} in 2019, level with its record in {month_year(top[0])}", []
    return f"the ratio of openings to job seekers {verb} {now}, from {r19:.1f} in 2019 and a record {top[1]:.1f} in {month_year(top[0])}", []


def fig_unemployed_count(D):
    return fmt(D.get("unemployed")["obs"][-1][1], "k_millions1"), ["https://fred.stlouisfed.org/series/UNEMPLOY"]


def _eci(D):
    obs = D.get("eci_wages")["obs"]
    d, v = obs[-1]
    end = _d(d)
    end_month = date(end.year, end.month + 2, 1).isoformat()          # the quarter's last month
    return d, v, (obs[-2] if len(obs) > 1 else None), end_month


def fig_eci_month(D):
    return month_year(_eci(D)[3]), []


def fig_eci_now(D):
    return fmt(_eci(D)[1], "pct1"), ["https://fred.stlouisfed.org/series/CIU2020000000000I"]


def fig_eci_vs_prev(D):
    d, v, prev, _ = _eci(D)
    if not prev:
        raise KeyError("no previous quarter")
    pe = _d(prev[0])
    prev_month = MONTHS[(pe.month + 2) - 1]
    if round(v, 1) == round(prev[1], 1):
        return f"the same pace as in the year to {prev_month}", []
    return f"{'up' if v > prev[1] else 'down'} from {prev[1]:.1f}% in the year to {prev_month}", []


def fig_eci_real(D):
    d, v, prev, end_month = _eci(D)
    cpi = dict(D.get("cpi")["obs"])[end_month]
    real = ((1 + round(v, 1) / 100) / (1 + round(cpi, 1) / 100) - 1) * 100
    if abs(real) < 0.05:
        return "about even after inflation", []
    return f"{'up' if real > 0 else 'down'} {abs(real):.1f}% after inflation", []


FIGS = {
    "claims_low": fig_claims_low,
    "continuing_claims": fig_continuing_claims,
    "pension_3000_2019": fig_pension_3000_2019,
    "pay_cpi_month": fig_pay_cpi_month, "pay_cpi_pay": fig_pay_cpi_pay, "pay_cpi_cpi": fig_pay_cpi_cpi,
    "pay_cpi_buys": fig_pay_cpi_buys, "pay_cpi_verdict": fig_pay_cpi_verdict, "real_wage_run": fig_real_wage_run,
    "cpi_mom": fig_cpi_mom, "cpi_mom_annual": fig_cpi_mom_annual,
    "epop_vs_record": fig_epop_vs_record, "payrolls_vs_avg": fig_payrolls_vs_avg,
    "gdp_quarterly": fig_gdp_quarterly, "ten_year_rank": fig_ten_year_rank,
    "pmt_now": fig_pmt_now, "pmt_diff": fig_pmt_diff, "pmt_diff_year": fig_pmt_diff_year,
    "pay_rank_norm": fig_pay_rank_norm,
    "starts_month": fig_starts_month, "starts_total": fig_starts_total, "starts_houses": fig_starts_houses,
    "starts_apartments": fig_starts_apartments,
    "trade_3mo_month": fig_trade_3mo_month, "trade_3mo": fig_trade_3mo, "trade_3mo_share": fig_trade_3mo_share,
    "gas_tank": fig_gas_tank, "gas_tank_year_ago": fig_gas_tank_year_ago, "gas_real_rank": fig_gas_real_rank,
    "gas_2022_today": fig_gas_2022_today, "gas_real_max": fig_gas_real_max,
    "hires_rank": fig_hires_rank, "quits_vs_2019": fig_quits_vs_2019,
    "pmt2000_2020": fig_pmt2000_2020, "pmt2000_2022": fig_pmt2000_2022, "prices_since_2020": fig_prices_since_2020,
    "pmt_gap_100": fig_pmt_gap_100, "price_level_int": fig_price_level_int, "price_level_pct": fig_price_level_pct,
    "real_ff_words": fig_real_ff_words, "claims_history_pos": fig_claims_history_pos,
    "pp_month": fig_pp_month, "pay_since_2019": fig_pay_since_2019, "prices_since_2019": fig_prices_since_2019,
    "real_gain_since_2019": fig_real_gain_since_2019, "rent_since_2019": fig_rent_since_2019, "rent_month": fig_rent_month,
    "rent3_pay": fig_rent3_pay, "rent3_prices": fig_rent3_prices, "rent_verdict": fig_rent_verdict,
    "search_mean": fig_search_mean, "long_term_pct": fig_long_term_pct,
    "pay_since_sep2019": fig_pay_since_sep2019, "prices_since_sep2019": fig_prices_since_sep2019,
    "sep2019_month": fig_sep2019_month, "real_raise_sep2019": fig_real_raise_sep2019,
    "search_median": fig_search_median, "search_median_vs_2019": fig_search_median_vs_2019,
    "long_term_words": fig_long_term_words, "long_term_count": fig_long_term_count, "long_term_2019": fig_long_term_2019,
    "openings_month": fig_openings_month, "openings": fig_openings, "openings_vs_2019": fig_openings_vs_2019,
    "unemployed_aligned": fig_unemployed_aligned, "unemployed_2019": fig_unemployed_2019, "ratio_sentence": fig_ratio_sentence,
    "unemployed_count": fig_unemployed_count,
    "eci_month": fig_eci_month, "eci_now": fig_eci_now, "eci_vs_prev": fig_eci_vs_prev, "eci_real": fig_eci_real,
}
VALUES = {      # usable on the left of a check as fig:<name>
    "claims_rule_last": val_claims_rule_last,
    "cpi_core_gap": val_cpi_core_gap, "u6_gap": val_u6_gap, "trade_share": val_trade_share,
    "gas_vs_2022_real": val_gas_vs_2022_real, "gas_real_max_year": val_gas_real_max_year,
    "rent_minus_prices": val_rent_minus_prices, "unemployed_vs_2019": val_unemployed_vs_2019,
    "real_raise_sep2019": val_real_raise_sep2019, "openings_vs_2019": val_openings_vs_2019,
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
                    if field in ("lowest_since", "highest_since", "since"):
                        text = month_year(v)
                    else:
                        text = period(d, {"day": "d", "month": "m", "year": "a"}.get(kw.get("as"), s["freq"]))
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
