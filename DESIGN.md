---
name: Economy in Context
description: The main numbers on the U.S. economy, each shown against its own history.
colors:
  neutral-ground-teal: "#0b7a75"
  neutral-ground-teal-dark: "#2bb3a8"
  teal-button-ink: "#0b6b66"
  teal-button-ink-dark: "#5cc8be"
  paper: "#f6f6f3"
  paper-dark: "#121211"
  sheet: "#ffffff"
  sheet-dark: "#1a1a19"
  ink: "#1b1b1a"
  ink-dark: "#f0efec"
  ink-secondary: "#5a5955"
  ink-secondary-dark: "#c3c2b7"
  ink-muted: "#72716b"
  ink-muted-dark: "#898781"
  hairline: "#e3e2dc"
  hairline-dark: "#2c2c2a"
  gridline: "#ebeae4"
  gridline-dark: "#262624"
  reference-gray: "#6b6a66"
  reference-gray-dark: "#a09e97"
  framing-banner: "#fff4d6"
  framing-banner-ink: "#5a4300"
  framing-banner-dark: "#3a2f10"
  framing-banner-ink-dark: "#f3dfa0"
  range-bar: "#c4c2b9"
  range-bar-dark: "#45443f"
  companion-1: "#903a03"
  companion-2: "#5624c1"
  companion-3: "#b88e2f"
  companion-4: "#eb4ec8"
  companion-1-dark: "#fb8304"
  companion-2-dark: "#9980fe"
  companion-3-dark: "#7c6713"
  companion-4-dark: "#ba0f9b"
  lane-democratic: "#b2cdfa"
  lane-republican: "#f7bbb7"
  lane-divided: "#e6e5df"
  lane-democratic-dark: "#2b4775"
  lane-republican-dark: "#6e3332"
  lane-divided-dark: "#2f2f2c"
  lane-easing: "#d9d6cb"
  lane-tightening: "#9f9b90"
  lane-easing-dark: "#4a4944"
  lane-tightening-dark: "#66645d"
  era-light: "#d8d6cd"
  era-mid: "#c3c1b7"
  era-war: "#6e6c66"
  era-war-dark: "#5e5c57"
typography:
  display:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "40px"
    fontWeight: 700
    lineHeight: 1.1
    letterSpacing: "-0.015em"
  reading:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "40px"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "clamp(28px, 4.4vw, 40px)"
    fontWeight: 700
    lineHeight: 1.12
    letterSpacing: "-0.015em"
  title:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "22px"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.01em"
  tile-title:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "19px"
    fontWeight: 700
    lineHeight: 1.25
  body:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "17px"
    fontWeight: 400
    lineHeight: 1.55
  body-compact:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: 1.5
  context:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "15px"
    fontWeight: 600
  meta:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "13.5px"
    fontWeight: 400
  caption:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "12.5px"
    fontWeight: 400
  label:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "12.5px"
    fontWeight: 600
    letterSpacing: "0.05em"
  chart-text:
    fontFamily: "Public Sans, system-ui, -apple-system, Segoe UI, sans-serif"
    fontSize: "11px"
    fontWeight: 400
    fontFeature: "tnum"
rounded:
  hairline: "2px"
  control: "4px"
  frame: "6px"
spacing:
  gutter: "16px"
  grid-gap: "16px"
  tile-padding: "18px 18px 14px"
  page-max: "1120px"
  measure: "39em"
components:
  tile:
    backgroundColor: "{colors.sheet}"
    rounded: "{rounded.frame}"
    padding: "{spacing.tile-padding}"
  button-full-chart:
    textColor: "{colors.teal-button-ink}"
    rounded: "{rounded.control}"
    padding: "3px 11px"
  button-full-chart-hover:
    backgroundColor: "{colors.teal-button-ink}"
    textColor: "{colors.sheet}"
  range-button:
    textColor: "{colors.ink-secondary}"
    padding: "3px 9px"
  range-button-pressed:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.sheet}"
  action-button:
    backgroundColor: "{colors.sheet}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "4px 10px"
  framing-banner:
    backgroundColor: "{colors.framing-banner}"
    textColor: "{colors.framing-banner-ink}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
  tooltip:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.sheet}"
    rounded: "{rounded.control}"
    padding: "6px 9px"
