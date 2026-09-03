# Pre-registered analysis plan: external validation of the Dice Roll Method on three independent corpora

Version 1.0, frozen 2026-09-03. Frozen by git commit in the `rankfor-ops` repository; the commit
hash is recorded in `SUBMISSION-REGISTER.md` and in `outputs/FREEZE.txt` immediately after the
commit. Any change after freezing is a labelled deviation reported in the results document.

Author of the validated method: Dmitrij Żatuchin. Analysis executed by Claude (Fable 5) under
the author's direction; all analytic decisions below were fixed before any confirmatory
statistic was computed on any of the three corpora.

## 1. Purpose

The Dice Roll Method paper (currently `aip-submission/dice-roll-arxiv.tex`) derives iteration
requirements for LLM audits from four studies collected by the author's own group. Reviewer 2
of the prior Discover AI submission asked for validation on data the group did not collect.
This plan pre-registers that validation on the three strongest publicly available repeated-query
corpora, each collected by an independent group for an unrelated purpose.

The claims under test are the paper's formal hypotheses as revised (Table
`tab:hypothesis_summary` of the manuscript):

- H1 (power): n = 5 iterations does not reach 80% power even for large effects
  (Cliff's |δ| ≥ 0.474); the 80% threshold is first met at n ≈ 15.
- H2 (convergence): SE(n) follows a diminishing-returns curve, power-law exponent ≈ 0.51
  (indistinguishable from logarithmic); 80% of asymptotic precision is reached by n ≤ 10
  (observed n = 7).
- H3 (generalizability): G = 0.58 at n = 5, 0.74 at n = 10, 0.81 at n = 15 in the original
  design; G ≥ 0.80 is first reached at n = 15.
- H5 (stationarity): the KS + PSI + NB drift battery flags no cells over a short collection
  window.
- Motivating claim (temperature-0 boundary): between-run variance persists at temperature 0.

H4 (cost knee) requires per-corpus pricing that the external corpora do not carry and is out of
scope. H6 (embedding ensemble) requires recomputing embeddings on third-party text and is
deferred to a possible secondary analysis; it is not part of this plan.

## 2. Corpora, acquisition state at freezing, and disclosure of prior data contact

| Corpus | Source | Design | License |
|---|---|---|---|
| C1 Motoki, Pinho Neto & Rodrigues (Public Choice, 2024) | Harvard Dataverse doi:10.7910/DVN/KGMEYI, file `gpt-dados.xlsx` | Political Compass, 62 questions × 100 rounds × personas (default, democrat, republican, radDemocrat, radRepublican; country and profession variants; 60-question placebo arm) | CC BY-NC-ND 4.0 |
| C2 Rozado (PLOS ONE, 2024) | Zenodo record 10553530, file `results.rar` | 11 political-orientation tests × 10 administrations × 24 conversational LLMs (plus base and fine-tuned models, excluded; §5) | CC BY 4.0 |
| C3 Atil et al., llm-stability | github.com/breckbaldwin/llm-stability, experiment archives `v3/runs.tgz`, `temperature_1.0`, `top_p_k_0_vs_1` | Benchmark tasks × models × 10 runs per identical prompt, per-run raw responses, decoding configs varied | Apache-2.0 |

Disclosure. C1 was downloaded on 2026-09-03 during corpus scouting; its sheet names, column
headers, and row counts were inspected to write this plan (codebook-level inspection). No
variance component, G coefficient, effect size, convergence statistic, or drift statistic has
been computed on it. C2 and C3: only public file listings and documentation were read; no data
file had been downloaded at the time this plan was written. Acquisition of C2 and C3 may begin
while this plan is being committed; no archive is opened before the freezing commit exists.

## 3. Variable mapping

The Dice Roll design is prompt × model × iteration with a numeric per-response outcome. The
mapping per corpus, fixed here:

| Dice Roll facet | C1 Motoki | C2 Rozado | C3 llm-stability |
|---|---|---|---|
| Object of measurement ("prompt") | question (62) | test (11) | task |
| Model facet | persona (5: chatGPT, democrat, republican, radDemocrat, radRepublican) | model (24 conversational) | model |
| Iteration facet | round (1..100) | administration (1..10) | run (1..10) |
| Outcome | Likert agreement score per question × persona × round (sheet `dataset_eua`); secondary: per-round economic and social axis scores (sheet `quadrant_calculation`) | the test's primary numeric scale score per administration, as produced by Rozado's own pipeline inside the archive; where only per-question responses exist, scored with the instrument's published key | accuracy per task × model × run (fraction of items correct in that run, computed with the repo's own evaluation code) |

