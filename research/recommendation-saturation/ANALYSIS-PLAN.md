# How many answers does an LLM have? Analysis plan, frozen before computation

Frozen 2026-09-04, committed before any statistic below was computed. Question: when the same
buying question is put to the same model repeatedly, how fast does the set of recommended
brands stop growing, and how much of the model's repertoire has an auditor seen after n runs?

## Corpora (both already collected, both this group's own; the note says so plainly)

- **C-A, breadth:** the Category Ownership deposit (Zenodo 10.5281/zenodo.20788142, CC BY),
  `brand_mentions.parquet`: 250 brand-free category buying questions x 3 models
  (GPT-5.2, Gemini 3 Flash, Perplexity sonar-pro), up to 5 iterations, 737 non-empty
  query x model cells. Brand strings are used exactly as deposited; a case-insensitive
  dedup is the only sensitivity check. Cells with fewer than 4 iterations are excluded
  from cell-level statistics and counted.
- **C-B, depth:** two recommendation recall probes (UK supermarkets, Nordic care), 2 models
  x 24 identical runs each, `brandsNamed` per run as recorded; 4 prompt x model cells.
  Secondary: the `domains` field gives a citation-surface twin of every estimator.

## Estimators (exact, closed-form; no simulation, no seeds)

Per cell, build the brand x run incidence matrix; r_b = number of runs naming brand b,
n = runs in the cell, S_obs = distinct brands.

1. **Accumulation curve**: exact expected richness after k runs,
   A(k) = S_obs - sum_b C(n - r_b, k) / C(n, k) (sample-based rarefaction).
2. **Final-run yield**: A(n) - A(n-1) = Q1/n, where Q1 = brands appearing in exactly one
   run. A cell is "still rising" iff Q1 > 0.
3. **Next-run novelty**: the Turing estimate Q1/n of the probability-weighted number of new
   brands the (n+1)-th run would add; reported as a heuristic, labeled as such.
4. **Repertoire size**: Chao2 incidence estimator
   S_chao2 = S_obs + ((n-1)/n) * Q1^2 / (2 Q2), with the standard correction
   S_obs + ((n-1)/n) * Q1 (Q1 - 1) / 2 when Q2 = 0. **Share seen** = S_obs / S_chao2.
5. **Headline counting stat** (reported whichever way it falls): the number of cells with
   Q1 > 0, i.e. cells where the last run collected still added a brand no other run named;
   plus the median share-seen at n = 5 (C-A) and the shape of A(k) to k = 24 (C-B).
6. **Secondary**: cross-model union vs single-model repertoires per query (C-A); the domain
   versions of estimators 1-5 (C-B).

## Reporting

Descriptive study; no hypothesis test is claimed. All numbers reported regardless of
direction. Output tables to `outputs/`, one figure in the house style (grey per-cell curves,
mint mean), and a three-page note in the one-claim format if and only if the curves carry a
one-sentence claim.
