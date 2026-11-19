---
title: What's My Own Inflation Rate?
dek: What you spend each month, line by line: how much your own prices rose over the past year, next to the figure for prices overall, and the raise it would take to keep up.
date: 2026-11-19
kind: tool
---

<div class="mr-mount" data-tool="myrate"><p class="rb-noscript">This tool needs JavaScript. The section How it's worked out, below, explains the arithmetic, and Sources links to the figures.</p></div>
<script src="../assets/myrate.js?v=20261119"></script>

## How it's worked out

For each line, the tool takes what you spend now and works out what the same things cost a year earlier. It uses that line's national price index from the Bureau of Labor Statistics, or your own year-ago amount where you give one. Your rate is the change in the total. The national figure works the same way, weighting each kind of spending by what the average household spends on it. Here the weights are yours.

The national figures cover the 12 months to {{fig myrate_month else="September 2026"}}, the latest the Bureau can compare with a year earlier. October 2025 prices were never collected during the federal shutdown, so there's no 12-month figure for October 2026. The figures aren't seasonally adjusted, like the Bureau's own 12-month figures.{{due 2027-01-15 "inflation tool: once the tool's month is well past October 2026, the sentence about the October 2025 gap can go"}}

Internet service, property tax and home insurance use only your own figures: the site doesn't carry a national figure for them.

The national index leaves out mortgage payments and home prices. For homeowners it counts what their homes would rent for instead, a figure called owners' equivalent rent. The Bureau's reasoning is that buying a home is partly an investment. Some analysts argue that this undercounts what owning costs when home prices, mortgage rates, taxes and insurance rise quickly. A fixed-rate mortgage payment doesn't change, so the tool counts it as unchanged unless you give a year-ago amount.

A national index is an average. Your own prices for the same things can rise faster or slower, depending on where you live and where you shop. Where you know what you paid a year ago, using it gets closer to your own.

It measures prices, not choices. If you moved, changed cars or started paying for something new, that difference isn't inflation.

The examples are made-up households.

Nothing you type is saved or sent anywhere. A link carries your numbers only if you copy one with them.

## Read more

- [Has It Kept Up With Prices?](/tools/kept-up.html): check your own pay, rent or benefit against prices overall, over any span of years.
- [What Inflation Is](what-is-inflation.html): what the national figure covers and leaves out.

## Sources

- Consumer Price Index, via FRED, all not seasonally adjusted: [all items (CPIAUCNS)](https://fred.stlouisfed.org/series/CPIAUCNS) · [rent (CUUR0000SEHA)](https://fred.stlouisfed.org/series/CUUR0000SEHA) · [groceries, food at home (CUUR0000SAF11)](https://fred.stlouisfed.org/series/CUUR0000SAF11) · [eating out, food away from home (CUUR0000SEFV)](https://fred.stlouisfed.org/series/CUUR0000SEFV) · [electricity (CUUR0000SEHF01)](https://fred.stlouisfed.org/series/CUUR0000SEHF01) · [natural gas, utility gas service (CUUR0000SEHF02)](https://fred.stlouisfed.org/series/CUUR0000SEHF02) · [water, sewer and trash (CUUR0000SEHG)](https://fred.stlouisfed.org/series/CUUR0000SEHG) · [phone service (CUUR0000SEED)](https://fred.stlouisfed.org/series/CUUR0000SEED) · [gasoline (CUUR0000SETB01)](https://fred.stlouisfed.org/series/CUUR0000SETB01) · [car repairs (CUUR0000SETD)](https://fred.stlouisfed.org/series/CUUR0000SETD) · [public transportation (CUUR0000SETG)](https://fred.stlouisfed.org/series/CUUR0000SETG) · [medical care (CPIMEDNS)](https://fred.stlouisfed.org/series/CPIMEDNS) · [apparel (CPIAPPNS)](https://fred.stlouisfed.org/series/CPIAPPNS) · [owners' equivalent rent (CUUR0000SEHC)](https://fred.stlouisfed.org/series/CUUR0000SEHC)
- Consumer Price Index, from the Bureau of Labor Statistics' own data service, not seasonally adjusted: [car insurance (CUUR0000SETE)](https://data.bls.gov/timeseries/CUUR0000SETE) · [child care, day care and preschool (CUUR0000SEEB03)](https://data.bls.gov/timeseries/CUUR0000SEEB03)
- [BLS: why there's no 12-month change for October 2026](https://www.bls.gov/cpi/notices/2026/12m-changes-202610.htm)
- [BLS: rent and owners' equivalent rent, questions and answers](https://www.bls.gov/cpi/additional-resources/rent-oer-faq.htm)
- [Congressional Research Service: Housing and the Consumer Price Index](https://www.everycrsreport.com/reports/IF12164.html)
