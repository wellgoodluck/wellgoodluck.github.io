#!/usr/bin/env python3
"""Generates data/overlays.json for economyincontext.org. Hand-compiled; edit
here (or the JSON directly), re-run, commit."""
import json, sys

D, R = "D", "R"

# ---- Presidency: start = inauguration (or succession). ---------------------
presidents = [
    ("1929-03-04", "Hoover", R), ("1933-03-04", "F. Roosevelt", D), ("1945-04-12", "Truman", D),
    ("1953-01-20", "Eisenhower", R), ("1961-01-20", "Kennedy", D), ("1963-11-22", "Johnson", D),
    ("1969-01-20", "Nixon", R), ("1974-08-09", "Ford", R), ("1977-01-20", "Carter", D),
    ("1981-01-20", "Reagan", R), ("1989-01-20", "G.H.W. Bush", R), ("1993-01-20", "Clinton", D),
    ("2001-01-20", "G.W. Bush", R), ("2009-01-20", "Obama", D), ("2017-01-20", "Trump", R),
    ("2021-01-20", "Biden", D), ("2025-01-20", "Trump", R),
]

# ---- Congress: start = seating (Mar 4 before 1935, Jan 3 after). -----------
# Senate majority (which party organized the chamber).
senate = [
    ("1933-03-04", D), ("1947-01-03", R), ("1949-01-03", D), ("1953-01-03", R), ("1955-01-03", D),
    ("1981-01-03", R), ("1987-01-03", D), ("1995-01-03", R),
    ("2001-01-03", D),   # 50–50, Vice President Gore's tie-break for 17 days
    ("2001-01-20", R),   # 50–50, Vice President Cheney's tie-break
    ("2001-06-06", D),   # Sen. Jeffords (VT) leaves the Republican conference
    ("2003-01-03", R), ("2007-01-03", D), ("2015-01-03", R),
    ("2021-01-03", R),   # Georgia's two senators not yet seated
    ("2021-01-20", D),   # 50–50, Vice President Harris's tie-break
    ("2025-01-03", R),
]
house = [
    ("1933-03-04", D), ("1947-01-03", R), ("1949-01-03", D), ("1953-01-03", R), ("1955-01-03", D),
    ("1995-01-03", R), ("2007-01-03", D), ("2011-01-03", R), ("2019-01-03", D), ("2023-01-03", R),
]

def segments(starts, end=None):
    out = []
    for i, s in enumerate(starts):
        nxt = starts[i + 1][0] if i + 1 < len(starts) else end
        seg = {"start": s[0], "end": nxt}
        if len(s) == 3: seg["label"], seg["party"] = s[1], s[2]
        else: seg["party"] = s[1]
        out.append(seg)
    return out

# ---- Fed chairs -------------------------------------------------------------
fed_chairs = [
    ("1934-11-15", "Eccles"), ("1948-04-15", "McCabe"), ("1951-04-02", "Martin"), ("1970-02-01", "Burns"),
    ("1978-03-08", "Miller"), ("1979-08-06", "Volcker"), ("1987-08-11", "Greenspan"), ("2006-02-01", "Bernanke"),
    ("2014-02-03", "Yellen"), ("2018-02-05", "Powell"), ("2026-05-22", "Warsh"),
]
fed_chair_segments = []
for i, (s, n) in enumerate(fed_chairs):
    fed_chair_segments.append({"start": s, "end": fed_chairs[i + 1][0] if i + 1 < len(fed_chairs) else None, "label": n})
# gaps between chairs are short (weeks); the lane simply runs each tenure to the next start.

