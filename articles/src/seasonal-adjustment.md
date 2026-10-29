---
title: Seasonal Adjustment: Why December Doesn't Count as a Boom
dek: Nearly every number on this site has had the calendar removed from it. That is the right thing to do, and it is the reason some months look strange.
date: 2026-10-28
kind: concept
---

## In one sentence

Seasonal adjustment removes the part of a month's change that happens every year at that time, so that what's left is the part that's news.

## The analogy

A store's December. Sales double every December and fall by half every January, and nobody who runs the store treats January as a collapse. The owner compares this December with last December, or asks whether this December was a bigger jump than usual. Seasonal adjustment is that second question, done by formula: the statistical agencies estimate what each month normally does, from the last several years, and report the difference. A seasonally adjusted gain of 100,000 jobs in January means the economy did 100,000 better than the usual January layoffs; the raw count was probably negative.

The raw swings are much larger than the news. Unemployment claims run over 300,000 a week in early January, raw, against about 200,000 adjusted; the economy adds roughly a million jobs every June and loses more than two million every January before adjustment; gasoline prices rise every spring. Without adjustment the charts on this site would be a sawtooth, and the recessions would be hard to see in it.

{{chart id=cpi range=5y ov=cpi_first caption="Inflation as first reported against the current figure. The gaps are mostly the seasonal factors being recalculated each February; the index itself is never revised."}}

## Where the analogy breaks

The store owner knows her December. The agencies estimate it, from a few years of history, and the estimate goes wrong in three ways. When a holiday moves (Easter in March one year and April the next), the usual pattern misfires. When something unusual lands in a usual month, the adjustment can't tell them apart: the 2020 shutdown fell in March and April and spent the next five years distorting what "normal" looked like for those months, which is the main reason spring data were strange through 2025. And the factors are recalculated every year, so last year's adjusted figures change a little each February and January; that is the gap in the chart above. Some patterns also survive the adjustment: first-quarter GDP ran weak for a decade for reasons the Bureau of Economic Analysis eventually traced to its own method, and fixed in stages.

## What people argue about

**Whether the adjustment hides more than it reveals.** When the adjusted number says "up" and the raw number says "down," one side says the adjustment is doing its job; the other says the raw number is what happened and the adjustment is an estimate layered on top. Both are right, and the honest reading is to look at the raw year-over-year change when the adjusted monthly figure looks odd, which the agencies publish alongside it. January and the weeks around Thanksgiving and Christmas are the months and weeks this applies to most.

**The post-2020 distortion.** The pandemic months were so far outside any pattern that the agencies had to decide whether to treat them as normal variation or as an outlier to exclude. They chose differently for different series, and for several years the spring readings of inflation, claims and payrolls carried a residual that economists argued about every March. One camp says the agencies should have excluded 2020 everywhere; the other says that would have been a judgment call baked into the data, and that five years of new history has mostly washed it out.

**Whether to publish the raw figures first.** A few economists argue the raw numbers should lead, with the adjusted ones as a companion, on the grounds that the public should see what was actually counted. The agencies' answer is the sawtooth: a raw series is unreadable month to month, and the adjusted one is the only version in which a turn in the economy is visible before it is a year old.

## See also

- [Revisions and vintages](revisions-and-vintages.html): the other reason a published number changes after publication.
- [Jobless claims](what-are-jobless-claims.html): the weekly number where the calendar bites hardest.
- [The jobs report](what-is-the-jobs-report.html): the January benchmark and seasonal recalculation.

## Sources

- [BLS, Seasonal adjustment in the CPI](https://www.bls.gov/cpi/seasonal-adjustment/), including the annual recalculation.
- [BLS, Seasonal adjustment of the Current Employment Statistics](https://www.bls.gov/web/empsit/cesseasadj.htm).
- [Federal Reserve Bank of San Francisco, "The Puzzle of Weak First-Quarter GDP Growth" (2015)](https://www.frbsf.org/wp-content/uploads/el2015-16.pdf), the residual-seasonality finding, and [BEA working paper 2021-2](https://www.bea.gov/system/files/papers/BEA-WP2021-2.pdf) on what was changed.
- [FRED: initial claims, not seasonally adjusted (ICNSA)](https://fred.stlouisfed.org/series/ICNSA) against [seasonally adjusted (ICSA)](https://fred.stlouisfed.org/series/ICSA), the sawtooth and the signal.
