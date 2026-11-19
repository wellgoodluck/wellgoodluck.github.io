---
title: What Will My Savings Grow To?
dek: Your starting amount, what you add each month and your account's rate: the balance it could grow to, how much of it is interest, and how long money takes to double.
date: 2026-11-19
kind: tool
---

<div class="mt-mount" data-tool="save"><p class="rb-noscript">This tool needs JavaScript. The section How it's worked out, below, explains the arithmetic.</p></div>
<script src="../assets/moneytools.js?v=20261119"></script>

## How it's worked out

Interest is added each month. The monthly rate is the one that adds up to the yearly rate you enter after twelve months of compounding. That's what an APY (annual percentage yield) means, so these figures match what an account paying that APY would earn. Deposits go in at the end of each month, and the starting amount at the start. The tool repeats this month by month and adds it up.

The doubling time is the exact number of years money left alone takes to double at that rate. The rule of 72, dividing 72 by the rate, is the quick estimate. It's close at everyday rates and gets rough at very low ones.

It assumes the rate never changes, though savings rates do: they tend to follow the Federal Reserve's rate up and down. It leaves out taxes on the interest and any fees. The balance is in future dollars. Prices rise too, so it will buy less than the same sum does today. Over the 12 months to {{v cpi period}}, consumer prices rose {{v cpi}}.{{check cpi.value > 0 "savings tool: 'prices rose' needs a positive 12-month CPI change"}}

The example's rates come from [The 0.38% Account](how-saving-works.html): 4% is about what many online banks and credit unions were paying in November 2026, and 0.38% was the national average for savings accounts in October 2026.

Nothing you type is saved or sent anywhere. A link carries your numbers only if you copy one with them.

## Read more

- [The 0.38% Account](how-saving-works.html): where to keep savings, what's insured, and why the rate matters.
- [Interest on Interest](compound-interest.html): how compounding works, for savings and for debt.

## Sources

- [FDIC national rate: savings, via FRED (0.38%, October 2026)](https://fred.stlouisfed.org/data/SNDR)
- [Bankrate, best savings account rates (3.90%–4.35% examples; APY as of November 11, 2026)](https://www.bankrate.com/banking/savings/10-best-savings-account-rates/?pid=pt8)
- [Regulation DD, 12 CFR 1030.4 (how banks must state the APY)](https://www.law.cornell.edu/cfr/text/12/1030.4)
- [BLS, Consumer Price Index, via FRED (CPIAUCSL, change from a year earlier)](https://fred.stlouisfed.org/series/CPIAUCSL)
