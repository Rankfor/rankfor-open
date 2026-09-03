# External validation of the Dice Roll Method: results

Pre-registered plan: `PREREGISTRATION.md`, frozen at rankfor-ops commit
`c0bc686b5a03d1de03f83b2980e5f098833858f8` (2026-09-03) before any confirmatory statistic ran.
Estimators: the manuscript's own notebook code, collected in `dice_roll_estimators.py`. All
tables under `outputs/`. All three corpora executed 2026-09-03.

## Verdict table

| Item | Claim under test | C1 Motoki | C2 Rozado | C3 llm-stability |
|---|---|---|---|---|
| EV1a | G(n) monotone, concave | replicates | replicates | replicates |
| EV1b | G(5) < G(10) < G(15), all G(5) < 0.80 | fails (informative) | fails (informative) | fails (informative) |
| EV2 | D-study components predict out-of-sample reliability | **replicates, 10/10 cells** | **replicates, 22/24 cells (2 partial, 0 fail)** | **replicates, 5/5 cells** |
| EV3a | power/log family wins SE(n) AIC vote | fails (MM wins on long grid) | replicates (log 99%) | replicates (log 100%) |
| EV3b | power exponent in the CLT band [0.35, 0.65] | replicates (0.500) | fails (0.075, fit degenerate on n ≤ 10) | fails (0.046, fit degenerate on n ≤ 10) |
| EV3c | 80% of asymptotic precision by n ≤ 10 | fails (n = 16 vs n = 50 asymptote) | replicates (n = 8) | replicates (n = 8) |
| EV4a | median power at n = 5 below 0.80 for large δ | **replicates (0.43 vs paper's simulated 0.44)** | n/a | n/a |
| EV4b | first n with median power ≥ 0.80 is ≥ 10 | replicates (n = 10) | n/a | n/a |
| EV5a | drift flag rate ≤ 10% | fails (see diagnosis) | n/a | fails (see diagnosis) |
| EV5b | placebo: median \|δ\| < 0.147 and ≤ 10% flags | fails (see diagnosis) | n/a | n/a |
| EV6a | non-determinism at temperature 0 | n/a | n/a | replicates (100% of cells, 0 deterministic models) |
| EV6b | var(T = 1) ≥ var(T = 0), paired | n/a | n/a | not evaluable (4 pairs; needs ≥ 5) |

## The headline

The paper's core machinery survives contact with data it never saw. Across all three corpora,
the out-of-sample D-study prediction (EV2) replicates in 37 of 39 cells with 2 partials and
zero failures: variance components estimated from 10 iterations predicted measurement
reliability at n = 20 and n = 50 on Motoki's 100-round corpus with a maximum absolute error of
0.038 across all five personas, at n = 5 on Rozado's 24 models with a maximum error of 0.070,
and at n = 5 on llm-stability with error ≤ 0.002 across all five models. Median empirical
power at n = 5 for large effects, computed by direct subsampling from 100 real rounds, is 0.43;
the manuscript's GLMM simulation had put it at 0.44 (EV4a). Non-determinism at temperature 0 is
universal in the llm-stability corpus: no model and no cell is deterministic (EV6a), which is
the premise the whole method rests on. One descriptive echo worth a sentence: at the paper's
own facet size (n_M = 3), the pooled Rozado D-study gives G(10) = 0.748 against the paper's
G(10) = 0.74.

What fails, fails in a way that sharpens the method rather than undermining it: the fixed
iteration prescriptions (the "n = 15" constant) do not transfer across corpora, while the
formula that generates them does; and two components of the drift battery over-flag outside
their operating range, with the failure modes now characterized precisely (below).

## C1: Motoki, Pinho Neto & Rodrigues (Public Choice 2024)

Design twin: 62 questions × 5 personas × 100 rounds, Likert outcomes, plus a 60-question
placebo arm. Ingestion in `ingest_motoki.py` (5-level ordinal coding; rank-based estimators are
invariant to it).

- **EV1a replicates.** Pooled D-study G is monotone and concave on the grid (0.151 → 0.334 at
  n_M = 5). The pooled level is low because persona variance is a deliberate manipulation here
  (σ²_M = 1.53 vs σ²_P = 0.19), exactly the regime difference §3 of the plan anticipated.
- **EV1b fails, informatively.** Single-facet G(5) per persona: republicans 0.60, democrats
  0.79, radRepublican 0.83, chatGPT 0.90, radDemocrat 0.95. The claim "G(5) < 0.80 always" is
  false for highly consistent respondents: radical personas answer so stably that five rounds
  already suffice. The iteration requirement is a function of the variance ratio, which is what
  the D-study formula computes; the corpus-independent constant is what fails.
- **EV2 replicates, 10/10 cells.** Components from rounds 1-10 predicted G at n = 20 within
  0.000-0.038 and at n = 50 within 0.002-0.020 of the model-free empirical reliability
  (200 disjoint-split correlations per cell). This is a 5x extrapolation beyond the fitting
  horizon on independent data.
- **EV3a fails; EV3b replicates.** On the long grid (n = 2..50) Michaelis-Menten wins 93% of
  per-cell AIC votes; the paper's power/log verdict was an artifact of its n ≤ 10 grid. The
  mean-SE curve's fitted power exponent is 0.500, exactly the CLT rate the paper's 0.51
  estimated.
- **EV3c fails.** Against a proper n = 50 asymptote, 80% of asymptotic precision arrives at
  n = 16, twice the paper's n = 7 (which was measured against an n = 10 ceiling). The
  convergence claim needs restating relative to an explicit asymptote horizon.
- **EV4a and EV4b replicate.** 42/62 questions show |δ| ≥ 0.474. Median empirical power:
  0.43 (n = 5), 0.80 (n = 10), 0.95 (n = 15), 0.99 (n = 20).
- **EV5a and EV5b fail; the diagnosis isolates one defective component.** Flag sources on the
  primary arm (310 cells): GEE window test 305, PSI 157, KS 50. On the placebo (180 cells):
  window 142, PSI 1, **KS 0**. The GEE window test is anticonservative in the within-cell,
  single-cluster configuration (sandwich variance degenerates when dispersion is near zero),
  and it, not the data, produces the blanket failure. The KS component behaves: it clears the
  placebo completely and flags 16% of primary cells, concentrated in the default (17/62) and
  democrat (25/62) personas and absent in the radical ones (0-1/62), a coherent pattern of
  real nonstationarity across Motoki's collection arc. Placebo median |δ| = 0.197 exceeds the
  0.147 bound: persona prompting shifts answers even on politically neutral questions, so the
  placebo arm is a weaker negative control than assumed (an observation about the corpus, and
  worth a sentence in the manuscript).

## C3: Atil et al., llm-stability

16 prompt cells (8 tasks × 2 shot conditions) × 5 models × 10 runs, temperature 0, per-run
accuracy from the repo's own published evaluation. Primary arm: v3 top_p_k = 1.0 (the complete
80-cell factorial).

