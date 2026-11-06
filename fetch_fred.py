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
from datetime import date, datetime, timedelta, timezone
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
#            chart — clipped points are marked and labeled, never hidden;
#            adjust "cpi" (prices of things) bases the typical range and the
#            "higher than" sentence on the inflation-adjusted history, in dollars
#            of the latest reading's month, because a raw price only trends up.
#            The headline, comparisons and chart stay as charged.
#            year "calendar": a yearly (freq a) tile whose years are calendar
#            years, labeled "2025"; without it yearly readings read "FY 2025".
#            wide True: when the tile's section has an odd number of tiles, this
#            tile spans both columns at the top of the section on desktop
#            (index.html). Ignored when the count is even. An odd section with
#            no flag widens its last tile.
#   agency   who publishes the data, short form, from the series' Source on FRED; the
#            charts' credit line reads "Data: <agency> via FRED · economyincontext.org"
# ---------------------------------------------------------------------------
TILES = [
    # ---- Jobs -------------------------------------------------------------
    {
        "id": "payrolls",
        "agency": "BLS",
        "section": "Jobs",
        "title": "Jobs added",
        "subtitle": "Nonfarm payrolls, change from the month before",
        "series": "PAYEMS",
        "params": {"units": "chg", "observation_start": "1939-02-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 0, "suffix": "K", "signed": True,
                    "unit": "thousands of jobs", "clip": [-1500, 1500], "wide": True},
        "note": "Seasonally adjusted. The first two prints for any month are revised.",
    },
    {
        "id": "unemployment",
        "agency": "BLS",
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
        # A computed tile (Nov 3): job openings divided by the number of unemployed, same month. Computed tiles
        # are built before the companions are fetched, so the "series_ratio" op fetches its two inputs itself.
        "id": "openings_ratio",
        "agency": "BLS",
        "section": "Jobs",
        "title": "Openings per job seeker",
        "subtitle": "Unfilled jobs for each person looking for work, monthly",
        "series": "JTSJOL",
        "params": {},
        "freq": "m",
        "computed": {"op": "series_ratio", "a": "JTSJOL", "b": "UNEMPLOY", "start": "2000-12-01"},
        "display": {"scale": 1, "decimals": 2, "suffix": "", "signed": False,
                    "unit": "job openings per unemployed person"},
        "note": "Job openings from the Bureau of Labor Statistics' survey of employers (JOLTS, JTSJOL), divided by the number of unemployed people from its household survey (UNEMPLOY), for the same month; both seasonally adjusted. Openings are counted since December 2000 and come out about a month after the unemployment figures, so the latest month here trails the jobs report. A reading of 1.0 means one open job for every person looking. The hires, quits and layoffs rates are on the chart page.",
    },
    {
        "id": "claims",
        "agency": "Labor Department",
        "section": "Jobs",
        "title": "New jobless claims",
        "subtitle": "First-time unemployment filings, 4-week average",
        "series": "IC4WSA",
        "params": {"observation_start": "1967-01-01"},
        "freq": "w",
        "display": {"scale": 1000, "decimals": 0, "suffix": "K", "signed": False,
                    "unit": "claims per week", "clip": [0, 700000]},
        "note": "Seasonally adjusted. Weekly, so it moves before the monthly jobs numbers do.",
    },
    {
        "id": "pay",
        "agency": "BLS",
        "section": "Jobs",
        "title": "Hourly pay",
        "subtitle": "Average hourly earnings, change from a year ago",
        "series": "AHETPI",
        "params": {"units": "pc1", "observation_start": "1965-01-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": False,
                    "unit": "percent, year over year"},
        "note": "Production and nonsupervisory workers, about four-fifths of private employment; seasonally adjusted. An average, so it jumps when low-paid jobs disappear, as in 2020.",
    },
    {
        "id": "health_jobs",
        "agency": "BLS",
        "section": "Jobs",
        "title": "Health care jobs",
        "subtitle": "Jobs added in health care over the past 12 months",
        "series": "CES6562000101",
        "params": {"units": "ch1", "observation_start": "1990-01-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 0, "suffix": "K", "signed": True,
                    "unit": "thousands of jobs, change from a year earlier", "clip": [-600, 800]},
        "note": "Hospitals, doctors' and dentists' offices, outpatient centers, home health care, and nursing and residential care; seasonally adjusted. Social assistance, such as child care, is not included. Revised with the rest of the payroll numbers.",
    },
    {
        "id": "newspaper_jobs",
        "agency": "BLS",
        "section": "Jobs",
        "title": "Newspaper jobs",
        "subtitle": "People employed by newspaper publishers, yearly",
        "series": "IPUJN511110W200000000",
        "params": {"observation_start": "1987-01-01"},
        "freq": "a",
        "display": {"scale": 1, "decimals": 0, "suffix": "K", "signed": False,
                    "unit": "thousands of jobs", "year": "calendar"},
        "note": "Everyone working for newspaper publishers, from reporters to printing, ad sales and delivery, including the self-employed; a person with jobs at two papers counts twice. Online-only outlets were counted in a separate industry until the 2022 industry codes grouped them with publishers of the same kind. From the BLS productivity program; each year posts the following spring. Magazine and broadcasting jobs are on the chart page.",
    },
    # ---- Prices -----------------------------------------------------------
    {
        "id": "cpi",
        "agency": "BLS",
        "section": "Prices",
        "title": "Inflation",
        "subtitle": "Consumer prices, change from a year ago",
        "series": "CPIAUCSL",
        "params": {"units": "pc1", "observation_start": "1948-01-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": False,
                    "unit": "percent, year over year", "wide": True},
        "note": "All items, all urban consumers (CPI-U), seasonally adjusted.",
    },
    {
        "id": "core_cpi",
        "agency": "BLS",
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
    {
        "id": "rent",
        "agency": "BLS",
        "section": "Prices",
        "title": "Rent",
        "subtitle": "Rent of primary residence (CPI), change from a year ago",
        "series": "CUSR0000SEHA",
        "params": {"units": "pc1", "observation_start": "1948-01-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": False,
                    "unit": "percent, year over year"},
        "note": "What renters pay across all leases, not just new ones, so it trails asking rents by about a year. Seasonally adjusted.",
    },
    # ---- Growth & rates ---------------------------------------------------
    {
        "id": "gdp",
        "agency": "BEA",
        "section": "Growth & rates",
        "title": "Economic growth",
        "subtitle": "Real GDP, quarterly change at an annual rate",
        "series": "A191RL1Q225SBEA",
        "params": {"observation_start": "1947-04-01"},
        "freq": "q",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True,
                    "unit": "percent, annualized", "clip": [-15, 15], "wide": True},
        "note": "Inflation-adjusted. Each quarter is revised twice after its first estimate.",
    },
    {
        "id": "fed_funds",
        "agency": "Federal Reserve Board",
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
        "agency": "Federal Reserve Board",
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
        "agency": "Census Bureau and HUD",
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
        "agency": "Freddie Mac",
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
    {
        # Nov 6: FHFA's purchase-only index (public domain on FRED), not Case-Shiller, which S&P does not allow
        # to be republished without permission (see the About page).
        "id": "home_prices",
        "agency": "FHFA",
        "section": "Housing",
        "title": "Home prices",
        "subtitle": "Prices of single-family houses, change from a year ago",
        "series": "HPIPONM226S",
        "params": {"units": "pc1", "observation_start": "1991-01-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": False,
                    "unit": "percent, year over year"},
        "note": "The Federal Housing Finance Agency's purchase-only index: each house is compared with its own earlier sale, so the figure tracks prices rather than which homes happened to sell. Covers houses bought with loans that Fannie Mae or Freddie Mac acquired, so jumbo-loan, cash and most FHA purchases are not counted. Seasonally adjusted.",
    },
    {
        # Nov 6, from a reader's suggestion. No free national foreclosure series is on FRED; this is the
        # longest free national read on missed mortgage payments.
        "id": "mortgage_delinquency",
        "agency": "Federal Reserve Board",
        "section": "Housing",
        "title": "Mortgage delinquency",
        "subtitle": "Share of home loans held by banks that are 30 or more days behind, quarterly",
        "series": "DRSFRMACBS",
        "params": {"observation_start": "1991-01-01"},
        "freq": "q",
        "display": {"scale": 1, "decimals": 2, "suffix": "%", "signed": False,
                    "unit": "percent of loans"},
        "note": "Single-family mortgages on commercial banks' own books, by dollar amount: loans 30 or more days past due plus loans the bank has stopped counting interest on. Loans sold into Fannie Mae, Freddie Mac and Ginnie Mae securities, which include most FHA loans, are not counted, so this is a partial view. Seasonally adjusted; each quarter is published about two months after it ends.",
    },
    # ---- Government and trade ---------------------------------------------
    {
        "id": "deficit",
        "agency": "OMB and the St. Louis Fed",
        "section": "Government and trade",
        "title": "Federal deficit",
        "subtitle": "What Washington borrowed in the fiscal year, as a share of the economy",
        "series": "FYFSGDA188S",
        "params": {"observation_start": "1929-01-01"},
        "freq": "a",
        # FRED publishes this as surplus (+) or deficit (−). It is shown the way it is reported, a deficit as a
        # positive number, so "Federal deficit: 5.8%" reads as it sounds; the rare surplus years fall below zero.
        "flip": True,
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": False,
                    "unit": "percent of GDP", "sense": "deficit-up", "flipped": True},
        "note": "Fiscal years end September 30. Shown as a positive number, the way deficits are reported (FRED lists them as negative); the rare surplus years fall below zero.",
    },
    {
        "id": "debt",
        "agency": "OMB and the St. Louis Fed",
        "section": "Government and trade",
        "title": "Federal debt",
        "subtitle": "Debt held by the public, as a share of the economy",
        "series": "FYGFGDQ188S",
        "params": {"observation_start": "1970-01-01"},
        "freq": "q",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": False,
                    "unit": "percent of GDP", "wide": True},
        "note": "Excludes the debt the government owes its own trust funds. The level, not the yearly change; the deficit is the change.",
    },
    {
        "id": "trade",
        "agency": "Census Bureau and BEA",
        "section": "Government and trade",
        "title": "Trade balance",
        "subtitle": "Goods and services: exports minus imports, monthly; below zero is a deficit",
        "series": "BOPGSTB",
        "params": {"observation_start": "1992-01-01"},
        "freq": "m",
        "display": {"scale": 1000, "decimals": 1, "prefix": "$", "suffix": "B", "signed": True,
                    "unit": "billions of dollars", "clip": [-150000, 20000], "sense": "deficit"},
        "note": "Seasonally adjusted. Negative means the country bought more from abroad than it sold.",
    },
    # ---- What things cost -------------------------------------------------
    # BLS average prices (collected for the CPI) and EIA's weekly pump survey.
    # Not seasonally adjusted. adjust "cpi": see the display notes above.
    {
        "id": "gas",
        "agency": "EIA",
        "section": "What things cost",
        "title": "Gasoline",
        "subtitle": "Regular, U.S. average pump price per gallon, weekly",
        "series": "GASREGW",
        "params": {"observation_start": "1990-08-20"},
        "freq": "w",
        "display": {"scale": 1, "decimals": 2, "prefix": "$", "signed": False,
                    "unit": "dollars per gallon", "adjust": "cpi", "wide": True},
        "note": "Not seasonally adjusted. EIA's weekly survey of retail stations, all formulations. The chart shows the price as charged; the range and the comparison above it are adjusted for inflation.",
    },
    {
        "id": "electricity",
        "agency": "BLS",
        "section": "What things cost",
        "title": "Electricity",
        "subtitle": "U.S. average price per kilowatt-hour, the unit on a power bill, monthly",
        "series": "APU000072610",
        "params": {"observation_start": "1978-11-01"},
        "freq": "m",
        "display": {"scale": 0.01, "decimals": 1, "suffix": "¢", "signed": False,
                    "unit": "cents per kilowatt-hour", "csv_unit": "dollars per kilowatt-hour", "adjust": "cpi"},
        "note": "Not seasonally adjusted. BLS average price across U.S. cities, collected for the CPI. The chart shows the price as charged; the range and the comparison above it are adjusted for inflation.",
    },
    {
        # A computed tile (Nov 2): built from the two tiles above after they are fetched, not from a FRED
        # series of its own. "series" names the FRED page its source line links to; "computed" says how.
        "id": "drive_cost",
        "agency": "EIA and BLS",
        "section": "What things cost",
        "title": "Electric mile vs. gas mile",
        "subtitle": "What a mile costs on electricity as a share of what it costs on gasoline, at 3.5 miles per kWh and 27.1 mpg, monthly",
        "series": "APU000072610",
        "params": {},
        "freq": "m",
        "computed": {"op": "per_mile_ratio", "gas": "gas", "electricity": "electricity", "mpg": 27.1, "mi_per_kwh": 3.5},
        "display": {"scale": 1, "decimals": 0, "suffix": "%", "signed": False,
                    "unit": "percent of the cost of a mile on gasoline"},
        "note": "Computed from the almanac's two fuel prices: the BLS average electricity price (APU000072610) divided by 3.5 miles per kilowatt-hour, against the EIA average gasoline price (GASREGW, averaged over each month) divided by 27.1 miles per gallon, the efficiency figures the Electric Vehicles article uses for a typical EV and a typical gas car. A reading of 35% means a mile on electricity at home costs about a third of a mile on gasoline; public fast charging costs two to three times the home rate. A ratio of two prices needs no inflation adjustment. Both lines are on the chart page, in cents per mile.",
    },
    {
        "id": "natural_gas",
        "agency": "BLS",
        "section": "What things cost",
        "title": "Natural gas",
        "subtitle": "Piped utility gas, U.S. average price per therm (about 100 cubic feet), monthly",
        "series": "APU000072620",
        "params": {"observation_start": "1978-11-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 2, "prefix": "$", "signed": False,
                    "unit": "dollars per therm", "adjust": "cpi"},
        "note": "Not seasonally adjusted. BLS average price across U.S. cities, collected for the CPI; all piped gas, including taxes and the fuel and purchased-gas adjustments on the bill. The chart shows the price as charged; the range and the comparison above it are adjusted for inflation.",
    },
    {
        "id": "eggs",
        "agency": "BLS",
        "section": "What things cost",
        "title": "Eggs",
        "subtitle": "Grade A large, U.S. average price per dozen, monthly",
        "series": "APU0000708111",
        "params": {"observation_start": "1980-01-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 2, "prefix": "$", "signed": False,
                    "unit": "dollars per dozen", "adjust": "cpi"},
        "note": "Not seasonally adjusted. BLS average price across U.S. cities, collected for the CPI. The chart shows the price as charged; the range and the comparison above it are adjusted for inflation.",
    },
    {
        "id": "milk",
        "agency": "BLS",
        "section": "What things cost",
        "title": "Milk",
        "subtitle": "Whole, U.S. average price per gallon, monthly",
        "series": "APU0000709112",
        "params": {"observation_start": "1995-07-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 2, "prefix": "$", "signed": False,
                    "unit": "dollars per gallon", "adjust": "cpi"},
        "note": "Not seasonally adjusted. BLS average price across U.S. cities, collected for the CPI; whole milk only, since July 1995. The chart shows the price as charged; the range and the comparison above it are adjusted for inflation.",
    },
    {
        "id": "bread",
        "agency": "BLS",
        "section": "What things cost",
        "title": "Bread",
        "subtitle": "White, U.S. average price per pound, monthly",
        "series": "APU0000702111",
        "params": {"observation_start": "1980-01-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 2, "prefix": "$", "signed": False,
                    "unit": "dollars per pound", "adjust": "cpi"},
        "note": "Not seasonally adjusted. BLS average price across U.S. cities, collected for the CPI; packaged white bread of any loaf size, priced per pound. The chart shows the price as charged; the range and the comparison above it are adjusted for inflation.",
    },
    {
        "id": "coffee",
        "agency": "BLS",
        "section": "What things cost",
        "title": "Coffee",
        "subtitle": "Ground roast, U.S. average price per pound, monthly",
        "series": "APU0000717311",
        "params": {"observation_start": "1980-01-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 2, "prefix": "$", "signed": False,
                    "unit": "dollars per pound", "adjust": "cpi"},
        "note": "Not seasonally adjusted. BLS average price across U.S. cities, collected for the CPI. The chart shows the price as charged; the range and the comparison above it are adjusted for inflation.",
    },
    {
        "id": "ground_beef",
        "agency": "BLS",
        "section": "What things cost",
        "title": "Ground beef",
        "subtitle": "100% beef, U.S. average price per pound, monthly",
        "series": "APU0000703112",
        "params": {"observation_start": "1984-01-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 2, "prefix": "$", "signed": False,
                    "unit": "dollars per pound", "adjust": "cpi"},
        "note": "Not seasonally adjusted. BLS average price across U.S. cities, collected for the CPI. Sirloin steak is on the chart page. The chart shows the price as charged; the range and the comparison above it are adjusted for inflation.",
    },
    {
        "id": "chicken",
        "agency": "BLS",
        "section": "What things cost",
        "title": "Whole chicken",
        "subtitle": "Fresh, U.S. average price per pound, monthly",
        "series": "APU0000706111",
        "params": {"observation_start": "1980-01-01"},
        "freq": "m",
        "display": {"scale": 1, "decimals": 2, "prefix": "$", "signed": False,
                    "unit": "dollars per pound", "adjust": "cpi"},
        "note": "Not seasonally adjusted. BLS average price across U.S. cities, collected for the CPI; fresh whole broiler-fryers, priced per pound with bone and skin. Boneless breast is on the chart page. The chart shows the price as charged; the range and the comparison above it are adjusted for inflation.",
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
        "id": "ppi",
        "label": "Producer prices (PPI final demand), change from a year ago",
        "for": ["cpi", "core_cpi"],
        "series": "PPIFIS",
        "params": {"units": "pc1", "observation_start": "2009-11-01"},
        "freq": "m",
        "why": "What domestic producers are paid for goods, services and construction sold to final buyers, seasonally adjusted. Prices from the seller's side: taxes, subsidies and distribution costs can open a gap with the CPI, and part of what it covers, such as exports, government purchases and new equipment, never reaches a store shelf. The index starts in November 2009, so the change from a year earlier starts in November 2010.",
    },
    {
        "id": "cpi_shelter",
        "label": "Shelter (CPI), change from a year ago",
        "for": ["cpi", "core_cpi", "rent"],
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
        "id": "restaurant_prices",
        "label": "Restaurant meals (CPI, food away from home), change from a year ago",
        "for": ["cpi", "core_cpi"],
        "series": "CUSR0000SEFV",
        "params": {"units": "pc1", "observation_start": "1953-01-01"},
        "freq": "m",
        "why": "Meals and snacks bought away from home: full-service and fast-food restaurants, plus food at work, school and vending machines. Seasonally adjusted. By the restaurant industry's own estimate food is only about a third of a restaurant's costs and labor another third, so menu prices follow wages more than grocery prices.",
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
        "why": "3-month average unemployment rate minus its low of the prior 12 months, as first published each month. It reached 0.5 within four months of the start of every recession since 1970, and twice without one: for a month in late 1976, and in 2024.",
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
        "for": ["cpi", "core_cpi", "rent"],
        "series": "AHETPI",
        "params": {"units": "pc1", "observation_start": "1965-01-01"},
        "freq": "m",
        "why": "Pay for production and nonsupervisory workers, about four-fifths of private employment. When this line is above inflation, typical paychecks are gaining ground.",
    },
    {
        "id": "cpi_on_pay",
        "label": "Inflation (CPI, all items)",
        "for": ["pay"],
        "series": "CPIAUCSL",
        "params": {"units": "pc1", "observation_start": "1965-01-01"},
        "freq": "m",
        "why": "Prices, the other half of a paycheck. When this line is above pay growth, an hour of work buys less than it did a year before.",
    },
    {
        "id": "premiums",
        "label": "Health insurance premiums (PPI), change from a year ago",
        "for": ["cpi", "core_cpi", "pay"],
        "series": "PCU524114524114",
        "params": {"units": "pc1", "observation_start": "2002-12-01"},
        "freq": "m",
        "why": "What health insurers charge for the same policies, from the Producer Price Index for health insurance carriers: the whole premium, the employer's share included; plans employers pay for themselves are not covered. Not seasonally adjusted, so most of each year's change shows up in January. It is not the CPI's health insurance index, which tracks what insurers keep after paying claims (adjusted for medical prices) and can fall while premiums rise. The index starts in December 2002, so the change from a year earlier starts in December 2003.",
    },
    {
        "id": "receipts",
        "label": "Federal receipts, share of GDP",
        "for": ["deficit"],
        "series": "FYFRGDA188S",
        "params": {"observation_start": "1929-01-01"},
        "freq": "a",
        "why": "Taxes and other revenue. The deficit is this minus outlays; when people argue about the deficit they are arguing about which of these two lines to move.",
    },
    {
        "id": "outlays",
        "label": "Federal outlays, share of GDP",
        "for": ["deficit"],
        "series": "FYONGDA188S",
        "params": {"observation_start": "1929-01-01"},
        "freq": "a",
        "why": "Spending, including interest on the debt. Compare with receipts.",
    },
    {
        "id": "interest_gdp",
        "label": "Interest on the debt, share of GDP",
        "for": ["debt", "deficit"],
        "series": "FYOIGDA188S",
        "params": {"observation_start": "1940-01-01"},
        "freq": "a",
        "why": "What the debt costs each year. Set by the level of the debt and the interest rate, not by this year's deficit.",
    },
    {
        "id": "gross_debt",
        "label": "Gross federal debt, share of GDP (incl. trust funds)",
        "for": ["debt"],
        "series": "GFDEGDQ188S",
        "params": {"observation_start": "1966-01-01"},
        "freq": "q",
        "why": "The larger figure often quoted. Includes what the government owes its own Social Security and Medicare trust funds.",
    },
    {
        "id": "trade_goods",
        "label": "Goods balance only",
        "for": ["trade"],
        "series": "BOPGTB",
        "params": {"observation_start": "1992-01-01"},
        "freq": "m",
        "why": "Merchandise alone. The U.S. runs a deficit in goods and a surplus in services; the headline is the sum.",
    },
    {
        "id": "trade_services",
        "label": "Services balance only",
        "for": ["trade"],
        "series": "BOPSTB",
        "params": {"observation_start": "1992-01-01"},
        "freq": "m",
        "why": "Software, finance, travel, education, royalties. The part of trade that is usually in surplus.",
    },
    {
        "id": "dollar_index",
        "label": "Dollar index (trade-weighted, broad)",
        "for": ["trade"],
        "series": "DTWEXBGS",
        "params": {"observation_start": "2006-01-01", "frequency": "m", "aggregation_method": "avg"},
        "freq": "m",
        "why": "A stronger dollar makes imports cheaper and exports dearer, and tends to widen the deficit with a lag. Different scale: an index, 2006 = 100.",
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
    {
        "id": "uempmed",
        "label": "Median weeks unemployed",
        "for": ["unemployment"],
        "series": "UEMPMED",
        "params": {"observation_start": "1967-07-01"},
        "freq": "m",
        "why": "How long the typical unemployed person has been looking so far. It rises when jobs are scarce and falls when they are plentiful. Different scale: weeks.",
        "panel": "own", "display": {"scale": 1, "decimals": 1, "suffix": " wks"},
    },
    # Health care and social assistance in the 12 largest metro areas (Census Bureau, Vintage 2025), as change from a year
    # earlier, all in one shared sub-panel on the health care jobs chart (panel "group:hc_metros"), beside the national figure.
    # Miami (8th) has no such series from BLS; Chicago is its core division. Ids stay stable: health_jobs_ie predates the group.
    {
        "id": "hc_metro_us", "label": "United States, all areas", "for": ["health_jobs"],
        "series": "CES6562000001", "params": {"units": "pc1", "observation_start": "1990-01-01"}, "freq": "m",
        "why": "The whole country, seasonally adjusted: health care and social assistance, the same measure as the metro lines, so the fair comparison for them.",
        "group": "Metro areas", "panel": "group:hc_metros", "panel_title": "Health care and social assistance jobs, change from a year earlier",
        "group_note": "The 12 largest metro areas by population (Census Bureau estimates for 2025), each against its own level a year earlier, so areas of any size line up on one scale, beside the same measure for the whole country. Miami (8th) is left out: BLS doesn't publish this series for that metro. Chicago is its core division, the part BLS publishes. Health care and social assistance together, because that is what BLS publishes for metro areas; the tile above counts health care alone. Metro figures aren't seasonally adjusted, arrive about two weeks after the national ones and are revised each March.",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True},
    },
    {
        "id": "hc_metro_nyc", "label": "New York area", "for": ["health_jobs"],
        "series": "SMU36356206562000001", "params": {"units": "pc1", "observation_start": "1990-01-01"}, "freq": "m",
        "why": "The New York–Newark–Jersey City metro area (NY, NJ), 1st by population.",
        "group": "Metro areas", "panel": "group:hc_metros", "panel_title": "Health care and social assistance jobs, change from a year earlier",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True},
    },
    {
        "id": "hc_metro_la", "label": "Los Angeles area", "for": ["health_jobs"],
        "series": "SMU06310806562000001", "params": {"units": "pc1", "observation_start": "1990-01-01"}, "freq": "m",
        "why": "The Los Angeles–Long Beach–Anaheim metro area (CA), 2nd by population.",
        "group": "Metro areas", "panel": "group:hc_metros", "panel_title": "Health care and social assistance jobs, change from a year earlier",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True},
    },
    {
        "id": "hc_metro_chi", "label": "Chicago area (core division)", "for": ["health_jobs"],
        "series": "SMU17169846562000001", "params": {"units": "pc1", "observation_start": "1990-01-01"}, "freq": "m",
        "why": "The Chicago–Naperville–Schaumburg division, the core of the Chicago metro area (3rd by population). BLS doesn't publish this series for the whole metro.",
        "group": "Metro areas", "panel": "group:hc_metros", "panel_title": "Health care and social assistance jobs, change from a year earlier",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True},
    },
    {
        "id": "hc_metro_dfw", "label": "Dallas–Fort Worth area", "for": ["health_jobs"],
        "series": "SMU48191006562000001", "params": {"units": "pc1", "observation_start": "1990-01-01"}, "freq": "m",
        "why": "The Dallas–Fort Worth–Arlington metro area (TX), 4th by population.",
        "group": "Metro areas", "panel": "group:hc_metros", "panel_title": "Health care and social assistance jobs, change from a year earlier",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True},
    },
    {
        "id": "hc_metro_hou", "label": "Houston area", "for": ["health_jobs"],
        "series": "SMU48264206562000001", "params": {"units": "pc1", "observation_start": "1990-01-01"}, "freq": "m",
        "why": "The Houston–Pasadena–The Woodlands metro area (TX), 5th by population.",
        "group": "Metro areas", "panel": "group:hc_metros", "panel_title": "Health care and social assistance jobs, change from a year earlier",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True},
    },
    {
        "id": "hc_metro_atl", "label": "Atlanta area", "for": ["health_jobs"],
        "series": "SMU13120606562000001", "params": {"units": "pc1", "observation_start": "1990-01-01"}, "freq": "m",
        "why": "The Atlanta–Sandy Springs–Roswell metro area (GA), 6th by population.",
        "group": "Metro areas", "panel": "group:hc_metros", "panel_title": "Health care and social assistance jobs, change from a year earlier",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True},
    },
    {
        "id": "hc_metro_dc", "label": "Washington, D.C., area", "for": ["health_jobs"],
        "series": "SMU11479006562000001", "params": {"units": "pc1", "observation_start": "1990-01-01"}, "freq": "m",
        "why": "The Washington–Arlington–Alexandria metro area (DC, VA, MD, WV), 7th by population.",
        "group": "Metro areas", "panel": "group:hc_metros", "panel_title": "Health care and social assistance jobs, change from a year earlier",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True},
    },
    {
        "id": "hc_metro_phl", "label": "Philadelphia area", "for": ["health_jobs"],
        "series": "SMU42379806562000001", "params": {"units": "pc1", "observation_start": "1990-01-01"}, "freq": "m",
        "why": "The Philadelphia–Camden–Wilmington metro area (PA, NJ, DE, MD), 9th by population.",
        "group": "Metro areas", "panel": "group:hc_metros", "panel_title": "Health care and social assistance jobs, change from a year earlier",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True},
    },
    {
        "id": "hc_metro_phx", "label": "Phoenix area", "for": ["health_jobs"],
        "series": "SMU04380606562000001", "params": {"units": "pc1", "observation_start": "1990-01-01"}, "freq": "m",
        "why": "The Phoenix–Mesa–Chandler metro area (AZ), 10th by population.",
        "group": "Metro areas", "panel": "group:hc_metros", "panel_title": "Health care and social assistance jobs, change from a year earlier",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True},
    },
    {
        "id": "hc_metro_bos", "label": "Boston area", "for": ["health_jobs"],
        "series": "SMU25144606562000001", "params": {"units": "pc1", "observation_start": "1990-01-01"}, "freq": "m",
        "why": "The Boston–Cambridge–Newton metro area (MA, NH), 11th by population.",
        "group": "Metro areas", "panel": "group:hc_metros", "panel_title": "Health care and social assistance jobs, change from a year earlier",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True},
    },
    {
        "id": "health_jobs_ie", "label": "Riverside–San Bernardino area", "for": ["health_jobs"],
        "series": "SMU06401406562000001", "params": {"units": "pc1", "observation_start": "1990-01-01"}, "freq": "m",
        "why": "The Riverside–San Bernardino–Ontario metro area (CA), the Inland Empire, 12th by population.",
        "group": "Metro areas", "panel": "group:hc_metros", "panel_title": "Health care and social assistance jobs, change from a year earlier",
        "display": {"scale": 1, "decimals": 1, "suffix": "%", "signed": True},
    },
    {
        "id": "wti",
        "label": "Crude oil (WTI), dollars per barrel",
        "for": [],
        "series": "WTISPLC",
        "params": {"observation_start": "1946-01-01"},
        "freq": "m",
        "why": "Used to compute crude oil in today's dollars.",
    },
    {
        "id": "customs_duties",
        "label": "Customs duties collected",
        "for": [],
        "series": "B235RC1Q027SBEA",
        "params": {"observation_start": "1959-01-01"},
        "freq": "q",
        "why": "Used to compute the effective tariff rate.",
    },
    {
        "id": "goods_imports",
        "label": "Imports of goods",
        "for": [],
        "series": "A255RC1Q027SBEA",
        "params": {"observation_start": "1959-01-01"},
        "freq": "q",
        "why": "Used to compute the effective tariff rate.",
    },
    {
        "id": "gs3m",
        "label": "3-month Treasury yield, monthly average",
        "for": [],
        "series": "GS3M",
        "params": {"observation_start": "1981-09-01"},
        "freq": "m",
        "why": "Used to compute the 10-year minus 3-month spread.",
    },
    # Series read only by the live figures in article text (tools/figures.py), offered on no chart.
    # All tagged Public Domain: Citation Requested on FRED (checked Oct 30, 2026).
    {"id": "pay_level", "label": "Average hourly earnings, production and nonsupervisory workers, dollars",
     "for": [], "series": "AHETPI", "params": {"observation_start": "2018-01-01"}, "freq": "m",
     "why": "Used for pay since 2019 in article text."},
    {"id": "unemployed", "label": "Unemployed people, thousands", "for": [], "series": "UNEMPLOY",
     "params": {"observation_start": "2015-01-01"}, "freq": "m", "why": "Used for the unemployed count in article text."},
    {"id": "openings", "label": "Job openings, thousands (JOLTS)", "for": [], "series": "JTSJOL",
     "params": {"observation_start": "2000-12-01"}, "freq": "m", "why": "Used for openings per unemployed person in article text."},
    {"id": "hires_level", "label": "Hires, thousands (JOLTS)", "for": [], "series": "JTSHIL",
     "params": {"observation_start": "2015-01-01"}, "freq": "m", "why": "Used for the number of hires in article text."},
    {"id": "uempmean", "label": "Average weeks unemployed", "for": [], "series": "UEMPMEAN",
     "params": {"observation_start": "2015-01-01"}, "freq": "m", "why": "Used for search length in article text."},
    {"id": "long_term_share", "label": "Share of the unemployed out of work 27 weeks or more", "for": [], "series": "LNS13025703",
     "params": {"observation_start": "2015-01-01"}, "freq": "m", "why": "Used for long-term unemployment in article text."},
    {"id": "rent_level", "label": "CPI, rent of primary residence, index", "for": [], "series": "CUSR0000SEHA",
     "params": {"observation_start": "2018-01-01"}, "freq": "m", "why": "Used for rent since 2019 in article text."},
    {"id": "home_price_level", "label": "FHFA purchase-only house price index, level", "for": [], "series": "HPIPONM226S",
     "params": {"observation_start": "2018-01-01"}, "freq": "m", "why": "Used for home prices since 2019 on the home prices tile (Nov 6)."},
    {"id": "eci_wages", "label": "Employment Cost Index, private wages and salaries, change from a year ago (not seasonally adjusted)",
     "for": [], "series": "CIU2020000000000I", "params": {"units": "pc1", "observation_start": "2002-01-01"}, "freq": "q",
     "why": "Used for the ECI line on the hourly pay page; not seasonally adjusted, as BLS headlines it."},
    {"id": "fafh_level", "label": "CPI, food away from home, index", "for": [], "series": "CUSR0000SEFV",
     "params": {"observation_start": "2018-01-01"}, "freq": "m", "why": "Used for restaurant prices in article text (Nov 2)."},
    {"id": "restaurant_jobs", "label": "All employees, food services and drinking places, thousands", "for": [],
     "series": "CES7072200001", "params": {"observation_start": "2018-01-01"}, "freq": "m",
     "why": "Used for restaurant employment in article text (Nov 2)."},
    # A second cut of the same item, priced in the same unit, drawn on the tile's own axis (Nov 2).
    {"id": "chicken_breast", "label": "Boneless chicken breast, as charged", "for": ["chicken"],
     "series": "APU0000FF1101", "params": {"observation_start": "2006-01-01"}, "freq": "m",
     "why": "The pricier cut: boneless and skinless, so none of the pound is bone. BLS has priced it since 2006."},
    {"id": "sirloin", "label": "Sirloin steak, as charged", "for": ["ground_beef"],
     "series": "APU0000703613", "params": {"observation_start": "1989-01-01"}, "freq": "m",
     "why": "The upscale cut: boneless USDA Choice sirloin steak. BLS has priced it since 1989."},
    # Other news employers, counted the same way as the newspaper tile (BLS productivity program, yearly,
    # thousands of jobs, self-employed included), so they share its axis.
    {"id": "periodical_jobs", "label": "Magazine and periodical publishers", "for": ["newspaper_jobs"],
     "series": "IPUJN51112W200000000", "params": {"observation_start": "1987-01-01"}, "freq": "a",
     "why": "Everyone employed by magazine, journal and newsletter publishers, counted the same way as the newspaper line. Most periodicals are not news publications."},
    {"id": "broadcast_jobs", "label": "Radio and TV broadcasting", "for": ["newspaper_jobs"],
     "series": "IPUJN5151W200000000", "params": {"observation_start": "1987-01-01"}, "freq": "a",
     "why": "Everyone employed by radio and TV stations and networks, counted the same way as the newspaper line: newsrooms, but also entertainment programming, ad sales and engineering. Cable networks such as CNN are not included."},
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
    {"id": "population", "series": "POPTHM", "label": "U.S. population",
     "params": {"observation_start": "2015-01-01"}},
    {"id": "gross_debt_dollars", "series": "FYGFDPUN", "label": "Federal debt held by the public, dollars",
     "params": {"observation_start": "2015-01-01"}},
    {"id": "nominal_gdp", "series": "GDP", "label": "Nominal GDP, billions, annual rate",
     "params": {"observation_start": "2015-01-01"}},
    # The deficit tile (FYFSGDA188S) divides by calendar-year GDP, so a fiscal year's share of GDP
    # appears only once that calendar year's GDP is complete, about four months after the year
    # closes. The dollar figure arrives in October; the household line reports it in the gap.
    {"id": "deficit_dollars", "series": "FYFSD", "label": "Federal surplus or deficit, millions of dollars, fiscal year",
     "params": {"observation_start": "2015-01-01"}},
    # FOMC Summary of Economic Projections, longer-run medians (quarterly; dated by meeting).
    {"id": "fomc_longrun_ffr", "series": "FEDTARMDLR", "label": "FOMC longer-run Fed funds rate, median",
     "params": {"observation_start": "2012-01-01"}},
    {"id": "fomc_longrun_unrate", "series": "UNRATEMDLR", "label": "FOMC longer-run unemployment rate, median",
     "params": {"observation_start": "2012-01-01"}},
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
        # Pay against prices for the same month; the jobs report usually lands before that month's CPI.
        p, pd = cur("pay"), T["pay"]["context"]["current"]["date"]
        cpi_by_month = {month_key(d): v for d, v in T["cpi"]["observations"]}
        infl = cpi_by_month.get(month_key(pd))
        month = lambda d: datetime.strptime(d, "%Y-%m-%d").strftime("%B")
        if infl is not None:
            lead = f"In {month(pd)} pay was up {p:.1f}% from a year earlier and prices {infl:.1f}%"
        else:
            infl, cd = cur("cpi"), T["cpi"]["context"]["current"]["date"]
            lead = f"Pay in {month(pd)} was up {p:.1f}% from a year earlier; prices, last measured in {month(cd)}, were up {infl:.1f}%"
        real = ((1 + p / 100) / (1 + infl / 100) - 1) * 100
        lines["pay"] = (lead + (f", so an hour of work bought about {abs(real):.1f}% {'more' if real > 0 else 'less'} than a year before."
                                if abs(real) >= 0.05 else ", so an hour of work bought about what it did a year before."),
                        [{"series": "CPIAUCSL", "url": "https://fred.stlouisfed.org/series/CPIAUCSL"}])
    except Exception: pass
    try:
        # Health care's share of all jobs added over the same 12 months. The payrolls tile holds
        # monthly changes, so twelve of them, ending in the same month, sum to the 12-month change.
        h, hd = cur("health_jobs"), T["health_jobs"]["context"]["current"]["date"]
        pay_m = {month_key(d): v for d, v in T["payrolls"]["observations"]}
        def months_back(d, n):
            y, m = int(d[:4]), int(d[5:7])
            out = []
            for _ in range(n):
                out.append(f"{y:04d}-{m:02d}"); m -= 1
                if m == 0: y, m = y - 1, 12
            return out
        def total_12m(d):
            ks = months_back(d, 12)
            return sum(pay_m[k] for k in ks) if all(k in pay_m for k in ks) else None
        p = total_12m(hd)
        jobs = lambda v: f"{abs(round(v * 1000, -2)):,.0f}"
        mon = datetime.strptime(hd, "%Y-%m-%d").strftime("%B")
        if p is not None:
            if h > 0 and p > 0 and h <= p:
                txt = (f"Of the {jobs(p)} jobs the country added in the 12 months to {mon}, "
                       f"health care added {jobs(h)}, or {round(100 * h / p)}%.")
            elif h > 0 and p > 0:
                txt = (f"In the 12 months to {mon}, health care added {jobs(h)} jobs, more than the {jobs(p)} "
                       f"the whole country added, so every other industry together lost {jobs(h - p)}.")
            elif h > 0:
                txt = (f"In the 12 months to {mon}, health care added {jobs(h)} jobs while the country as a whole "
                       + (f"lost {jobs(p)}." if p < 0 else "added none."))
            else:
                txt = (f"In the 12 months to {mon}, health care " + (f"lost {jobs(h)} jobs" if h < 0 else "added no jobs")
                       + (f"; the country as a whole {'added' if p > 0 else 'lost'} {jobs(p)}." if p != 0
                          else "; the country's total was unchanged."))
            # The same share in 2015-19, from the averages of both 12-month changes.
            hb = [v for d, v in T["health_jobs"]["observations"] if "2015-01" <= d[:7] <= "2019-12"]
            pb = [total_12m(d) for d, _ in T["health_jobs"]["observations"] if "2015-01" <= d[:7] <= "2019-12"]
            if hb and pb and None not in pb and mean(pb) > 0:
                txt += f" In 2015{EN}19 its share was about {round(100 * mean(hb) / mean(pb))}%."
            lines["health_jobs"] = (txt, [{"series": "PAYEMS", "url": "https://fred.stlouisfed.org/series/PAYEMS"}])
    except Exception: pass
    try:
        # Newspaper jobs (yearly, thousands): the latest year against 2019 and against the series' peak.
        ob = [(d[:4], v) for d, v in T["newspaper_jobs"]["observations"]]
        yr, v = ob[-1]
        k = lambda x: f"{round(x) * 1000:,}"
        txt = f"In {yr} newspaper publishers employed about {k(v)} people"
        v19 = dict(ob).get("2019")
        if v19 is not None and yr > "2019":
            txt += (", about the same as in 2019." if round(v) == round(v19)
                    else f", {'down' if v < v19 else 'up'} from about {k(v19)} in 2019.")
        else:
            txt += "."
        py, pv = max(ob, key=lambda p: p[1])
        txt += (f" That is the most since {ob[0][0]}." if py == yr
                else f" The most since {ob[0][0]} was about {k(pv)}, in {py}.")
        lines["newspaper_jobs"] = (txt, [])
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
        # A round $1,000 rent, as electricity prices 1,000 kWh: a reference, not a typical rent.
        txt = f"Across all leases, a rent that was $1,000 a month a year ago is about {money(1000 * (1 + cur('rent') / 100))} now."
        rl, pl_ = C.get("rent_level") or [], C.get("pay_level") or []
        r19 = [v for d, v in rl if d.startswith("2019-")]
        p19 = [v for d, v in pl_ if d.startswith("2019-")]
        srcs = []
        if len(r19) == 12 and len(p19) == 12:
            r_up, p_up = (rl[-1][1] / mean(r19) - 1) * 100, (pl_[-1][1] / mean(p19) - 1) * 100
            txt += f" Since 2019 rents are up {r_up:.0f}% and hourly pay {p_up:.0f}%."
            srcs = [{"series": "AHETPI", "url": "https://fred.stlouisfed.org/series/AHETPI"}]
        lines["rent"] = (txt, srcs)
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
    try:
        # A round $400,000 house, as the rent line uses a round $1,000: a reference, not a typical price.
        txt = (f"Comparing each house with its own earlier sale, one that sold for $400,000 a year ago "
               f"would sell for about {money(round(400000 * (1 + cur('home_prices') / 100), -3))} now.")
        hl, pl_ = C.get("home_price_level") or [], C.get("pay_level") or []
        h19 = [v for d, v in hl if d.startswith("2019-")]
        p19 = [v for d, v in pl_ if d.startswith("2019-")]
        srcs = []
        if len(h19) == 12 and len(p19) == 12:
            h_up, p_up = (hl[-1][1] / mean(h19) - 1) * 100, (pl_[-1][1] / mean(p19) - 1) * 100
            txt += f" Since 2019 home prices are up {h_up:.0f}% and hourly pay {p_up:.0f}%."
            srcs = [{"series": "AHETPI", "url": "https://fred.stlouisfed.org/series/AHETPI"}]
        lines["home_prices"] = (txt, srcs)
    except Exception: pass
    try:
        # "1 in N" for the latest quarter, the series' peak and its low, all from the tile's own history.
        ob = T["mortgage_delinquency"]["observations"]
        hi_d, hi_v = max(ob, key=lambda o: o[1]); lo_d, lo_v = min(ob, key=lambda o: o[1])
        lines["mortgage_delinquency"] = (
            f"About 1 in {round(100 / cur('mortgage_delinquency'))} home loans on banks' books is at least a month behind. "
            f"At the peak, in {hi_d[:4]}, it was about 1 in {round(100 / hi_v)}; at the low, in {lo_d[:4]}, about 1 in {round(100 / lo_v)}.", [])
    except Exception: pass

    try:
        rc, ol = latest("receipts"), latest("outlays")
        d_ = cur("deficit")
        # the deficit tile is shown positive (see TILES): above zero is a deficit
        txt = (f"Of every dollar the government spent, about {round(d_ / ol * 100)}\u00a2 was borrowed." if ol and d_ > 0
               else f"The government took in more than it spent, a surplus of {-d_:.1f}% of GDP." if d_ <= 0 else "")
        if txt and d_ > 0:
            txt += f" The deficit was {d_:.1f}% of GDP; the 2015{EN}19 average was {base('deficit'):.1f}%."
        if txt:
            srcs = []
            # A newer fiscal year in dollars (FYFSD dates are fiscal-year ends) than the tile's share of GDP
            dd, fy_tile = X.get("deficit_dollars"), int(T["deficit"]["context"]["current"]["date"][:4])
            if dd and int(dd["date"][:4]) > fy_tile:
                fy, v, pv = int(dd["date"][:4]), dd["value"], dd.get("previous")
                def tril(m): return f"${abs(m) / 1e6:.2f} trillion"
                word = "deficit" if v < 0 else "surplus"
                txt += f" Fiscal {fy}'s {word} is already reported: {tril(v)}"
                if pv and int(pv["date"][:4]) == fy - 1 and v < 0 and pv["value"] < 0:
                    txt += f", {'up' if abs(v) > abs(pv['value']) else 'down'} from {tril(pv['value'])} in fiscal {fy - 1}"
                txt += f". As a share of GDP it appears here once full-year {fy} GDP is published, in early {fy + 1}."
                srcs = src("deficit_dollars")
            lines["deficit"] = (txt, srcs)
    except Exception: pass
    try:
        ig = latest("interest_gdp"); pop = extra("population"); gd = extra("gross_debt_dollars"); ng = extra("nominal_gdp")
        parts = []
        if gd and pop:
            parts.append(f"The debt held by the public comes to about {money(gd * 1e6 / (pop * 1000))} per person.")
        if ig is not None:
            parts.append(f"Interest on it costs about {ig:.1f}% of GDP a year" + (f", roughly {money(ig / 100 * ng * 1e9 / (pop * 1000))} per person." if pop and ng else "."))
        if parts:
            lines["debt"] = (" ".join(parts), src("gross_debt_dollars", "population", "nominal_gdp"))
    except Exception: pass
    try:
        tr = cur("trade"); pop = extra("population")
        if pop:
            lines["trade"] = (f"At this month's pace the country buys about {money(-tr * 1e6 * 12 / (pop * 1000))} more from abroad per person each year than it sells.", src("population"))
    except Exception: pass

    # What things cost: the price now, a year ago, and the 2019 average, which is also
    # restated in today's dollars (the price level, 2019 = 100, for the latest reading's month).
    def price_level_for(d):
        pl = C.get("price_level") or []
        by_month = {month_key(x): v for x, v in pl}
        return by_month.get(month_key(d), pl[-1][1] if pl else None)
    def average_in(tid, year):
        vals = [v for d, v in T[tid]["observations"] if d.startswith(f"{year}-")]
        return mean(vals) if vals else None
    def price(v): return cents(v) if v < 20 else money(v)
    cpi_src = [{"series": "CPIAUCSL", "url": "https://fred.stlouisfed.org/series/CPIAUCSL"}]
    price_lines = {   # tile id: (opening, how the 2019 figure is named, quantity)
        "gas": ("Filling a 15-gallon tank costs", "a tank", 15),
        "electricity": ("At this price, 1,000 kilowatt-hours cost", "the same 1,000 kilowatt-hours", 1000),
        "eggs": ("A dozen costs", "a dozen", 1),
        "milk": ("A gallon costs", "a gallon", 1),
        "ground_beef": ("A pound costs", "a pound", 1),
        "coffee": ("A pound costs", "a pound", 1),
        "natural_gas": ("At this price, 50 therms cost", "the same 50 therms", 50),
        "bread": ("A pound costs", "a pound", 1),
        "chicken": ("A pound costs", "a pound", 1),
    }
    for tid, (opening, noun, qty) in price_lines.items():
        if tid not in T:
            continue
        try:
            now = qty * cur(tid)
            txt = f"{opening} {price(now)}"
            ya = year_ago(tid)
            if ya:
                ya *= qty
                txt += (f", up from {price(ya)} a year ago" if now > ya * 1.005 else
                        f", down from {price(ya)} a year ago" if now < ya * 0.995 else ", about the same as a year ago")
            txt += "."
            y19 = average_in(tid, 2019)
            if y19:
                y19 *= qty
                pl = price_level_for(T[tid]["context"]["current"]["date"])
                txt += f" In 2019 {noun} averaged {price(y19)}" + (f", about {price(y19 * pl / 100)} in today's dollars." if pl else ".")
            lines[tid] = (txt, cpi_src)
        except Exception: pass
    # A second cut, from its companion, when it is priced for the same month as the tile (Nov 2).
    other_cut = {   # tile id: (companion id, series, how the line names it)
        "chicken": ("chicken_breast", "APU0000FF1101", "Boneless breast runs"),
        "ground_beef": ("sirloin", "APU0000703613", "Sirloin steak runs"),
    }
    for tid, (cid, series, words) in other_cut.items():
        if tid not in lines or not C.get(cid):
            continue
        try:
            d, v = C[cid][-1]
            if month_key(d) != month_key(T[tid]["context"]["current"]["date"]):
                continue
            text, sources = lines[tid]
            lines[tid] = (text + f" {words} {price(v)} a pound.",
                          sources + [{"series": series, "url": f"https://fred.stlouisfed.org/series/{series}"}])
        except Exception: pass

    # Electric mile vs. gas mile (Nov 2): the year's fuel bill three ways, at the two tiles' latest prices.
    # Rounded to $10 as the Electric Vehicles article's worked example is; the hybrid is a round 50-mpg reference.
    try:
        g, e = T["gas"]["context"]["current"], T["electricity"]["context"]["current"]
        miles, mpg, mi_per_kwh, hybrid_mpg = 15000, 27.1, 3.5, 50
        gd, ed = to_date(g["date"]), to_date(e["date"])
        ten = lambda v: money(round(v / 10) * 10)
        lines["drive_cost"] = (
            f"At gasoline's {cents(g['value'])} a gallon (the week ending {gd.strftime('%B')} {gd.day}) and {e['value'] * 100:.1f}¢ "
            f"per kilowatt-hour ({ed.strftime('%B')}), driving 15,000 miles a year costs about {ten(miles / mpg * g['value'])} on gasoline "
            f"at 27.1 mpg, about {ten(miles / hybrid_mpg * g['value'])} in a 50-mpg hybrid, and about {ten(miles / mi_per_kwh * e['value'])} "
            f"on electricity at home at 3.5 miles per kilowatt-hour.",
            [{"series": "GASREGW", "url": "https://fred.stlouisfed.org/series/GASREGW"}])
    except Exception: pass

    # Openings per job seeker (Nov 3): the two counts behind the ratio, the ratio per 10 job seekers, the same month
    # a year earlier (exactly that month; none when it is missing, as October 2025 is), and the 2019 average.
    try:
        t = T["openings_ratio"]
        d = t["context"]["current"]["date"]
        r = t["context"]["current"]["value"]
        o, u = dict(C["openings"]).get(d), dict(C["unemployed"]).get(d)
        per10 = lambda v: int(v * 10 + 0.5)
        obs = dict((x, v) for x, v in t["observations"])
        ya = obs.get(f"{int(d[:4]) - 1}{d[4:]}")
        r19 = [v for x, v in t["observations"] if x.startswith("2019")]
        n, m = per10(r), (per10(ya) if ya is not None else None)
        month = f"{to_date(d).strftime('%B')} {d[:4]}"
        mil = lambda v: f"{v / 1000:.1f} million"
        if n == 10:
            count = "about one opening for every job seeker"
            unit = " for every 10"
        else:
            count = f"about {n} openings for every 10 job seekers"
            unit = ""
        if m is None:
            change = ""
        elif m == n:
            change = ", the same as a year earlier"
        else:
            change = f", {'up' if n > m else 'down'} from {m}{unit} a year earlier"
        text = f"In {month} there were {mil(o)} open jobs and {mil(u)} people looking for work, {count}{change}."
        if len(r19) == 12:
            text += f" In 2019 there were about {per10(sum(r19) / 12)}{unit}."
        lines["openings_ratio"] = (text, [{"series": "UNEMPLOY", "url": "https://fred.stlouisfed.org/series/UNEMPLOY"}])
    except Exception: pass

    for t in tiles_out:
        if t["id"] in lines:
            text, sources = lines[t["id"]]
            t["household"] = {"text": text, "sources": sources}