The persona facet in C1 and the model facet in C2/C3 play the role of the paper's 3-provider
model facet. Personas are deliberately manipulated conditions, so their facet variance is
expected to exceed provider variance; this affects the level of G, and for that reason all
replication criteria in §4 are stated on within-design quantities (orderings, increments,
predicted-vs-empirical agreement), never on matching the original paper's absolute G values.

## 4. Confirmatory analyses, predictions, and decision rules

All estimators are the manuscript's own, taken verbatim from `dice_roll_method_v2.ipynb` and
collected into `dice_roll_estimators.py` (cells 14, 16, 19, 21, 27: `cliffs_delta`, `bca_ci`,
`mbb_se`, `fit_curves`, the mixedlm G-study with D-study formula
G(n_I, n_M) = σ²_P / (σ²_P + σ²_resid/n_I + σ²_M/n_M), and `psi` + `drift_tests`).
Pre-registered adaptations, forced by outcome type: the log(count + 0.5) transform applies to
counts only; C1 Likert and axis scores and C3 accuracies enter untransformed; the NB family in
the GEE drift test becomes Gaussian for C1 scores and binomial for C3 accuracy. No other
change to any estimator is permitted.

### EV1. Generalizability structure (paper H3)

Per corpus: fit the G-study on the full data with the mapping of §3; compute the D-study grid
G(n_I) for n_I ∈ {2, 3, 5, 7, 10, 15, 20} (n_I capped at the corpus maximum for C2/C3) at the
corpus's model-facet size and, for comparability, at n_M = 3.

Predictions and criteria:
- EV1a (all corpora): G(n_I) is strictly increasing and concave in n_I (increments decrease).
  Replicates if both hold on the D-study grid.
- EV1b (all corpora): G(5) < G(10) < G(15) with G(5) below 0.80 in the single-facet per-model
  analysis of EV2. (The pooled-facet G level is reported but carries no pass/fail criterion,
  per §3.)

### EV2. Out-of-sample D-study prediction (the strongest test; C1 primary, C2/C3 reduced)

Single-facet reliability per persona/model: object = question (C1) / test (C2) / task (C3),
facet = iteration. For each persona (C1) or model (C2, C3):

1. Estimate σ²_P and σ²_resid from the FIRST 10 iterations only (the paper's typical audit
   budget), using the same mixedlm decomposition.
2. Predict Ĝ(n) = σ²_P / (σ²_P + σ²_resid/n) for n ∈ {20, 50} (C1) and n ∈ {5} via
   split-half on the 10 available iterations (C2, C3).
3. Compute empirical G_emp(n) without the model: draw two disjoint random n-iteration subsets,
   compute each unit's subset mean, take the Pearson correlation across units between the two
   subset means; average over 200 random splits (seed 2026).

Criteria per persona/model cell: |Ĝ(n) − G_emp(n)| ≤ 0.05 replicates; ≤ 0.10 partial;
otherwise fails. Corpus verdict: replicates if ≥ 80% of cells replicate; partial if ≥ 80%
reach at least partial.

### EV3. Convergence (paper H2)

Per corpus: `mbb_se` per cell (unit × persona/model), subsample grid n = 2..50 for C1,
n = 2..10 for C2 and C3; `fit_curves` AIC comparison per cell; mean-SE curve and
percent-of-asymptotic-precision table exactly as in notebook cell 19.

Predictions and criteria:
- EV3a: power-law and logarithmic families jointly win the per-cell AIC vote (combined
  plurality over Michaelis-Menten and linear). Replicates if their combined share ≥ 50%.