- **EV1a replicates** (0.698 → 0.878 at the full model facet, monotone and concave).
- **EV1b fails, same boundary as C1.** Between-task accuracy spread dwarfs run noise, so
  single-facet G(5) ≈ 0.997-1.000 for every model: five runs already rank tasks almost
  perfectly. Again the constant fails while the formula stands.
- **EV2 replicates, 5/5 cells,** with predicted-vs-empirical differences ≤ 0.002.
- **EV3a and EV3c replicate** (log wins 100% of AIC votes; 80% precision at n = 8). **EV3b
  fails:** the three-parameter power fit is degenerate on a 9-point grid (exponent 0.046 with
  the offset absorbing the curvature); the family vote, not the exponent, is the informative
  statistic at n ≤ 10.
- **EV5c fails; diagnosis matches C1.** 80/80 cells flagged: PSI 74 (saturated at 5 samples
  per half), window 77 (same degeneracy), KS 2. Mean |early-late| accuracy difference is
  0.007 with a maximum of 0.034, so the flags mark substantively negligible shifts.
- **EV6a replicates.** Every task × model cell at temperature 0 has nonzero between-run
  variance; no model is deterministic anywhere. **EV6b not evaluable:** the corpus holds only
  4 temperature-1 cells after deduplication (2 models × 2 tasks, few-shot only), below the
  pre-registered minimum of 5 pairs. Descriptively, median between-run variance is higher at
  temperature 1 in 3 of 4 pairs.

## C2: Rozado (PLOS ONE 2024)

Model-facet sweep: 8 unit tests × 24 conversational models × 8-10 administrations (1,861 run
records), outcome = the test's primary scale score per administration from Rozado's own
per-trial pipeline output, min-max normalized per test over the observed range (deviations
5-7). Three of the archive's 11 tests fall to the plan's exclusion clause: politicalTypologyQuiz
emits only a categorical classification, and the two iSideWith tests emit per-party agreement
vectors with no primary scale and unstable field order. Rozado's pipeline substitutes a random
answer when a model refuses; only 8 of 189 cells contain any substitution, and a sensitivity
fit without them moves no variance component at the third decimal.

