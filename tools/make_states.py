#!/usr/bin/env python3
"""Generates assets/states.json for economyincontext.org: each state's resident
population (annual, thousands, from the Census Bureau via FRED), the three
components of change (births minus deaths, net international migration, net
domestic migration) from the Census Bureau's latest vintage of state estimates,
and which states each state's movers came from and went to (the American
Community Survey state-to-state migration flows).
Read by /tools/state-population.html (assets/states.js).

Not run by the workflows: the data is annual. Rerun when the Census Bureau
releases a new vintage (usually winter; Vintage 2025 came January 27, 2026),
then ship the new assets/states.json. Each vintage revises the whole series back
to the 2020 census and supersedes the old one, so replace, never merge.

With network access (run from a machine that can reach census.gov and
fred.stlouisfed.org):
    python3 tools/make_states.py

Without (the usual case in a Claude workspace, where those hosts are blocked):
fetch the two inputs through the built-in browser and save them, then
    python3 tools/make_states.py --pop pop_raw.json --comp comp_raw.json --flows flows_raw.json
Input formats, as the browser extraction writes them:
  pop_raw.json   {"CA": {"first": 1900, "vals": [1490, ...]}, ...}   thousands,
                 one value a year, from FRED fredgraph.csv?id=CAPOP etc.
                 (fredgraph.csv serves at most 12 series a request: batch by 10.)
  comp_raw.json  {"California": ["06", pop2020..pop2025, births2021..2025,
                 deaths2021..2025, natural2021..2025, intl2021..2025,
                 dom2021..2025], ...} from NST-EST2025-ALLDATA.csv.
  flows_raw.json {"names": [52 names: the 50 states and DC alphabetically, then
                 "Puerto Rico"], "E": [[...]], "M": [[...]]} with E[to][from] the
                 estimate and M[to][from] its 90% margin of error, null for the
                 diagonal ('X') and for cells the Census Bureau suppresses ('N'),
                 from the ACS state-to-state migration flows table (FLOWS_XLSX).
When a new vintage lands, update VINTAGE, CENSUS_CSV and YEARS below. The flows
are a separate, survey-based product released each fall-to-winter for the year
before (the 2024 table came January 21, 2026): update FLOWS_YEAR and FLOWS_XLSX
when the next one appears; they need not move with the vintage."""
import json
import os
import sys
import urllib.request

VINTAGE = "Vintage 2025, released January 27, 2026"
CENSUS_CSV = ("https://www2.census.gov/programs-surveys/popest/datasets/"
              "2020-2025/state/totals/NST-EST2025-ALLDATA.csv")
YEARS = [2021, 2022, 2023, 2024, 2025]      # component years this vintage carries whole
EST_YEARS = [2020, 2021, 2022, 2023, 2024, 2025]
FREDGRAPH = "https://fred.stlouisfed.org/graph/fredgraph.csv?id="
FLOWS_YEAR = 2024
FLOWS_RELEASED = "January 21, 2026"
FLOWS_XLSX = ("https://www2.census.gov/programs-surveys/demo/tables/geographic-mobility/"
              "2024/state-to-state-migration/State_to_State_Migration_Table_2024_T13.xlsx")
TOP = 5                                     # partners shown each way

NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California",
    "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware", "DC": "District of Columbia",
    "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
    "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan",
    "MN": "Minnesota", "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire", "NJ": "New Jersey",
    "NM": "New Mexico", "NY": "New York", "NC": "North Carolina", "ND": "North Dakota",
    "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee",
    "TX": "Texas", "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington",
    "WV": "West Virginia", "WI": "Wisconsin", "WY": "Wyoming",
}


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as r:
        return r.read().decode("utf-8")


def pop_from_fred():
    """{"CA": {"first": 1900, "vals": [...]}, ...} from fredgraph.csv, 10 ids a request."""
    out = {}
    abs_ = sorted(NAMES)
    for i in range(0, len(abs_), 10):
        ids = ",".join(ab + "POP" for ab in abs_[i:i + 10])
        lines = fetch(FREDGRAPH + ids).strip().split("\n")
        hdr = lines[0].split(",")
        for col in range(1, len(hdr)):
            ab = hdr[col].replace("POP", "").strip()
            vals, first = [], None
            for line in lines[1:]:
                c = line.split(",")
                v = c[col] if col < len(c) else "."
                if v in (".", ""):
                    if first is not None:
                        vals.append(None)
                    continue
                if first is None:
                    first = int(c[0][:4])
                vals.append(round(float(v)))
            while vals and vals[-1] is None:
                vals.pop()
            out[ab] = {"first": first, "vals": vals}
    return out