- EV3b: fitted power-law exponent on the mean-SE curve lies in [0.35, 0.65] (the CLT n^(-1/2)
  band the paper's 0.51 sits in). Replicates if inside the band.
- EV3c: 80% of asymptotic precision reached by n ≤ 10 on the mean-SE curve (paper: n = 7).
  For C1 the asymptote is taken at n = 50, which makes this a sharper test than the original's
  n = 10 ceiling.

### EV4. Empirical power (paper H1; C1 only, its 100 rounds make power empirical)

Per question, contrast democrat vs republican persona scores. First compute Cliff's δ with BCa
95% CI per question on the full 100 rounds (estimator of cell 14). Then, for
n ∈ {5, 10, 15, 20} and 500 resamples per (question, n) (seed 2026): draw n rounds per arm,
test with two-sided Mann-Whitney U (scipy, asymptotic, tie-corrected), record the rejection
fraction at α = 0.05 as empirical power.

Predictions and criteria, restricted to questions with full-data |δ| ≥ 0.474 (the paper's
"large" class):
- EV4a: median empirical power at n = 5 is below 0.80. Replicates if it is.
- EV4b: the smallest n in the grid at which median power ≥ 0.80 is 10 or larger (the paper's
  revision puts it at 15 for its own data). Replicates if ≥ 10; the observed value is reported
  either way.

### EV5. Stationarity and negative control (paper H5)

- EV5a (C1): `drift_tests` (cell 27, Gaussian GEE per §4 header) on rounds ordered 1..100,
  cells = question × persona. Prediction: flagged-cell rate ≤ 10%. Replicates if so.
- EV5b (C1 placebo): on `dataset_placebo` (60 politically neutral questions), per-question
  democrat vs republican Cliff's δ. Prediction: median |δ| < 0.147 (Romano's negligible bound)
  and ≤ 10% of placebo questions flagged by the drift battery. Both must hold to replicate.
- EV5c (C3): drift battery across the 10 ordered runs per task × model cell at fixed decoding
  config. Prediction: flag rate ≤ 10%.

### EV6. Temperature-0 boundary (motivating claim; C3 only)

From the `temperature_1.0` and `top_p_k_0_vs_1` experiments plus v3 defaults: per task × model
cell, between-run variance of accuracy at temperature 0.

- EV6a: the share of temperature-0 cells with nonzero between-run variance is ≥ 50%, and no
  model is deterministic across all its cells (Atil et al.'s own headline, recomputed with our
  estimator). Replicates if both hold.
- EV6b: mean between-run variance at temperature 1 ≥ mean at temperature 0, paired by
  task × model where both configs exist (one-sided Wilcoxon signed-rank, α = 0.05).

## 5. Exclusions and missing data, fixed in advance

- C1: primary analysis uses `dataset_eua` (5 personas) and `quadrant_calculation` axis scores;
  `dataset_placebo` only for EV5b; country (`dataset_brazil`, `dataset_uk`) and `profession`
  sheets are held out as secondary descriptives, no criteria attached. Repeat-collection sheets
  `dataset_eua_2`, `dataset_eua_3`, `dataset_eua_reg` are excluded from confirmatory analysis
  (different sub-designs); they may appear in secondary robustness tables.
- C2: the 24 conversational LLMs only; the 5 base models and 3 politically fine-tuned models
  are excluded (interventions, off the audit population). A test × model cell with fewer than
  8 of the 10 administrations recoverable from the archive is excluded and listed with reason.
- C3: primary experiment is `v3`; `json_schema` and `logprob` are excluded (different
  manipulations); `temperature_1.0` and `top_p_k_0_vs_1` enter only through EV6.
- Global: cells with fewer than 4 iterations are excluded from convergence, fewer than 4 from
  drift (half-split needs ≥ 2 per half); every exclusion is counted and reported.

## 6. Multiplicity, inference posture, software, and reproducibility

Each EV item carries exactly one pre-stated criterion; there is no post hoc promotion of a
secondary descriptive to a confirmatory claim. Within the drift battery the original α/3
Bonferroni is retained. α = 0.05 throughout. The final verdict table reports every EV item as
replicates / partial / fails; failures are reported with the same prominence as successes.

Seeds: estimator-internal seeds stay as in the notebook (0 and 42); all new resampling uses
seed 2026. Software: Python 3.11+, numpy, pandas, scipy, statsmodels, openpyxl; exact versions
written to `outputs/environment.txt` at run time. All ingestion and analysis code lives in
`external-validation/`, outputs in `external-validation/outputs/<corpus>/`, and everything is
committed. The C1 file is used in place under its ND clause: results and statistics are
published, the derived per-row data are never redistributed.

## 7. Reporting

Results go to `external-validation/RESULTS.md` with the verdict table first, then per-corpus
detail. The manuscript gains an external-validation section (or appendix) that reports all
verdicts, including failures, and states plainly that no public brand-domain repeated-query
corpus from another group exists, so brand-domain external validation remains open pending the
two data requests recorded in `VALIDATION-PLAN.md`. Deviations from this plan, if any become
unavoidable (e.g., an archive lacking a documented field), are listed in a "Deviations"
section of RESULTS.md with the reason and the decision taken.
