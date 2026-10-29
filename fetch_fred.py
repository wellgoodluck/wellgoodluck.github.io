#!/usr/bin/env python3
"""
Fetch the Economy in Context indicator set from FRED and write data/series.json
(the tiles) and data/companions.json (overlay series for the detail page).

Standard library only. Needs FRED_API_KEY in the environment.
Usage:  python3 fetch_fred.py [output-path]      (default: data/series.json)

Data: FRED, Federal Reserve Bank of St. Louis (https://fred.stlouisfed.org).
Every value is the current vintage as published by the source agency; past
months are revised, so figures here can differ from first-print headlines.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from statistics import mean

API = os.environ.get("FRED_API_BASE", "https://api.stlouisfed.org/fred").rstrip("/")
API_KEY = os.environ.get("FRED_API_KEY", "").strip()

# ---------------------------------------------------------------------------
# The indicator set. Order here is the order on the page.
#
#   series   FRED series id for the history (with any FRED-side transform)
#   params   extra query params: units (chg, pc1), frequency, aggregation_method
#   freq     observation spacing of the *fetched* history: m / q / w / d
#   latest   optional second series used only for the headline value, when the
#            history series lags (e.g. monthly average vs. daily close)
#   display  how the page formats values: scale divides the raw value, then
#            decimals/prefix/suffix apply; signed adds a leading + on positives;
#            clip [lo, hi] (raw units) keeps one freak reading from flattening the
#            chart — clipped points are marked and labeled, never hidden
# ---------------------------------------------------------------------------
TILES = [
    # ---- Jobs -------------------------------------------------------------
    {
        "id": "payrolls",
        "section": "Jobs",
        "title": "Jobs added",
        "subtitle": "Nonfarm payrolls, change from the month before",
        "series": "PAYEMS",
        "params": {"units": "chg", "observation_start": "1939-02-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 0, "suffix": "K", "signed": True,
                    "unit": "thousands of jobs", "clip": [-1500, 1500]},
        "note": "Seasonally adjusted. The first two prints for any month are revised.",
    },
    {
        "id": "unemployment",
        "section": "Jobs",
        "title": "Unemployment rate",
        "subtitle": "Share of the labor force looking for work",
        "series": "UNRATE",
        "params": {"observation_start": "1948-01-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": False,
                    "unit": "percent"},
        "note": "Seasonally adjusted, from the monthly household survey.",
    },
    {
        "id": "claims",
        "section": "Jobs",
        "title": "New jobless claims",
        "subtitle": "First-time unemployment filings, 4-week average",
        "series": "IC4WSA",
        "params": {"observation_start": "1967-01-01"},
        "freq": "w",
        "display": {"scale": 1000, "decimals": 0, "suffix": "K", "signed": False,
                    "unit": "claims per week", "clip": [0, 1200000]},
        "note": "Seasonally adjusted. Weekly, so it moves before the monthly jobs numbers do.",
    },
    # ---- Prices -----------------------------------------------------------
    {
        "id": "cpi",
        "section": "Prices",
        "title": "Inflation",
        "subtitle": "Consumer prices, change from a year ago",
        "series": "CPIAUCSL",
        "params": {"units": "pc1", "observation_start": "1948-01-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": False,
                    "unit": "percent, year over year"},
        "note": "All items, all urban consumers (CPI-U), seasonally adjusted.",
    },
    {
        "id": "core_cpi",
        "section": "Prices",
        "title": "Core inflation",
        "subtitle": "Consumer prices excluding food and energy, change from a year ago",
        "series": "CPILFESL",
        "params": {"units": "pc1", "observation_start": "1958-01-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": False,
                    "unit": "percent, year over year"},
        "note": "Strips out the two most volatile groups to show the underlying trend.",
    },
    # ---- Growth & rates ---------------------------------------------------
    {
        "id": "gdp",
        "section": "Growth & rates",
        "title": "Economic growth",
        "subtitle": "Real GDP, quarterly change at an annual rate",
        "series": "A191RL1Q225SBEA",
        "params": {"observation_start": "1947-04-01"},
        "freq": "q",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True,
                    "unit": "percent, annualized", "clip": [-15, 15]},
        "note": "Inflation-adjusted. Each quarter is revised twice after its first estimate.",
    },
    {
        "id": "fed_funds",
        "section": "Growth & rates",
        "title": "Fed funds rate",
        "subtitle": "The Federal Reserve's policy rate, monthly average",
        "series": "FEDFUNDS",
        "params": {"observation_start": "1954-07-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 2, "suffix": "%", "signed": False,
                    "unit": "percent"},
        "note": "Effective rate: what banks actually paid to borrow overnight.",
    },
    {
        "id": "ten_year",
        "section": "Growth & rates",
        "title": "10-year Treasury yield",
        "subtitle": "What the U.S. government pays to borrow for ten years",
        "series": "GS10",
        "params": {"observation_start": "1953-04-01"},
        "freq": "m",
        "latest": {"series": "DGS10", "params": {"sort_order": "desc", "limit": "10"}},
        "display": {"scale": 1, "decimals": 2, "suffix": "%", "signed": False,
                    "unit": "percent"},
        "note": "History is the monthly average; the headline is the latest daily close.",
    },
    # ---- Housing ----------------------------------------------------------
    {
        "id": "housing_starts",
        "section": "Housing",
        "title": "Housing starts",
        "subtitle": "New homes begun, annual rate",
        "series": "HOUST",
        "params": {"observation_start": "1959-01-01"},
        "freq": "m",
        "display": {"scale": 1000, "decimals": 2, "suffix": "M", "signed": False,
                    "unit": "millions of units per year"},
        "note": "Seasonally adjusted annual rate: the month's pace, if it continued all year.",
    },
    {
        "id": "mortgage",
        "section": "Housing",
        "title": "30-year mortgage rate",
        "subtitle": "Average fixed rate on new mortgages, weekly",
        "series": "MORTGAGE30US",
        "params": {"observation_start": "1971-04-02"},
        "freq": "w",
        "display": {"scale": 1, "decimals": 2, "suffix": "%", "signed": False,
                    "unit": "percent"},
        "note": "Freddie Mac's weekly survey of lenders.",
    },
]

# ---------------------------------------------------------------------------
# Companion series: shown only on the detail page (chart.html) as overlays on
# one or more tiles. Same shape as a tile entry, minus section/title/note, plus
#   for      tile ids this companion can be drawn on (same units as that tile)
#   label    legend text on the detail page
#   why      one line shown beside the overlay toggle
# They never appear on the main page. A companion that fails to fetch is
# skipped with a warning; the tiles still publish.
# ---------------------------------------------------------------------------
COMPANIONS = [
    {
        "id": "pce",
        "label": "PCE inflation",
        "for": ["cpi"],
        "series": "PCEPI",
        "params": {"units": "pc1", "observation_start": "1960-01-01"},
        "freq": "m",
        "why": "The Fed's 2% target is set on this index, not the CPI. It usually runs a few tenths lower.",
    },
    {
        "id": "core_pce",
        "label": "Core PCE inflation",
        "for": ["core_cpi"],
        "series": "PCEPILFE",
        "params": {"units": "pc1", "observation_start": "1960-01-01"},
        "freq": "m",
        "why": "The Fed's preferred measure of underlying inflation; its 2% target applies here.",
    },
    {
        "id": "core_cpi_on_cpi",
        "label": "Core CPI (ex food and energy)",
        "for": ["cpi"],
        "series": "CPILFESL",
        "params": {"units": "pc1", "observation_start": "1958-01-01"},
        "freq": "m",
        "why": "When headline and core diverge, food or energy prices are doing the work.",
    },
    {
        "id": "cpi_on_core",
        "label": "Headline CPI (all items)",
        "for": ["core_cpi"],
        "series": "CPIAUCSL",
        "params": {"units": "pc1", "observation_start": "1948-01-01"},
        "freq": "m",
        "why": "The all-items index, including food and energy.",
    },
    {
        "id": "cpi_shelter",
        "label": "Shelter (CPI), change from a year ago",
        "for": ["cpi", "core_cpi"],
        "series": "CUSR0000SAH1",
        "params": {"units": "pc1", "observation_start": "1954-01-01"},
        "freq": "m",
        "why": "About a third of the index: rent, plus what homeowners would pay to rent their own homes. It lags new-lease rents by about a year, so it kept inflation up through 2023 after asking rents had cooled.",
    },
    {
        "id": "cpi_rent",
        "label": "Rent of primary residence (CPI), change from a year ago",
        "for": ["cpi", "core_cpi"],
        "series": "CUSR0000SEHA",
        "params": {"units": "pc1", "observation_start": "1948-01-01"},
        "freq": "m",
        "why": "What renters actually pay, averaged over all leases, not just new ones. The renter's own inflation line.",
    },
    {
        "id": "hires_rate",
        "label": "Hires rate (JOLTS)",
        "for": ["unemployment"],
        "series": "JTSHIR",
        "params": {"observation_start": "2000-12-01"},
        "freq": "m",
        "why": "Hires in the month as a share of employment. Low hiring with low layoffs is the 'frozen' job market: hard to lose a job, hard to find one. Published since December 2000.",
    },
    {
        "id": "quits_rate",
        "label": "Quits rate (JOLTS)",
        "for": ["unemployment"],
        "series": "JTSQUR",
        "params": {"observation_start": "2000-12-01"},
        "freq": "m",
        "why": "Workers leaving voluntarily as a share of employment. People quit when they are confident of the next job; a falling quits rate is confidence draining out.",
    },
    {
        "id": "layoffs_rate",
        "label": "Layoffs and discharges rate (JOLTS)",
        "for": ["unemployment"],
        "series": "JTSLDR",
        "params": {"observation_start": "2000-12-01"},
        "freq": "m",
        "why": "Involuntary separations as a share of employment. The monthly counterpart of weekly jobless claims.",
    },
    {
        "id": "productivity",
        "label": "Labor productivity, change from a year ago",
        "for": ["gdp"],
        "series": "OPHNFB",
        "params": {"units": "pc1", "observation_start": "1947-01-01"},
        "freq": "q",
        "why": "Output per hour worked in the nonfarm business sector. The number where technology shows up, usually years after the investment. Note the 1995\u20132004 run.",
    },
    {
        "id": "u6",
        "label": "U-6 (incl. part-time for economic reasons and marginally attached)",
        "for": ["unemployment"],
        "series": "U6RATE",
        "params": {"observation_start": "1994-01-01"},
        "freq": "m",
        "why": "The broadest official measure of slack. Only published since 1994.",
    },
    {
        "id": "prime_age_epop",
        "label": "Prime-age (25–54) employment-to-population ratio",
        "for": ["unemployment"],
        "series": "LNS12300060",
        "params": {"observation_start": "1948-01-01"},
        "freq": "m",
        "why": "Share of 25–54-year-olds with a job. Sidesteps arguments about who counts as 'looking for work'. Different scale: read it against its own level, not the unemployment rate's.",
    },
    {
        "id": "nrou",
        "label": "CBO estimate of the natural rate of unemployment",
        "for": ["unemployment"],
        "series": "NROU",
        "params": {"observation_start": "1949-01-01"},
        "freq": "q",
        "why": "The Congressional Budget Office's estimate of the rate consistent with stable inflation. An estimate, revised over time.",
    },
    {
        "id": "sahm",
        "label": "Sahm rule indicator",
        "for": ["unemployment"],
        "series": "SAHMREALTIME",
        "params": {"observation_start": "1959-12-01"},
        "freq": "m",
        "why": "3-month average unemployment rate minus its low of the prior 12 months. A reading of 0.5 or more has coincided with the start of every recession since 1970.",
    },
    {
        "id": "household_employment",
        "label": "Household survey employment, change from month before",
        "for": ["payrolls"],
        "series": "CE16OV",
        "params": {"units": "chg", "observation_start": "1948-02-01"},
        "freq": "m",
        "why": "The other monthly jobs count, from the survey of households rather than employers. Noisier, and it counts the self-employed.",
    },
    {
        "id": "continuing_claims",
        "label": "Continuing claims",
        "for": ["claims"],
        "series": "CCSA",
        "params": {"observation_start": "1967-01-07"},
        "freq": "w",
        "why": "People still collecting benefits, not just newly filing. Different scale: it runs several times larger than initial claims.",
    },
    {
        "id": "single_family_starts",
        "label": "Single-family starts",
        "for": ["housing_starts"],
        "series": "HOUST1F",
        "params": {"observation_start": "1959-01-01"},
        "freq": "m",
        "why": "Starts of one-unit homes only. The rest of the total is apartments, which move on a different cycle.",
    },
    {
        "id": "cpi_index",
        "label": "Consumer price index",
        "for": [],
        "series": "CPIAUCSL",
        "params": {"observation_start": "1947-01-01"},
        "freq": "m",
        "why": "Used to compute the price level.",
    },
    {
        "id": "wages",
        "label": "Average hourly earnings, change from a year ago",
        "for": ["cpi", "core_cpi"],
        "series": "AHETPI",
        "params": {"units": "pc1", "observation_start": "1965-01-01"},
        "freq": "m",
        "why": "Pay for production and nonsupervisory workers, about four-fifths of private employment. When this line is above inflation, typical paychecks are gaining ground.",
    },
    {
        "id": "mortgage_monthly",
        "label": "30-year mortgage rate, monthly average",
        "for": [],
        "series": "MORTGAGE30US",
        "params": {"observation_start": "1971-04-01", "frequency": "m", "aggregation_method": "avg"},
        "freq": "m",
        "why": "Used to compute the mortgage spread.",
    },
]

# Derived series, computed here from the fetched data so the page never has to
# align two calendars. op: diff = a - b on matching dates; avg3 = trailing
# 3-period mean of a.
# ---------------------------------------------------------------------------
# Extra series used only for the "in household terms" line on each tile.
# Latest value only; each fails soft and the line it feeds drops that clause.
# ---------------------------------------------------------------------------
EXTRAS = [
    {"id": "median_home_price", "series": "MSPUS", "label": "Median sales price of houses sold",
     "params": {"observation_start": "2015-01-01"}},
    {"id": "card_rate", "series": "TERMCBCCALLNS", "label": "Average credit card interest rate, all accounts",
     "params": {"observation_start": "2015-01-01"}},
    {"id": "tbill_3m", "series": "DTB3", "label": "3-month Treasury bill",
     "params": {"observation_start": "2015-01-01"}},
    {"id": "labor_force", "series": "CLF16OV", "label": "Civilian labor force",
     "params": {"observation_start": "2015-01-01"}},
]


def mortgage_payment(principal, rate_pct, years=30):
    r = rate_pct / 100 / 12
    n = years * 12
    return principal * r / (1 - (1 + r) ** -n)


def household_lines(tiles_out, companions_out, extras):
    """Attach {"text", "sources"} to each tile: the reading restated in household terms.
    Every figure comes from data already fetched; a missing input drops that clause, or the line."""
    T = {t["id"]: t for t in tiles_out}
    C = {c["id"]: c["observations"] for c in companions_out}
    X = extras
    EN = "\u2013"

    def cur(tid): return T[tid]["context"]["current"]["value"]
    def base(tid): return T[tid]["context"]["baseline_2015_19"]
    def year_ago(tid):
        ya = T[tid]["context"].get("year_ago"); return ya["value"] if ya else None
    def latest(cid): return C[cid][-1][1] if C.get(cid) else None
    def extra(eid): return X[eid]["value"] if eid in X else None
    def src(*eids): return [{"series": X[e]["series"], "url": X[e]["url"]} for e in eids if e in X]
    def money(v): return f"${v:,.0f}"
    def cents(v): return f"${v:,.2f}"
    def big(v):
        v = round(v / 1000) * 1000
        return f"{v / 1e6:.1f} million" if v >= 1e6 else f"{v:,.0f}"

    lines = {}
    try:
        lines["payrolls"] = (f"At this month's pace the economy adds about {big(12 * cur('payrolls') * 1000)} jobs a year. "
                             f"The 2015{EN}19 pace was about {big(12 * base('payrolls') * 1000)} a year.", [])
    except Exception: pass
    try:
        lf = extra("labor_force"); k = round(100 / cur("unemployment"))
        n = cur("unemployment") / 100 * lf * 1000 if lf else None
        txt = (f"About {n / 1e6:.1f} million people are looking for work, one in {k} of everyone in the labor force." if n
               else f"One in {k} of everyone in the labor force is looking for work.")
        lines["unemployment"] = (txt, src("labor_force"))
    except Exception: pass
    try:
        c, b = cur("claims"), base("claims"); pct = (c / b - 1) * 100
        lines["claims"] = (f"About {big(c)} people filed for unemployment benefits in an average week, "
                           f"{abs(pct):.0f}% {'below' if pct < 0 else 'above'} the 2015{EN}19 norm of about {big(b)}.", [])
    except Exception: pass
    try:
        pl = latest("price_level")
        lines["cpi"] = (f"What cost $100 a year ago costs {cents(100 * (1 + cur('cpi') / 100))} now."
                        + (f" What cost $100 in 2019 costs {cents(pl)}." if pl else ""), [])
    except Exception: pass
    try:
        lines["core_cpi"] = (f"Leaving out food and energy, what cost $100 a year ago costs {cents(100 * (1 + cur('core_cpi') / 100))} now.", [])
    except Exception: pass
    try:
        g = cur("gdp"); q = ((1 + g / 100) ** 0.25 - 1) * 100
        lines["gdp"] = (f"In the quarter itself the economy grew {q:.1f}%; \u201c{g:.1f}%\u201d is that pace continued for a full year.", [])
    except Exception: pass
    try:
        tb, cc = extra("tbill_3m"), extra("card_rate")
        lines["fed_funds"] = ("Money market funds and online savings follow it within days"
                              + (f" (3-month Treasury bills pay {tb:.1f}%)" if tb is not None else "") + "; credit cards within a statement"
                              + (f" (the average card charges {cc:.1f}%)" if cc is not None else "") + "; mortgages only through the 10-year yield.",
                              src("tbill_3m", "card_rate"))
    except Exception: pass
    try:
        sp = latest("mortgage_minus_ten")
        lines["ten_year"] = (f"Borrowing $1,000 for ten years costs the Treasury {money(10 * cur('ten_year'))} a year at this yield, "
                             f"{money(10 * base('ten_year'))} at the 2015{EN}19 average."
                             + (f" Mortgage rates run about {sp:.1f} points above it." if sp is not None else ""), [])
    except Exception: pass
    try:
        sf = latest("single_family_starts"); tot = cur("housing_starts")
        if sf is not None:
            lines["housing_starts"] = (f"At this pace, about {big(sf * 1000)} houses and {big((tot - sf) * 1000)} apartments get started in a year.", [])
    except Exception: pass
    try:
        mp = extra("median_home_price"); r = cur("mortgage"); ya = year_ago("mortgage"); b = base("mortgage")
        loan = 0.8 * mp if mp else 400000.0
        lead = f"On the median home sold ({money(mp)}), a mortgage with 20% down costs" if mp else "A $400,000 mortgage costs"
        lines["mortgage"] = (f"{lead} {money(mortgage_payment(loan, r))} a month at this rate"
                             + (f", {money(mortgage_payment(loan, ya))} at a year ago's rate" if ya else "")
                             + f", and {money(mortgage_payment(loan, b))} at the 2015{EN}19 average. Principal and interest only.",
                             src("median_home_price"))
    except Exception: pass

    for t in tiles_out:
        if t["id"] in lines:
            text, sources = lines[t["id"]]
            t["household"] = {"text": text, "sources": sources}


DERIVED = [
    {
        "id": "payrolls_3mo",
        "label": "3-month average",
        "for": ["payrolls"],
        "op": "avg3", "a": "payrolls", "freq": "m",
        "why": "Smooths the month-to-month noise; the first print of any month is revised twice.",
    },
    {
        "id": "real_fed_funds",
        "label": "Real Fed funds rate (minus core CPI inflation)",
        "for": ["fed_funds"],
        "op": "diff", "a": "fed_funds", "b": "core_cpi", "freq": "m",
        "why": "The policy rate after inflation. Above zero means money costs something in real terms; below zero, policy is loose whatever the headline rate says.",
    },
    {
        "id": "ten_minus_ff",
        "label": "10-year yield minus Fed funds rate",
        "for": ["ten_year", "fed_funds"],
        "op": "diff", "a": "ten_year", "b": "fed_funds", "freq": "m",
        "why": "The slope of the curve. Below zero (an inverted curve) has preceded every recession since the 1970s, usually by a year or more.",
    },
    {
        "id": "price_level",
        "label": "Price level, 2019 average = 100",
        "for": ["cpi", "core_cpi"],
        "op": "rebase", "a": "cpi_index", "base_start": "2019-01-01", "base_end": "2019-12-31", "freq": "m",
        "why": "The index itself rather than its growth rate: what a 2019 dollar's worth of goods costs now. Inflation is the slope of this line; the line itself does not come back down.",
    },
    {
        "id": "real_wages",
        "label": "Real wage growth (hourly earnings minus CPI inflation)",
        "for": ["cpi", "core_cpi"],
        "op": "diff", "a": "wages", "b": "cpi", "freq": "m",
        "why": "Wage growth after inflation, as a simple difference. Above zero, pay is outrunning prices; below, prices are winning. Compares against headline CPI on both charts.",
    },
    {
        "id": "mortgage_minus_ten",
        "label": "Mortgage rate minus 10-year yield",
        "for": ["mortgage"],
        "op": "diff", "a": "mortgage_monthly", "b": "ten_year", "freq": "m",
        "why": "The spread lenders charge over Treasuries. Normally 1.5–2 points; wider in stress, as in 2022–24.",
    },
]

# ---------------------------------------------------------------------------
# First prints: what each month's figure was when it was first reported, from
# ALFRED (FRED's vintage archive). History never changes, so it is kept in
# data/firstprints.json and only missing months are fetched: one request per
# month, capped per run, so the backfill completes over a few scheduled runs.
#
#   tile       tile id whose current-vintage history this sits beside
#   series     the FRED series; the tile's own transform (units) is applied
#              at the original release date, which reproduces the headline
#              exactly (e.g. the jobs figure as first announced)
# ---------------------------------------------------------------------------
FIRST_PRINTS = [
    {"id": "payrolls_first", "tile": "payrolls", "label": "Jobs added, as first reported",
     "why": "The number announced on jobs day, before the two later revisions. The gap to the current line is the revision."},
    {"id": "gdp_first", "tile": "gdp", "label": "GDP growth, advance estimate",
     "why": "The first of three estimates for each quarter. Revisions of a full point are not unusual."},
    {"id": "unemployment_first", "tile": "unemployment", "label": "Unemployment rate, as first reported",
     "why": "Rarely revised by more than 0.1 point; here mainly to show that."},
    {"id": "cpi_first", "tile": "cpi", "label": "Inflation, as first reported",
     "why": "Seasonal factors are recalculated each February, so past months shift slightly."},
]
FIRST_PRINTS_STORE = os.environ.get("FIRST_PRINTS_STORE", "data/firstprints.json")   # in the repo, committed each run
FIRST_PRINTS_PER_RUN = int(os.environ.get("FIRST_PRINTS_PER_RUN", "400"))
ALFRED_EARLIEST = "1776-07-04"              # FRED's sentinel for "from the first vintage"
ALFRED_LATEST = "9999-12-31"

RECESSIONS_SERIES = "USREC"       # NBER recession months, 1 = recession
RECESSIONS_START = "1939-01-01"

BASELINE_START = date(2015, 1, 1)  # pre-pandemic comparison window
BASELINE_END = date(2019, 12, 31)

# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------
def fred_get(endpoint, params, retries=4):
    q = dict(params)
    q["api_key"] = API_KEY
    q["file_type"] = "json"
    url = f"{API}/{endpoint}?{urllib.parse.urlencode(q)}"
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "economyincontext.org fetcher"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            last_err = f"HTTP {e.code} for {endpoint} {params.get('series_id')}: {body}"
            if e.code in (400, 404):      # bad series or params — retrying won't help
                break
        except Exception as e:           # network blip, timeout
            last_err = f"{type(e).__name__}: {e}"
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(last_err)


def get_observations(series_id, params):
    data = fred_get("series/observations", {"series_id": series_id, **params})
    out = []
    for o in data.get("observations", []):
        v = o.get("value", ".")
        if v in (".", "", None):
            continue
        out.append((o["date"], float(v)))
    if params.get("sort_order") == "desc":
        out.reverse()
    return out


def get_series_info(series_id):
    data = fred_get("series", {"series_id": series_id})
    s = data["seriess"][0]
    return {
        "title": s.get("title"),
        "units": s.get("units"),
        "frequency": s.get("frequency"),
        "seasonal_adjustment": s.get("seasonal_adjustment_short"),
        "last_updated": s.get("last_updated"),
    }


# ---------------------------------------------------------------------------
# Context math
# ---------------------------------------------------------------------------
def to_date(s):
    return datetime.strptime(s, "%Y-%m-%d").date()


def context_for(obs, freq):
    """obs: list of (date_str, value), ascending. Returns the context block."""
    if len(obs) < 3:
        raise RuntimeError("not enough observations")
    values = [v for _, v in obs]
    cur_date, cur = obs[-1]
    prev_date, prev = obs[-2]

    # The reading closest to one calendar year before the current one (date-based,
    # so a missing week or an irregular calendar never shifts the comparison).
    cd = to_date(cur_date)
    try:
        target = cd.replace(year=cd.year - 1)
    except ValueError:                      # Feb 29
        target = cd.replace(year=cd.year - 1, day=28)
    year_ago = min(obs[:-1], key=lambda o: abs((to_date(o[0]) - target).days))
    if abs((to_date(year_ago[0]) - target).days) > 45:
        year_ago = None

    history = values[:-1]                       # everything before the current reading
    below = sum(1 for v in history if v < cur)
    equal = sum(1 for v in history if v == cur)
    pct_below = 100.0 * (below + 0.5 * equal) / len(history)

    base_vals = [v for d, v in obs if BASELINE_START <= to_date(d) <= BASELINE_END]
    baseline = mean(base_vals) if base_vals else None

    lo_i = min(range(len(obs)), key=lambda i: obs[i][1])
    hi_i = max(range(len(obs)), key=lambda i: obs[i][1])

    # Typical range: 5th–95th percentile of the whole history, so one freak
    # month (April 2020) doesn't stretch the range strip to uselessness.
    ranked = sorted(values)
    p5 = ranked[int(0.05 * (len(ranked) - 1))]
    p95 = ranked[int(0.95 * (len(ranked) - 1))]

    # "Highest since …" / "lowest since …": the most recent earlier date whose
    # value was at least (at most) the current one.
    highest_since = None
    lowest_since = None
    for d, v in reversed(obs[:-1]):
        if highest_since is None and v >= cur:
            highest_since = d
        if lowest_since is None and v <= cur:
            lowest_since = d
        if highest_since and lowest_since:
            break

    return {
        "current": {"date": cur_date, "value": cur},
        "previous": {"date": prev_date, "value": prev},
        "year_ago": {"date": year_ago[0], "value": year_ago[1]} if year_ago else None,
        "percentile_below": round(pct_below, 1),
        "since": obs[0][0],
        "baseline_2015_19": round(baseline, 4) if baseline is not None else None,
        "min": {"date": obs[lo_i][0], "value": obs[lo_i][1]},
        "max": {"date": obs[hi_i][0], "value": obs[hi_i][1]},
        "typical_low": round(p5, 4),
        "typical_high": round(p95, 4),
        "highest_since": highest_since,   # None means this is the highest on record
        "lowest_since": lowest_since,     # None means this is the lowest on record
    }


def first_release_dates(series_id, params):
    """{observation_date: date it was first published}, from ALFRED's initial-release view.
    Observations older than the archive itself all carry the archive's first vintage
    date; those are unknowable and dropped."""
    q = {k: v for k, v in params.items() if k not in ("units", "frequency", "aggregation_method")}
    q.update({"output_type": "4", "realtime_start": ALFRED_EARLIEST, "realtime_end": ALFRED_LATEST})
    data = fred_get("series/observations", {"series_id": series_id, **q})
    rel = {}
    for o in data.get("observations", []):
        if o.get("value", ".") in (".", "", None):
            continue
        rel[o["date"]] = o["realtime_start"]
    if not rel:
        return {}
    earliest = min(rel.values())
    return {d: r for d, r in rel.items() if r != earliest}


def value_at_vintage(series_id, params, obs_date, vintage):
    """The transformed value for obs_date as it stood on the vintage date (None if absent)."""
    q = dict(params)
    q.update({"observation_start": obs_date, "observation_end": obs_date,
              "realtime_start": vintage, "realtime_end": vintage})
    data = fred_get("series/observations", {"series_id": series_id, **q})
    for o in data.get("observations", []):
        if o.get("value", ".") not in (".", "", None):
            return float(o["value"])
    return None


def update_first_prints(path, tiles_by_id):
    """Load data/firstprints.json, fetch up to FIRST_PRINTS_PER_RUN missing months, save.
    Returns the list of companion entries to publish. Never raises."""
    store = {}
    try:
        with open(path, encoding="utf-8") as f:
            store = json.load(f).get("series", {})
    except (OSError, ValueError):
        store = {}
    per_series = max(1, FIRST_PRINTS_PER_RUN // max(1, len(FIRST_PRINTS)))
    for fp in FIRST_PRINTS:
        budget = per_series
        t = tiles_by_id.get(fp["tile"])
        if not t:
            continue
        entry = store.setdefault(fp["id"], {"observations": {}, "complete": False})
        have = entry["observations"]
        try:
            rel = first_release_dates(t["series"], t["params"])
            time.sleep(0.4)
        except Exception as e:
            print(f"{fp['id']:16s} release dates failed: {e}", file=sys.stderr, flush=True)
            continue
        missing = sorted((d for d in rel if d not in have), reverse=True)   # newest first: recent revisions matter most
        fetched = 0
        for d in missing:
            if budget <= 0:
                break
            try:
                v = value_at_vintage(t["series"], t["params"], d, rel[d])
                time.sleep(0.5)                 # FRED allows 120 requests a minute
            except Exception as e:
                print(f"{fp['id']:16s} {d}: {e}", file=sys.stderr, flush=True)
                break
            budget -= 1
            fetched += 1
            have[d] = None if v is None else round(v, 3)
        entry["complete"] = all(d in have for d in rel)
        entry["as_of"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        print(f"{fp['id']:16s} first prints: {len(have)} held, {fetched} fetched, "
              f"{len(missing) - fetched} to go", flush=True)
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"note": "First-release values from ALFRED, fetched incrementally. Do not edit.",
                       "series": store}, f, separators=(",", ":"), sort_keys=True)
    except OSError as e:
        print(f"could not write {path}: {e}", file=sys.stderr, flush=True)
    out = []
    for fp in FIRST_PRINTS:
        entry = store.get(fp["id"])
        t = tiles_by_id.get(fp["tile"])
        if not entry or not t:
            continue
        obs = sorted((d, v) for d, v in entry["observations"].items() if v is not None)
        if len(obs) < 3:
            continue
        out.append({
            "id": fp["id"], "label": fp["label"], "for": [fp["tile"]], "freq": t["freq"],
            "why": fp["why"] + ("" if entry.get("complete") else " History is still being backfilled; earlier months arrive over the next few days."),
            "source": {"series": t["series"], "url": f"https://alfred.stlouisfed.org/series?seid={t['series']}",
                       "fred_title": "ALFRED vintages of " + t["series"], "transform": t["params"].get("units", "lin")},
            "observations": [[d, v] for d, v in obs],
        })
    return out


def month_key(d):
    return d[:7]


def derive(spec, by_id):
    """Compute a derived series from already-fetched ones. Returns [(date, value)]."""
    a = by_id.get(spec["a"])
    if not a:
        raise RuntimeError(f"missing input {spec['a']}")
    if spec["op"] == "avg3":
        vals = [v for _, v in a]
        return [(a[i][0], mean(vals[i - 2:i + 1])) for i in range(2, len(a))]
    if spec["op"] == "rebase":
        base = [v for d, v in a if spec["base_start"] <= d <= spec["base_end"]]
        if not base:
            raise RuntimeError("base window empty")
        m = mean(base)
        return [(d, 100.0 * v / m) for d, v in a]
    if spec["op"] == "diff":
        b = by_id.get(spec["b"])
        if not b:
            raise RuntimeError(f"missing input {spec['b']}")
        # Align on year-month: both inputs are monthly (or monthly-aggregated).
        bm = {month_key(d): v for d, v in b}
        out = [(d, v - bm[month_key(d)]) for d, v in a if month_key(d) in bm]
        if len(out) < 3:
            raise RuntimeError("inputs do not overlap")
        return out
    raise RuntimeError(f"unknown op {spec['op']}")


def recession_spans(obs):
    """USREC 0/1 monthly -> [[start, end], ...] where end is the last month in recession."""
    spans, start, last = [], None, None
    for d, v in obs:
        if v >= 0.5 and start is None:
            start = d
        if v < 0.5 and start is not None:
            spans.append([start, last])
            start = None
        last = d
    if start is not None:
        spans.append([start, last])
    return spans


# ---------------------------------------------------------------------------
def main():
    out_path = sys.argv[1] if len(sys.argv) > 1 else "data/series.json"
    if not API_KEY:
        print("FRED_API_KEY is not set", file=sys.stderr)
        sys.exit(2)

    tiles_out = []
    for t in TILES:
        print(f"{t['id']:16s} {t['series']}", flush=True)
        obs = get_observations(t["series"], t["params"])
        time.sleep(0.4)
        info = get_series_info(t["series"])
        time.sleep(0.4)
        ctx = context_for(obs, t["freq"])

        headline = None
        if "latest" in t:
            lt = t["latest"]
            lobs = get_observations(lt["series"], lt["params"])
            time.sleep(0.4)
            if lobs:
                headline = {"series": lt["series"], "date": lobs[-1][0], "value": lobs[-1][1],
                            "url": f"https://fred.stlouisfed.org/series/{lt['series']}"}

        tiles_out.append({
            "id": t["id"],
            "section": t["section"],
            "title": t["title"],
            "subtitle": t["subtitle"],
            "note": t["note"],
            "freq": t["freq"],
            "display": t["display"],
            "source": {
                "series": t["series"],
                "url": f"https://fred.stlouisfed.org/series/{t['series']}",
                "fred_title": info["title"],
                "fred_units": info["units"],
                "frequency": info["frequency"],
                "seasonal_adjustment": info["seasonal_adjustment"],
                "last_updated": info["last_updated"],
                "transform": t["params"].get("units", "lin"),
            },
            "headline": headline,
            "context": ctx,
            "observations": [[d, round(v, 3)] for d, v in obs],
        })

    # Companion series for the detail page. Tolerant: one bad series is skipped.
    today = date.today().isoformat()
    by_id = {t["id"]: t["observations"] for t in tiles_out}
    companions_out = []
    for c in COMPANIONS:
        print(f"{c['id']:16s} {c['series']} (companion)", flush=True)
        try:
            params = dict(c["params"])
            params.setdefault("observation_end", today)   # NROU is projected years ahead
            obs = get_observations(c["series"], params)
            time.sleep(0.4)
            info = get_series_info(c["series"])
            time.sleep(0.4)
            if len(obs) < 3:
                raise RuntimeError("not enough observations")
        except Exception as e:
            print(f"  skipped: {e}", file=sys.stderr, flush=True)
            continue
        by_id[c["id"]] = obs
        companions_out.append({
            "id": c["id"], "label": c["label"], "for": c["for"], "why": c["why"], "freq": c["freq"],
            "source": {
                "series": c["series"],
                "url": f"https://fred.stlouisfed.org/series/{c['series']}",
                "fred_title": info["title"], "fred_units": info["units"],
                "frequency": info["frequency"], "last_updated": info["last_updated"],
                "transform": c["params"].get("units", "lin"),
            },
            "observations": [[d, round(v, 3)] for d, v in obs],
        })

    for dv in DERIVED:
        try:
            obs = derive(dv, by_id)
        except Exception as e:
            print(f"{dv['id']:16s} skipped: {e}", file=sys.stderr, flush=True)
            continue
        print(f"{dv['id']:16s} derived ({len(obs)} obs)", flush=True)
        companions_out.append({
            "id": dv["id"], "label": dv["label"], "for": dv["for"], "why": dv["why"], "freq": dv["freq"],
            "derived": {k: dv[k] for k in ("op", "a", "b") if k in dv},
            "observations": [[d, round(v, 3)] for d, v in obs],
        })

    # First prints from ALFRED, incremental.
    try:
        companions_out.extend(update_first_prints(FIRST_PRINTS_STORE, {t["id"]: t for t in TILES}))
    except Exception as e:                     # belt and braces: never let this stage fail the run
        print(f"first prints skipped: {e}", file=sys.stderr, flush=True)

    # Extra series for the household line on each tile. Latest value only; fail soft.
    extras = {}
    for x in EXTRAS:
        print(f"{x['id']:16s} {x['series']} (extra)", flush=True)
        try:
            obs = get_observations(x["series"], x["params"])
            time.sleep(0.4)
            if not obs:
                raise RuntimeError("no observations")
            extras[x["id"]] = {"series": x["series"], "label": x["label"], "date": obs[-1][0], "value": obs[-1][1],
                               "url": f"https://fred.stlouisfed.org/series/{x['series']}"}
        except Exception as e:
            print(f"  skipped: {e}", file=sys.stderr, flush=True)
    try:
        household_lines(tiles_out, companions_out, extras)
    except Exception as e:
        print(f"household lines skipped: {e}", file=sys.stderr, flush=True)

    print("recessions      USREC", flush=True)
    rec = get_observations(RECESSIONS_SERIES, {"observation_start": RECESSIONS_START})

    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "attribution": "Source: FRED, Federal Reserve Bank of St. Louis. Underlying data from "
                       "the Bureau of Labor Statistics, Bureau of Economic Analysis, Census Bureau, "
                       "Federal Reserve Board, Freddie Mac and the NBER.",
        "baseline": {"label": "2015–19 average", "start": BASELINE_START.isoformat(),
                     "end": BASELINE_END.isoformat()},
        "recessions": recession_spans(rec),
        "extras": extras,
        "tiles": tiles_out,
    }

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"), ensure_ascii=False)
    size = os.path.getsize(out_path)
    print(f"wrote {out_path} ({size/1024:.0f} KB, {len(tiles_out)} indicators)")

    # Companions go in their own file so the main page never downloads them.
    comp_path = os.path.join(os.path.dirname(out_path) or ".", "companions.json")
    with open(comp_path, "w", encoding="utf-8") as f:
        json.dump({"generated": payload["generated"], "companions": companions_out},
                  f, separators=(",", ":"), ensure_ascii=False)
    print(f"wrote {comp_path} ({os.path.getsize(comp_path)/1024:.0f} KB, {len(companions_out)} companion series)")


if __name__ == "__main__":
    main()