def comp_from_census():
    """{name: [fips, pop2020..2025, births.., deaths.., natural.., intl.., dom..]}"""
    lines = fetch(CENSUS_CSV).strip().split("\n")
    hdr = lines[0].split(",")
    idx = {h: i for i, h in enumerate(hdr)}
    out = {}
    for line in lines[1:]:
        c = line.split(",")
        if c[idx["SUMLEV"]] not in ("040", "010"):
            continue
        rec = [c[idx["STATE"]]]
        rec += [int(c[idx["POPESTIMATE%d" % y]]) for y in EST_YEARS]
        for field in ("BIRTHS", "DEATHS", "NATURALCHG", "INTERNATIONALMIG", "DOMESTICMIG"):
            rec += [int(c[idx["%s%d" % (field, y)]]) for y in YEARS]
        out[c[idx["NAME"]]] = rec
    return out


def flows_from_census():
    """The flows table is long-format: column A current residence, B residence a
    year earlier, C estimate, D margin of error, one row a pair."""
    import io
    try:
        import openpyxl
    except ImportError:
        sys.exit("states: the flows table is an .xlsx; pip install openpyxl, or pass --flows")
    with urllib.request.urlopen(FLOWS_XLSX, timeout=60) as r:
        wb = openpyxl.load_workbook(io.BytesIO(r.read()), read_only=True, data_only=True)
    return flows_from_rows(wb.worksheets[0].iter_rows(values_only=True))


def flows_from_rows(rows):
    names = [NAMES[k] for k in sorted(NAMES, key=lambda k: NAMES[k])] + ["Puerto Rico"]
    at = {n: i for i, n in enumerate(names)}
    E = [[None] * len(names) for _ in names]
    M = [[None] * len(names) for _ in names]

    def num(v):
        if v is None or str(v).strip() in ("X", "N", ""):
            return None
        return int(str(v).replace(",", ""))
    for row in rows:
        if not row or len(row) < 4:
            continue
        to, fr = (str(row[0] or "").strip(), str(row[1] or "").strip())
        if to in at and fr in at:           # skips "U.S. Island Areas" and "Foreign country"
            E[at[to]][at[fr]], M[at[to]][at[fr]] = num(row[2]), num(row[3])
    return {"names": names, "E": E, "M": M}


def build_flows(fl):
    """For each state: the TOP states that sent it the most people, the TOP it sent the
    most to, and the partners with its largest net gain and net loss that clear the
    margin of error. Each row is [partner, in, in_moe, out, out_moe]; null = suppressed."""
    problems = []
    code = {v: k for k, v in NAMES.items()}
    code["Puerto Rico"] = "PR"
    names, E, M = fl["names"], fl["E"], fl["M"]
    n = len(names)
    if sorted(names) != sorted(list(NAMES.values()) + ["Puerto Rico"]):
        problems.append("flows: names are not the 50 states, DC and Puerto Rico")
        return None, problems
    if len(E) != n or any(len(r) != n for r in E) or len(M) != n or any(len(r) != n for r in M):
        problems.append("flows: grid is not %dx%d" % (n, n))
        return None, problems
    for i in range(n):
        if E[i][i] is not None:
            problems.append("flows: %s to itself is not blank" % names[i])
        for j in range(n):
            if (E[i][j] is None) != (M[i][j] is None):
                problems.append("flows: %s from %s has an estimate or a margin, not both" % (names[i], names[j]))
            if E[i][j] is not None and (E[i][j] < 0 or M[i][j] < 0):
                problems.append("flows: negative value, %s from %s" % (names[i], names[j]))
    if problems:
        return None, problems

    def sig(r):                             # net clears the margin of the difference (90%)
        if r[1] is None or r[3] is None:
            return False
        return abs(r[1] - r[3]) > (r[2] ** 2 + r[4] ** 2) ** 0.5
    out = {}
    for x in range(n):
        ab = code[names[x]]
        if ab == "PR":
            continue                        # a partner, not a pick: the tool covers the states and DC
        rows = [[code[names[y]], E[x][y], M[x][y], E[y][x], M[y][x]] for y in range(n) if y != x]
        top_in = sorted([r for r in rows if r[1] is not None], key=lambda r: (-r[1], r[0]))[:TOP]
        top_out = sorted([r for r in rows if r[3] is not None], key=lambda r: (-r[3], r[0]))[:TOP]
        sigs = [r for r in rows if sig(r)]
        gains = sorted([r for r in sigs if r[1] > r[3]], key=lambda r: (r[3] - r[1], r[0]))[:2]
        losses = sorted([r for r in sigs if r[1] < r[3]], key=lambda r: (r[1] - r[3], r[0]))[:2]
        out[ab] = {"in": top_in, "out": top_out, "gain": gains, "loss": losses}
    block = {
        "year": FLOWS_YEAR, "released": FLOWS_RELEASED, "source": FLOWS_XLSX,
        "note": ("American Community Survey %d 1-year state-to-state migration flows: people 1 year and over "
                 "living in a state at the survey who lived in another a year earlier. Rows are [partner, moved "
                 "in from it, margin, moved out to it, margin]; margins are 90%%; null where the Census Bureau "
                 "suppresses the cell (too few sample cases). gain and loss: the two largest nets either way "
                 "whose net clears the margin of the difference, sqrt(m1^2 + m2^2), largest first (so the tool "
                 "can say when the top two are too close to call)." % FLOWS_YEAR),
        "names": {"PR": "Puerto Rico"},
        "states": out,
    }
    return block, problems


