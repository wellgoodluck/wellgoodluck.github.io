---
title: The Frozen Job Market
dek: Nobody is being laid off and nobody is being hired. The almanac's numbers have shown that combination for fifteen months. Here is what it has meant before.
date: 2026-10-28
---

## The reading

Four of the almanac's numbers describe the same thing from four sides. Payrolls grew 0.3% over the past year, the slowest twelve-month pace outside a recession in the record since 1972. Jobless claims average about 198,000 a week, and measured against the size of the workforce, 1.3 filings per thousand workers, they set a record low in August. The unemployment rate has sat between 4.1% and 4.5% for twenty months. And the Labor Department's turnover survey fills in the rest: in August, employers hired 3.3% of their workforce, laid off 1.0%, and 1.9% of workers quit, the hiring and quitting rates at levels last seen in the early 2010s and the layoff rate near the lowest on record. {{check unemployment.value >= 4.1 "unemployment between 4.1% and 4.5%"}} {{check unemployment.value <= 4.5 "unemployment between 4.1% and 4.5%"}} {{check hires_rate.value <= 3.5 "hiring at early-2010s levels"}} {{check quits_rate.value <= 2.0 "quits at early-2010s levels"}} {{check layoffs_rate.percentile <= 10 "layoffs near the record low"}} {{check claims.value <= 230000 "claims about 198,000"}}

That is a market in which it is very hard to lose a job and very hard to find one. For the employed it reads as security. For the twenty-two-year-old, the laid-off, and the person who wants to leave a bad job, it reads as a wall. The pages on [claims](what-are-jobless-claims.html), [unemployment](what-is-the-unemployment-rate.html), [wage work](you-work-for-a-wage.html) and [small business](you-run-a-small-business.html) each touch it. This article asks what the combination has meant historically.

{{chart id=unemployment range=10y ov=hires_rate,quits_rate,layoffs_rate caption="The unemployment rate with the three turnover rates from the JOLTS survey. The 2026 pattern is low layoffs, low hiring, low quits: the market has stopped churning in both directions."}}

## The precedents

Searching the record since 1972 for stretches of at least five months in which payroll growth ran below 1% a year, claims were below their five-year norm, and no recession had ended within the prior two years turns up four episodes, two of them in the last two years:

<table><thead><tr><th>Episode</th><th>Months</th><th>Payroll growth, year over year</th><th>Claims vs. prior five years</th><th>Unemployment, start → end</th><th>Unemployment a year after</th><th>What followed</th></tr></thead><tbody><tr><td>Dec 2003 – Apr 2004</td><td>5</td><td>0.4%</td><td>-8%</td><td>5.7% → 5.6%</td><td>5.2%</td><td>Recovery; hiring resumed in spring 2004</td></tr><tr><td>Aug 2007 – Dec 2007</td><td>5</td><td>0.9%</td><td>-5%</td><td>4.6% → 5.0%</td><td>7.3%</td><td>Recession began Jan 2008</td></tr><tr><td>Aug 2024 – May 2025</td><td>10</td><td>0.8%</td><td>-2%</td><td>4.2% → 4.3%</td><td>4.3%</td><td>Neither; slid into the current episode</td></tr><tr><td>Jul 2025 – Sept 2026</td><td>15</td><td>0.3%</td><td>-4%</td><td>4.3% → 4.2%</td><td>—</td><td>Open</td></tr></tbody></table>

The two older episodes resolved in opposite directions, and the difference between them is the thing to watch.

**Winter 2003–04** was the tail of the "jobless recovery." Growth had resumed after 2001, but payrolls fell for two more years as businesses squeezed output from the staff they had. Claims were low because the firing was over; hiring was low because nobody trusted the recovery. It broke in the spring of 2004: hiring resumed, payrolls added 300,000 in March, and unemployment fell for the next three years. The thaw came from demand; the Fed's rate was 1% and housing was accelerating.