# ---- "In short": one plain paragraph per section, from the same figures the tiles show -------------------------
# Templates, not prose: every number is a tile's current reading or its rank in its own history, and the only words
# that are not numbers are the connectives ("but", "and well above"). No adjectives of judgment ("soaring", "healthy").
# A missing input drops its clause; a section with nothing to say gets no paragraph. Shown under each section heading
# on the almanac (data/series.json "summaries").

def rank_words(pct_below, higher_word="higher", lower_word="lower"):
    """"higher than in three-quarters of months", from a percentile, in the fractions people say; None near the middle."""
    p = pct_below
    if p is None: return None
    if 40 <= p <= 60: return "near the middle of its history"
    hi = p >= 50
    share = p if hi else 100 - p
    frac = ("nearly all" if share >= 97 else "nine-tenths" if share >= 88 else "seven-eighths" if share >= 85 else
            "four-fifths" if share >= 78 else "three-quarters" if share >= 70 else "two-thirds" if share >= 63 else "most")
    return f"{higher_word if hi else lower_word} than in {frac}" + ("" if frac == "nearly all" else " of")


def section_summaries(tiles_out):
    T = {t["id"]: t for t in tiles_out}
    EN = "\u2013"
    def ctx(tid):
        t = T[tid]; return t.get("context_real") if t["display"].get("adjust") and t.get("context_real") else t["context"]
    def cur(tid): return ctx(tid)["current"]["value"]
    def since(tid): return str(ctx(tid)["since"])[:4]
    def noun(tid): return {"a": "years", "q": "quarters", "w": "weeks", "d": "days"}.get(T[tid]["freq"], "months")
    def rank(tid, hi="higher", lo="lower"):
        r = rank_words(ctx(tid)["percentile_below"], hi, lo)
        if r is None or r.startswith("near"): return r
        return f"{r} {noun(tid)}" if r.endswith("nearly all") else f"{r} {noun(tid)} since {since(tid)}"
    def record(tid):
        c = ctx(tid); return "the highest on record" if c.get("highest_since") is None else "the lowest on record" if c.get("lowest_since") is None else None
    def lowest_since_year(tid):
        c = ctx(tid); v = c.get("lowest_since"); return (str(v)[:4] if v and int(str(v)[:4]) < int(since(tid)) + 200 and int(str(v)[:4]) <= int(c["current"]["date"][:4]) - 1 else None)
    def highest_since_year(tid):
        c = ctx(tid); v = c.get("highest_since"); return (str(v)[:4] if v and int(str(v)[:4]) <= int(c["current"]["date"][:4]) - 1 else None)
    def month(tid):
        d = ctx(tid)["current"]["date"]; return datetime.strptime(d[:7], "%Y-%m").strftime("%B")
    def pct(v, nd=1): return f"{v:.{nd}f}%"
    out = {}

    # Jobs
    try:
        cl = []
        p = cur("payrolls"); r = rank("payrolls", "more", "fewer")
        hiring = f"{abs(p) * 1000:,.0f} jobs {'added' if p >= 0 else 'lost'} in {month('payrolls')}" + (f", {r}" if r else "")
        slow = ctx("payrolls")["percentile_below"] < 40
        cl.append(("Hiring is slow (" if slow else "Hiring is steady (" if ctx("payrolls")["percentile_below"] <= 60 else "Hiring is strong (") + hiring + ")")
        losing = []
        ls = lowest_since_year("claims"); rc = record("claims")
        if rc: losing.append(f"new jobless claims are {rc}")
        elif ls: losing.append(f"new jobless claims are the lowest since {ls}")
        else:
            r = rank("claims"); losing.append(f"new jobless claims are {r}" if r else f"new jobless claims are {cur('claims') / 1000:,.0f},000 a week")
        r = rank("unemployment")
        losing.append(f"unemployment, at {pct(cur('unemployment'))}, is {r}" if r else f"unemployment is {pct(cur('unemployment'))}")
        few = ctx("claims")["percentile_below"] < 40 and ctx("unemployment")["percentile_below"] < 40
        text = cl[0] + (" but few people are losing work: " if slow and few else "; " if few else " and ") + losing[0] + ", and " + losing[1] + "."
        if "openings_ratio" in T:
            o = cur("openings_ratio"); text += f" There are about {round(o * 10)} openings for every 10 people looking."
        if "pay" in T and "cpi" in T:
            pay, cpi = cur("pay"), cur("cpi"); gap = pay - cpi
            text += f" Pay is up {pct(pay)} from a year ago, " + ("a little behind prices." if -1 <= gap < -0.2 else "well behind prices." if gap < -1 else "about even with prices." if gap <= 0.2 else "a little ahead of prices." if gap <= 1 else "well ahead of prices.")
        if "health_jobs" in T and T["health_jobs"].get("household"):
            import re as _re
            m = _re.search(r"health care added [\d,]+, or (\d+)%", T["health_jobs"]["household"]["text"])
            if m:
                sh = int(m.group(1)); words = "three-quarters" if sh >= 72 else "two-thirds" if sh >= 62 else "half" if sh >= 45 else "a third" if sh >= 28 else None
                if words: text += f" {words.capitalize()} of the year's new jobs were in health care."
        out["Jobs"] = text
    except Exception as e:
        print(f"summary Jobs skipped: {e}", file=sys.stderr, flush=True)

    # Prices
    try:
        c, b = cur("cpi"), ctx("cpi")["baseline_2015_19"]; r = rank("cpi")
        ratio = c / b if b else None
        mult = ("more than double" if ratio and ratio >= 2 else "about double" if ratio and ratio >= 1.8 else "well above" if ratio and ratio >= 1.3 else "about" if ratio and 0.8 <= ratio <= 1.2 else "below" if ratio else None)
        text = f"Inflation is {pct(c)}" + (f", {r}" if r else "") + (f" and {mult} the 2015{EN}19 average" if mult else "") + "; "
        r2 = rank("core_cpi"); text += f"leaving out food and energy it is {pct(cur('core_cpi'))}" + (f", {r2}" if r2 else "") + "."
        if "rent" in T:
            rr = rank("rent"); prev = T["rent"]["context"].get("year_ago"); rv = cur("rent")
            slower = prev and rv < prev["value"] - 0.5
            text += f" Rent is rising {'more slowly than it was, ' if slower else ''}{pct(rv)} a year" + (f", {rr}" if rr else "") + "."
        out["Prices"] = text
    except Exception as e:
        print(f"summary Prices skipped: {e}", file=sys.stderr, flush=True)

    # Growth & rates
    try:
        g = cur("gdp"); r = rank("gdp", "faster", "slower")
        text = f"The economy grew at a {pct(g)} annual pace last quarter" + (f", {r}" if r else "") + "."
        ff = cur("fed_funds"); rf = rank("fed_funds"); ty = cur("ten_year"); hs = highest_since_year("ten_year"); rt = record("ten_year") or (f"the highest since {hs}" if hs else rank("ten_year"))
        if rf and r and rf == r: rf = "near the middle too" if rf.startswith("near") else rf
        text += f" The Fed's rate, {pct(ff, 2)}, is " + (rf if rf else "unchanged") + (", but" if rt and ("highest" in rt or "lowest" in rt) else ", and") + f" the 10-year Treasury yield, {pct(ty, 2)}, is {rt}, which is what sets mortgage rates."
        out["Growth & rates"] = text
    except Exception as e:
        print(f"summary Growth skipped: {e}", file=sys.stderr, flush=True)

    # Housing
    try:
        hs_ = cur("housing_starts"); r = rank("housing_starts")
        text = f"Builders started homes at a {hs_ / 1000:.2f} million-a-year pace in {month('housing_starts')}" + (f", {r}" if r else "") + "."
        m = cur("mortgage"); rm = rank("mortgage"); b = ctx("mortgage")["baseline_2015_19"]
        text += f" The 30-year mortgage rate, {pct(m, 2)}, " + (f"is {rm}" if rm else "") + (f" and well above the {pct(b)} of 2015{EN}19" if b and m - b >= 1.5 else f" and above the {pct(b)} of 2015{EN}19" if b and m - b >= 0.5 else "")
        hh = T["mortgage"].get("household", {}).get("text", "")
        import re as _re
        mm = _re.search(r"costs (\$[\d,]+) a month at this rate.*?(\$[\d,]+) at the 2015", hh)
        if mm: text += f": the payment on the median home is about {mm.group(1)} a month, against {mm.group(2)} at the 2015{EN}19 rate"
        text += "."
        # Nov 6: home prices and delinquency, each its own clause so either can drop alone.
        if "home_prices" in T:
            try:
                hp = cur("home_prices")
                rh = rank("home_prices", "faster", "slower") if hp > 0 else rank("home_prices")
                text += (f" Home prices were {'up' if hp >= 0 else 'down'} {pct(abs(hp))} from a year earlier in {month('home_prices')}"
                         + (f", {rh}" if rh else "") + ".")
            except Exception as e:
                print(f"summary Housing: home prices skipped: {e}", file=sys.stderr, flush=True)
        if "mortgage_delinquency" in T:
            try:
                dq = cur("mortgage_delinquency"); rd_ = rank("mortgage_delinquency")
                qn = ["first", "second", "third", "fourth"][(int(ctx("mortgage_delinquency")["current"]["date"][5:7]) - 1) // 3]
                text += (f" At banks, {pct(dq, 2)} of home loans were at least a month behind in the {qn} quarter"
                         + (f", {rd_}" if rd_ else "") + ".")
            except Exception as e:
                print(f"summary Housing: delinquency skipped: {e}", file=sys.stderr, flush=True)
        out["Housing"] = text
    except Exception as e:
        print(f"summary Housing skipped: {e}", file=sys.stderr, flush=True)

    # Government and trade
    try:
        d = cur("deficit"); rd = rank("deficit", "larger", "smaller"); fy = ctx("deficit")["current"]["date"][:4]
        text = f"The federal deficit was {pct(d)} of GDP in fiscal {fy}" + (f", {rd}" if rd else "") + "; "
        dv = cur("debt"); rec_d = record("debt"); near = ctx("debt")["percentile_below"] >= 95
        text += f"the debt, at {dv:.0f}% of GDP, is " + ("at its record" if rec_d == "the highest on record" else "near its record" if near else (rank("debt") or "")) + "; "
        tv = cur("trade"); rec_t = record("trade"); tm = month("trade")
        text += f"the trade deficit, ${abs(tv) / 1000:.1f} billion in {tm}, is " + ("the widest on record" if rec_t == "the lowest on record" else (rank("trade", "narrower", "wider") or "")) + "."
        out["Government and trade"] = text
    except Exception as e:
        print(f"summary Government skipped: {e}", file=sys.stderr, flush=True)

    # What things cost
    try:
        goods = [("ground_beef", "ground beef"), ("coffee", "coffee"), ("eggs", "eggs"), ("milk", "milk"), ("bread", "bread"), ("chicken", "chicken"), ("natural_gas", "natural gas"), ("electricity", "electricity")]
        high, low, ordinary = [], [], []
        for tid, name in goods:
            if tid not in T: continue
            pb = ctx(tid)["percentile_below"]
            (high if pb >= 85 else low if pb <= 15 else ordinary).append(name)
        def lst(xs): return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]
        parts = []
        if high: parts.append(f"{lst(high)} {'are' if len(high) > 1 else 'is'} near the highest {'they have' if len(high) > 1 else 'it has'} ever been")
        if "gas" in T:
            gp = cur("gas"); ya = T["gas"]["context"].get("year_ago"); pb = ctx("gas")["percentile_below"]
            word = "high" if pb >= 70 else "low" if pb <= 30 else "ordinary"
            parts.append(f"gasoline is {word} (${gp:.2f}" + (f", {'up' if ya and gp > ya['value'] else 'down'} from ${ya['value']:.2f} a year ago" if ya and abs(gp - ya['value']) >= 0.05 else "") + ")")
        if low: parts.append(f"{lst(low)} {'are' if len(low) > 1 else 'is'} near the lowest {'they have' if len(low) > 1 else 'it has'} been")
        if ordinary: parts.append(f"{lst(ordinary)} {'are' if len(ordinary) > 1 else 'is'} ordinary")
        text = "After inflation, " + lst(parts) + "." if parts else ""
        if "drive_cost" in T:
            share = cur("drive_cost")
            frac = "about a quarter" if share < 30 else "about a third" if share < 40 else "about half" if share < 60 else "about two-thirds" if share < 75 else "about as much as"
            text += f" Driving a mile on home electricity costs {frac} {'of ' if frac != 'about as much as' else ''}driving it on gasoline."
        if text: out["What things cost"] = text
    except Exception as e:
        print(f"summary What things cost skipped: {e}", file=sys.stderr, flush=True)
    return out


