---
title: Your State's Population, and Where It's Changing
title_tag: State Population Over Time: Every State Since 1900
dek: Pick a state. Its population back to 1900, where the last five years' change came from — births and deaths, other countries, and other states — and which states its newcomers came from and its leavers went to.
date: 2026-11-22
kind: tool
more_tools: kept-up, my-inflation-rate
---

<div class="sp-mount" data-src="/assets/states.json"><p class="rb-noscript">This tool needs JavaScript. The section How it's worked out, below, explains where the figures come from, and Sources links to them.</p></div>
<script src="../assets/states.js?v=20261122d"></script>

## How it's worked out

The Census Bureau counts everyone once a decade and estimates each state's population every July in between. The figures here are its Vintage 2025 estimates, released January 27, 2026, which run through July 1, 2025. Each year's release revises the whole series back to the 2020 census, so these numbers can differ a little from what was published a year earlier.

The bars split each year's change into three parts, the Census Bureau's "components of change." Births minus deaths is called natural change. The two migration parts are nets: how many more people moved in than moved out, counted against other countries and against other states. A bar's year runs from July 1 to June 30 — the 2025 bars cover July 2024 through June 2025. The three parts need not add exactly to the change in the total; the Census Bureau's method leaves a small residual.

Migration is the hardest part to estimate. Births and deaths come from vital records; moves are estimated from tax returns, Medicare records and other administrative data, and they are the figures that swing most from year to year.

The population line is the Census Bureau's resident-population series as carried by FRED, one value a year back to 1900 for most states (1950 for Alaska and Hawaii, which became states in 1959). Earlier decades come from the bureau's historical intercensal estimates, so the line is an estimate between censuses, not a yearly count.

The last section, which states people came from and went to, comes from a different source: the Census Bureau's American Community Survey, which asks a sample of U.S. residents where they lived a year earlier. The figures are its 2024 state-to-state migration flows, released January 21, 2026, and they count people one year and older. Because they come from a survey, each has a margin of error, shown as ±; the Census Bureau publishes them at 90% confidence, meaning there's about a 90% chance the true figure falls within that range (counting sampling error only). The net with a state is people moved in minus people moved out, and the tool marks a net that is smaller than its own margin, since the survey can't say with 90% confidence which way that one runs. It also says when the top two states in a list are too close to call. A few small flows aren't published at all because too few people in the sample made that move; those show as n/a.

These flows won't match the "other states, net" bar above. They come from 2024 survey answers about the year before, not the year to July 2025; they come from a survey rather than from tax and Medicare records; and the population estimates count moves between the states and Puerto Rico as international migration, while these tables list Puerto Rico separately. Use them for where people went, and the bars for how much each state gained or lost.

Nothing you pick is saved or sent anywhere. A link carries your state only if you copy one with it.

## Read more

- [Where Americans Are Moving](../articles/where-americans-are-moving.html): what changed in the 2025 estimates, and what people argue the moves mean.

## Sources

- [Census Bureau, Vintage 2025 state population estimates and components of change (NST-EST2025-ALLDATA)](https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/state/totals/NST-EST2025-ALLDATA.csv)
- [Census Bureau press release, January 27, 2026: "Nation's Population Growth Slows"](https://www.census.gov/newsroom/press-releases/2026/population-growth-slows.html)
- [Census Bureau resident population by state, annual, via FRED (California shown; every state has a series)](https://fred.stlouisfed.org/series/CAPOP)
- [Census Bureau, population estimates methodology](https://www.census.gov/programs-surveys/popest/technical-documentation/methodology.html)
- [Census Bureau, 2024 state-to-state migration flows, American Community Survey 1-year estimates (Table 1, Excel)](https://www2.census.gov/programs-surveys/demo/tables/geographic-mobility/2024/state-to-state-migration/State_to_State_Migration_Table_2024_T13.xlsx)
- [Census Bureau tip sheet, January 21, 2026: "2024 State-to-State Migration Flows Statistics Now Available" (CB26-TPS.03)](https://www.census.gov/newsroom/press-releases/2026/2024-state-to-state-migration.html)
- [Census Bureau, state-to-state migration flows: tables and notes](https://www.census.gov/data/tables/time-series/demo/geographic-mobility/state-to-state-migration.html)
