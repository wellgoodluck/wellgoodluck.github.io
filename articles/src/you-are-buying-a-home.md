---
title: You're Buying a Home
dek: You borrow at a rate set in the bond market, pay a price set by the handful of houses for sale near you, hand over cash at closing to people you met that month, and then start two bills that can rise for as long as you own the place. The numbers reach you in that order.
date: 2026-11-11
kind: path
order: 9
hook: how the numbers reach a home buyer
---

## What reaches you, in order

1. **The [mortgage rate](what-is-the-mortgage-rate.html)**, every Thursday. It follows the 10-year Treasury more than it follows the Fed.
2. **The price**, slowly. National [home prices](../chart.html?id=home_prices) move a few percent a year in most years; the houses for sale near you can move faster in either direction.
3. **What is for sale.** How many homes are listed, and how long they sit, decides who has the leverage. [How to read a housing headline](how-to-read-a-housing-headline.html) covers those numbers.
4. **The cash to close**: the down payment, plus the tolls in [Who gets paid when a house sells](who-gets-paid-when-a-house-sells.html).
5. **The bills that start after the keys**: property tax and [homeowner's insurance](what-homeowners-insurance-costs.html), usually collected with the mortgage payment.
6. **Your own pay**, because a lender counts it and you live on what's left. [You work for a wage](you-work-for-a-wage.html) follows those numbers.

Figures below are as of early November 2026. This page describes how the numbers work. It doesn't say whether to buy.

## The rate

The average 30-year fixed rate was {{v mortgage fmt=pct2}} on {{v mortgage period as=day}} ([Freddie Mac, via FRED](https://fred.stlouisfed.org/series/MORTGAGE30US)). {{check mortgage.value >= 6.74 "payment examples on this page use 7.24%, the late-October 2026 rate"}}{{check mortgage.value <= 7.74 "payment examples on this page use 7.24%, the late-October 2026 rate"}} On a $400,000 house with 20% down, the loan is $320,000. At 7.24%, the average in late October 2026, the monthly principal and interest is $2,181. A rate one point lower makes it $1,968; one point higher, $2,402. So each point is worth roughly $215 to $220 a month on that loan. At 3%, where rates stood in 2021, the same loan cost $1,349.

Turn it around and the rate sets the price you can pay. The $2,181 that carries a $320,000 loan at 7.24% would carry about $354,600 at 6.24% and about $290,600 at 8.24%.

{{chart id=mortgage range=25y caption="The average 30-year fixed mortgage rate. Each point is worth roughly $215 to $220 a month on a $320,000 loan."}}

Paying points at closing lowers the rate: a point is interest paid up front. In 2023 more than half of single-family loans carried some ([CFPB](https://www.consumerfinance.gov/about-us/newsroom/cfpb-report-finds-significant-drop-in-annual-mortgage-applications-and-originations-in-2023)).

## The price

The almanac's home price number, an index that follows the same houses from one sale to the next, was up {{v home_prices}} in {{v home_prices period}} from a year earlier. Hourly pay was up {{v pay}} in {{v pay period}}. The median existing home sold in September for $417,500, the highest for any September on record ([NAR](https://www.nar.realtor/newsroom/existing-home-sales-increased-1-5-in-september-according-to-nar-report); [Associated Press](https://www.ajc.com/news/2026/10/us-home-sales-rose-in-september-but-slowed-from-a-year-earlier-as-mortgage-rates-prices-rose/)). The median new house sold for $400,400, 3.9% less than a year earlier, a difference within the survey's margin of error ([Census Bureau](https://www.census.gov/construction/nrs/pdf/newressales_202609.pdf)). It was the seventh month in a row that the median new house cost less than the median existing one ([Real Estate News](https://www.realestatenews.com/2026/10/27/new-home-sales-slowed-in-september-but-still-beat-forecasts)).

None of those is the price of the house you want. [Four numbers for one house](four-numbers-for-one-house.html) covers why the asking price, the online estimate, the appraisal and the tax value all differ.

## The cash to close

Besides the down payment, a buyer pays the lender's charges. The median home-purchase borrower paid $6,684 in loan costs in 2023, the latest year reported ([CFPB](https://files.consumerfinance.gov/f/documents/cfpb_2023-mortgage-market-activity-and-trends_2024-12.pdf)). Title insurance, transfer taxes and, since 2024, sometimes the buyer's own agent can be added to that, depending on the state and on what the seller agrees to pay. [Who gets paid when a house sells](who-gets-paid-when-a-house-sells.html) goes booth by booth.

## After the keys

A fixed-rate loan fixes principal and interest. Two other parts of the monthly payment are not fixed.

**Property tax.** Your bill may not be the seller's bill. In California the taxable value resets to the purchase price when a house sells and then generally rises no more than 2% a year ([California Board of Equalization](https://www.boe.ca.gov/proptaxes/pdf/pub29.pdf)); other states revalue on their own schedules. [How a property tax rate is set](how-a-property-tax-rate-is-set.html) and [how states limit property taxes](property-tax-limits-by-state.html) cover both.

**Insurance.** A lender requires it. The average single-family borrower paid $209 a month for property insurance in the second quarter of 2026, 9.6% of the average payment and nearly 80% more than at the start of 2020. It ranged from 4.3% of the payment in San Jose to 24.3% in New Orleans ([ICE](https://www.businesswire.com/news/home/20260910688065/en/); [HousingWire](https://www.housingwire.com/articles/ice-property-insurance-record-high/)).

## If you keep renting

Rents were up {{v rent}} in {{v rent period}} from a year earlier. [You rent](you-rent.html) follows a renter's numbers the same way this page follows a buyer's.

## Where you come out ahead

More houses are for sale than a year ago: 1.60 million existing homes at the end of September, up 4.6%, a 4.8-month supply ([NAR](https://www.nar.realtor/newsroom/existing-home-sales-increased-1-5-in-september-according-to-nar-report)). By Redfin's count, 60.5% of homes sold that month went for less than their original asking price ([Redfin](https://www.redfin.com/news/pending-home-sales-sink-rates/)). Against that: the rate is above 7%{{check mortgage.value >= 7 "the buying path says the rate is above 7%"}}, so the same house costs far more a month than it did in 2021; existing-home prices have risen from a year earlier for 39 months in a row ([NAR](https://www.nar.realtor/newsroom/existing-home-sales-increased-1-5-in-september-according-to-nar-report)); and insurance, at $209 a month, is the highest in ICE's records.

## What people argue about

**Buy now or wait.** Those who say prices will hold point to the 39 straight months of year-over-year increases in existing-home prices. Those who say a buyer gains by waiting point to rising inventory and to the one listing in five that has cut its price ([Redfin](https://www.redfin.com/news/housing-market-update-pending-sales-lowest-level-since-2023)). Both are reading the same reports. This page doesn't pick.

**Whether the rate will fall.** A lower Fed rate does not promise a lower mortgage rate. In late 2024 the Fed cut by a full point and the average mortgage rate rose, from 6.09% in mid-September to 6.85% at the end of December. In 2025 the Fed cut again and the rate fell, from 7.04% in January to 6.17% at the end of October ([Freddie Mac, via FRED](https://fred.stlouisfed.org/series/MORTGAGE30US)). [What the mortgage rate is](what-is-the-mortgage-rate.html) explains what moves it.

## See also

- [What the mortgage rate is](what-is-the-mortgage-rate.html), [Who gets paid when a house sells](who-gets-paid-when-a-house-sells.html), [Four numbers for one house](four-numbers-for-one-house.html) and [What homeowner's insurance costs](what-homeowners-insurance-costs.html).
- [How to read a housing headline](how-to-read-a-housing-headline.html): the monthly reports behind this page.
- [You rent](you-rent.html): the same numbers for a renter.
- Charts: [mortgage rate](../chart.html?id=mortgage), [home prices](../chart.html?id=home_prices) and [rent](../chart.html?id=rent).

## Sources

- The rate: [Freddie Mac 30-year fixed rate, via FRED](https://fred.stlouisfed.org/series/MORTGAGE30US). Payments are principal and interest on a 30-year loan, our arithmetic.
- The figures that update with the almanac, via FRED: [FHFA purchase-only house price index (HPIPONM226S)](https://fred.stlouisfed.org/series/HPIPONM226S); [average hourly earnings (AHETPI)](https://fred.stlouisfed.org/series/AHETPI); [rent of primary residence (CUSR0000SEHA)](https://fred.stlouisfed.org/series/CUSR0000SEHA).
- Prices and supply: [National Association of Realtors, existing-home sales, September 2026](https://www.nar.realtor/newsroom/existing-home-sales-increased-1-5-in-september-according-to-nar-report) (October 13, 2026); [Associated Press, via the Atlanta Journal-Constitution](https://www.ajc.com/news/2026/10/us-home-sales-rose-in-september-but-slowed-from-a-year-earlier-as-mortgage-rates-prices-rose/); [Census Bureau and HUD, Monthly New Residential Sales, September 2026](https://www.census.gov/construction/nrs/pdf/newressales_202609.pdf) (October 27, 2026); [Real Estate News, on new home sales](https://www.realestatenews.com/2026/10/27/new-home-sales-slowed-in-september-but-still-beat-forecasts) (October 27, 2026); [Redfin, September 2026 housing report](https://www.redfin.com/news/pending-home-sales-sink-rates/); [Redfin, four weeks ending September 13, 2026](https://www.redfin.com/news/housing-market-update-pending-sales-lowest-level-since-2023).
- Costs: [CFPB, 2023 Mortgage Market Activity and Trends](https://files.consumerfinance.gov/f/documents/cfpb_2023-mortgage-market-activity-and-trends_2024-12.pdf) and [its summary](https://www.consumerfinance.gov/about-us/newsroom/cfpb-report-finds-significant-drop-in-annual-mortgage-applications-and-originations-in-2023); [California State Board of Equalization, California Property Tax: An Overview](https://www.boe.ca.gov/proptaxes/pdf/pub29.pdf); [ICE, September 2026 Mortgage Monitor release](https://www.businesswire.com/news/home/20260910688065/en/) and [HousingWire's report on it](https://www.housingwire.com/articles/ice-property-insurance-record-high/).