**Autumn 2007** looked the same from the claims side and was the month before a recession. Payroll growth had slowed to 0.9%, claims were still below their norm, unemployment had edged up from 4.6% to 5.0%. The tell, visible only in hindsight, was that claims had turned: still low, but rising from their 2006 floor, and continuing claims were climbing faster. By the following December unemployment was 7.3%.

The 2024–25 episode slid into the current one without resolving. What the current episode has in common with 2003–04 is that claims are still falling, not rising; what it has in common with 2007 is a Fed that has been raising rates and a housing market that has stalled. The record offers one of each.

## What is different this time

Two things have no precedent in the table. The first is the size of the workforce effect: immigration fell sharply in 2025, so the number of jobs needed to hold unemployment steady fell with it, to well under 100,000 a month by most estimates. Payroll growth of 0.3% would have meant rising unemployment in any earlier episode; in this one unemployment has been flat, which is why the jobs number and the unemployment rate have been telling different stories all year. The second is the Fed's direction. In both 2003 and 2007 the Fed was holding or cutting; in 2026 it raised rates into the freeze to meet an oil shock, which [supply vs. demand](supply-vs-demand.html) takes up.

## What people argue about

**Strong or stuck.** One side: a 4.2% unemployment rate with record-low layoffs is a healthy market that has simply stopped growing because the workforce has, and the people inside it are doing fine. The other: a market with the hiring rate of 2013 and the quits rate of 2014 is one in which nobody can move, which the 2003–04 episode shows is survivable and the 2007 episode shows is fragile. Both readings fit the numbers; which one you hold mostly depends on whether you have a job.

**Whether it thaws from the top or the bottom.** A thaw from the top means hiring resumes, as in 2004, and it needs demand: lower rates, or a shock passing. A thaw from the bottom means layoffs start, as in 2008, and claims will show it first; the rule of thumb on the claims page is a sustained rise of 50,000 in the four-week average. Economists who expect the first point to the balance sheets of households and firms, which are stronger than in 2007; those who expect the second point to the Fed's direction and a job market that has been living off low churn for two years.

**Whether the Fed should cut into it.** Cutting would thaw hiring and risks feeding the inflation it is fighting; holding risks turning the freeze into the 2007 kind. The committee split in October, with two members wanting a hike. The almanac will show which way it went in the claims line before it shows it anywhere else.

## See also

- [Jobless claims](what-are-jobless-claims.html): the smoke detector, and the 50,000 rule of thumb.
- [The unemployment rate](what-is-the-unemployment-rate.html): why it can hold still while hiring stops.
- [The jobs report](what-is-the-jobs-report.html): the breakeven number, and why it fell.
- [You work for a wage](you-work-for-a-wage.html) and [you run a small business](you-run-a-small-business.html): the freeze from both sides of the hiring desk.

## Sources

- [BLS, Job Openings and Labor Turnover Survey, August 2026](https://www.bls.gov/news.release/archives/jolts_09292026.htm): hires 3.3%, quits 1.9%, layoffs and discharges 1.0%; [FRED JTSHIR](https://fred.stlouisfed.org/series/JTSHIR), [JTSQUR](https://fred.stlouisfed.org/series/JTSQUR), [JTSLDR](https://fred.stlouisfed.org/series/JTSLDR).
- Episodes computed from the almanac's data: [FRED PAYEMS](https://fred.stlouisfed.org/series/PAYEMS) (twelve-month growth), [IC4WSA](https://fred.stlouisfed.org/series/IC4WSA) (monthly average of the four-week average, divided by payroll employment and compared with the median of the prior sixty months), [UNRATE](https://fred.stlouisfed.org/series/UNRATE). Criteria: payroll growth under 1.0%, claims below the five-year median, no recession ended within the prior 24 months, at least five consecutive months.
- [NBER, business cycle dates](https://www.nber.org/research/business-cycle-dating).
