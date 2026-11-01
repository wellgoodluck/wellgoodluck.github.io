# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Primary: everyday adult readers in the United States trying to make sense of economic news. They have just heard a number (inflation, jobs, gas, the deficit) and want to know whether it is high, low or normal, and what it means for a household like theirs. Many arrive on a phone, from a search result or a shared link, and read for a few minutes. They are not economists and should not need to be.

Secondary, reaching the site through links: teachers and students, librarians building research guides, and journalists and fact-checkers who need a neutral chart they can cite. When the audiences pull in different directions, everyday readers win.

## Product Purpose

Economy in Context puts the main U.S. economic numbers in context. Every indicator is shown against its own history, with its typical range, a 2015–19 reference and a sentence in plain words, so a reader can judge a number without being told what to think about it. Plain-language articles explain what each number measures, how it reaches a household, and what people argue about, and household paths ("You rent", "You're retired on a fixed income") gather the numbers that matter to one situation.

Success is a reader who leaves able to place the number they came with, and who trusts the page enough to share or cite it.

## Positioning

- Each number is judged against its own history, not against a target or a party's claim: the range strip, the percentile sentence and today's-dollars adjustment for prices.
- Neutral by construction: political overlays show each side's actual claim and a framing line, the data line never takes a party's color, and an indicator's track record names its false alarms as well as its hits.
- Every figure links to its primary source (FRED and the agencies behind it), and the site says how each overlay was chosen.
- No ads, no cookies, no login, no tracking of individuals; free to reuse under CC BY 4.0.

## Operating Context

- The almanac (home page) is one long page: an "At a glance" overview of every indicator, then a tile per indicator grouped in six sections, each linking to its chart page.
- Each indicator has a chart page with range buttons, a custom range, optional overlays (reference lines, companion series, eras such as party control and Fed cycles, events), a readings table, CSV download, a downloadable image and embed code.
- Articles embed live charts; many article figures update automatically with each data refresh, while timely articles stay dated as arguments of their moment.
- Data refreshes twice each weekday from FRED. Readers often compare the site with headlines, other charts, or a claim they heard.

## Capabilities and Constraints

- A static site on GitHub Pages: plain HTML, CSS and JavaScript with no framework; Python standard library scripts fetch data and build articles. No server, no database.
- Light and dark color schemes follow the reader's system setting. Pages must work from 375px phones to desktop, print cleanly, and work in embeds.
- Charts are SVG drawn in the browser. No dual y-axes: different scales go in a stacked sub-panel.
- Changes reach the site through manual uploads to the repository; there is no automated deploy from an assistant.
- The site is published without a byline under its own identity. Nothing on it may identify the person who runs it: no personal accounts, no career or local detail, no links to personal profiles.
- Page views are counted without cookies (GoatCounter); the privacy wording on the site must change if counting changes.

## Brand Commitments

- Name: Economy in Context; domain economyincontext.org.
- The mark: two brackets around a dot (`assets/icon.svg`), with the favicon set and social card in `assets/`.
- Voice: plain words, short sentences, numbers with their period and source. No advice, no villains, no mascots, no sports analogies; every analogy says where it breaks.
- Restraint is the brand: no value-judgment colors (good/bad, red/green) on readings, and nothing that reads as a thumb on the scale.
- License line: charts and writing are CC BY 4.0; data is credited to its agency.

## Evidence on Hand

- Real data for every indicator in `data/series.json`, companions in `data/companions.json`, hand-compiled eras and events with sources in `data/overlays.json`.
- About 36 articles in `articles/src/` (indicator explainers, idea pages, household paths, timely pieces), each with sources and dated corrections where needed.
- No testimonials, endorsements, press, user counts or traffic figures exist; do not invent any. No author biography exists by design.

## Product Principles

1. Context before conclusion: show where a number sits in its own history and let the reader decide what it means.
2. Neutral by construction, not by disclaimer: design choices (color, order, framing) must not favor a party or a reading.
3. Plain words over expertise: anything a non-economist would stumble on gets explained where it appears.
4. Every number is checkable: its period, its source and its link travel with it, including into downloads and embeds.
5. Quiet and durable: no ads, trackers, logins or attention tricks; the page should still read correctly in five years.

## Accessibility & Inclusion

WCAG 2.1 AA is the standard: 4.5:1 for text, 3:1 for marks a reader needs to understand a chart, full keyboard access with visible focus, and meaning never carried by color alone (labels, legends and tables back up every color). Charts must stay readable for color-blind readers in both color schemes.
