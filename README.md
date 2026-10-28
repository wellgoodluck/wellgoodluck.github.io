# Economy in Context

An almanac of the main U.S. economic indicators, each shown against its own
history. Live at [economyincontext.org](https://economyincontext.org).

## How it works

- `index.html` is the whole site: one page, no framework, no tracking. The
  typeface (Public Sans, open license) is served from `assets/fonts/`, so the
  page makes no third-party requests.
- `fetch_fred.py` pulls the indicator set from the FRED API (Federal Reserve
  Bank of St. Louis) and writes `data/series.json` with the history, the latest
  reading, and context statistics (percentile in own history, 2015–19 average,
  typical range, record highs and lows).
- `.github/workflows/refresh.yml` runs the fetch twice each weekday and
  publishes the result to GitHub Pages. It needs one repository secret,
  `FRED_API_KEY` (a free key from fredaccount.stlouisfed.org/apikeys).

To add or change an indicator, edit the `TILES` list at the top of
`fetch_fred.py`. The page reads whatever the JSON contains.

## Data

Source: FRED, Federal Reserve Bank of St. Louis. Underlying data from the
Bureau of Labor Statistics, Bureau of Economic Analysis, Census Bureau, Federal
Reserve Board, Freddie Mac and the National Bureau of Economic Research. All
figures are the current vintage and are subject to revision by the agencies.