---

# Design System: Economy in Context

## Overview

**Creative North Star: "The Public Record"**

The site should look like something a fact-checker could put on screen without apology: neutral, citable, plain. Every visual decision serves one question a reader brings ("is this number high, low or normal?") and refuses to answer a second one ("is that good or bad?"). The look is a well-set page of warm off-white paper and near-black ink, one typeface, hairline rules, and a single teal accent that marks the reading itself. Color is spent on identity (which line is which), never on judgment.

The system has two registers. The almanac and the articles are **printed and plain**: text links with hairline underlines, tiles that read like boxed entries in a reference book, generous measure for reading. Chart pages are **quiet instruments**: compact segmented range controls, tabular numerals, an overlay panel of labeled toggles, a crosshair and tooltip. Both share the same tokens; the chart page simply packs them tighter.

Restraint is the identity. Confirmed rejections: no custom display typeface or brand color system, no motion or transitions, no shadows, no red/green or any value-judgment color on readings, no watermarks across charts, no dual y-axes.

**Key Characteristics:**
- Warm paper and near-black ink, light and dark schemes from the reader's system setting.
- One typeface (Public Sans, self-hosted, 400/600/700); hierarchy by size and weight.
- One accent, Neutral Ground Teal, for the data line, the latest-reading dot and the chart button.
- Flat surfaces separated by 1px hairlines; no elevation.
- Every chart carries its source credit inside the frame.

## Colors

A warm-neutral paper-and-ink palette with one teal accent and a reserved set of identity colors that appear only inside charts.

