---
title: Lesson: A Record in Which Dollars?
dek: One class period on real and nominal prices, using a number everyone notices: the price of a gallon of gas. For teachers; the student handout is a separate page.
date: 2026-11-12
kind: page
menu: articles
---

## At a glance

- **Who:** grades 9–12 economics or personal finance; adult education. Works as a follow-up to [Lesson 1, Inflation in Context](lesson-inflation.html).
- **Time:** 45 minutes (hook 5, chart 15, activity 15, discussion 10).
- **Standard:** Council for Economic Education, [National Content Standards in K–12 Economics, 3rd ed. (2025)](https://www.councilforeconed.org/wp-content/uploads/National-Content-Standards-in-K–12-Economics-3rd-Edition.pdf), Standard 15: Inflation, and Standard 4: Markets.
- **Pages used:** the [Gasoline chart](../chart.html?id=gas&range=all), [Real vs. Nominal](real-vs-nominal.html), [What Sets the Price of Gas](what-sets-the-price-of-gas.html) and [Has It Kept Up With Prices?](/tools/kept-up.html).
- **Materials:** one device per pair, and the [student handout](lesson-gas-in-todays-dollars-handout.html), printed.
- **Students leave able to:** restate an old price in today's dollars; say when "a record high" is true and when it misleads; read a chart with an as-charged line and a today's-dollars line.

## Opening hook (5 minutes)

Ask: "When was gas the most expensive it has ever been in the U.S.?"

Students who remember usually say 2022. The highest national average on the pump sign since 1990 was {{v gas.max fmt=usd2}}, in {{v gas.max period}}. Then ask: "Is a dollar in 2022 the same as a dollar now? Or in 2008?" Bridge: "Today we find out which record is the real one."

## Reading the chart together (15 minutes)

Project the [Gasoline chart](../chart.html?id=gas&range=all). It opens with two lines.

1. **Two lines.** The key names them: the price **as charged**, what the pump sign said at the time, and the price **in today's dollars**, each old price restated at today's price level. A gallon cost {{v gas fmt=usd2}} in {{v gas period}}.
2. **Where they meet.** Ask: "Why do the two lines meet at the right-hand edge?" (Today's dollars *are* today's prices, so the newest week is the same on both.)
3. **Two peaks.** Have students hover the 2008 and 2022 peaks on both lines. In today's dollars, the summer 2008 peak would be about {{fig gas_real_max else="$6.33"}}, and the June 2022 peak about {{fig gas_2022_today else="$5.71"}}. Ask: "Which year was the real record?" {{check fig:gas_real_max_year == 2008 "the real peak is 2008"}} {{check fig:gas_vs_2022_real < 0 "below the June 2022 peak in today's dollars"}}
4. **Is gas expensive now?** Read the bar under the number: its range is in today's dollars. By that measure, gas is {{fig gas_real_rank else="higher than about 80% of weeks since 1990"}}.
5. **Why the old line slopes.** Point out that the as-charged line drifts up over the decades even when gas isn't getting harder to afford. That drift is inflation, the subject of [Real vs. Nominal](real-vs-nominal.html).

## Activity: Restate the price (15 minutes)

In pairs, using [Has It Kept Up With Prices?](/tools/kept-up.html) and choosing **Something else**, with only the "Then" amount filled in, so the tool gives what it comes to now:

1. **The 2008 peak.** $4.11, July 2008. What does it come to now?
2. **The cheapest gas on the chart.** $0.91, February 1999. What does it come to now?
3. **Grandparents' gallon.** Ask an older relative what gas cost when they started driving (or use $0.36, the 1970 average for leaded regular). Enter it with that year. What does it come to now?

Then compare each answer with this week's price on the chart.

**Exit ticket:** "Finish the sentence: 'Gas hit a record high in 2022' is true if… and misleading if…"

## Discussion questions (10 minutes)

1. *Reading it.* In your own words: what is the difference between a nominal price and a real price?
2. Why does the today's-dollars line change a little every month, even for prices from long ago?
3. *Placing it.* A headline says gas "hit a record." What two questions would you ask before believing it means gas was harder to afford than ever?
4. Wages rise with inflation too. Why might a better test of "expensive" be how many minutes of work a gallon costs?
5. *Judging it.* Two headlines can both be true: "Gas hit a record in 2022" and "Gas cost more in 2008 than in 2022." Which would you want a candidate to use, and what would you want added to it?
6. [What Sets the Price of Gas](what-sets-the-price-of-gas.html) says the biggest part of the price is set on a world market. How much credit or blame should a president get for the pump price?

## Answer key

**Activity (the tool uses the Consumer Price Index; answers move slightly each month as new prices come in):**

1. Close to the chart's {{fig gas_real_max else="$6.33"}} for the 2008 peak. The tool works from monthly prices and the chart from weekly ones, so they differ by a few cents. When this lesson was written, in October 2026 dollars, the tool gave $6.31.
2. In October 2026 dollars the tool gave $1.87.
3. Depends on the year. In October 2026 dollars, $0.36 in 1970 came to $3.13, so gas at 36 cents was less of a bargain than it sounds.

Students compare each answer with this week's price on the chart; the comparison is theirs to make.

Questions:

1. Nominal is the number at the time. Real is that number adjusted for inflation, so it measures what the money could buy.
2. "Today's dollars" means the newest month's prices. Each new month resets what "today" means, so every old price is restated again.
3. In which dollars? Compared with what pay? A record as charged is common, because prices rise over time; a record in today's dollars is rarer.
4. Pay rises with inflation too, so minutes of work per gallon measures what gas costs a worker, not just a dollar. It's the same idea as real prices, using wages instead of the price index.
5. Either headline is true; what misleads is leaving out which dollars. A fair answer asks for the measure to be named and used the same way whichever side it helps. The "A record in which dollars?" section of [How a True Number Can Mislead](how-a-true-number-can-mislead.html) makes the same point with milk.
6. The page's argument section gives each side's case. A fair answer names what a president can do (release oil from the Strategic Petroleum Reserve, waive summer fuel rules or shipping restrictions, shape permits and leasing over years, use diplomacy and sanctions) and what a president can't (set the world price of crude, or suspend the federal gas tax, which only Congress can do).

## Sources

- [Regular gasoline, U.S. average retail price (GASREGW), EIA via FRED](https://fred.stlouisfed.org/series/GASREGW)
- [Consumer Price Index for All Urban Consumers, not seasonally adjusted (CPIAUCNS), FRED](https://fred.stlouisfed.org/series/CPIAUCNS), which the kept-up tool uses
- [EIA, Monthly Energy Review, Table 9.4, retail motor gasoline prices](https://www.eia.gov/totalenergy/data/monthly/pdf/sec9_6.pdf) (the 1970 average for leaded regular)