def build(pop, comp):
    ny = len(YEARS)

    def slot(rec, k):                      # k-th block of ny values after fips + 6 estimates
        return rec[7 + k * ny: 7 + (k + 1) * ny]

    states, problems = {}, []
    for ab in sorted(NAMES):
        name = NAMES[ab]
        p, c = pop.get(ab), comp.get(name)
        if not p or not c:
            problems.append("%s: missing input" % ab)
            continue
        est = {("y%d" % y): c[1 + i] for i, y in enumerate(EST_YEARS)}
        births, deaths, natural, intl, dom = (slot(c, k) for k in range(5))
        # FRED's series is the same vintage in thousands: the overlap must agree.
        last_year = p["first"] + len(p["vals"]) - 1
        for i, y in enumerate(EST_YEARS):
            j = y - p["first"]
            if 0 <= j < len(p["vals"]) and p["vals"][j] is not None:
                if abs(p["vals"][j] * 1000 - est["y%d" % y]) > 600:
                    problems.append("%s %d: FRED %s thousand vs census %s" % (ab, y, p["vals"][j], est["y%d" % y]))
        if last_year != YEARS[-1]:
            problems.append("%s: FRED series ends %d, not %d (stale vintage?)" % (ab, last_year, YEARS[-1]))
        # components + residual = change; the residual should stay small
        for i, y in enumerate(YEARS):
            change = est["y%d" % y] - est["y%d" % (y - 1)]
            resid = change - (natural[i] + intl[i] + dom[i])
            if abs(resid) > 20000:
                problems.append("%s %d: residual %d" % (ab, y, resid))
        if [a - b for a, b in zip(births, deaths)] != natural:
            problems.append("%s: births - deaths != natural change" % ab)
        states[ab] = {"name": name, "first": p["first"], "pop": p["vals"], "est": est,
                      "births": births, "deaths": deaths, "natural": natural,
                      "intl": intl, "dom": dom}
    us = comp["United States"]
    us_births, us_deaths, us_natural, us_intl, us_dom = (slot(us, k) for k in range(5))
    data = {
        "generated": None,                  # filled below
        "vintage": VINTAGE,
        "note": ("Population: Census Bureau resident population via FRED (<ST>POP), thousands, one value a year "
                 "(July 1 estimates; decennial years bridge the census count). Components: Census Bureau "
                 "NST-EST2025-ALLDATA.csv; each year runs July 1 to June 30 and is revised with every vintage. "
                 "Components need not sum to the change in the estimate (a small residual remains). Do not edit: "
                 "rerun tools/make_states.py with the new vintage instead."),
        "comp_years": YEARS,
        "us": {"est": {"y2020": us[1], "y%d" % YEARS[-1]: us[1 + len(EST_YEARS) - 1]},
               "natural": us_natural, "intl": us_intl, "dom": us_dom},
        "states": states,
    }
    return data, problems


def main():
    args = dict(zip(sys.argv[1::2], sys.argv[2::2]))
    if "--pop" in args:
        with open(args["--pop"]) as f:
            pop = json.load(f)
    else:
        pop = pop_from_fred()
    if "--comp" in args:
        with open(args["--comp"]) as f:
            comp = json.load(f)
    else:
        comp = comp_from_census()
    if "--flows" in args:
        with open(args["--flows"]) as f:
            fl = json.load(f)
    else:
        fl = flows_from_census()
    data, problems = build(pop, comp)
    flows, fp = build_flows(fl)
    problems += fp
    data["flows"] = flows
    for p in problems:
        print("states: WARNING " + p)
    if problems:
        sys.exit("states: %d problem(s); nothing written" % len(problems))
    import datetime
    data["generated"] = datetime.date.today().isoformat()
    # assets/, not data/: the workflows copy assets/ wholesale but name the data/ files one by one,
    # so a new data/ file would need a workflow change to publish. Move it when a workflow batch happens.
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "states.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"), ensure_ascii=False)
        f.write("\n")
    n = len(data["states"])
    print("states: wrote %s (%d states + DC, components %d-%d, %s; flows %d)"
          % (out, n - 1, YEARS[0], YEARS[-1], VINTAGE.split(",")[0], FLOWS_YEAR))


if __name__ == "__main__":
    main()
