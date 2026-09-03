# Dice Roll external validation: verified candidate corpora and study plan

Scouted and repository-verified 2026-09-03 (two independent web sweeps; every repository tree
inspected, the Motoki file downloaded and parsed row-level). Purpose: answer the Discover AI
Reviewer 2 demand for validation on data this group did not collect, before any fourth journal
submission.

## The finding that frames everything

No public brand- or product-domain corpus with repeated identical prompts exists from any other
group. Kamruzzaman et al.'s brand-bias release is single-run per prompt; the Tow Center data is
single-run; GEO-bench holds inputs only; commercial trackers are customer-gated. External
validation therefore runs on out-of-domain repeated-query corpora and validates the STATISTICAL
machinery (variance components, iteration tiers, G-theory, drift), with brand-domain external
validation named as the remaining step. Two email routes could still land a brand-domain corpus
(below).

## Verified corpora, ranked

| # | Corpus | Repetition structure | License | Role in the validation |
|---|---|---|---|---|
| 1 | **Motoki, Pinho Neto & Rodrigues (Public Choice 2024)**, Harvard Dataverse doi:10.7910/DVN/KGMEYI | Political Compass, 62 questions x **100 rounds** x 5+ personas x 3 countries + a 6,000-row placebo arm; `round` column preserved | CC BY-NC-ND 4.0 | **The design twin.** G-theory with question x persona x round facets; Cliff's delta between personas; drift across sequential rounds; the placebo arm is a ready-made negative control. Do the n = 5/10/15 tiers hold on someone else's data? Working copy: `motoki-gpt-dados.xlsx` (one afternoon of ingestion; do not redistribute derived data, ND clause). |
| 2 | **Rozado (PLOS ONE 2024)**, zenodo.org/records/10553530 | 11 political-orientation tests x **10 administrations** x 24+ conversational LLMs, per-administration jsonl in a 4.3 GB RAR | CC BY 4.0 | **The model-facet sweep.** Widest model breadth found anywhere; tests whether G(n) behaves as the D-study predicts when the model facet is 24 wide instead of 3. |
| 3 | **Atil et al., `github.com/breckbaldwin/llm-stability`** | 8 benchmark tasks x **10 runs** per identical prompt per model x decoding config (temp 0 vs 1, top_p/k, schema, seeds), raw response text per run, 66,280 evaluations | Apache-2.0 | **The mechanics check.** Purpose-built non-determinism data; validates the drift diagnostics and the temperature-0 boundary claim (what the generative model predicts should happen to instability). |
| 4 | Mei et al. (PNAS 2024), `github.com/yutxie/ChatGPT-Behavioral` | 6 behavioral games x roles x **30 sessions**, MIT, plus ~88k-subject human baselines | MIT | Far-domain robustness check, clearly labeled. |
| 5 | Ouyang et al., `github.com/ShuyinOuyang/LLM-is-a-box-of-chocolate` | 829 code problems x temp configs x **5 instances** | **No license file** | Use only with author permission, or drop. |

Rejected with verified reasons: Argyle et al. (single completion or token probabilities, no
repeats), Salinas & Morstatter (perturbation design, one run per variant), Kirsten et al. (two
waves, n = 2, no release), Yang search-arena (arena design, no same-model repeats),
Dominguez-Olmedo (ordering permutations, never byte-identical prompts), all medical repeats
corpora (on-request or aggregate-only), PsychoBench and ConsistencyAI (no usable per-run data),
HuggingFace sweep (nothing documented).

## Two email routes to a brand-domain corpus

1. **Li & Sinnamon** (alice.li@ubc.ca, luanne.sinnamon@ubc.ca): their audit ran the same 48
   queries 7 times each on 3 engines (N = 1,008), exactly the needed design; data unpublished,
   no availability statement. One polite request citing their paper.
2. **ChoiceEval authors** (`stupidhumanAI/ChoiceEval`, Oxford coauthors): brand/product
   preference audit with 5 repeats per task by design; repo currently ships question banks
   only. Ask whether response data can be shared.

## Study shape (the validation paper or appendix)

Three corpora, three claims: Motoki tests the iteration tiers and drift machinery on a
100-round design twin; Rozado tests generalizability across a 24-model facet; llm-stability
tests the decoding-config boundary. Pre-register the analysis plan before touching the data
(R2 asked for exactly this), report per-corpus whether the per-cell power values and G
thresholds reproduce, and state plainly that brand-domain external validation awaits a corpus
that does not yet publicly exist, with the two requests above in flight.