- **EV1a replicates** (monotone, concave; 0.695 → 0.898 at the 24-model facet). At the paper's
  n_M = 3, G(10) = 0.748 vs the paper's 0.74.
- **EV1b fails, same boundary a third time.** 22 of 24 models sit at single-facet G(5) ≥ 0.80:
  political positions are stable enough across administrations that 5 retakes already place a
  model on a test. The outlier is instructive: qwen-14b-chat has G(5) ≈ 0.07, a model whose
  administrations barely correlate, exactly the case where the pilot-then-solve prescription
  would demand a much larger n.
- **EV2 replicates, 22/24 cells (2 partial: claude-instant-1 at 0.070, qwen-14b-chat at 0.053,
  the latter at the bottom of the G scale where the criterion is tightest).** Median absolute
  prediction error across models: 0.008.
- **EV3a and EV3c replicate** (log wins 189-cell AIC vote at 99%; 80% precision at n = 8).
  **EV3b fails** the same degenerate way as C3: the three-parameter power fit is unidentifiable
  on a 9-point grid (exponent 0.075 with the offset absorbing curvature).
- **Secondary, labeled exploratory:** reliability of ranking *models* by an n-administration
  mean, per test on raw scales. Political Compass and Spectrum need n ≈ 3 for G ≥ 0.80; the
  Eysenck test does not reach 0.80 even at n = 10 (G = 0.60). Iteration requirements are a
  property of the instrument, which is the Dice Roll thesis restated in Rozado's domain.

## What the manuscript gains

1. **A pre-registered external validation section** with a frozen plan, a public freeze hash,
   and failures reported at the same prominence as successes: EV2 (37/39 cells across three
   corpora, zero failures) and EV4a are the two strongest results and both are direct hits
   (0.43 vs 0.44 deserves a figure).
2. **A sharpened central prescription.** Both corpora refute the corpus-independent iteration
   constant and confirm the variance-ratio formula that replaces it: report "estimate
   components on a 10-iteration pilot, then solve G(n) ≥ 0.80 for n" as the method's output,
   with the paper's n = 15 as the value that solution takes on its own data.
3. **Operating bounds for the drift battery, with fixes.** PSI needs ≥ 20 iterations per half;
   the GEE window test needs replacement by a permutation test on the half-mean difference (or
   proper multi-cell clustering) plus a practical-significance margin; KS is the component
   that works as intended at both n = 5 and n = 50 per half. External data found a real defect
   the original data could not see; that is the validation working.
4. **The temperature-0 premise confirmed on independent data** (EV6a), citable directly.

## Deviations from the pre-registered plan

1. **v3 decoding arms (C3).** The v3 experiment folder contains two decoding arms the plan did
   not anticipate; the complete top_p_k = 1.0 factorial (80 cells, N = 10 everywhere) is the
   primary, the partial 0.0 arm feeds only the EV6b temperature pairing.
2. **Duplicate collections (C3).** Where a (model, task, shots, config) cell was collected on
   several dates, the latest collection is kept.
3. **Verdict-check correction (EV1a).** The concavity check as first coded compared raw
   increments on an unevenly spaced n-grid; concavity requires slopes per unit n. Corrected
   for both corpora before any reporting; C1's EV1a verdict changed from fails to replicates
   under the correct mathematics (G(n) = σ²_P/(σ²_P + a/n + c) is analytically concave). The
   git history preserves both states.
4. **Likert coding (C1).** The plan fixed the outcome as the Likert agreement score without
   fixing the numeric coding; the standard 5-level ordinal coding was used. Rank-based
   estimators are invariant to any monotone coding; the Gaussian G-study is not, which is a
   scale limitation shared with the original paper's log-count transform.
5. **Primary scale field (C2).** The plan named "the test's primary numeric scale score"
   without a per-test field map. Fixed deterministically before analysis: the economic-type
   axis where one exists (6 tests), the instrument's canonical first axis otherwise (Eysenck
   radical_to_traditional, ideologies progressivism). Three tests excluded under the plan's
   own clause: no numeric primary scale exists (categorical typology; per-party vectors).
6. **Scale harmonization (C2).** The pooled G-study needs commensurate units across tests;
   the plan was silent. Per-test min-max normalization over the observed range across all 33
   models and all trials (deterministic, reproducible from the archive alone). Per-test
   linear maps leave within-test structure and all rank-based statistics untouched.
7. **Refusal substitutions (C2).** Rozado's pipeline answers randomly on refusal, which
   injects variance the method would read as non-determinism. Not anticipated by the plan;
   handled by reporting the substitution counter (8 of 189 cells affected) and a sensitivity
   fit without those cells, which changes no component at the third decimal.