### Primary
- **Neutral Ground Teal** (light / dark in the frontmatter): the main data series, the latest-reading dot on range strips (hollow when the reading is outside its range), the focus ring and the tint of the "Add context" button. Chosen because no party owns it; it must stay distinct from both party lanes.
- **Wayfinding Ochre** (`--nav`, #8a6100 light / #d9a83a dark; 5.5:1 on white, 8:1 on the dark sheet): navigation only, never data, so the rule is simple: teal is the numbers, ochre is how you get around. A 3px rule along the top of the section bar, the "ON THIS PAGE" label, the 3px marker under the section in view and the hover marker, the 2px underlines of Articles and About, "↑ At a glance" and the crumb on article pages. Chosen Nov 5 over terracotta (too close to the first companion line in the Chart to try picture) and plum (hard to tell from the teal for deuteranopes in dark mode, ΔE 4.6); ochre clears the teal by 12 (light) and 14 (dark) under color-blind simulation, and sits in the same warm family as the framing banner.

### Secondary
- **Companion slots 1–4**: the colors of optional companion series and sub-panel lines on chart pages: rust, violet, ochre and pink in light mode; orange, lavender, dark ochre and deep magenta in dark. Every pair, and each against the teal, stays apart under protanopia and deuteranopia (worst pair 12.9 light, 15.4 dark, OKLab ΔE ×100). A series keeps the slot it was given when it was turned on until it is turned off; four at a time at most. They never appear outside a chart and never carry meaning beyond "which line".

### Tertiary
- **Era lanes**: Democratic blue and Republican red as light tints (dark tints in dark mode) of equal lightness, so neither party looks heavier and the data line stays the loudest mark, with dark labels; a pale neutral for divided government; two alternating warm grays for Fed chairs and similar eras; a dark gray with white labels for wars. Fed cycle and balance-sheet lanes use two neutrals, lighter for easing or expanding and darker for tightening or shrinking, so no traffic-light reading; the darker one is also hatched with sheet-colored diagonals, so the two differ by more than lightness, and a label on it gets a halo in that shade. A Fed segment too narrow for its name takes a short form: C and H for cutting and hiking, QE and QT for the balance sheet (never R, which reads as Republican beside the party lanes). Used only in the lanes under a chart, always labeled, and keyed in the legend whenever the color carries the meaning (Democratic, Republican, Divided; "Fed cutting rates / buying bonds", "Fed raising rates / shrinking its holdings", each with its short form in parentheses when one is drawn).
- **Framing Banner** (warm cream with dark amber ink): the one tinted block, reserved for the framing line that appears whenever a political overlay is on.

### Neutral
- **Paper**: page background.
- **Sheet**: tiles, chart frames and other raised-by-border surfaces (white in light mode).
- **Ink**: headings, values, primary text; also the pressed range button (light mode) and the tooltip background.
- **Ink Secondary**: sentences, notes, captions, event markers.
- **Ink Muted**: dates, periods, axis labels, credits (4.5:1 on paper at its lightest; do not lighten it).
- **Hairline**: borders, row dividers, link underlines.
- **Range Bar**: the typical-range track on range strips; darker than a hairline because it carries meaning.
- **Gridline**: chart grid, deliberately quieter than the hairline.
- **Reference Gray**: dashed reference lines and their labels.

### Named Rules
**The Identity-Not-Judgment Rule.** Color says which, never whether. No good/bad, up/down or red/green coloring of any reading, anywhere.

**The Neutral Ground Rule.** The data line never takes a party's hue. Companion colors avoid blue, red, teal and green: those belong to the parties and the main series.

**The Four Lines Rule.** A chart carries at most four companion or sub-panel lines, each in its own slot color, and a line keeps its color while it is on. A fifth waits until one is turned off; colors are never reused on one chart.

**The Three Copies Rule.** The tokens are copied in `index.html`, `chart.html` and `assets/site.css`. Change all three together, in both schemes.

## Typography

**Display Font:** Public Sans (with system-ui, -apple-system, Segoe UI, sans-serif)
**Body Font:** Public Sans
**Label/Mono Font:** Public Sans with tabular numerals for figures in charts and tables

**Character:** A sturdy public-sector grotesque, open and unfussy; it reads as institutional without being cold, and its tabular figures keep columns of numbers honest.

### Scale
The almanac and chart pages use one scale: **11 · 12.5 · 13.5 · 15 · 16 (base) · 17 · 19 · 22 · 28 · 40 · 44px**, with four steps between 11 and 15. Chart text is 11px everywhere inside an SVG (axes, lanes, events, credits), except range-strip labels, which are 12.5px: they are the context the site is named for, so they are never the smallest text on the page. The images made for download and social posts have their own sizes, set for the image's frame. Article pages (`assets/site.css`) use the same scale from 17px body text: the title 40px (28px on phones), the dek 19px (17px), section heads 22px, list titles 22px, captions, datelines and footers 13.5px, small labels 12.5px.

### Hierarchy
- **Display** (700, 40px; 28px on phones, 1.1): the site name on the almanac masthead, set as the lockup (see Masthead): "Economy" in 700, "in Context" in 400 Ink Secondary, an ink period. A chart page's indicator name is 28px at every width, so the reading stays the largest thing on screen.
- **Reading** (600, 40px on tiles, 44px on chart pages, 1.0, tight tracking): the latest value of an indicator. The largest number on any screen is always the reading.
- **Headline** (700, clamp 28–40px, 1.12): article titles.
- **Title** (700, 22px, 1.2): section and article h2 headings; the "At a glance" heading.
- **Tile title** (700, 19px, 1.25): indicator names on tiles.
- **Body** (400, 17px, 1.55, 39em measure): article text. The almanac runs at 16px/1.5.
- **Context** (600, 15px): the one-sentence verdict under a range strip ("Higher than 67% of months since 1948").
- **Meta** (400, 13.5px, Ink Secondary or Muted): subtitles, periods, notes, sources, controls (range buttons, custom range, actions), tables.
- **Caption** (400, 12.5px): legends, the hover box, overlay notes, counts, print footers.
- **Label** (600, 12.5px, 0.05em, uppercase): small section labels in the overview and "Events in view"; the Featured label uses Ink Secondary and 0.06em.
- **Chart text** (400, 11px, tabular numerals): axes, lane labels, event labels and numbers, credits. Range-strip labels are 12.5px.

### Named Rules
**The Reading Is Loudest Rule.** On any screen the latest value is the largest, heaviest number. Nothing decorative competes with it.

## Layout

A single centered column, max 1120px, with a 16px side gutter at every width. The almanac opens with the masthead, a section nav, the "At a glance" overview (three columns of compact rows on desktop, one on phones), then indicator tiles two to a row with a 16px gap. In a section with an odd number of tiles, the designated wide tile spans the row at ≥761px: reading and notes on the left (5/12), a taller 300px chart on the right (7/12).

Articles hold text to a 39em measure (about 76 characters at 17px); embedded charts break out to 860px. Chart pages place the chart and its controls left and a sticky overlay panel right at ≥861px; below that the panel sits right under the chart's key and framing line (the events list, notes and actions follow it), with jump links about 44px tall between chart and panel and a bar at the bottom of the screen that leads back to the chart while the panel is in view and the chart isn't.

The section nav, a labeled bar on the almanac and the articles index alike, sticks to the top at every width; at ≤760px it becomes one sideways-scrolling row with 46px targets. Anchor targets carry a scroll margin of the nav's measured height so jumps land below it, and range buttons grow to about 36px tall. Strips and charts reserve their height before drawing so the page doesn't jump.

Print hides navigation and controls, keeps tiles and charts whole, and ends with the domain.

## Elevation & Depth

Flat. There are no shadows anywhere in the system. Depth is tonal and structural only: white sheets on warm paper (dark: slightly lifted charcoal on near-black), separated by 1px hairlines. The pressed range button and the tooltip invert to ink, which is the only "raised" state; in dark mode the pressed button fills with the Range Bar gray instead, with ink text in 600, because an ink block glares on the dark sheet.

### Named Rules
**The Paper Rule.** Surfaces are flat. A border separates; nothing floats.

## Shapes

Gently squared. Three radii: 2px for small swatches and focus outlines, 4px for buttons, the segmented range control, the framing banner and the tooltip, and 6px for tiles, chart frames and article embeds. Borders are 1px hairlines. Chart marks are round-capped 2px lines (1.6px for companions), round dots with a 2px sheet-colored ring, and small triangles for event markers and outside-the-range arrows.

## Components

### Buttons
- **Shape:** gently squared (4px).
- **Add context:** the one tinted button, on every tile. Teal-ink text on a 10% teal wash with a 45% teal border, 600 weight, 3px 11px padding; hover inverts to teal fill with sheet-colored text. Its label names what the chart page adds that the tile does not ("Add context: presidents, the Fed, events →"), since the tile already shows the chart itself; the three named apply to every indicator. Embeds and article figures keep "Full chart and context →", because there the context is already on and the link opens it at full size.
- **Range buttons:** a segmented group in one hairline frame, 13px Ink Secondary labels, hairline dividers; the pressed state fills with ink (dark mode: the Range Bar gray, ink text in 600). About 36px tall on phones. Tiles carry two (25 yrs, All); chart pages carry the full set and a custom range.
- **Action buttons** (Download CSV, Download image, Copy link, Copy embed code): sheet background, hairline border, 13.5px ink text, 4px 10px padding.
- **Download image menu:** the button opens a list (a disclosure, so it works by keyboard; Escape or a click elsewhere closes it): Full width, Wide 16:9, Square, Portrait 4:5, Story 9:16, each a 600-weight name over a 12.5px Muted line with its pixel size and platforms. Sheet background, hairline border, 4px radius, no shadow; under the button on desktop, opening in place on phones.
- **Focus:** 2px teal outline with 2px offset on everything focusable.

### Cards / Containers
- **Tiles:** sheet background, 1px hairline border, 6px radius, 18px 18px 14px padding, no shadow. Parts in order: title (links to the chart page), subtitle, reading and period, previous and year-ago, range strip, context sentence, household line, plain-words link, chart head with the button and range control, chart, then one disclosure holding the note, sources and recent readings: open with no summary on desktop, closed on phones behind "Notes, source and recent readings", opened for printing.
- **Chart frame:** sheet background, hairline border, 6px radius; the source credit sits inside the frame along the bottom edge so a cropped screenshot keeps it.
- **Static figure (articles):** every article carries at least one figure; where no live chart fits, a `{{figure}}` built from numbers in the text, in plain HTML so it follows both themes and reads at phone width. Three kinds: ranked bars (one hue, Neutral Ground Teal, the value at each tip in text tokens, 14px bars with 4px rounded ends and a square baseline), paired bars (teal and the first companion color, 11px bars, a legend), and a split whole (a 28px segmented bar in teal, c1, c3 and ink with 2px gaps, each part's value printed on it; a part under 8% prints none and carries its value on its legend entry). A title line (15px/600), a caption with the source in Muted, and an accessible name listing every value, so nothing is color-only.

### Navigation
- **The lead (Featured card and Chart to try):** two cards side by side above the overview on the almanac and above the list on the articles index, 7:5 at desktop width, stacked on phones; both 2px ink rule along the top, hairline sides and bottom, 6px radius, 14px 18px padding, 15px text. The Featured card is the one tinted block on either page: the teal wash (`--series-wash`) with a 45% teal border, the "FEATURED" / "FEATURED SERIES" label in the button's teal ink; Chart to try sits on the Sheet. Chosen Nov 4 after a reader said the plain ink rule (the Nov 1 choice) left the top of the page monotonous; the wash is the site's own tint, so it marks the lead without saying anything about the content. Each card: label (12.5px uppercase), title in 700 at 19px with an arrow, the dek in Ink Secondary cut at two lines (three in Chart to try and on phones), and a picture at the foot (see Chart to try) so the two pictures line up whatever the text above them does. A featured series (articles/series.json, whose `featured:` date wins a tie with an article's) shows its parts in reading order as pill buttons: Sheet fill, 45% teal border, 999px radius, numbered circle plus the short label in 600 teal ink, 30px tall (38px on phones); hover darkens the border and the text to ink. The Featured card's picture comes from the item's `picture` field (a tile id with an optional range and ov; in the front matter for an article, in series.json for a series); without one the card has no picture.
- **Summary zone and the break into detail (almanac):** the page has two halves. The summary (the lead cards and At a glance) sits on a full-width Sheet band, drawn with a spread `box-shadow` clipped to the zone so it reaches the window's edges without widening the page; inside it Chart to try takes the page color. Then a labeled break: a 3px ink rule, "The numbers in detail" (28px bold, 24px on phones; `#in-detail`) and one Ink Secondary sentence, before the first section. In `?view=tiles` there is no overview, so no break. Print drops the band and starts the detail on a new page. Chosen Nov 4 (option D of four) after a reader said the summary and the detail ran together. Within the detail, each section after the first has a 2px Muted rule above it (28px above, 22px below): three levels in all, the 3px ink break, the section rules, the hairline rows (chosen Nov 4, option D of four; a 1px Ink Secondary rule shipped first and was swapped the same day).
- **In short:** one plain paragraph under each section heading on the almanac, 15px Ink Secondary, max 46em, led by "In short:" in 600 ink. Written at every refresh by `section_summaries()` in `fetch_fred.py` from templates, never by a model: every number is a tile's current reading, its rank in its own history ("lower than in three-quarters of months since 1948", "near the middle of its history"), a record, or a figure from a household line; the only non-number words are connectives ("but", "and well above") and four plain bins (high, low, ordinary, near the record). No adjectives of judgment. A missing input drops its clause; a section with nothing to say gets no paragraph. Added Nov 4 after a reader asked for a quick summary of what each section's charts mean.
- **Series box (articles):** on each part, right under the dateline: a 2px ink rule down the left, 14px in, 15px text. "SERIES, PART 2 OF 3" as a label, the series title (600, hairline underline) linking to the series group on the articles index, then the parts as pill buttons in one wrapping row, the same pills as the Featured card's (Sheet fill, 45% teal border, 999px radius, numbered circle, 600 teal ink; hover to ink): the part you are reading is the filled one, teal with sheet-colored text, and is not a link (`aria-current="page"`). Chosen Nov 4 from three mocks so the series looks the same on the almanac, the articles index and the article itself. 30px tall, 38px on phones.
- **Next in this series:** the same left rule before See also (or Sources): "NEXT IN THIS SERIES, PART 3 OF 3" and the next part's full title with an arrow; the last part instead reads "EARLIER IN THIS SERIES" with numbered links back. Not printed. On the articles index the series' parts sit together under The ideas, at the first part's place, under a "SERIES" label and the series title (15px ink), in the series' order.
- **Masthead:** site name left, "Articles" and "About" right on the same row (16px apart, the same underlined link style), tagline in Ink Secondary, a short Updated line in Muted, then the Coming up line. The site name is the lockup (chosen Nov 4): the mark (two Ink brackets around a teal dot, `assets/icon.svg` without its tile) at 1.05em, its left bracket on the text edge, then "Economy" in 700 Ink, "in Context" in 400 Ink Secondary, and a period in Ink. The mark's dot is the only teal in it, so the accent still means "the reading". The h1's accessible name is just "Economy in Context" (mark and period hidden). On phones (≤760px) Articles and About move to a small row at the top right and the lockup sits on one line below it at 26px (23px under 340px); a two-line stacked lockup was tried and read as clunky. The social card and the weekly email's header use the same lockup.
- **Crumb home link:** on article and chart pages the first crumb carries the mark at 1.55em and the name as "Economy" in 700 Ink and "in Context" in Ink Secondary (no period, since a crumb continues), with the hairline underline under the name only.
- **Weekly digest signup:** a card before the footer of the almanac, every article page and the articles index, styled like Chart to try (Sheet, 2px ink rule on top, hairline sides, 6px radius, 15px text, at most the reading measure wide): "THE WEEKLY DIGEST" label, one sentence on what the email holds, a labeled email field (44px, Page fill, a Muted border so the field passes 3:1) and a "Subscribe" button (44px, filled in the button's teal ink, Sheet text; hover Ink), then "Past issues · How addresses are kept" in 13.5px. A plain HTML form posting to Buttondown, no script; hidden in print.
- **Coming up:** one quiet line under the Updated line, 13.5px in Ink Secondary: "Next releases:" and up to four headline releases, soonest first, each the release's reader-facing name as an underlined link to the agency's release page, a space, and the date as "Fri, Nov 6" (U.S. English, no time, no year; a name and its date never break across lines). Separated by " · ", so it reads as a sentence, not a list. Drawn from the release calendar the refresh writes into `data/series.json`, through a curated table of eight releases (jobs, consumer prices, GDP, PCE, job openings, housing starts, producer prices, the trade balance); daily and weekly releases are left out, as is BLS's Average Price Data, which always comes out with the CPI, and a date within ten days of the release's previous date is treated as a revision or supplement and skipped. Written at build time for the build's date and redrawn by the script for the reader's date; nothing upcoming, or no calendar, means no line. Not printed.
- **Section nav:** the same bar on the almanac and the articles index, between the title block and the lead items: a Sheet-colored strip with a 3px Wayfinding Ochre rule along the top and a hairline below, an "ON THIS PAGE" label (12.5px uppercase, ochre) and the section links at 15px/600 in Ink Secondary with no underline, so it reads as a menu and not as a line of links. The section whose top has passed under the bar is marked (`aria-current`): ink text and a 3px ochre marker on the bar's bottom edge (hover: the same marker). Sticky at the top at every width. On phones the label goes and the row scrolls sideways: 46px targets, fades at an edge with more to scroll to, the marked link kept in view. Jumps land just below it (scroll margin from its measured height). The articles index gets the bar from `build_articles.py` and its wayfinding from `assets/secnav.js`; the almanac builds both in index.html.
- **Back to the overview:** "↑ At a glance" at the right of every section heading (not in the tiles-only view).
- **Skip links:** the first Tab stop on each page, hidden until focused (ink with sheet text): "Skip to the numbers" on the almanac; "Skip to the chart" and "Skip to overlays" on chart pages.
- **Overlay panel:** collapsible groups (Reference lines, Companion series, Eras, Events) with a count. Companion series is open on every page that has any, and Reference lines when nothing is on; a group with something on is open; Eras and Events start closed. A rule shared by several overlays (how party control is dated, how events are chosen) is said once at the top of its group. Each checkbox's label is the overlay's name only; under it, the note's first sentence and its Source, with the rest behind a "More" text button (a first sentence under 40 characters takes the next with it). A color swatch appears only once a companion is on. An "On now" row under the panel's lead is always present (with nothing on it reads "nothing yet. Tick a box below." at a chip's height, so the list never shifts under the pointer when the first box is ticked) and lists each overlay that is on as a chip in list order: the name (shortened past 36 characters, full in its title) opens its group and focuses its checkbox; × turns it off and moves focus to the next chip. Chips are flat: hairline border, 4px radius, 12.5px text, 28px tall (40px on phones).
- **See-the-chart bar (phones):** fixed to the bottom edge, sheet background, hairline top border, 44px tall, 600-weight ink text: "N overlays on · See the chart ↑". Shown only while the overlay panel is in view and the chart is not.

- **Messages in place:** a bad custom range says why beside the Apply button ("The start has to come before the end."); a refused copy says so and shows the text selected for copying by hand. No dialogs.

### Range Strip (signature component)
The site's most original element, and a ranking rather than a ruler. The track (Range Bar) spans an indicator's typical range, the 5th to the 95th percentile of its own history; the latest reading is a teal dot with a sheet-colored ring placed at its rank, so it always agrees with the sentence beneath it; the 2015–19 average is a tick in Ink Secondary placed at that average's own rank, drawn over the dot when the two meet so it is never hidden. The end labels are the readings at the 5th and 95th percentiles. The center of the track is the median by construction; a short Muted notch marks it, and the label above names it in the longest form that fits between the end labels ("typical range · median 4.2%", else "median 4.2%"; on price tiles "typical range, in today's dollars · median $3.27", else "in today's dollars · median $3.27", else "in today's dollars", since the qualifier outranks the median). Naming the median is what shows the bar is a ranking, not a ruler. A reading outside the range keeps the dot, pinned at that end of the track but hollow (Sheet fill, teal ring), with an arrow outside it pointing outward and, on tiles, the label "below/above the range" stepped clear of the tick, both in Ink Secondary, the 2015–19 tick's gray: the hollow dot is still the reading, in the reading's color, and the arrow and label are an annotation, so they wear the annotation color (chosen Nov 3 from mocks; ink was tried and was the heaviest mark on the page in dark mode). The dot stays because its absence was the easiest thing on the page to miss, and outside the range is the one state a reader should stop at. On tiles it carries end labels and the average's value; in the overview it is compact and unlabeled, with the full sentence in its accessible name. Its own accessible name says whether the reading is within, below or above the range and gives the average. Price indicators use the range in today's dollars.

### At-a-glance Row
One line per indicator: title, latest value with its period in Muted, and a compact range strip with the median notch (keyed "median, always the middle"); rows grouped under small uppercase section labels, separated by hairlines, each at least 44px tall and linking to its tile.

### Chart to try
The right-hand card of the lead (see above): the "CHART TO TRY" label, a headline that links to a ready-made chart view (19px bold) with an arrow, one or two sentences in Ink Secondary at 15px cut at three lines, and at the foot a picture of the view, full card width by 56px, drawn by the articles build from the site's own data: the indicator in teal over the view's range, the first companion series the view turns on in the chart page's first companion color (`--c1`), a faint zero line when the scale crosses zero, no axes, and an end dot drawn as a round-capped stroke so it stays round when the picture is stretched to the card's width. The picture repeats the headline's link and is hidden from assistive technology. Set by a dated entry in `articles/chart-prompts.json` (`title`, `text`, `chart`, `query`). Hidden in print.

### Static readings (before the script)
The almanac's HTML carries every reading as a plain list, written at build time: a Muted "as of" line, then each section as a 19px heading over a bulleted list (title linking to the chart page, the value in bold, period, context sentence, household line), max 46em wide. The script replaces it with the tiles; if the figures fail to load it stays, under the retry line. No styling beyond the type scale: it is a fallback, not a second design.

### Framing Banner
A cream block with dark amber text and 4px radius, shown under a chart whenever a political overlay is on, stating how control is dated and that policy acts with a lag.

### Tooltip
Ink background, sheet-colored 12px text, 4px radius; the value in 600, then each companion with a small color key. It wraps rather than running off a phone screen (at most 320px, and never wider than the chart frame), stays inside the frame, and drops below the point when there is no room above.

### Lanes and events on narrow charts
Below 560px of chart width, lane names sit above their lanes, left-aligned with the plot, so the plot keeps its width. Party lanes name every full term the same way: full names if all fit, else last names, else letters; a term shorter than the office's own (four years for a president, two for Congress), still running or cut off by the window may drop to its letter. Every event has its own hairline and tick at its own date; marks are never merged. On a narrow chart, or in an image where a name wouldn't fit, each event gets its own number (1 to N by date). Numbers within 18px share a label ("3,4", "3–5", never spanning more than 30px), and a one-line key under the legend names them ("1 Oct 1979 Volcker shock · 2 …"); in an embed the key folds behind "What the numbers mark (N events)" and the frame refits when it opens. The full list with notes stays below on the page. The key's glyph is ▼, as drawn.

### Images for social posts
Each shape is laid out for its own frame, never cropped from the wide image: title (19px bold) and subtitle, the reading (32px, 28px in Wide) and its date, the percentile sentence (14px semibold; beside the reading in Wide), the today's-dollars note on price pages, the chart with its plot stretched to fill but no taller than about 3:4 of its width (a taller plot steepens every slope), the key, the framing banner when a party lane is on, numbered events listed (two columns if needed; an image numbers and lists its events whenever the chart would leave a marker unnamed, the full-width image too), and a hairline footer: the site's mark (the brackets around the Series dot, drawn in Ink at about 1.55× the footer's type size), the name set as in the masthead lockup ("Economy" 700 Ink, "in Context" 400 Ink Secondary, an Ink period), then the chart's address in Muted, with CC BY 4.0 at the right. When the address doesn't fit, the footer drops to the bare domain, then to the mark and address alone. The full-width image uses the same footer at 12px. Drawn at 480 CSS px across (720 for Wide) and scaled to the platform's pixels, so type reads in a phone feed; a crowded view is drawn up to 1.6× smaller rather than cut, and only then does a long events list end "…and N more on the chart page". Story keeps the top and bottom 14% empty. Always the light colors.

Clipped-value labels ("Apr 2020: −20,469K, off the chart") take the longest form that fits, beside the mark or else within the plot's width; a companion's name is kept before "off the chart" is.

### Embeds
An article's frame has one height for every screen. On this site's own pages the embedded chart grows its frame to fit its content (never shrinks it); in a frame on another site it gives up plot height instead, down to 120px. The embed code still sizes the frame from sub-panels, lanes, framing and events.

## Do's and Don'ts

### Do:
- **Do** keep the reading the largest number on the screen (40px tiles, 44px chart pages).
- **Do** give every number its period and source, including in downloads, embeds and printed pages.
- **Do** label every color: legends for series, text in every lane segment wide enough to hold it, a legend key for lane colors that carry meaning, hover titles for the rest.
- **Do** check every change in both color schemes at 1280px and 375px, with contrast computed: text ≥4.5:1, meaningful marks ≥3:1 or backed by labels.
- **Do** put different scales in a stacked sub-panel under the main chart. Lines measured the same way (the metro areas on the health care chart, each a percent change) share one sub-panel and one scale, named for the measure, and get their own heading in the overlay panel.
- **Do** let a sub-panel's name wrap to the plot's width, and a long name in a downloaded image's key wrap under itself; nothing runs off the chart.
- **Do** place anything on a range strip by rank, never by value, so the picture and the sentence agree.
- **Do** say "as charged" wherever a price is drawn as charged beside a range or sentence in today's dollars.
- **Do** give the median and the 2015–19 average different line patterns (dotted and dashed), keyed in the legend.
- **Do** show a deficit the way it is reported: the federal deficit as a positive number (FRED's sign flipped, and the note and CSV say so), so "5.8%" reads as it sounds. A balance that can go either way (trade) keeps its sign, says "balance" in its title and "below zero is a deficit" in its subtitle. Either way the sentence says "a larger/smaller deficit", never "higher/lower".
- **Do** change tokens in all three files at once.

### Don't:
- **Don't** add shadows, gradients, motion or transitions (the legend's hatch swatch is drawn with a CSS gradient function, but it is a pattern, not a gradient).
- **Don't** color a reading by whether it is good or bad, and don't use red and green as a pair anywhere.
- **Don't** give the data line or any companion a party's hue (blue or red), or teal or green for companions.
- **Don't** use a dual y-axis.
- **Don't** reuse a companion color on one chart, or repaint a line when another is turned on or off.
- **Don't** add a second typeface or a brand color system beyond these tokens.
- **Don't** put watermarks across the plot area or add text to copied content.
