---
title: You Rent
dek: Four numbers reach a renter directly, and the one that matters most arrives a year late.
date: 2026-10-28
updated: 2026-10-30
kind: path
order: 1
---

## What reaches you, in order

1. **Rent itself**, which the Consumer Price Index tracks a year behind the listings. Your lease is the lag.
2. **Mortgage rates**, though you don't have one. They decide who stays a renter and who leaves, and so who you're bidding against.
3. **Apartment starts**, two years before you feel them. The buildings competing for your next lease were started in 2024 and 2025.
4. **Your paycheck against prices**, the real wage, which decides whether a rent increase is survivable.
5. **The Fed**, behind all four, with lags from a few days to a couple of years.

Jobless claims, the unemployment rate and GDP reach you the way they reach everyone, through your job. This page is about the other four.

## Rent

The rent line inside the inflation number is the slowest part of it. The index samples all renters, most of whom are mid-lease, so it reports what people are paying, not what landlords are asking. Asking rents move first; the index catches up over about twelve months. In 2022 the listings sites were already showing rents flattening while the official rent figure was still climbing toward its 2023 peak of nearly 9% a year. In 2024 and 2025 the opposite happened: listings went flat or down in the cities that had built the most, and the index spent a year easing toward them.

Over the whole stretch since 2019, rent in the index is up about 36% ([CUSR0000SEHA](https://fred.stlouisfed.org/series/CUSR0000SEHA)), against about 31% for prices overall. If your rent tracked the average, your inflation ran above the headline, and the gap is one reason the official number has felt low to renters for five years.

The index has a second housing line, "owners' equivalent rent," an estimate of what homeowners would pay to rent their own homes. It is larger than the rent line and it is not your rent; when people argue that housing inflation is overstated, that is the line they mean.

{{chart id=cpi range=10y ov=cpi_rent,cpi_shelter,wages caption="Headline inflation with the rent line and the full shelter line (rent plus owners' equivalent rent) beside it, and wage growth for comparison. Rent peaked a year after asking rents did, and came down a year after them too."}}

## Mortgage rates, though you don't have one

Two ways. First, who is in the market with you. When mortgage rates doubled in 2022, the people who would have bought their first home stayed renters, and first-time buyers' share of purchases fell to its lowest on record. Those households are competing for the same apartments you are. Second, who leaves. Owners holding 3% mortgages don't sell, which keeps the ownership door narrow and the rental market full. Neither effect shows up in the rent index for a year, but both are visible in [the mortgage rate](what-is-the-mortgage-rate.html) today, which is why it is worth a renter's attention.

The reverse holds too. When rates fall far enough to let renters buy, demand for rentals eases. That takes a drop of a point or two, and it has not happened since 2021.

## Apartment starts

Apartment construction is the supply side of your rent, two years early. Developers started more apartments in late 2022 than in any year since 1986, chasing the pandemic rent surge with cheap construction loans; those buildings opened through 2024 and 2025, and in the metros that built the most, rents went flat or fell. Starts have since dropped by about a third. On the two-year lag, that is the 2028 rental market being decided now, and in most places it points toward fewer new buildings competing for tenants.

The almanac's [housing starts](what-are-housing-starts.html) page shows the total with single-family starts underneath. The gap between the lines is apartments; watch the gap, not the total.

{{chart id=housing_starts range=10y ov=single_family_starts caption="Housing starts, with single-family starts underneath. The gap is apartments: wide in 2022, narrowing since. Add two years to read it as rental supply."}}

## Your paycheck against prices

Whether a rent increase is survivable depends on the real wage, pay minus inflation. Typical hourly pay is up about 39% since 2019 ([AHETPI](https://fred.stlouisfed.org/series/AHETPI)); prices overall about 31%; rent about 36%. So the average worker has gained ground on prices overall and, narrowly, on rent, the largest single item in most renters' budgets. [Real vs. nominal](real-vs-nominal.html) explains the subtraction. The year-over-year version is on the inflation chart as a companion, and it has been negative since the spring of 2026 as energy prices rose.

## The Fed

Every line above traces back to [the Fed funds rate](what-is-the-fed-funds-rate.html), with different lags. Rate cuts reach apartment starts in months and the rent index in two to three years; they reach mortgage rates only through the 10-year yield, which can go the other way, as in late 2024. The Fed does not target rents and cannot lower them directly. What it can do is make building cheaper or dearer, which is the slowest channel there is.

## Where you come out ahead

Renters are the one group fully insulated from the two costs that have hit owners hardest since 2022: property insurance, up by half or more in the states with hurricanes and wildfires, and property taxes following home prices up. A renter also keeps the option of moving when the job market or the rent says to, which the lock-in effect has taken away from owners. And a renter's rent rises with inflation; an owner's fixed mortgage shrinks with it. That last one is the structural disadvantage, and the one the arguments below are mostly about.

## What people argue about

**Whether renting is "throwing money away."** The claim rests on the mortgage shrinking in real terms while rent doesn't, which is true. The counter is that at 7% mortgage rates the first years of a mortgage are nearly all interest, which is rent paid to a bank, plus taxes, insurance and maintenance that a renter doesn't carry. Which comes out ahead depends on rates, how long you stay, and what the money would otherwise earn, and the answer has flipped since 2021.

**Whether building helps renters, or only rich ones.** One side points to the 2024–25 evidence: the metros that added the most apartments saw rents fall, including in older buildings as tenants moved up the chain. The other says new buildings raise rents nearby and the chain takes years to reach the bottom. Both effects are documented, and [the housing starts page](what-are-housing-starts.html) carries the argument.

**Rent control.** Supporters say it keeps people housed through exactly the kind of rent spike 2021–23 produced. Economists across the spectrum say it reduces the supply and upkeep of rental housing over time, and point to the cities that have tried it. The evidence on both claims is real; the disagreement is about which cost matters more and over what horizon.

## See also

- [Inflation](what-is-inflation.html): where rent sits in the index and why it lags.
- [Housing starts](what-are-housing-starts.html): the supply side, two years early.
- [Mortgage rates](what-is-the-mortgage-rate.html): why they decide who you're bidding against.
- [Real vs. nominal](real-vs-nominal.html): the paycheck subtraction.

## Sources

- [FRED: CPI rent of primary residence (CUSR0000SEHA)](https://fred.stlouisfed.org/series/CUSR0000SEHA), [CPI shelter (CUSR0000SAH1)](https://fred.stlouisfed.org/series/CUSR0000SAH1), [CPI all items (CPIAUCSL)](https://fred.stlouisfed.org/series/CPIAUCSL), [average hourly earnings (AHETPI)](https://fred.stlouisfed.org/series/AHETPI).
- [BLS, How the CPI measures shelter](https://www.bls.gov/cpi/factsheets/owners-equivalent-rent-and-rent.htm), the rent and owners' equivalent rent lines.
- [FRED: Housing starts, five units or more (HOUST5F)](https://fred.stlouisfed.org/series/HOUST5F) and [completions (COMPUTSA)](https://fred.stlouisfed.org/series/COMPUTSA).
- [National Association of Realtors, research and statistics](https://www.nar.realtor/research-and-statistics), the first-time buyer share.
- [Federal Housing Finance Agency, "The Lock-In Effect of Rising Mortgage Rates"](https://www.fhfa.gov/research/papers/wp2403).

## Corrections

October 30, 2026: An earlier version put the rise in rent since 2019 at about 41% and said the average worker had gained ground on everything except rent. The BLS rent index is up about 36%, a little less than average hourly pay (about 39%).
