# Batch 2026-11-01f — new article: Who Lobbies on Health Care

Built on main 3c44b66 (the Nov 1 "Who Gains and Who Pays" upload). Nothing else staged. Not for upload before the Nov 3 election.

This MANIFEST and `health-lobbying-classification.csv` sit beside the batch folder on purpose: don't upload them. Upload only what is inside `economyincontext-batch-2026-11-01f/`.

## Files
- `articles/src/who-lobbies-on-health-care.md` (new). Plain words idea page (`kind: concept`, `order: 12`, label "Who lobbies on health care"), dated 2026-11-04. If it ships on another day, change `date:` to the ship date first. Not featured; "Who Gains and Who Pays" stays the Featured line.

## Upload
GitHub (signed in as wellgoodluck — check the avatar) → `articles/src` → Add file → Upload files → drag `who-lobbies-on-health-care.md` from inside this batch's `articles/src` folder → commit to main. Only the Publish workflow runs (about 2–6 minutes).

Optional housekeeping in the same session: the Nov 1 upload (3c44b66) put that batch's `MANIFEST.md` at the repo root. Open it on GitHub → ⋯ → Delete file → commit. No workflow runs for it and nothing on the site changes.

## Verify
- Actions: "Publish site changes" green.
- https://economyincontext.org/articles/who-lobbies-on-health-care.html loads: 12 sections, three tables (spending by group, topics by group, patient groups' funding disclosures), no raw `{{`, no chart embeds.
- The articles index lists "Who lobbies on health care" under The ideas, after "Who gains and who pays in health care". The feed gains one entry; the sitemap goes from 61 to 62 URLs.
- Local build of this batch: figures 131 live values, 57 checks (0 failing), 26 due dates (0 passed); 667 internal links, none broken; only `articles/index.html`, `feed.xml`, `sitemap.xml` and the new page differ from main's build. Rendered at 375px and 1280px, light and dark: no horizontal page scroll, no console errors; all three tables fit the 714px column on desktop and scroll in their frames on phones.

## Format decision
Plain words idea page rather than timely. The durable core is explanatory (what a lobbying report counts, the double-count rule, tax-law vs LDA definitions, what's left out, patient-group funding, what research says lobbying buys); the numbers update on a fixed calendar (quarterly filings, annual NHE and GAO), which suits `{{due}}` markers. As a timely piece the method would be frozen with the numbers. It also reads as order 12 right after the Nov 1 piece it extends.

## Data and method (also in the article)
- Senate LDA API (lda.senate.gov now redirects to lda.gov), queried from the built-in browser on Nov 1, 2026: about 330 anonymous requests (limit 15/minute, 25 results/page), about 4,500 filings, LD-2 reports for 2025 and Q1–Q3 2026.
- 93 organizations in 10 groups, matched by client name (the API matches words, so e.g. "Johnson & Johnson" also returned Johnson Controls; every returned name is in the CSV with included/excluded and why).
- Latest amendment per registrant/client/quarter. In-house filer: its expenses; outside firms' income from it dropped (OpenSecrets' rule). Firms-only clients: sum of firms' income. "Less than $5,000" = 0.
- Cross-check vs OpenSecrets 2025: AARP, AHIP, PCMA, FAH, HCA (also CHA, Tenet, Humana) to the dollar; PhRMA, AMA within 3%; UnitedHealth and Kaiser 6–7% lower here (OpenSecrets adds affiliates); OpenSecrets' AHA $32.0M = AHA's own $25.47M + 25 state associations.
- 18 of 93 use tax-law definitions (Methods B/C); flagged in the tables.
- Totals: $418.8M (2025), $312.4M (Q1–Q3 2026, −4.4% vs Q1–Q3 2025). Late filers: AAP's Q3 2026 report hadn't posted.
- Topic counts come from text patterns on each report's specific-issue text; the Medicare for All pattern was tightened after it caught a PhRMA report calling a drug-pricing model "single-payer" price controls.
- OpenSecrets is used only to check totals and for the health-sector ($878M) and all-lobbying ($5.08B) context figures, each cited. Its data is CC BY-NC-SA; no OpenSecrets data is reproduced beyond those cited figures.
- LDA terms of service require citing the retrieval date and the Senate Office of Public Records disclaimer sentence; both are in the article and its Sources.

## Review dates added (invisible `{{due}}`)
- 2026-11-30: CY2027 outpatient final rule — did CMS finalize site-neutral imaging?
- 2027-01-04: 120th Congress — bill numbers in the page are the 119th's.
- 2027-01-20: Q4 2026 reports due — full-year 2026 totals, amendments, late filers, topic table.
- 2027-01-20: CMS 2025 national health expenditures — per-$100 comparisons.
- 2027-02-01: OpenSecrets 2026 sector and all-lobbying totals.
- 2027-07-01: GAO's annual LDA compliance report.

## Fact check
An independent agent that didn't write the piece checked every figure against its source (44 LDA API calls on top of the pull, plus original filing pages), all 14 quotes (all verbatim, all under 15 words), every link, and balance. Changed after it:
- Errors: OpenSecrets comparison now says UnitedHealth and Kaiser differ (affiliates), and the method says subsidiaries under other names aren't added; Blue Cross wording ("most" under insurance); tax-law definitions also count fewer executive-branch contacts, so not strictly comparable; JAMA survey dated 2013–14; "$4,000 one isn't reported" → shows as a checked box counted as zero; Section 508 "raised local health spending"; ADA share now cites total revenue and says unaudited; CFF sold royalty rights to Royalty Pharma (via an affiliate); ACS tiers are dollar ranges; EPIC Act "13 years before negotiated prices apply"; PBM rebate pass-through applies to contracts starting 30 months after enactment; "imaging without contrast"; "25 state hospital associations and affiliates"; the Nov 1 article named and linked.
- Links: PhRMA link now returns only its own four in-house reports; AMA-left-the-Partnership link now Politico Aug 2019; LDA filings quoted are linked to their original pages; Alzheimer's company list linked; PCMA's argument now sourced to its Feb 3 memo.
- Balance: "Medicaid cuts" header → "Medicaid changes"; added a supporter on provider taxes (Paragon); dropped the CMS administrator quote; labeled all PhRMA grantees (center-right, conservative, center-left); Arnold Ventures' $455,000 to Patients for Affordable Drugs stated; selection caveat after the first table (independent Blue plans, state hospital associations, other single-payer filers not counted); AMA vs AARP definitions noted; "monopoly prices" → "prices set without negotiation"; PFCD described by its full partner range and its disclaimer; ACS CAN's, the Heart Association's and AARP's responses added; overstatements softened ("much of," "we found no peer-reviewed study," GAO's sample as the only check; the "building invites visitors" line now rests on the act's exceptions rather than an unattributed claim).
- Not independently re-verified by the checker: PhRMA's $228.6M Schedule C figure (verified by the author from the e-filed 990 data), NHE's $306B, and the U.S. Chamber naming Medicare for All (in the author's text search of filings).

## Rollback
Delete `articles/src/who-lobbies-on-health-care.md` on GitHub (open the file → ⋯ → Delete file → commit). Publish runs and the page, index entry, feed entry and sitemap URL disappear. Nothing else depends on it.
