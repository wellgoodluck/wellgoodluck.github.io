---
title: What Will My Savings Grow To?
title_tag: Savings Growth Calculator: What Will My Savings Grow To?
dek: Your starting amount, what you add each month and your account's rate: the balance it could grow to, how much of it is interest, and how long money takes to double.
date: 2026-11-19
kind: tool
more_tools: kept-up
---

<div class="mt-mount" data-tool="save"><p class="rb-noscript">This tool needs JavaScript. The section How it's worked out, below, explains the arithmetic.</p></div>
<script src="../assets/moneytools.js?v=20261119b"></script>

## How it's worked out

Interest is added each month. The monthly rate is the one that adds up to the yearly rate you enter after twelve months of compounding. That's what an APY (annual percentage yield) means, so these figures match what an account paying that APY would earn. Deposits go in at the end of each month, and the starting amount at the start. The tool repeats this month by month and adds it up.

The doubling time is the exact number of years money left alone takes to double at that rate. The rule of 72, dividing 72 by the rate, is the quick estimate. It's close at everyday rates and gets rough at very low ones.

It assumes the rate never changes, though savings rates do: they tend to follow the Federal Reserve's rate up and down. It leaves out taxes on the interest and any fees. The balance is in future dollars. Prices rise too, so it will buy less than the same sum does today. Over the 12 months to {{fig cpi12_month}}, consumer prices rose {{fig cpi12}}.{{check fig:cpi12 > 0 "savings tool: 'prices rose' needs a positive 12-month CPI change"}}

The example's rates come from [The 0.38% Account](how-saving-works.html): 4% is about what many online banks and credit unions were paying in November 2026, and 0.38% was the national average for savings accounts in October 2026.

The Treasury bill rate is the Federal Reserve's weekly average yield on 3-month bills: {{v tbill_3mo fmt=pct2 else="the latest weekly average"}} for {{v tbill_3mo period else="the latest week"}}. Treasury bills are bought through TreasuryDirect or a brokerage, not a bank. They're backed by the federal government rather than FDIC insurance, and their interest is exempt from state and local income tax. A bill's yield isn't worked out quite the way an APY is. At today's rates the difference is less than a tenth of a point.{{check tbill_3mo.value < 5.2 "savings tool: 'less than a tenth of a point' (a 3-month yield against an APY) holds only below about 5.2%"}}

Nothing you type is saved or sent anywhere. A link carries your numbers only if you copy one with them.

## Read more

- [The 0.38% Account](how-saving-works.html): where to keep savings, what's insured, and why the rate matters.
- [Interest on Interest](compound-interest.html): how compounding works, for savings and for debt.

## Sources

- [FDIC national rate: savings, via FRED (0.38%, October 2026)](https://fred.stlouisfed.org/data/SNDR)
- [Bankrate, best savings account rates (3.90%–4.35% examples; APY as of November 11, 2026)](https://www.bankrate.com/banking/savings/10-best-savings-account-rates/?pid=pt8)
- [Regulation DD, 12 CFR 1030.4 (how banks must state the APY)](https://www.law.cornell.edu/cfr/text/12/1030.4)
- [BLS, Consumer Price Index, via FRED (CPIAUCNS, not seasonally adjusted, change from a year earlier)](https://fred.stlouisfed.org/series/CPIAUCNS)
- [BLS: why there's no 12-month change for October 2026](https://www.bls.gov/cpi/notices/2026/12m-changes-202610.htm)
- [3-month Treasury yield, weekly, Federal Reserve via FRED (WGS3MO)](https://fred.stlouisfed.org/series/WGS3MO)
