---
title: You Own With a Fixed Mortgage
dek: The payment never changes, which is the whole point. Everything around it does, and the thing that changes most is what the payment is worth.
date: 2026-10-28
updated: 2026-10-30
kind: path
order: 2
---

## What reaches you, in order

1. **Insurance and property tax**, the two parts of a house payment that aren't fixed. They reset every year and they have been doing the moving since 2022.
2. **Inflation**, which shrinks your payment in real terms every month without your noticing. The quiet one.
3. **The Fed**, through what your savings earn and what a home equity line or credit card costs: days to a statement.
4. **Mortgage rates**, though yours is locked. Today's rate sets the price of leaving and the pool of buyers for your house.
5. **Housing starts**, slowly, through what gets built near you.

Jobs, jobless claims and GDP reach you the way they reach everyone, through your paycheck. This page is about the five above.

## Insurance and property tax

If your payment includes an escrow for taxes and insurance, the fixed part of it is the smaller surprise. Homeowners insurance premiums rose by roughly half between 2020 and 2025 in the states most exposed to hurricanes, hail and wildfire, and by a quarter or more elsewhere, as rebuilding costs rose with the price of lumber and labor and as insurers repriced catastrophe risk. Several large insurers stopped writing new policies in parts of California and Florida. Property taxes follow home prices with a lag of one to three years, depending on how often your county reassesses, and the 45% rise in prices from 2020 to 2023 is still working through assessment rolls in much of the country. Some states cap the annual increase in assessed value; most don't.

Neither cost shows up in the almanac directly. Both sit inside the inflation number, where insurance is a line of its own and property tax is not counted at all, which is one of the gaps between the index and what owners feel.

## Inflation shrinks your payment

A $2,000 monthly payment fixed in 2020 is about {{fig pmt2000_2020 else="$1,540"}} in 2020 dollars at {{v cpi_index period else="September 2026"}} prices: prices have risen {{fig prices_since_2020 else="30%"}} since, and the payment hasn't. Fixed in 2022, it is about {{fig pmt2000_2022 else="$1,740"}}. This is the mirror image of the saver's loss in [real vs. nominal](real-vs-nominal.html): the lender agreed to a fixed number of dollars, and every month of inflation makes those dollars easier to come by. Your wages, rent for the next owner, and the price of the house all rose; the debt didn't. Over a 30-year loan at even 2–3% inflation, the final payments are made in dollars worth about half the first ones.

{{chart id=cpi range=10y ov=price_level height=720 caption="Inflation (top) and the price level (below, 2019 = 100). A fixed payment is a horizontal line against the lower chart: whatever the level does, the dollars owed stay put."}}

## The Fed, through everything that isn't the mortgage

Your mortgage rate ignores the Fed. The rest of your finances don't. A home equity line is priced at prime plus a margin, and prime moves the day the Fed does. Credit cards and car loans move within a statement or two. On the other side, a high-yield savings account or money market fund reprices within days, so a Fed cut is a cut to your interest income, and the 2022–23 hikes were the first time since 2007 that cash paid a real return. [The Fed funds rate](what-is-the-fed-funds-rate.html) has the full order of arrival.

## Mortgage rates, though yours is locked

Two effects, both about leaving. First, the price of moving: if you hold a 3% mortgage and the average rate on {{v mortgage period as=day}} was {{v mortgage fmt=pct1}}, the same loan on the next house costs about {{fig pmt_gap_100}} more a month per $400,000 borrowed, and the Federal Housing Finance Agency estimates that each point of gap cuts the chance of a sale by about 18%. That is the lock-in effect, and it is why so few homes are for sale. Second, the price of your house: fewer buyers can qualify at 7% than at 3%, {{check mortgage.value >= 6.5 "rates near 7%"}} which should push prices down, and mostly hasn't, because lock-in cut the number of sellers at the same time. The result is a market with few transactions at high prices, which is good for your net worth on paper and bad for anyone who needs to move.

{{chart id=mortgage range=10y caption="The 30-year mortgage rate. The gap between where it was in 2020–21 and where it is now is the lock-in effect: the cost of trading a loan taken at the low for one taken today."}}

## Housing starts

Slowly, and locally. New supply holds prices down over years, and the effect is strongest within a few miles. A subdivision or apartment project nearby competes with your house when you sell and lowers rents for whoever would otherwise have bought it. [Housing starts](what-are-housing-starts.html) has the lags.

## Where you come out ahead

Nearly everywhere, which is why the arguments below are mostly about whether that's fair. The payment is fixed while rents rose about 36% since 2019 ([BLS rent index](https://fred.stlouisfed.org/series/CUSR0000SEHA)); inflation erodes the debt; the house rose with prices; and the interest on the mortgage is partly deductible. Against that, three things. You carry the costs a renter doesn't: insurance, property tax, and maintenance, which is mostly labor and has risen faster than the index. Your wealth is in one asset in one zip code that you can't spend without borrowing against it or moving, and moving is what the lock-in makes expensive. And the fixed payment that protected you on the way up would protect you just as well if prices fell, which they sometimes do.

## What people argue about

**Whether home equity is wealth.** On paper, American homeowners gained trillions since 2020. One side says that is real wealth: it can be borrowed against, left to heirs, or realized by downsizing. The other says a gain you can only spend by selling into a market where the next house costs the same, or by borrowing at today's rates, is wealth only in the net-worth survey, and that the lock-in effect has made it less liquid than at any time on record. Both are describing the same balance sheet.

**Property tax caps.** States that cap assessment increases (California since 1978, Florida, others) protect long-time owners from being taxed out of their homes by price rises they didn't cause. Critics say the cap shifts the burden to new buyers, who pay several times the tax of an identical house next door, starves the local services that made the neighborhood valuable, and adds to lock-in by making a move a tax event. Both are true; the argument is about who should bear a price rise nobody chose.

**Insurance regulation.** In the states where premiums rose most, regulators had held rates below what insurers wanted. One side says that protected owners from gouging; the other says it drove insurers out and left owners with state-run insurers of last resort and no competition. The 2023–25 exits from California and Florida are cited by both sides.

## See also

- [You rent](you-rent.html): the other side of every number on this page.
- [Mortgage rates](what-is-the-mortgage-rate.html): why the Fed can't lower them, and the lock-in effect.
- [Inflation](what-is-inflation.html): where insurance sits in the index and where property tax doesn't.
- [Real vs. nominal](real-vs-nominal.html): the shrinking-ruler version of your payment.

## Sources

- [FRED: CPI (CPIAUCSL)](https://fred.stlouisfed.org/series/CPIAUCSL), the price level is this index rebased; [30-year mortgage rate (MORTGAGE30US)](https://fred.stlouisfed.org/series/MORTGAGE30US); [CPI tenants' and household insurance (CUSR0000SEHD)](https://fred.stlouisfed.org/series/CUSR0000SEHD).
- [Federal Housing Finance Agency, "The Lock-In Effect of Rising Mortgage Rates" (working paper 24-03)](https://www.fhfa.gov/research/papers/wp2403).
- [U.S. Treasury, Federal Insurance Office, "Analyses of U.S. Homeowners Insurance Markets, 2018–2022" (January 2025)](https://home.treasury.gov/news/press-releases/jy2791), premiums by region and risk.
- [Federal Reserve, Survey of Consumer Finances](https://www.federalreserve.gov/econres/scfindex.htm), housing wealth by household.

## Corrections

October 30, 2026: An earlier version said rents rose 41% since 2019. The BLS rent index is up about 36%.
