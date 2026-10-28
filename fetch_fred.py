#!/usr/bin/env python3
"""
Fetch the Economy in Context indicator set from FRED and write data/series.json.

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
        "tiles": tiles_out,
    }

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, separators=(",", ":"), ensure_ascii=False)
    size = os.path.getsize(out_path)
    print(f"wrote {out_path} ({size/1024:.0f} KB, {len(tiles_out)} indicators)")


if __name__ == "__main__":
    main()