# ---- Wars -------------------------------------------------------------------
wars = [
    {"start": "1941-12-08", "end": "1945-09-02", "label": "World War II", "note": "Declaration of war to the Japanese surrender."},
    {"start": "1950-06-27", "end": "1953-07-27", "label": "Korea", "note": "U.S. forces committed under a UN resolution; never declared or authorized by Congress. Ends at the armistice."},
    {"start": "1964-08-07", "end": "1973-03-29", "label": "Vietnam", "note": "Gulf of Tonkin Resolution to the withdrawal of the last U.S. combat troops."},
    {"start": "1991-01-12", "end": "1991-02-28", "label": "Gulf War", "note": "Congressional authorization to the ceasefire."},
    {"start": "2001-09-18", "end": "2021-08-30", "label": "Afghanistan", "note": "2001 authorization to the completion of the withdrawal."},
    {"start": "2002-10-16", "end": "2011-12-18", "label": "Iraq", "note": "2002 authorization (combat began March 2003) to the departure of the last U.S. troops."},
]

def flatten(segments):
    """Split overlapping periods into non-overlapping segments; where two overlap, the label joins both.
    Afghanistan (2001-21) and Iraq (2002-11) otherwise draw on top of each other and the label is clipped."""
    edges = sorted({d for sg in segments for d in (sg["start"], sg["end"])})
    out = []
    for a, b in zip(edges, edges[1:]):
        active = [sg for sg in segments if sg["start"] <= a and sg["end"] >= b]
        if not active:
            continue
        label = " & ".join(sg["label"] for sg in active)
        note = " ".join(f"{sg['label']}: {sg['note']}" for sg in active if sg.get("note")) if len(active) > 1 else active[0].get("note", "")
        if out and out[-1]["label"] == label and out[-1]["end"] == a:
            out[-1]["end"] = b
        else:
            out.append({"start": a, "end": b, "label": label, **({"note": note} if note else {})})
    return out


wars = flatten(wars)

# ---- Fed balance sheet ---------------------------------------------------------
qe = [
    {"start": "2008-11-25", "end": "2010-03-31", "label": "QE1", "kind": "expand"},
    {"start": "2010-11-03", "end": "2011-06-30", "label": "QE2", "kind": "expand"},
    {"start": "2012-09-13", "end": "2014-10-29", "label": "QE3", "kind": "expand", "note": "Purchases tapered from December 2013."},
    {"start": "2017-10-01", "end": "2019-08-01", "label": "Runoff", "kind": "shrink"},
    {"start": "2020-03-15", "end": "2022-03-09", "label": "Pandemic QE", "kind": "expand"},
    {"start": "2022-06-01", "end": "2025-12-01", "label": "Runoff", "kind": "shrink"},
]

# ---- Fed rate cycles ------------------------------------------------------------
# Rule: a cycle runs from the first change in the Fed funds target in one direction
# to the last change before a move the other way, and must contain at least two
# moves. A cycle still under way is shown from its first move. Before 1988 the
# Fed did not announce a target and adjusted it in frequent small steps, so those
# years are left blank rather than guessed.
fed_cycles = [
    {"start": "1988-03-30", "end": "1989-05-17", "label": "Hikes", "kind": "tighten", "note": "6.50% to 9.81%"},
    {"start": "1989-06-06", "end": "1992-09-04", "label": "Cuts", "kind": "ease", "note": "9.81% to 3.00%"},
    {"start": "1994-02-04", "end": "1995-02-01", "label": "Hikes", "kind": "tighten", "note": "3.00% to 6.00%"},
    {"start": "1995-07-06", "end": "1996-01-31", "label": "Cuts", "kind": "ease", "note": "6.00% to 5.25%"},
    {"start": "1998-09-29", "end": "1998-11-17", "label": "Cuts", "kind": "ease", "note": "5.50% to 4.75%, after the LTCM collapse"},
    {"start": "1999-06-30", "end": "2000-05-16", "label": "Hikes", "kind": "tighten", "note": "4.75% to 6.50%"},
    {"start": "2001-01-03", "end": "2003-06-25", "label": "Cuts", "kind": "ease", "note": "6.50% to 1.00%"},
    {"start": "2004-06-30", "end": "2006-06-29", "label": "Hikes", "kind": "tighten", "note": "1.00% to 5.25%, a quarter point at 17 straight meetings"},
    {"start": "2007-09-18", "end": "2008-12-16", "label": "Cuts", "kind": "ease", "note": "5.25% to 0–0.25%"},
    {"start": "2015-12-16", "end": "2018-12-19", "label": "Hikes", "kind": "tighten", "note": "0–0.25% to 2.25–2.50%"},
    {"start": "2019-07-31", "end": "2020-03-15", "label": "Cuts", "kind": "ease", "note": "2.25–2.50% to 0–0.25%"},
    {"start": "2022-03-16", "end": "2023-07-26", "label": "Hikes", "kind": "tighten", "note": "0–0.25% to 5.25–5.50%, the fastest since the early 1980s"},
    {"start": "2024-09-18", "end": "2025-12-10", "label": "Cuts", "kind": "ease", "note": "5.25–5.50% to 3.50–3.75%"},
    {"start": "2026-09-16", "end": None, "label": "Hikes", "kind": "tighten", "note": "3.50–3.75% to 3.75–4.00%; one move so far"},
]

