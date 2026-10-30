---
title: You're Looking for Work
dek: In a market where few people are laid off and few are hired, the person between jobs carries most of the cost. Three numbers say how long the wait is likely to be, and two programs decide what it costs.
date: 2026-10-29
kind: path
order: 6
---

## What reaches you, in order

1. **Openings and hires**, which decide how many doors there are. In August there was about one opening for every unemployed person, half the ratio of 2022.
2. **How long searches last**, which decides how far the money has to stretch. The typical search had lasted {{fig search_median else="11.5 weeks"}} in {{v uempmed period else="September 2026"}}, and {{fig long_term_words else="more than a quarter"}} of job seekers had been looking for six months or longer.
3. **Unemployment insurance**, which replaces part of your pay for a set number of weeks. Most states pay up to 26 weeks; fourteen pay fewer, as few as 12.
4. **Health coverage**, if it came with the job. Keeping the employer's plan means paying its full cost, about $2,400 a month for a family.
5. **The Fed**, which is cooling hiring on purpose while inflation runs above its target.

The other paths cover rent, a mortgage, a paycheck, retirement income and running a business. This one is about the gap between two paychecks.

## Openings and hires: the doors

Employers listed {{fig openings else="7.1 million"}} open jobs in {{fig openings_month else="August 2026"}} ([JTSJOL](https://fred.stlouisfed.org/series/JTSJOL)), {{fig openings_vs_2019 else="about as many as in 2019"}}. What changed is the line in front of them. There were {{fig unemployed_aligned else="7.0 million"}} unemployed people that month ([UNEMPLOY](https://fred.stlouisfed.org/series/UNEMPLOY)), against {{fig unemployed_2019 else="about 6 million"}} in 2019, so {{fig ratio_sentence else="the ratio of openings to job seekers fell to about one to one, from 1.2 in 2019 and a record 2.0 in March 2022"}}. {{check fig:unemployed_vs_2019 > 5 "more unemployed than in 2019 (the line in front of the openings)"}} {{check fig:openings_vs_2019 > -10 "openings roughly level with 2019 (what changed is the line, not the jobs)"}}

Openings are ads; hires are doors that actually open. Employers hired 5.2 million people in August, about 11% fewer than in a typical month of 2019, even though the workforce is larger now. As a share of the workforce, {{v hires_rate period else="August 2026"}}'s {{v hires_rate fmt=pct1 else="3.3%"}} hiring rate was {{fig hires_rank else="lower than in about three months out of four since 2000"}}. Layoffs, at {{v layoffs_rate fmt=pct1 else="1.0%"}}, were near the record low, {{check layoffs_rate.percentile <= 10 "layoffs near the record low"}} and that is the other half of the frozen market: few people are being pushed out, so few seats open up. [The frozen job market](the-frozen-job-market.html) has what the combination has meant before.

## How long it takes

The median unemployed person in {{v uempmed period else="September 2026"}} had been looking for {{fig search_median else="11.5 weeks"}} ([UEMPMED](https://fred.stlouisfed.org/series/UEMPMED)), {{fig search_median_vs_2019 else="up from an average of 9.2 in 2019"}}. The average was {{fig search_mean else="24.8 weeks"}} ([UEMPMEAN](https://fred.stlouisfed.org/series/UEMPMEAN)), pulled up by the long searches: {{fig long_term_pct else="27.1%"}} of the unemployed ([LNS13025703](https://fred.stlouisfed.org/series/LNS13025703)), {{fig long_term_count else="about 1.9 million"}} people, had been looking for 27 weeks or more, against {{fig long_term_2019 else="21%"}} in 2019. At the worst of the last long slump, in 2010, the median was 25 weeks and nearly half of the unemployed had been looking for more than six months.

Long searches carry a penalty of their own. In a field experiment that sent fictitious résumés to real job openings in 100 cities, employers called back applicants less often the longer they had been out of work, with most of the drop in the first eight months, and the penalty was steepest where jobs were plentiful: employers there read a long gap as a warning sign.

{{chart id=unemployment range=25y ov=uempmed height=720 caption="The unemployment rate, and below it the median number of weeks the unemployed have been looking. The two usually rise together; in 2020 the median fell because millions were laid off at once and had been out only a few weeks."}}

## Unemployment insurance, and where it ends

Unemployment insurance is run by the states, so how much and for how long depend on where you worked. Twenty-six weeks is the standard. As of July 2026, fourteen states paid fewer at most, as few as 12 in Arkansas and Florida, and several of them tie the number of weeks to their own unemployment rate, so the limit rises if the state's job market worsens; Massachusetts pays up to 30. In the second quarter of 2026 the average weekly benefit was about $501, people collected for an average of 15.8 weeks, and about four in ten people who started collecting used up all their weeks. Benefits are taxable income.

Only people who lose a job through no fault of their own qualify. People who quit, people entering the workforce for the first time, and most gig and contract workers do not, which is why [jobless claims](what-are-jobless-claims.html) undercount the unemployed: about {{v continuing_claims fmt=millions1 else="1.7 million"}} people were collecting benefits in {{v continuing_claims period else="mid-October"}}, against {{fig unemployed_count else="7.1 million"}} unemployed in {{v unemployed period else="September 2026"}} ([UNEMPLOY](https://fred.stlouisfed.org/series/UNEMPLOY)).

## Health coverage

If your coverage came with the job, two options pick it up. COBRA lets you stay on your employer's plan for up to 18 months, but you pay the whole premium, your share and the employer's, plus up to 2%. With the average employer plan costing $9,804 a year for one person and $28,303 for a family in 2026, that comes to about $830 or $2,400 a month. The other route is the ACA marketplace, which lets you enroll outside the annual window within 60 days of losing coverage. Marketplace coverage costs more for many people in 2026 than it did in 2025: the extra subsidies Congress added in 2021 expired, and marketplace enrollment fell for the first time in seven years.

## The offer

Finding a job is not the same as getting back to where you were. Of the 3.3 million workers who lost jobs they had held for at least three years in 2023–25, 66% were working again in January 2026, 18% were still looking and 16% had stopped. Of those back in full-time jobs, about half were earning as much as or more than before; two years earlier the share was about 62%. The cost lasts: Steven Davis and Till von Wachter estimated that men who lost long-held jobs in mass layoffs gave up the equivalent of 1.4 years of earnings over the next twenty years when unemployment was below 6%, and 2.8 years when it was above 8%.

## The Fed is cooling hiring on purpose

The Fed raised its rate in September and held it at 3.75–4% on October 28, with two of the twelve voting members wanting another increase. Its aim is to keep the oil shock from spreading into wages and prices, and the channel it works through is hiring: higher rates mean fewer expansions and fewer new positions. For someone already employed, that shows up as a smaller raise. For someone looking, it shows up as fewer openings. [The fed funds rate](what-is-the-fed-funds-rate.html) traces the lag, and [supply vs. demand](supply-vs-demand.html) is the argument about whether an oil shock calls for it at all.

## Where you come out ahead

Few people are being laid off, so the line behind you is short: new claims for unemployment insurance have averaged under 200,000 a week, low for a workforce this size. With immigration down sharply, the economy needs fewer new jobs each month to keep unemployment steady, and the 50,000 or so a month it has been adding is close to that pace, which is why the rate has barely moved. And the people who do land somewhere new are being paid for it again: the extra raise for changing jobs, which disappeared in 2024–25, is back to about its 2019 size. Against that: half as many openings per job seeker as in 2022, searches that last longer than before the pandemic, and benefits that run out before the typical long search ends in the states that pay the fewest weeks.

## What people argue about

**Whether benefits make searches longer.** One side: paying people while they look reduces the pressure to take the first offer, which is the argument states have made for cutting the number of weeks. The other: the largest increase in unemployment benefits in U.S. history, in 2020–21, had small effects on how fast people found jobs, and Raj Chetty estimated that about 60% of benefits' effect on search length comes from giving people enough cash to keep looking for a better match, not from weaker incentives. Both sides agree that benefits keep spending up while people look; the argument is over what a longer search buys.

**Whether AI is behind weak entry-level hiring.** One side: Stanford researchers found that employment of 22-to-25-year-olds in the occupations most exposed to AI fell 13% relative to other workers after generative AI spread, while older workers in the same occupations held steady or grew. The other: the Budget Lab at Yale found no discernible disruption in the broader labor market in the 33 months after ChatGPT's release, and slow hiring of young people also fits a cooling market and high interest rates. Both are reading the same few years, which may be too few to tell.

## See also

- [The unemployment rate](what-is-the-unemployment-rate.html): who is counted, and the broader U-6 measure.
- [Jobless claims](what-are-jobless-claims.html): the weekly filings, and who they leave out.
- [The frozen job market](the-frozen-job-market.html): low hiring and low layoffs, and what that has meant before.
- [You work for a wage](you-work-for-a-wage.html): pay, prices and leverage, once the job is found.
- [Growth without hiring](growth-without-hiring.html): why the economy grew in the summer while hiring barely moved.

## Sources

- [FRED: job openings (JTSJOL)](https://fred.stlouisfed.org/series/JTSJOL), [hires (JTSHIL)](https://fred.stlouisfed.org/series/JTSHIL) and [hires rate (JTSHIR)](https://fred.stlouisfed.org/series/JTSHIR), [layoffs and discharges rate (JTSLDR)](https://fred.stlouisfed.org/series/JTSLDR), [unemployed persons (UNEMPLOY)](https://fred.stlouisfed.org/series/UNEMPLOY).
- [FRED: median weeks unemployed (UEMPMED)](https://fred.stlouisfed.org/series/UEMPMED), [average weeks (UEMPMEAN)](https://fred.stlouisfed.org/series/UEMPMEAN), [share unemployed 27 weeks or longer (LNS13025703)](https://fred.stlouisfed.org/series/LNS13025703), [number unemployed 27 weeks or longer (UEMP27OV)](https://fred.stlouisfed.org/series/UEMP27OV).
- [U.S. Department of Labor, Significant Provisions of State Unemployment Insurance Laws, July 2026](https://oui.doleta.gov/unemploy/content/sigpros/2020-2029/July2026.pdf): weeks of benefits by state; [UI Data Summary, second quarter 2026](https://oui.doleta.gov/unemploy/data_summary/DataSum.asp): average weekly benefit, duration and exhaustions; [Department of Labor, unemployment insurance](https://www.dol.gov/general/topic/unemployment-insurance): who qualifies; [IRS, Topic 418, unemployment compensation](https://www.irs.gov/taxtopics/tc418); [FRED: continuing claims (CCSA)](https://fred.stlouisfed.org/series/CCSA).
- [Department of Labor, An Employee's Guide to Health Benefits Under COBRA](https://www.dol.gov/agencies/ebsa/about-ebsa/our-activities/resource-center/publications/an-employees-guide-to-health-benefits-under-cobra); [HealthCare.gov, special enrollment periods](https://www.healthcare.gov/coverage-outside-open-enrollment/special-enrollment-period/); [KFF, 2026 Employer Health Benefits Survey](https://www.kff.org/health-costs/2026-employer-health-benefits-survey/); [KFF, How Has ACA Marketplace Enrollment Changed Across States in 2026?](https://www.kff.org/affordable-care-act/how-has-aca-marketplace-enrollment-changed-across-states-in-2026/) (July 2026).
- [BLS, Worker Displacement: 2023–2025](https://www.bls.gov/news.release/disp.nr0.htm) (August 2026); [Davis and von Wachter, "Recessions and the Costs of Job Loss"](https://www.nber.org/papers/w17638) (2011); [Kroft, Lange and Notowidigdo, "Duration Dependence and Labor Market Conditions"](https://www.nber.org/papers/w18387) (2012).
- [Ganong, Greig, Noel, Sullivan and Vavra, "Spending and Job-Finding Impacts of Expanded Unemployment Benefits"](https://www.nber.org/papers/w30315); [Chetty, "Moral Hazard vs. Liquidity and Optimal Unemployment Insurance"](https://www.nber.org/papers/w13967) (2008); [Brynjolfsson, Chandar and Chen, "Canaries in the Coal Mine?"](https://siepr.stanford.edu/publications/working-paper/canaries-coal-mine-six-facts-about-recent-employment-effects-artificial) (Stanford, August 2025); [The Budget Lab at Yale, "Evaluating the Impact of AI on the Labor Market: Current State of Affairs"](https://budgetlab.yale.edu/sites/default/files/page_to_pdf/1154/publication_1154.pdf) (October 2025).
