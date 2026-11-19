---
title: What Does It Cost to Own a Car?
dek: One car, or two side by side: what each costs a year to own and drive, line by line, including the cost most people leave out, the value it loses.
date: 2026-11-19
kind: tool
---

<div class="cc-mount" data-tool="own"><p class="rb-noscript">This tool needs JavaScript. The section How it's worked out, below, explains the arithmetic, and Sources links to the figures.</p></div>
<script src="../assets/carcost.js?v=20261119"></script>

## How it's worked out

The tool adds up six yearly costs, the same ones AAA counts in its Your Driving Costs study: the value the car loses, loan interest, insurance, fuel or charging, maintenance and repairs, and taxes and fees.

**The value it loses.** If you give a price, it's the price minus what you expect the car to be worth when you sell it, spread over the years you keep it. The starting estimate of that value uses iSeeCars' five-year averages: cars overall lost 42% of their value in five years, hybrids 35% and electric cars 57%. For other lengths of ownership the tool assumes the car loses value at the same pace each year. Cars lose value fastest in the first years, so for a short keep this probably understates the loss, and for a long one it overstates it. Without a price, the tool uses AAA's average for that type of car.

**Loan interest.** The interest you'd pay during the years you keep the car, worked out month by month from the price, down payment, rate and loan length, then spread over those years. Without a price, it uses AAA's average, which assumes a 60-month loan at the national average rate.

**Fuel or charging.** Miles divided by miles per gallon, times the price of a gallon. For an electric car: miles divided by miles per kilowatt-hour, times the price per kilowatt-hour, with any share at public fast chargers at that price. The starting prices are national averages the site tracks: regular gasoline for {{fig car_gas_week else="the latest week"}} ({{fig car_gas else="the national average"}}, from the Energy Information Administration) and electricity for {{fig car_elec_month else="the latest month"}} ({{fig car_elec else="the national average"}} a kilowatt-hour, from the Bureau of Labor Statistics). Public fast charging averaged about 54¢ a kilowatt-hour in mid-2026. Each type's starting efficiency is the one implied by AAA's own fuel figures.

**Insurance, maintenance and fees** start at AAA's 2026 averages for that type of car and what it runs on. AAA's taxes and fees include sales tax at purchase spread over the years, so the price box leaves sales tax out.

AAA's figures are averages for new cars driven 15,000 miles a year for five years. Your insurance and repairs can be far from them, so use your own amounts where you have them. The tool leaves out parking, tolls and a home charger.{{due 2027-09-30 "car tool: AAA's 2027 Your Driving Costs study; update the AAA table in assets/carcost.js and the 2026 references here"}}

Nothing you type is saved or sent anywhere. A link carries your numbers only if you copy one with them.

## Read more

- [Electric Vehicles: The Case For and the Case Against](electric-vehicles-case-for-and-against.html): what it costs to own one, charging, and what the arithmetic turns on.
- [What a Car Loan Costs, by Length](/tools/car-loan-length.html): the payment, total interest and what's still owed along the way, from 48 to 84 months.

## Sources

- [AAA: New Vehicle Ownership Costs Top $12,000 Annually (Your Driving Costs 2026, September 15, 2026)](https://mwg.aaa.com/news/press-release/september-15-2026)
- AAA's 2026 figures by vehicle type and what it runs on, as reported by [NerdWallet](https://nerdwallet.com/auto-loans/learn/total-cost-owning-car) and [Kelley Blue Book](https://www.kbb.com/car-news/aaa-hybrids-come-out-on-top-in-2026-ownership-cost-study/)
- [iSeeCars, cars that hold their value (five-year depreciation, 2026)](https://www.iseecars.com/cars-that-hold-their-value-study)
- [Paren, public fast-charging prices, second quarter of 2026](https://evchargingstations.com/chargingnews/paren-dc-fast-charging-q2-2026/)
- [Regular gasoline, weekly, Energy Information Administration via FRED (GASREGW)](https://fred.stlouisfed.org/series/GASREGW)
- [Average price of electricity per kilowatt-hour, Bureau of Labor Statistics via FRED (APU000072610)](https://fred.stlouisfed.org/series/APU000072610)
- [60-month new-car loan rate at commercial banks, Federal Reserve via FRED (RIFLPBCIANM60NM; {{fig car_apr else="7.54%"}}, {{fig car_apr_month else="August 2026"}})](https://fred.stlouisfed.org/series/RIFLPBCIANM60NM)