# ---- Events -------------------------------------------------------------------
RULE = ("An event is listed if it visibly moved at least one indicator on this site within three months, "
        "or committed federal money or changed federal policy on a scale that shows up in GDP investment, "
        "household income or an indicator here over the following years. Nothing is listed because it fits a story. "
        "Dates are when the thing happened or was signed, not when its effects showed up.")

shocks = [
    ("1973-10-17", "Oil embargo", "OPEC embargo begins; oil prices quadruple over the following months."),
    ("1979-01-16", "Second oil shock", "The Shah leaves Iran; oil output collapses and prices more than double."),
    ("1985-09-22", "Plaza Accord", "Five governments agree to push the dollar down."),
    ("1987-10-19", "Black Monday", "Stocks fall 22% in a day."),
    ("2000-03-10", "Dot-com peak", "The Nasdaq's high; it loses three-quarters of its value over the next two years."),
    ("2001-09-11", "September 11 attacks", ""),
    ("1990-08-02", "Iraq invades Kuwait", "Oil doubles within two months; the recession is dated from July."),
    ("2005-08-29", "Hurricane Katrina", "Jobless claims and energy prices jump in the weeks after."),
    ("2008-03-16", "Bear Stearns rescue", ""),
    ("2008-09-15", "Lehman Brothers fails", "The largest bankruptcy in U.S. history; credit markets seize."),
    ("2013-05-22", "Taper tantrum", "Bond yields jump after the Fed signals the end of QE3 purchases."),
    ("2020-03-13", "COVID national emergency", "Declared March 13; the WHO had called it a pandemic on the 11th."),
    ("2022-02-24", "Russia invades Ukraine", "Oil passes $120 and U.S. gasoline tops $5 by June; wheat and fertilizer prices jump."),
    ("2023-03-10", "Silicon Valley Bank fails", "Second-largest bank failure in U.S. history at the time."),
    ("2026-02-28", "U.S. and Israel strike Iran", "Iran closes the Strait of Hormuz to most shipping within days; gasoline is up a third over the following months. No congressional authorization, so not shown on the war lane."),
]
fiscal = [
    ("1986-10-22", "Tax Reform Act of 1986", "Lowers rates, broadens the base."),
    ("2001-06-07", "2001 tax cut (EGTRRA)", ""),
    ("2003-05-28", "2003 tax cut (JGTRRA)", ""),
    ("2008-10-03", "TARP", "$700 billion bank rescue signed."),
    ("2009-02-17", "Recovery Act (ARRA)", "$787 billion stimulus signed."),
    ("2013-03-01", "Sequestration", "Across-the-board federal spending cuts begin."),
    ("2017-12-22", "Tax Cuts and Jobs Act", ""),
    ("2020-03-27", "CARES Act", "$2.2 trillion pandemic relief signed."),
    ("2020-12-27", "Second pandemic relief bill", "$900 billion, including $600 payments, in the year-end appropriations act."),
    ("2021-03-11", "American Rescue Plan", "$1.9 trillion pandemic relief signed."),
    ("2021-11-15", "Infrastructure Investment and Jobs Act", "$1.2 trillion over several years for roads, transit, broadband, water and the grid."),
    ("2022-08-09", "CHIPS and Science Act", "$52 billion in grants and a 25% tax credit for semiconductor plants."),
    ("2022-08-16", "Inflation Reduction Act", "Energy and manufacturing tax credits, drug-price negotiation, a corporate minimum tax."),
    ("2025-07-04", "One Big Beautiful Bill Act", "Extends the 2017 tax cuts and changes spending programs."),
]
monetary = [
    ("1979-10-06", "Volcker shock", "The Fed shifts to targeting bank reserves; rates spike to break inflation."),
    ("2008-12-16", "Fed cuts to zero", ""),
    ("2015-12-16", "First hike after seven years at zero", ""),
    ("2020-03-15", "Fed cuts to zero", "Emergency Sunday action."),
    ("2022-03-16", "Rate hikes begin", "First of 11 increases over 16 months."),
    ("2024-09-18", "Rate cuts begin", ""),
    ("2026-09-16", "First hike since 2023", "Target range raised to 3¾–4%."),
]
trade = [
    ("1994-01-01", "NAFTA takes effect", ""),
    ("2001-12-11", "China joins the WTO", ""),
    ("2018-03-08", "Steel and aluminum tariffs", "Section 232 tariffs; broader China tariffs follow in July."),
    ("2025-04-02", "Broad tariffs announced", "'Liberation Day' tariffs on most trading partners."),
    ("2026-02-20", "Supreme Court strikes down IEEPA tariffs", "Replacement tariffs follow under other statutes."),
]
shutdowns = [
    ("1995-12-16", "Shutdown, 21 days", "Through January 6, 1996."),
    ("2013-10-01", "Shutdown, 16 days", "Through October 17, 2013."),
    ("2018-12-22", "Shutdown, 35 days", "Through January 25, 2019. Partial."),
    ("2025-10-01", "Shutdown, 43 days", "Through November 12, 2025. The longest on record; October's jobs and CPI reports were delayed or skipped."),
]
min_wage = [  # effective date, new federal minimum
    ("1938-10-24", 0.25), ("1939-10-24", 0.30), ("1945-10-24", 0.40), ("1950-01-25", 0.75), ("1956-03-01", 1.00),
    ("1961-09-03", 1.15), ("1963-09-03", 1.25), ("1967-02-01", 1.40), ("1968-02-01", 1.60), ("1974-05-01", 2.00),
    ("1975-01-01", 2.10), ("1976-01-01", 2.30), ("1978-01-01", 2.65), ("1979-01-01", 2.90), ("1980-01-01", 3.10),
    ("1981-01-01", 3.35), ("1990-04-01", 3.80), ("1991-04-01", 4.25), ("1996-10-01", 4.75), ("1997-09-01", 5.15),
    ("2007-07-24", 5.85), ("2008-07-24", 6.55), ("2009-07-24", 7.25),
]

