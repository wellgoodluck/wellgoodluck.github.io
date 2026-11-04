# Pile 2026-11-03dot — outside-the-range marker: hollow dot, gray arrow (option F)

Built on main 88ceb19 (the 4:41 pm upload with the Coming up line and the grocery article). Three files; rollback copies beside this folder. Drag the three onto the repo root; Publish runs, no data fetch.

| File | What changed |
|---|---|
| `index.html` | A reading outside its typical range is drawn as a hollow dot (Sheet fill, teal ring, `class="now off"`) pinned at that end of the track, on tiles and on the At a glance rows; the arrow outside it and the "below/above the range" label are in Ink Secondary, the 2015–19 tick's gray (`#5a5955` light, `#c3c2b7` dark), instead of teal. Within-range dots are untouched. The key's "outside the range" glyph is a ring and a gray arrow; "How to read" says "a hollow dot pinned at either end, with a gray arrow pointing outward". |
| `chart.html` | The same hollow dot and gray arrow on the chart page's strip. |
| `DESIGN.md` | The range strip and Neutral Ground Teal descriptions, with the reasoning (the hollow dot is still the reading in the reading's color; the arrow and label are an annotation and wear the annotation color; ink was tried and was the heaviest mark on the page in dark mode). |

Chosen Nov 3 from mocks A–F on the claims tile and its overview row: F = the open ring (B) with the arrow and label in Ink Secondary rather than ink (D), Tom's suggestion for a lighter gray in dark mode.

Checks (offline, main + pile, light and dark, 1280 and 375): all 8 outside-range strips (claims, trade, debt, ground beef; tile and overview) hollow with a teal ring, arrows and labels in Ink Secondary, within-range dots unchanged, key glyph and How-to-read text updated, the chart page strip the same; no console errors, no sideways scroll. 28/28.
