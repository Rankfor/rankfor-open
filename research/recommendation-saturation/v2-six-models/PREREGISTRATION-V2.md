# Saturation study v2, six engines: pre-registered design, frozen before collection

Frozen 2026-09-04, committed before any API call. Extends the saturation note
(`../RESULTS-SUMMARY.md`) from three engines at n = 5 to six engines at n = 15, with open
extraction as a first-class arm. The engine layer is the lotto experiment's
(`scripts/lotto-vs-models/run.py`), reused verbatim.

## Design

- **Engines (6):** gpt-5.6-luna (OpenAI), claude-sonnet-5 (Anthropic), gemini-3.7-flash
  (Google), grok-4.5 (xAI), mistral-large-latest (Mistral), sonar (Perplexity; web search on
  by design, all others off). Provider-default temperature, fresh context per call.
- **Queries (50):** the first 10 queries from each of the five industry files in the Category
  Ownership deposit (`queries/{saas,consulting,fintech,ecommerce,healthtech}_queries.json`),
  verbatim, deterministic selection.
- **Runs:** n = 15 per query x engine cell; 4,500 calls total; task order shuffled with seed
  2026; checkpointed and resumable; every response stored verbatim with timestamp and the
  provider-reported model version. Perplexity citation lists stored when returned.
- One smoke call per engine to verify credentials happens after this freeze and before the
  run; smoke responses are discarded and never analyzed.

## Extraction, fixed in advance, applied after collection completes

Two arms, both reported:
1. **Roster arm:** the deposit's brand-alias dictionary, unchanged (comparability with v1).
2. **Open arm (primary):** capitalized-candidate mining over all responses pooled across
   engines; adjudication of the pooled candidate list BEFORE any per-engine statistic is
   computed, by one written rule: a candidate counts if it names an organization that offers
   the queried product or service category. Loyalty programs, information sources, regulators,
   media, and product lines of an already-counted organization are excluded; parent and
   operating brands collapse to the parent only when one is a documented subsidiary of the
   other. The adjudicated list and every exclusion are committed.

## Estimators and pre-named headline statistics

The frozen estimator set of the v1 plan applies per cell (exact rarefaction A(k), final-run
yield Q1/n, Chao2, share seen). Reported regardless of direction:
- Per engine, open arm: share of cells still rising at n = 15 (Q1 > 0), median share seen at
  n = 5 and n = 15, median repertoire size.
- The v1 claims under test at depth: (a) brand curves reach 90%+ of Chao2 by n = 10 in the
  median cell of every engine; (b) A(1)/A(5) near 0.80 replicates per engine.
- Cross-engine: median share of the six-engine union covered by the best single engine;
  number of queries where an engine's repertoire contains a brand no other engine ever names.
- Sonar only: domain curves per cell (the citation-breadth replication the note calls for).

Exclusions: cells with fewer than 12 of 15 runs completed are excluded and counted. A call
failing after 5 retries is recorded as missing. No other exclusion is permitted.

## Reporting

Descriptive; all numbers reported. Outputs to `outputs/`; the note gains a v2 section or a
follow-up note. Deviations, if forced, are listed with reasons.