def items(lst):
    return [{"date": d, "label": l, **({"note": n} if n else {})} for d, l, n in sorted(lst)]

POLITICAL_NOTE = ("Control is shown as of inauguration (January 20) and the seating of each Congress (January 3). "
                  "Policy acts with a lag, often a year or more, and shocks do not follow the election calendar.")

overlays = [
    # ---- Reference lines ---------------------------------------------------
    {"id": "fed_target", "type": "line", "group": "Reference lines", "label": "Fed's 2% inflation target",
     "value": 2, "applies_to": ["cpi", "core_cpi"],
     "note": "The target is set on PCE inflation, which usually runs a few tenths below the CPI shown here. Turn on the PCE companion to see the index the target actually applies to.",
     "source": {"label": "Federal Reserve", "url": "https://www.federalreserve.gov/monetarypolicy/files/FOMC_LongerRunGoals.pdf"}},
    {"id": "fomc_longrun_ffr", "type": "line", "group": "Reference lines", "label": "FOMC longer-run Fed funds estimate (3.2%)",
     "value": 3.2, "applies_to": ["fed_funds"], "as_of": "September 2026",
     "note": "Median of FOMC participants' estimates of the rate consistent with full employment and 2% inflation, from the September 2026 projections. An estimate, revised quarterly.",
     "source": {"label": "FOMC Summary of Economic Projections", "url": "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260916.htm"}},
    {"id": "fomc_longrun_unrate", "type": "line", "group": "Reference lines", "label": "FOMC longer-run unemployment estimate (4.2%)",
     "value": 4.2, "applies_to": ["unemployment"], "as_of": "September 2026",
     "note": "Median FOMC estimate of the unemployment rate consistent with stable inflation, September 2026 projections. Compare the CBO's estimate under companion series.",
     "source": {"label": "FOMC Summary of Economic Projections", "url": "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260916.htm"}},
    {"id": "sahm_threshold", "type": "line", "group": "Reference lines", "label": "Sahm rule threshold (0.5)",
     "value": 0.5, "applies_to": ["unemployment"], "requires": "sahm",
     "note": "Applies to the Sahm indicator, not the unemployment rate itself. Shown only when that companion is on."},
    {"id": "baseline", "type": "stat", "stat": "baseline_2015_19", "group": "Reference lines", "label": "2015–19 average",
     "applies_to": "all", "note": "The last five full years before the pandemic. A stand-in for recent normal, not a target."},
    {"id": "median", "type": "stat", "stat": "median", "group": "Reference lines", "label": "Median since records began",
     "applies_to": "all", "note": "Half of all readings are above this line, half below."},
    # ---- Eras ----------------------------------------------------------------
    {"id": "president", "type": "era", "group": "Eras", "lane": "Presidency", "label": "Party of the president",
     "applies_to": "all", "political": True, "note": POLITICAL_NOTE, "segments": segments(presidents),
     "source": {"label": "The White House", "url": "https://www.whitehouse.gov/about-the-white-house/presidents/"}},
    {"id": "senate", "type": "era", "group": "Eras", "lane": "Senate", "label": "Senate majority",
     "applies_to": "all", "political": True, "note": POLITICAL_NOTE + " The Senate changed hands three times within the 2001–03 Congress; see the lane.",
     "segments": segments(senate),
     "source": {"label": "U.S. Senate, Party Division", "url": "https://www.senate.gov/history/partydiv.htm"}},
    {"id": "house", "type": "era", "group": "Eras", "lane": "House", "label": "House majority",
     "applies_to": "all", "political": True, "note": POLITICAL_NOTE, "segments": segments(house),
     "source": {"label": "U.S. House, Party Divisions", "url": "https://history.house.gov/Institution/Party-Divisions/Party-Divisions/"}},
    {"id": "unified", "type": "era", "group": "Eras", "lane": "Government", "label": "Unified or divided government",
     "applies_to": "all", "political": True, "derived_from": ["president", "senate", "house"],
     "note": POLITICAL_NOTE + " Unified means one party holds the presidency and both chambers."},
    {"id": "fed_chair", "type": "era", "group": "Eras", "lane": "Fed chair", "label": "Federal Reserve chair",
     "applies_to": "all", "note": "Monetary policy is set by a 12-member committee, not the chair alone, and its effects take a year or more to show.",
     "segments": fed_chair_segments,
     "source": {"label": "Federal Reserve Board", "url": "https://www.federalreserve.gov/aboutthefed/bios/board/boardmembership.htm"}},
    {"id": "fed_balance_sheet", "type": "era", "group": "Eras", "lane": "Fed balance sheet", "label": "Fed bond-buying (QE) and runoff",
     "applies_to": ["fed_funds", "ten_year", "mortgage", "cpi", "core_cpi"],
     "note": "Periods when the Fed was expanding its holdings of Treasuries and mortgage bonds (QE) or letting them shrink. Dates are the announced start and end of net purchases or runoff.",
     "segments": qe,
     "source": {"label": "Federal Reserve Board, Policy Tools", "url": "https://www.federalreserve.gov/monetarypolicy/bst.htm"}},
    {"id": "fed_cycles", "type": "era", "group": "Eras", "lane": "Fed cycle", "label": "Fed rate hikes and cuts",
     "applies_to": ["fed_funds", "ten_year", "mortgage", "cpi", "core_cpi", "housing_starts", "unemployment", "payrolls", "gdp"],
     "note": "From the first change in the Fed funds target in one direction to the last, two or more moves. Before 1988 the Fed did not announce a target and moved it in frequent small steps; those years are left blank.",
     "segments": fed_cycles,
     "source": {"label": "Federal Reserve Board, Open Market Operations", "url": "https://www.federalreserve.gov/monetarypolicy/openmarket.htm"}},
    {"id": "wars", "type": "era", "group": "Eras", "lane": "At war", "label": "U.S. at war",
     "applies_to": "all",
     "note": "Rule: declared wars and conflicts Congress authorized, from the authorization to the end of U.S. combat, plus Korea, fought under a UN resolution. Conflicts without an authorization (Kosovo, Libya, the 2026 strikes on Iran) are not shown here; those that moved an indicator are under Shocks and crises.",
     "segments": wars,
     "source": {"label": "Congressional Research Service, Declarations of War and Authorizations", "url": "https://crsreports.congress.gov/product/pdf/RL/RL31133"}},
    # ---- Events --------------------------------------------------------------
    {"id": "ev_shocks", "type": "events", "group": "Events", "label": "Shocks and crises", "applies_to": "all", "note": RULE, "items": items(shocks)},
    {"id": "ev_fiscal", "type": "events", "group": "Events", "label": "Major tax and spending laws", "applies_to": "all", "note": "Date signed. " + RULE, "items": items(fiscal)},
    {"id": "ev_monetary", "type": "events", "group": "Events", "label": "Fed turning points", "applies_to": ["fed_funds", "ten_year", "mortgage", "cpi", "core_cpi", "housing_starts"], "note": RULE, "items": items(monetary)},
    {"id": "ev_trade", "type": "events", "group": "Events", "label": "Trade policy", "applies_to": "all", "note": RULE, "items": items(trade)},
    {"id": "ev_shutdowns", "type": "events", "group": "Events", "label": "Government shutdowns (2 weeks or longer)", "applies_to": "all",
     "note": "Start dates. Shorter funding lapses, of which there have been several, are not shown.", "items": items(shutdowns)},
    {"id": "ev_min_wage", "type": "events", "group": "Events", "label": "Federal minimum wage increases", "applies_to": ["payrolls", "unemployment", "claims", "cpi", "core_cpi"],
     "note": "Effective dates of each increase in the federal minimum. Many states set higher minimums, so the federal rate has bound less and less of the workforce since the 1980s.",
     "items": [{"date": d, "label": "Minimum wage to $%.2f" % v} for d, v in min_wage],
     "source": {"label": "U.S. Department of Labor", "url": "https://www.dol.gov/agencies/whd/minimum-wage/history/chart"}},
]

out = {
    "version": "2026-10-28b",
    "maintenance": "Party lanes need a two-line edit every other January after a new Congress is seated (next: January 2027). Fed chair, FOMC estimates and events are edited as they happen.",
    "political_note": POLITICAL_NOTE,
    "overlays": overlays,
}
path = sys.argv[1] if len(sys.argv) > 1 else "data/overlays.json"
with open(path, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
    f.write("\n")
print("wrote", path, len(overlays), "overlays")
