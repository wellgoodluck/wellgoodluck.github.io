---
title: Your State's Population, and Where It's Changing
title_tag: State Population Over Time: Every State Since 1900
dek: A map of where each state gained and lost people in the latest year. Pick a state, or the whole country, for its population back to 1900, where the last five years' change came from — births and deaths, other countries, and other states — which states its newcomers came from and its leavers went to, and what a dollar is worth there.
date: 2026-11-22
kind: tool
more_tools: kept-up, my-inflation-rate
---

<div class="sp-mount" data-src="/assets/states.json" data-map="/assets/us-map.json"><p class="rb-noscript">This tool needs JavaScript. The section How it's worked out, below, explains where the figures come from, and Sources links to them.</p></div>
<script src="../assets/states.js?v=20261122n"></script>

## How it's worked out

The Census Bureau counts everyone once a decade and estimates each state's population every July in between. The figures here are its Vintage 2025 estimates, released January 27, 2026, which run through July 1, 2025. Each year's release revises the whole series back to the 2020 census, so these numbers can differ a little from what was published a year earlier.

The bars split each year's change into three parts, the Census Bureau's "components of change." Births minus deaths is called natural change. The two migration parts are nets: how many more people moved in than moved out, counted against other countries and against other states. A bar's year runs from July 1 to June 30 — the 2025 bars cover July 2024 through June 2025. The three parts need not add exactly to the change in the total; the Census Bureau's method leaves a small residual.

The map at the top shades every state by one of those parts, or by the total change, for the latest year, per 1,000 residents, so large and small states compare fairly. For the three parts these are the Census Bureau's own rates, which divide each part by the average of the state's population on July 1 at the start and end of the year; the total change is figured the same way. Gray means within 1 per 1,000 either way. The shapes are the bureau's 2017 cartographic state boundaries, simplified, with Alaska and Hawaii moved (and Alaska shrunk) to fit; the smallest states are also listed under the map so they're easy to pick.

Migration is the hardest part to estimate. Births and deaths come from vital records; moves are estimated from tax returns, Medicare records and other administrative data, and they are the figures that swing most from year to year.

The population line is the Census Bureau's resident-population series as carried by FRED, one value a year back to 1900 for most states (1950 for Alaska and Hawaii, which became states in 1959). Earlier decades come from the bureau's historical intercensal estimates, so the line is an estimate between censuses, not a yearly count.

Choosing United States adds up the 50 states and the District of Columbia. For 2020 through 2025 that sum is exactly the Census Bureau's national estimate; before 1950 the line leaves out Alaska and Hawaii, whose series begin that year. Moves between states cancel out for the country as a whole, so it has no other-states part and no movers tables.

The last section, which states people came from and went to, comes from a different source: the Census Bureau's American Community Survey, which asks a sample of U.S. residents where they lived a year earlier. The figures are its 2024 state-to-state migration flows, released January 21, 2026, and they count people one year and older. Because they come from a survey, each has a margin of error, shown as ±; the Census Bureau publishes them at 90% confidence, meaning there's about a 90% chance the true figure falls within that range (counting sampling error only). The net with a state is people moved in minus people moved out, and the tool marks a net that is smaller than its own margin, since the survey can't say with 90% confidence which way that one runs. It also says when the top two states in a list are too close to call. A few small flows aren't published at all because too few people in the sample made that move; those show as n/a.

These flows won't match the "other states, net" bar above. They come from 2024 survey answers about the year before, not the year to July 2025; they come from a survey rather than from tax and Medicare records; and the population estimates count moves between the states and Puerto Rico as international migration, while these tables list Puerto Rico separately. Use them for where people went, and the bars for how much each state gained or lost.

The last section, what a dollar is worth, uses the Bureau of Economic Analysis's figures for 2024. Income per person is personal income divided by everyone who lives in the state, children included. Personal income counts pay, business and investment income, and government benefits, including non-cash ones such as employer-paid health insurance and Medicare; it is measured before income taxes but after Social Security and Medicare payroll taxes, and it leaves out capital gains. Because it's an average pulled up by high earners, and includes more than pay, it isn't what a typical worker takes home. The price level is the bureau's regional price parity, released February 19, 2026, which compares what people in each state typically buy, rent included, with what the same things would cost at national-average prices. The bureau adjusts each state's income by its price level, and rebalances the states to add up to the national total, to put every state on national-average prices; the tool shows that figure in 2024 dollars, converted from the bureau's 2017 dollars with the national price index for consumer spending. The income per person shown is the version that estimate was built on; the bureau has revised it slightly since, which FRED's pages show. The ranks count the 50 states and the District of Columbia. The bureau's figures for 2025 are due December 10, 2026.

Nothing you pick is saved or sent anywhere. A link carries your state only if you copy one with it.

## Read more

- [Where Americans Are Moving](../articles/where-americans-are-moving.html): what changed in the 2025 estimates, and what people argue the moves mean.

## Sources

- [Census Bureau, Vintage 2025 state population estimates and components of change (NST-EST2025-ALLDATA)](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/state/totals/NST-EST2025-ALLDATA.csv)
- [Census Bureau press release, January 27, 2026: "Nation's Population Growth Slows"](https://www.census.gov/newsroom/press-releases/2026/population-growth-slows.html)
- [Census Bureau resident population by state, annual, via FRED (California shown; every state has a series)](https://fred.stlouisfed.org/series/CAPOP)
- [Census Bureau, cartographic boundary files, 2017 edition (the map's state shapes)](https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html), as prepared in [us-atlas](https://github.com/topojson/us-atlas)
- [Census Bureau, population estimates methodology](https://www.census.gov/programs-surveys/popest/technical-documentation/methodology.html)
- [Census Bureau, 2024 state-to-state migration flows, American Community Survey 1-year estimates (Table 1, Excel)](https://www2.census.gov/programs-surveys/demo/tables/geographic-mobility/2024/state-to-state-migration/State_to_State_Migration_Table_2024_T13.xlsx)
- [Census Bureau tip sheet, January 21, 2026: "2024 State-to-State Migration Flows Statistics Now Available" (CB26-TPS.03)](https://www.census.gov/newsroom/press-releases/2026/2024-state-to-state-migration.html)
- [Census Bureau, state-to-state migration flows: tables and notes](https://www.census.gov/data/tables/time-series/demo/geographic-mobility/state-to-state-migration.html)
- [Bureau of Economic Analysis, "Real Personal Consumption Expenditures by State and Real Personal Income by State, 2024," February 19, 2026](https://www.bea.gov/news/2026/real-personal-consumption-expenditures-state-and-real-personal-income-state-2024)
- [FRED, regional price parities, real personal income and income per person by state (California's price level shown; each state has its own series)](https://fred.stlouisfed.org/series/CARPPALL)
