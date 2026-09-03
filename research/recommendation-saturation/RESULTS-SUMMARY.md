# Saturation results (computed 2026-09-04, plan frozen at d193c2b before computation)

One sentence: repeating an identical buying question exhausts the set of brands a language
model recommends within about ten runs, while the set of sources it cites is still growing at
twenty-four.

## Brands: the list ends

- Depth (4 cells, n = 24, UK supermarkets + Nordic care, GPT + Gemini): all four cells flat,
  Q1 = 0, the 24th run adds nothing; plateaus of 5-9 brands reached by roughly run 10.
- Breadth (705 buying-question cells, n = 5, 250 queries x GPT/Gemini/Perplexity, 32 cells
  excluded at < 4 iterations): median repertoire 5 brands; median Chao2 share seen at n = 5 is
  100% (IQR 95-100%); one ask shows 80% of what five asks reveal (median A(1)/A(5), 684 n=5
  cells); yet the fifth run still added a never-seen brand in 339 of 705 cells (48%), so the
  tail is thin but real. Case-insensitive dedup sensitivity: unchanged.
- Cross-model (secondary): for one query in four, a single model's 5-run repertoire covers at
  most 83% of the three-model union.

## Sources: the list keeps growing

- The same 4 deep cells, `domains` field: all four still rising at run 24 (Q1 = 18, 6, 41,
  12); 59-84% of the Chao2-estimated citation surface seen; one run shows 16-23% of what
  twenty-four runs reveal. The largest cell has seen 97 domains of an estimated ~164.
- Boundary stated plainly: the source half rests on 4 deep cells from 2 prompts; the breadth
  corpus stores no citations. A breadth replication of the domain curves is the one collection
  this note could still want.

## Why it lands (the note's discussion in three lines)

Brand tracking is a bounded measurement: a handful of repeats and the answer set is known,
which prices an audit. Citation monitoring is unbounded at practical n: the model keeps
reaching for new sources, so a tracker sampling once per prompt sees a fifth of the surface
that twenty-four samples reveal. What AI says stabilizes; where it looks does not.

Files: `outputs/ca_cells.csv`, `ca_curves.csv`, `ca_union.csv`, `cb_cells.csv`,
`fig1_saturation.png`. Estimators: exact rarefaction, Q1/n final-run yield, Chao2. Data:
Zenodo 10.5281/zenodo.20788142 (CC BY, this group's deposit) + two recall probes in
`dev-specs/research/experiments/{uk-supermarkets,nordic-care}`.

## Robustness check, post-freeze (2026-09-04, labeled)

The deep probes' original extraction matched fixed rosters (10 UK, 6 Nordic) and both
plateaus sat one brand below the ceiling, so the flat curves could have been dictionary
artifacts. Open candidate mining over the raw responses (script
`robustness_open_extraction.py`) surfaced one missed UK brand (M&S) and five missed Nordic
providers (Ersta Diakoni, Blomsterfonden, Stora Skondal, Aleris, Bracke Diakoni). With the
extended rosters the repertoires grow to 11, 9, 9, 7 and the verdict is unchanged: Q1 = 0 in
all four cells, 91-100% of final size by run ten, run 24 adds nothing
(`outputs/cb_cells_corrected.csv`). The note now carries this check; the breadth curves are
described as roster-relative, which is the object a tracker monitors. Domains never had the
ceiling (recorded from actual citations), so the right panel needed no correction.