# ---- "In short" for the home page (Nov 6): four readings in a fixed order, from the same figures the tiles show ----------
# Same rules as section_summaries(): templates only, never a model. Every number is a tile's current reading (formatted as
# the tile formats it), its period, or its rank in its own history; the only other words are connectives and the fixed
# bins below. Fixed set and order: prices against pay, unemployment, the 30-year mortgage rate. A missing input drops its
# clause and its row; nothing at all means no "home" key, and the page shows no In short. Written to
# data/series.json summaries.home: the desktop paragraph as text and figure segments, and one clause per phone row.

def _half_up(x, nd):
    """x rounded to nd decimals the way the pages round (half away from zero, on the shortest decimal form)."""
    from decimal import Decimal, ROUND_HALF_UP
    q = Decimal(repr(abs(x))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)
    return float(q) * (-1 if x < 0 else 1)


def tile_share(pct_below):
    """The whole percent a tile's sentence prints ("Higher than 67% of months"): the share of the history below the
    reading, or above it for a reading in the lower half, kept between 1 and 99 (as contextSentence in index.html)."""
    v = pct_below if pct_below >= 50 else 100 - pct_below
    return int(min(99, max(1, _half_up(v, 0))))


# The share in words. Every band is true of every share in it: the bare fraction only at the whole percent nearest it
# (67, 75, 80, 90), "about" only from four points under it, "nearly" only within three points under it, "more than"
# only above it. So 63% is "about two-thirds" and 78% "more than three-quarters", never "four-fifths". Shares from 40%
# to 60% of the history never get here: they read "near the middle of its history".
FRACTION_WORDS = [            # (lowest share, highest share, words), shares as the whole percents the tiles print
    (60, 62, "more than half"),
    (63, 66, "about two-thirds"),
    (67, 67, "two-thirds"),
    (68, 71, "more than two-thirds"),
    (72, 74, "nearly three-quarters"),
    (75, 75, "three-quarters"),
    (76, 79, "more than three-quarters"),
    (80, 80, "four-fifths"),
    (81, 86, "more than four-fifths"),
    (87, 89, "nearly nine-tenths"),
    (90, 90, "nine-tenths"),
    (91, 96, "more than nine-tenths"),
    (97, 99, "nearly all"),
]


