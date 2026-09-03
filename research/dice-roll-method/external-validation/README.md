# External validation of the Dice Roll Method

Pre-registered validation of the Dice Roll Method's statistical machinery on three
repeated-query corpora collected by independent groups. The plan (`PREREGISTRATION.md`) was
frozen on 2026-09-03, commit `c0bc686b5a03d1de03f83b2980e5f098833858f8` in the group's internal
repository, before any confirmatory statistic ran; the hash and date are also stated in the
paper. Results and the full verdict table: `RESULTS.md`. Per-item statistics: `outputs/`.

## Reproducing

The third-party corpora are not redistributed here (Motoki et al. carries an ND clause; the
other two are large). Fetch them from their canonical sources:

1. **C1** Motoki, Pinho Neto & Rodrigues, Harvard Dataverse `doi:10.7910/DVN/KGMEYI`
   (`gpt-dados.xlsx`, place next to the scripts as `motoki-gpt-dados.xlsx`).
2. **C2** Rozado, Zenodo record 10553530 (`results.rar`, extract the per-trial `*.json` files
   to `corpora/rozado/`).
3. **C3** `git clone https://github.com/breckbaldwin/llm-stability` into `corpora/`.

Then:

```bash
python3 ingest_motoki.py && python3 analyze_c1.py
python3 analyze_c2.py
python3 analyze_c3.py
```

`dice_roll_estimators.py` holds the paper's own estimators, ported verbatim from the analysis
notebook; the pre-registered adaptations (outcome transform and GEE family per outcome type)
are the only differences and are documented inline. Software versions used for the reported
runs: `outputs/environment.txt`. Deviations from the frozen plan are listed at the end of
`RESULTS.md`.
