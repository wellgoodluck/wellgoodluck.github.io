# Batch 2026-11-01e — new article: Who Gains and Who Pays

Built on main 430a129 (design batch 5). Nothing else staged.

## Files
- `articles/src/who-gains-and-who-pays-in-health-care.md` (new). Plain words idea page (`kind: concept`, `order: 11`), dated 2026-11-01, with `featured: 2026-11-01`: it replaces How a True Number Can Mislead (featured since Oct 31) as the Featured line on the almanac and the articles index at this build.

## Upload
GitHub (signed in as wellgoodluck, check the avatar) → `articles/src` → Add file → Upload files → drag the .md from inside this batch's `articles/src` folder → commit to main. Only the Publish workflow runs (about 2–6 minutes).

## Verify
- Actions: "Publish site changes" green.
- https://economyincontext.org/articles/who-gains-and-who-pays-in-health-care.html loads, with ten sections, the cost table, the pay/premiums chart, and live figures in the "Keeping things as they are" section (premiums 7.0%, pay 3.3% for September 2026 at build time).
- The Featured line at the top of the almanac and the articles index shows this article's title and dek; the build log's Assemble step prints `featured: who-gains-and-who-pays-in-health-care (since 2026-11-01)`.
- The articles index lists "Who gains and who pays in health care" under The ideas, after the health insurance page. The feed gains one entry.
- Local build: figures 131 live values, 57 checks (0 failing), 20 due dates (0 passed). No horizontal scroll at 375px or 1280px, light or dark; no console errors.

## Review dates added (invisible `{{due}}`)
- 2026-11-05: midterm results; revisit the credits paragraph and the administration's plan.
- 2027-01-04: Medicaid work requirements and six-month renewals began; list any state exemptions.
- 2027-01-20: CMS 2025 national health expenditures; update totals and sponsor shares.

## Fact check
Independent agent checked every figure against its source on Nov 1. Two errors fixed (Urban offsets were from its 2016 study; Urban's public-option coverage belonged to the whole package), plus poll wording, Mercatus share (3.4%), CBO option description, Yale lives-saved breakdown, Medicare-vs-government price wording, OECD-median comparison, and balance fixes (parallel gains/pays lists, labels on all think tanks, administration's own CSR claim, Senate's December 2025 votes, a break that cuts against subsidies).

## Rollback
Delete `articles/src/who-gains-and-who-pays-in-health-care.md` on GitHub (open the file → ⋯ → Delete file → commit). Publish runs and the page, index entry, feed entry and sitemap URL disappear, and the Featured line falls back to How a True Number Can Mislead (its Oct 31 date becomes the newest again). To keep the article but stop featuring it, delete only its `featured:` line instead.