def fraction_words(share):
    for lo, hi, words in FRACTION_WORDS:
        if lo <= share <= hi:
            return words
    return None


def home_summary(tiles_out, today=None):
    """{"paragraph": [segment, …], "rows": {id: clause}, "order": [ids]} or None. A segment is a string or a figure,
    {"t": "3.7%", "id": "cpi", "name": "Inflation, 3.7%"}, which the page sets in bold as a link to that chart."""
    today = today or date.today()
    T = {t["id"]: t for t in tiles_out}
    EN = "–"
    MONTHS_LONG = ["January", "February", "March", "April", "May", "June", "July", "August", "September",
                   "October", "November", "December"]
    MONTHS = [m[:3] for m in MONTHS_LONG]

    def ctx(tid):
        return T[tid]["context"]                      # none of the four is a price tile, so never today's dollars

    def val(tid, v=None):
        d = T[tid]["display"]
        v = ctx(tid)["current"]["value"] if v is None else v
        nd = d.get("decimals", 0)
        return f"{abs(_half_up(v / (d.get('scale') or 1), nd)):.{nd}f}{d.get('suffix', '')}"

    def when(tid):
        """The reading's period: "September" (or "September 2025" when it is not this year), "Nov 5" for a week."""
        s = ctx(tid)["current"]["date"]
        y, m, dd = int(s[:4]), int(s[5:7]), int(s[8:10])
        if T[tid]["freq"] in ("w", "d"):
            return f"{MONTHS[m - 1]} {dd}" + (f", {y}" if y != today.year else "")
        return MONTHS_LONG[m - 1] + (f" {y}" if y != today.year else "")

    def noun(tid):
        return {"a": "years", "q": "quarters", "w": "weeks", "d": "days"}.get(T[tid]["freq"], "months")

    def rank(tid, hi_word, lo_word, hi_rec, lo_rec):
        """("rank words", where) with where in "high", "low", "middle", "record"."""
        c = ctx(tid)
        p = c["percentile_below"]
        if p >= 50 and c.get("highest_since") is None:
            return hi_rec, "record"
        if p < 50 and c.get("lowest_since") is None:
            return lo_rec, "record"
        if 40 <= p <= 60:
            return "near the middle of its history", "middle"
        words = fraction_words(tile_share(p))
        since = str(c["since"])[:4]
        of = " " if words == "nearly all" else " of "
        return f"{hi_word if p >= 50 else lo_word} than in {words}{of}{noun(tid)} since {since}", ("high" if p >= 50 else "low")

    def fig(tid, text, name):
        return {"t": text, "id": tid, "name": name}

    def cap(s):
        return s[:1].upper() + s[1:]

    sentences, rows, order = [], {}, []

    # 1. Prices, then pay against prices (one sentence when both are here)
    prices = None
    try:
        v = ctx("cpi")["current"]["value"]
        shown = _half_up(v, T["cpi"]["display"].get("decimals", 1))
        if shown > 0:
            r, _ = rank("cpi", "a faster rise", "a slower rise", "the fastest rise on record", "the slowest rise on record")
            r = r if not r.startswith("near") else "a rise near the middle of its history"
            prices = [f"prices in {when('cpi')} were ", fig("cpi", val("cpi"), f"Inflation, {val('cpi')}"), f" higher than a year earlier, {r}"]
        elif shown < 0:                                      # prices falling: "a fall larger than in …"
            r, _ = rank("cpi", "a fall smaller", "a fall larger", "the smallest fall on record", "the largest fall on record")
            prices = [f"prices in {when('cpi')} were ", fig("cpi", val("cpi"), f"Inflation, −{val('cpi')}"), f" lower than a year earlier, {r}"]
        else:                                                # 0.0% as printed: neither a rise nor a fall
            r, _ = rank("cpi", "higher", "lower", "the highest on record", "the lowest on record")
            prices = [f"prices in {when('cpi')} were unchanged from a year earlier, {r}"]
        rows["cpi"] = cap(r) + "."
        order.append("cpi")
    except Exception as e:                                   # noqa: BLE001
        print(f"home summary: prices skipped: {e}", file=sys.stderr, flush=True)
    pay = None
    try:
        pv = ctx("pay")["current"]["value"]
        r, _ = rank("pay", "faster", "slower", "the fastest on record", "the slowest on record")
        vs = None
        pay_month = ctx("pay")["current"]["date"][:7]
        cpi_then = next((v for d, v in T["cpi"]["observations"] if d[:7] == pay_month), None) if "cpi" in T else None
        if cpi_then is not None:                             # pay against prices in the same month, as the tiles print them
            gap = _half_up(pv, 1) - _half_up(cpi_then, 1)
            gap = round(gap, 1)
            vs = ("about the same as prices" if abs(gap) <= 0.2 else
                  ("a little ahead of prices" if gap > 0 else "a little behind prices") if abs(gap) <= 1.0 else
                  ("ahead of prices" if gap > 0 else "behind prices"))
        up = _half_up(pv, 1)
        dirn = "up " if up > 0 else "down " if up < 0 else ""
        pay = [f"pay in {when('pay')} was {dirn}" if dirn else f"pay in {when('pay')} was unchanged from a year earlier"]
        if dirn:
            pay.append(fig("pay", val("pay"), f"Hourly pay, {'−' if up < 0 else ''}{val('pay')}"))
        pay.append(f", {r}" + (f" and {vs}" if vs else ""))
        rows["pay"] = cap(r) + (f" and {vs}" if vs else "") + "."
        order.append("pay")
    except Exception as e:                                   # noqa: BLE001
        print(f"home summary: pay skipped: {e}", file=sys.stderr, flush=True)
    if prices and pay:
        sentences.append(prices + ["; "] + pay + ["."])
    elif prices or pay:
        sentences.append((prices or pay) + ["."])

    # 2. Unemployment
    try:
        r, _ = rank("unemployment", "higher", "lower", "the highest on record", "the lowest on record")
        sentences.append([f"unemployment in {when('unemployment')}, at ", fig("unemployment", val("unemployment"), f"Unemployment rate, {val('unemployment')}"), f", was {r}."])
        rows["unemployment"] = cap(r) + "."
        order.append("unemployment")
    except Exception as e:                                   # noqa: BLE001
        print(f"home summary: unemployment skipped: {e}", file=sys.stderr, flush=True)

    # 3. The 30-year mortgage rate, and the 2015–19 average beside it
    try:
        c = ctx("mortgage")
        r, _ = rank("mortgage", "higher", "lower", "the highest on record", "the lowest on record")
        m, b = c["current"]["value"], c.get("baseline_2015_19")
        base = None
        if b is not None:
            gap = _half_up(m, 2) - _half_up(b, 2)
            word = ("well above" if gap >= 1.5 else "above" if gap >= 0.5 else
                    "well below" if gap <= -1.5 else "below" if gap <= -0.5 else "about the same as")
            base = (f"{word} the ", fig("mortgage", val("mortgage", b), f"30-year mortgage rate, 2015 to 2019 average, {val('mortgage', b)}"), f" of 2015{EN}19")
        s = ["the 30-year mortgage rate was ", fig("mortgage", val("mortgage"), f"30-year mortgage rate, {val('mortgage')}"), f" on {when('mortgage')}, {r}"]
        if base:
            s += [" and " + base[0], base[1], base[2]]
        sentences.append(s + ["."])
        rows["mortgage"] = cap(r) + (f", {base[0]}{base[1]['t']}{base[2]}" if base else "") + "."
        order.append("mortgage")
    except Exception as e:                                   # noqa: BLE001
        print(f"home summary: mortgage skipped: {e}", file=sys.stderr, flush=True)

    if not sentences:
        return None
    para = []
    for s in sentences:
        s = list(s)
        s[0] = cap(s[0])
        if para:
            para.append(" ")
        para.extend(s)
    merged = []                                              # neighbouring strings joined, so the JSON stays small
    for seg in para:
        if isinstance(seg, str) and merged and isinstance(merged[-1], str):
            merged[-1] += seg
        else:
            merged.append(seg)
    return {"paragraph": merged, "rows": rows, "order": order}


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
        "why": "The slope of the curve. It went below zero (an inverted curve) before each of the eight recessions since 1969, and also in 1966–67, 1998 and 2022–24 with no recession following; it dipped below zero again briefly in 2025.",
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
        "for": ["cpi", "core_cpi", "pay"],
        "op": "diff", "a": "wages", "b": "cpi", "freq": "m",
        "why": "Wage growth after inflation, as a simple difference. Above zero, pay is outrunning prices; below, prices are winning. Compares against headline CPI on both charts.",
    },
    {
        "id": "ten_minus_3m",
        "label": "10-year yield minus 3-month Treasury yield",
        "for": ["ten_year", "fed_funds"],
        "op": "diff", "a": "ten_year", "b": "gs3m", "freq": "m",
        "why": "The slope of the curve the New York Fed uses in its recession model (FRED publishes it daily as T10Y3M). It went below zero before each of the four recessions since the series begins in 1982, and stayed below zero from late 2022 through 2024 with no recession; its monthly average dipped just below zero several times in 2025. Different scale: percentage points; below the zero line, the curve is inverted.",
        "panel": "own", "display": {"scale": 1, "decimals": 1, "suffix": ""},
    },
    {
        "id": "mortgage_minus_ten",
        "label": "Mortgage rate minus 10-year yield",
        "for": ["mortgage"],
        "op": "diff", "a": "mortgage_monthly", "b": "ten_year", "freq": "m",
        "why": "The spread lenders charge over Treasuries. Normally 1.5–2 points; wider in stress, as in 2022–24.",
    },
    {
        "id": "oil_real",
        "label": "Crude oil (WTI) in today's dollars, per barrel",
        "for": ["cpi", "core_cpi", "gas"],
        "op": "deflate", "a": "wti", "b": "cpi_index", "freq": "m",
        "why": "The price of a barrel of West Texas Intermediate crude, restated with the CPI in dollars of the latest month. Before 1982 it is the posted price, which changed only a few times a decade until the 1970s. Different scale: dollars per barrel.",
        "panel": "own", "display": {"scale": 1, "decimals": 0, "prefix": "$"},
    },
    {
        "id": "tariff_rate",
        "label": "Effective tariff rate (customs duties ÷ imports of goods)",
        "for": ["trade"],
        "op": "ratio", "a": "customs_duties", "b": "goods_imports", "freq": "q",
        "why": "What tariffs collected per dollar of goods imported: the average rate actually paid, after exemptions and shifts in what is bought. Quarterly; different scale: percent.",
        "panel": "own", "display": {"scale": 1, "decimals": 1, "suffix": "%"},
    },
    # The two sides of the Electric mile vs. gas mile tile, in cents per mile, in one shared sub-panel (Nov 2).
    {
        "id": "gas_monthly",
        "label": "Gasoline, monthly average",
        "for": [],
        "op": "monthly_avg", "a": "gas", "freq": "m",
        "why": "The weekly pump price averaged over each calendar month; an input to the per-mile lines.",
    },
    {
        "id": "gas_per_mile",
        "label": "Gasoline, cents per mile at 27.1 mpg",
        "for": ["drive_cost"],
        "op": "scale", "a": "gas_monthly", "k": 100 / 27.1, "freq": "m",
        "why": "The monthly average pump price divided by 27.1 miles per gallon, the gas-car efficiency the Electric Vehicles article assumes. Different scale: cents per mile.",
        "panel": "group:per_mile", "panel_title": "Cents per mile", "display": {"scale": 1, "decimals": 1, "suffix": "¢"},
    },
    {
        "id": "elec_per_mile",
        "label": "Electricity at home, cents per mile at 3.5 miles per kWh",
        "for": ["drive_cost"],
        "op": "scale", "a": "electricity", "k": 100 / 3.5, "freq": "m",
        "why": "The BLS average residential electricity price divided by 3.5 miles per kilowatt-hour, a typical EV's efficiency. Public fast charging costs two to three times this. Different scale: cents per mile.",
        "panel": "group:per_mile", "panel_title": "Cents per mile", "display": {"scale": 1, "decimals": 1, "suffix": "¢"},
    },
    # The labor turnover rates under Openings per job seeker (Nov 3), in one shared sub-panel. Copies (scale by 1)
    # of the hires, quits and layoffs companions, which stay on the unemployment chart's own axis; here the tile's
    # scale is a ratio, so the rates need a panel of their own.
    {
        "id": "turnover_hires",
        "label": "Hires rate",
        "for": ["openings_ratio"],
        "op": "scale", "a": "hires_rate", "k": 1, "freq": "m",
        "why": "Hires in the month as a share of employment (JOLTS, JTSHIR). Low hiring with low layoffs is the 'frozen' job market: hard to lose a job, hard to find one. Different scale: percent of employment.",
        # the shared panel's clip comes from its first member: 0-6.5%, so the spring 2020 layoffs spike (8.6% in
        # March) is marked off the chart and the ordinary 1-4% range stays readable; hires peaked at 6.1% in May 2020
        "panel": "group:turnover", "panel_title": "Share of workers, each month", "display": {"scale": 1, "decimals": 1, "suffix": "%", "clip": [0, 6.5]},
    },
    {
        "id": "turnover_quits",
        "label": "Quits rate",
        "for": ["openings_ratio"],
        "op": "scale", "a": "quits_rate", "k": 1, "freq": "m",
        "why": "Workers leaving voluntarily as a share of employment (JOLTS, JTSQUR). People tend to quit when they expect to find the next job. Different scale: percent of employment.",
        "panel": "group:turnover", "panel_title": "Share of workers, each month", "display": {"scale": 1, "decimals": 1, "suffix": "%"},
    },
    {
        "id": "turnover_layoffs",
        "label": "Layoffs and discharges rate",
        "for": ["openings_ratio"],
        "op": "scale", "a": "layoffs_rate", "k": 1, "freq": "m",
        "why": "Involuntary separations as a share of employment (JOLTS, JTSLDR), the monthly counterpart of weekly jobless claims. Different scale: percent of employment.",
        "panel": "group:turnover", "panel_title": "Share of workers, each month", "display": {"scale": 1, "decimals": 1, "suffix": "%"},
    },
]
# Each price tile also gets its inflation-adjusted line on the detail page: the same
# history the tile's range and "higher than" sentence are computed from.
for _t in TILES:
    if _t["display"].get("adjust") == "cpi":
        DERIVED.append({
            "id": _t["id"] + "_real",
            "label": "In today's dollars (adjusted for inflation)",
            "for": [_t["id"]],
            "op": "deflate", "a": _t["id"], "b": "cpi_index", "freq": _t["freq"],
            "why": "The same price with inflation taken out, in dollars of the latest reading's month, using the CPI. "
                   "The typical range and the comparison on the tile are computed from this line.",
        })

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
    # The 2015–19 average's own rank in the same history: the range strip places its tick by rank, as it does
    # the dot. The almanac can rank as-charged series itself, but not the today's-dollars history of a price.
    base_pct = None
    if baseline is not None:
        b_below = sum(1 for v in history if v < baseline)
        b_equal = sum(1 for v in history if v == baseline)
        base_pct = 100.0 * (b_below + 0.5 * b_equal) / len(history)

    lo_i = min(range(len(obs)), key=lambda i: obs[i][1])
    hi_i = max(range(len(obs)), key=lambda i: obs[i][1])

    # Typical range: 5th–95th percentile of the whole history, so one freak
    # month (April 2020) doesn't stretch the range strip to uselessness.
    ranked = sorted(values)
    p5 = ranked[int(0.05 * (len(ranked) - 1))]
    p95 = ranked[int(0.95 * (len(ranked) - 1))]
    # the median of the whole history: the range strip ranks readings, so the median is always at its center,
    # and labeling it shows the bar is a ranking, not a ruler (the chart's median line uses the same history)
    n = len(ranked)
    med = ranked[n // 2] if n % 2 else (ranked[n // 2 - 1] + ranked[n // 2]) / 2

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
        "baseline_percentile": round(base_pct, 1) if base_pct is not None else None,
        "min": {"date": obs[lo_i][0], "value": obs[lo_i][1]},
        "max": {"date": obs[hi_i][0], "value": obs[hi_i][1]},
        "typical_low": round(p5, 4),
        "typical_high": round(p95, 4),
        "median": round(med, 4),
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


def deflate(obs, cpi):
    """A price history restated in dollars of its latest reading's month, using the CPI.
    Each reading is scaled by its own month's index. Months after the latest CPI use the
    latest CPI (so the newest readings equal their prices as charged); a month missing
    inside the CPI's span (October 2025 was never published) uses the average of its
    neighbors. Readings before the CPI begins are dropped."""
    months = sorted((month_key(d), v) for d, v in cpi)
    if len(months) < 2:
        raise RuntimeError("no CPI")
    by_month = dict(months)
    first, last = months[0][0], months[-1][0]
    keys = [m for m, _ in months]

    def index_at(m):
        if m in by_month:
            return by_month[m]
        if m > last:
            return months[-1][1]
        if m < first:
            return None
        i = next(k for k, km in enumerate(keys) if km > m)      # neighbors around the gap
        return (months[i - 1][1] + months[i][1]) / 2

    base = index_at(month_key(obs[-1][0]))
    out = []
    for d, v in obs:
        c = index_at(month_key(d))
        if c:
            out.append((d, v * base / c))
    if len(out) < 3:
        raise RuntimeError("inputs do not overlap")
    return out


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
    if spec["op"] == "deflate":
        b = by_id.get(spec["b"])
        if not b:
            raise RuntimeError(f"missing input {spec['b']}")
        return deflate(a, b)
    if spec["op"] == "ratio":
        # a as a percent of b, matched on the same date (both inputs share a frequency)
        b = by_id.get(spec["b"])
        if not b:
            raise RuntimeError(f"missing input {spec['b']}")
        bd = dict(b)
        out = [(d, 100.0 * v / bd[d]) for d, v in a if bd.get(d)]
        if len(out) < 3:
            raise RuntimeError("inputs do not overlap")
        return out
    if spec["op"] == "monthly_avg":
        return monthly_average(a)
    if spec["op"] == "scale":
        return [(d, v * spec["k"]) for d, v in a]
    raise RuntimeError(f"unknown op {spec['op']}")


def monthly_average(obs):
    """Weekly or daily readings averaged by calendar month, dated the first of the month."""
    by_month = {}
    for d, v in obs:
        by_month.setdefault(month_key(d), []).append(v)
    return [(m + "-01", mean(vs)) for m, vs in sorted(by_month.items())]


def compute_tile(spec, by_id):
    """A tile's history computed from other tiles' histories (see the drive_cost tile). Returns [(date, value)]."""
    if spec["op"] == "per_mile_ratio":
        gas, elec = by_id.get(spec["gas"]), by_id.get(spec["electricity"])
        if not gas or not elec:
            raise RuntimeError("missing input")
        g = dict(monthly_average(gas))
        out = [(d, 100.0 * (v / spec["mi_per_kwh"]) / (g[d] / spec["mpg"])) for d, v in elec if g.get(d)]
        if len(out) < 3:
            raise RuntimeError("inputs do not overlap")
        return out
    if spec["op"] == "series_ratio":
        # a / b for two FRED series fetched here (they are not tiles), matched on the same date (Nov 3:
        # openings per job seeker). A month either series lacks is left out.
        params = {"observation_start": spec.get("start", "1776-07-04")}
        a = get_observations(spec["a"], params)
        time.sleep(0.4)
        b = dict(get_observations(spec["b"], params))
        time.sleep(0.4)
        out = [(d, v / b[d]) for d, v in a if b.get(d)]
        if len(out) < 3:
            raise RuntimeError("inputs do not overlap")
        return out
    raise RuntimeError(f"unknown op {spec['op']}")


def release_calendar(series_ids):
    """The last and next three scheduled release dates of every FRED release behind the given series,
    for the weekly check of what came out. Each failure is noted and skipped; never raises."""
    today = date.today().isoformat()
    releases = {}
    for sid in series_ids:
        try:
            r = fred_get("series/release", {"series_id": sid})["releases"][0]
        except Exception as e:
            print(f"  calendar: no release for {sid} ({e})", file=sys.stderr, flush=True)
            continue
        time.sleep(0.5)                        # FRED allows about 120 requests a minute
        rel = releases.setdefault(r["id"], {"id": r["id"], "name": r.get("name"), "link": r.get("link"), "series": []})
        rel["series"].append(sid)
    for rel in releases.values():
        try:
            data = fred_get("release/dates", {"release_id": rel["id"], "include_release_dates_with_no_data": "true",
                                              "sort_order": "desc", "limit": 400})
            ds = sorted({d["date"] for d in data.get("release_dates", [])})
            past = [d for d in ds if d <= today]
            rel["last"] = past[-1] if past else None
            rel["next"] = [d for d in ds if d > today][:3]
        except Exception as e:
            rel["error"] = str(e)[:160]
        time.sleep(0.5)
    out = sorted(releases.values(), key=lambda r: (r.get("next") or ["9999-12-31"])[0])
    return {"generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "releases": out}


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
        if "computed" in t:                     # built from other tiles once they are all fetched (below)
            tiles_out.append({"id": t["id"], "_spec": t})
            continue
        print(f"{t['id']:16s} {t['series']}", flush=True)
        obs = get_observations(t["series"], t["params"])
        if t.get("flip"):                       # shown with the sign people use (see the deficit tile)
            obs = [(d, -v) for d, v in obs]
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
            "agency": t.get("agency", ""),
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

    # Computed tiles (Nov 2): their history comes from other tiles' histories. Fail soft: a computed tile
    # that can't be built is dropped with a message; its inputs would already have failed the run.
    by_id = {t["id"]: t["observations"] for t in tiles_out if "observations" in t}
    for i, t in enumerate(tiles_out):
        spec = t.get("_spec")
        if not spec:
            continue
        try:
            obs = compute_tile(spec["computed"], by_id)
            print(f"{spec['id']:16s} computed from {', '.join(v for k, v in spec['computed'].items() if isinstance(v, str) and k not in ('op', 'start'))} ({len(obs)} obs)", flush=True)
            info = get_series_info(spec["series"])
            time.sleep(0.4)
        except Exception as e:
            print(f"{spec['id']:16s} computed tile skipped: {e}", file=sys.stderr, flush=True)
            tiles_out[i] = None
            continue
        by_id[spec["id"]] = obs
        tiles_out[i] = {
            "id": spec["id"], "section": spec["section"], "agency": spec.get("agency", ""),
            "title": spec["title"], "subtitle": spec["subtitle"], "note": spec["note"],
            "freq": spec["freq"], "display": spec["display"], "computed": spec["computed"],
            "source": {
                "series": spec["series"],
                "url": f"https://fred.stlouisfed.org/series/{spec['series']}",
                "fred_title": info["title"], "fred_units": info["units"], "frequency": info["frequency"],
                "seasonal_adjustment": info["seasonal_adjustment"], "last_updated": info["last_updated"],
                "transform": "computed",
            },
            "headline": None,
            "context": context_for(obs, spec["freq"]),
            "observations": [[d, round(v, 3)] for d, v in obs],
        }
    tiles_out = [t for t in tiles_out if t]

    # Companion series for the detail page. Tolerant: one bad series is skipped.
    today = date.today().isoformat()
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
            **{k: c[k] for k in ("panel", "display", "panel_title", "group", "group_note") if k in c},
            "source": {
                "series": c["series"],
                "url": f"https://fred.stlouisfed.org/series/{c['series']}",
                "fred_title": info["title"], "fred_units": info["units"],
                "frequency": info["frequency"], "last_updated": info["last_updated"],
                "transform": c["params"].get("units", "lin"),
            },
            "observations": [[d, round(v, 3)] for d, v in obs],
        })

    # Price tiles: the typical range and the "higher than" sentence come from the
    # inflation-adjusted history; the headline, comparisons and chart stay as charged.
    # Without the CPI the tile falls back to its raw history.
    for t in tiles_out:
        if t["display"].get("adjust") != "cpi":
            continue
        try:
            t["context_real"] = context_for(deflate(by_id[t["id"]], by_id["cpi_index"]), t["freq"])
        except Exception as e:
            print(f"{t['id']:16s} inflation-adjusted context skipped: {e}", file=sys.stderr, flush=True)

    for dv in DERIVED:
        try:
            obs = derive(dv, by_id)
        except Exception as e:
            print(f"{dv['id']:16s} skipped: {e}", file=sys.stderr, flush=True)
            continue
        print(f"{dv['id']:16s} derived ({len(obs)} obs)", flush=True)
        by_id[dv["id"]] = obs                   # so a later derived series can build on this one (Nov 2)
        companions_out.append({
            "id": dv["id"], "label": dv["label"], "for": dv["for"], "why": dv["why"], "freq": dv["freq"],
            "derived": {k: dv[k] for k in ("op", "a", "b", "k") if k in dv},
            **{k: dv[k] for k in ("panel", "display", "panel_title", "group", "group_note") if k in dv},
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
            if len(obs) > 1:
                extras[x["id"]]["previous"] = {"date": obs[-2][0], "value": obs[-2][1]}
        except Exception as e:
            print(f"  skipped: {e}", file=sys.stderr, flush=True)
    try:
        household_lines(tiles_out, companions_out, extras)
    except Exception as e:
        print(f"household lines skipped: {e}", file=sys.stderr, flush=True)
    summaries = {}
    try:
        summaries = section_summaries(tiles_out)      # after the household lines, which two of them read
    except Exception as e:
        print(f"summaries skipped: {e}", file=sys.stderr, flush=True)
    try:                                              # the home page's In short (a missing input drops its clause)
        home = home_summary(tiles_out)
        if home:
            summaries["home"] = home
    except Exception as e:
        print(f"home summary skipped: {e}", file=sys.stderr, flush=True)

    print("recessions      USREC", flush=True)
    rec = get_observations(RECESSIONS_SERIES, {"observation_start": RECESSIONS_START})

    # Release calendar for the weekly article check: which releases came out and which are next.
    calendar = None
    try:
        ids = [t["series"] for t in TILES] + [c["series"] for c in COMPANIONS] + [x["series"] for x in EXTRAS]
        print("calendar        FRED release dates", flush=True)
        calendar = release_calendar(list(dict.fromkeys(ids)))
        print(f"  {len(calendar['releases'])} releases", flush=True)
    except Exception as e:                     # never let the calendar fail the run
        print(f"calendar skipped: {e}", file=sys.stderr, flush=True)

    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "attribution": "Source: FRED, Federal Reserve Bank of St. Louis. Underlying data from "
                       "the Bureau of Labor Statistics, Bureau of Economic Analysis, Census Bureau, "
                       "Energy Information Administration, Federal Reserve Board, Freddie Mac and the NBER.",
        "baseline": {"label": "2015–19 average", "start": BASELINE_START.isoformat(),
                     "end": BASELINE_END.isoformat()},
        "recessions": recession_spans(rec),
        "extras": extras,
        "calendar": calendar,
        "summaries": summaries,
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
