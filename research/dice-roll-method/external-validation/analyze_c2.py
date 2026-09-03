"""C2 (Rozado) ingestion + confirmatory analysis: EV1, EV2 (reduced), EV3.

Outcome per PREREGISTRATION.md: the test's primary numeric scale score per
administration from Rozado's own pipeline (per-trial JSON). Implementation
decisions the plan left open, fixed here and logged in RESULTS.md deviations:
- Primary scale field per test: the economic-type axis where one exists, the
  instrument's canonical first axis otherwise (eysenck: radical_to_traditional,
  ideologies: progressivism). politicalTypologyQuiz (categorical only) and the
  two iSideWith tests (per-party vector, no primary scale, unstable field
  order) are excluded with reason -> 8 unit tests.
- Scale harmonization for the pooled G-study: per-test min-max normalization
  over the observed range across ALL models and trials (deterministic,
  data-driven; per-test linear maps leave within-test structure intact).
- Model exclusions per plan section 5: 5 base models, 3 politically
  fine-tuned (lwgpt, rwgpt, depolarizinggpt), plus the pipeline scaffold
  'fake-model' -> 24 conversational models.
- Rozado's pipeline substitutes a random answer when a model refuses; the
  per-trial counter is recorded and a sensitivity excluding cells with any
  substitution is reported alongside the primary.
"""

import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from dice_roll_estimators import (mbb_se, fit_curves, power_exponent, gstudy,
                                  dstudy_G, single_facet_components,
                                  empirical_G)

HERE = Path(__file__).parent
OUT = HERE / "outputs" / "c2"
OUT.mkdir(parents=True, exist_ok=True)
ROOT = HERE / "corpora" / "rozado" / "experiment_1"

PRIMARY_FIELD = {
    "eightValuesPoliticalTest": "economic_axis_score",
    "eysenckPoliticalTest": "radical_to_traditional_score",
    "ideologiesTest": "progressivism_score",
    "nolanTest": "economic_score",
    "politicalCompassTest": "economic_score",
    "politicalCoordinatesTest": "economic_score",
    "politicalSpectrumQuiz": "economic_score",
    "worldSmallestPoliticalQuiz": "economic_issues_score",
}
EXCLUDED_TESTS = {"politicalTypologyQuiz": "categorical classification only",
                  "iSideWithUK": "per-party vector, no primary scale",
                  "iSideWithUS": "per-party vector, no primary scale"}
EXCLUDED_MODELS = {"babbage-002", "davinci-002", "meta-llama_Llama-2-7b-hf",
                   "meta-llama_Llama-2-13b-hf", "meta-llama_Llama-2-70b-hf",
                   "lwgpt", "rwgpt", "depolarizinggpt", "fake-model"}
COUNTER = "number_of_questions_responded_with_random_answer_counter"

rows = []
for test, field in PRIMARY_FIELD.items():
    for mdir in sorted((ROOT / test).iterdir()):
        model = mdir.name
        for f in sorted(mdir.glob("*trial_*.json")):
            m = re.search(r"trial_(\d+)\.json$", f.name)
            d = json.loads(f.read_text())
            if field not in d:
                continue
            rows.append(dict(test=test, model=model, trial=int(m.group(1)),
                             y_raw=float(d[field]),
                             random_subs=int(d.get(COUNTER, 0))))
raw = pd.DataFrame(rows)
# observed-range normalization over ALL models (incl. excluded) and trials
rng = raw.groupby("test")["y_raw"].agg(["min", "max"])
rng.to_csv(OUT / "tab_normalization_ranges.csv")
raw = raw.merge(rng, on="test")
raw["y"] = (raw.y_raw - raw["min"]) / (raw["max"] - raw["min"])

long = raw[~raw.model.isin(EXCLUDED_MODELS)].copy()
cell_n = long.groupby(["test", "model"]).size()
small = cell_n[cell_n < 8]
if len(small):
    print("excluded cells (<8 administrations):")
    print(small)
    long = long[~long.set_index(["test", "model"]).index.isin(small.index)]
print(f"C2: {len(long)} rows, {long.test.nunique()} tests, "
      f"{long.model.nunique()} models, administrations per cell "
      f"{long.groupby(['test','model']).size().min()}-"
      f"{long.groupby(['test','model']).size().max()}")
subs_cells = (long.groupby(["test", "model"])["random_subs"].sum() > 0)
print(f"cells with any random-answer substitution: {subs_cells.sum()}/{len(subs_cells)}")
long.to_csv(OUT / "c2_long.csv", index=False)

verdicts = {}

# ---------------------------------------------------------------- EV1
print("\n== EV1 pooled G-study (test x model x administration) ==")
sigma_p, model_var, sigma_resid = gstudy(long, "test", "model", "y")
total = sigma_p + model_var + sigma_resid
print(f"sigma_P^2={sigma_p:.5f} ({sigma_p/total:.1%})  sigma_M^2={model_var:.5f} "
      f"({model_var/total:.1%})  resid={sigma_resid:.5f} ({sigma_resid/total:.1%})")
GRID = [2, 3, 5, 7, 10]
tab = []
for n_M in (3, long.model.nunique()):
    row = {"n_M": n_M}
    for n_I in GRID:
        row[f"n_I={n_I}"] = round(dstudy_G(sigma_p, model_var, sigma_resid, n_I, n_M), 3)
    tab.append(row)
dstudy_df = pd.DataFrame(tab)
dstudy_df.to_csv(OUT / "tab_ev1_dstudy.csv", index=False)
print(dstudy_df.to_string(index=False))
g_grid = [dstudy_G(sigma_p, model_var, sigma_resid, n, long.model.nunique()) for n in GRID]
inc = np.diff(g_grid); slopes = inc / np.diff(GRID)
verdicts["EV1a"] = "replicates" if ((inc > 0).all() and (np.diff(slopes) < 0).all()) else "fails"
print("EV1a monotone+concave:", verdicts["EV1a"])

MODELS = sorted(long.model.unique())
sf_rows = []
for m in MODELS:
    sp, sr = single_facet_components(long[long.model == m], "test", "y")
    g5, g10, g15 = (sp / (sp + sr / n) for n in (5, 10, 15))
    sf_rows.append(dict(model=m, G5=g5, G10=g10, G15=g15))
sf_df = pd.DataFrame(sf_rows)
sf_df.to_csv(OUT / "tab_ev1b_singlefacet.csv", index=False)
ev1b = bool(((sf_df.G5 < sf_df.G10) & (sf_df.G10 < sf_df.G15)).all()
            and (sf_df.G5 < 0.80).all())
verdicts["EV1b"] = "replicates" if ev1b else "fails"
print(f"EV1b: {verdicts['EV1b']} | G(5) range "
      f"{sf_df.G5.min():.3f}-{sf_df.G5.max():.3f}, models with G(5)>=0.80: "
      f"{(sf_df.G5 >= 0.80).sum()}/{len(sf_df)}")

# ---------------------------------------------------------------- EV2 (reduced)
print("\n== EV2 reduced: predicted vs empirical G at n=5 ==")
ev2_rows = []
for m in MODELS:
    sub = long[long.model == m]
    full = sub.groupby("test")["trial"].count()
    sub10 = sub[sub.test.isin(full[full >= 10].index)]
    if sub10.test.nunique() < 4:
        continue
    sp, sr = single_facet_components(sub10, "test", "y")
    g_pred = sp / (sp + sr / 5)
    g_emp = empirical_G(sub10, "test", "trial", "y", 5, splits=200, seed=2026)
    diff = abs(g_pred - g_emp)
    cell = "replicates" if diff <= 0.05 else "partial" if diff <= 0.10 else "fails"
    ev2_rows.append(dict(model=m, n_tests=sub10.test.nunique(),
                         G_pred=round(g_pred, 3), G_emp=round(g_emp, 3),
                         abs_diff=round(diff, 3), cell_verdict=cell))
ev2_df = pd.DataFrame(ev2_rows)
ev2_df.to_csv(OUT / "tab_ev2_prediction.csv", index=False)
print(ev2_df.to_string(index=False))
rep = (ev2_df.cell_verdict == "replicates").mean()
alp = (ev2_df.cell_verdict != "fails").mean()
verdicts["EV2"] = ("replicates" if rep >= 0.8 else "partial" if alp >= 0.8 else "fails")
print(f"EV2 verdict: {verdicts['EV2']} (replicate share {rep:.0%})")

# ---------------------------------------------------------------- EV3
print("\n== EV3 convergence (n=2..10) ==")
conv_ns = list(range(2, 11))
best_counts = {k: 0 for k in ["log", "power", "mm", "linear"]}
ses_all = []
excluded = 0
for (t, m), sub in long.groupby(["test", "model"]):
    x = sub.sort_values("trial").y.values.astype(float)
    if len(x) < 4:
        excluded += 1
        continue
    ns_here = [n for n in conv_ns if n <= len(x)]
    ses = [mbb_se(x, n, block=2, reps=200) for n in ns_here]
    if len(ns_here) == len(conv_ns):
        ses_all.append(ses)
    aics = fit_curves(ns_here, ses)
    best_counts[min(aics, key=aics.get)] += 1
total_cells = sum(best_counts.values())
for k, v in best_counts.items():
    print(f"  {k:8s}: {v}/{total_cells} ({v/total_cells:.0%})")
mean_se = np.mean(ses_all, axis=0)
asym = mean_se[-1]
pct = [(1 - (se - asym) / (mean_se[0] - asym)) * 100 for se in mean_se]
pd.DataFrame({"n": conv_ns, "mean_SE": mean_se, "pct_asymptotic": pct}
             ).to_csv(OUT / "tab_ev3_convergence.csv", index=False)
pd.DataFrame([best_counts]).to_csv(OUT / "tab_ev3_family_votes.csv", index=False)
share_pl = (best_counts["power"] + best_counts["log"]) / total_cells
verdicts["EV3a"] = "replicates" if share_pl >= 0.5 else "fails"
try:
    g_exp = power_exponent(conv_ns, mean_se)
except Exception:
    g_exp = float("nan")
verdicts["EV3b"] = "replicates" if 0.35 <= g_exp <= 0.65 else "fails"
n80 = next((n for n, pc in zip(conv_ns, pct) if pc >= 80), None)
verdicts["EV3c"] = "replicates" if (n80 is not None and n80 <= 10) else "fails"
print(f"EV3a power+log {share_pl:.0%}: {verdicts['EV3a']} | "
      f"EV3b exponent {g_exp:.3f}: {verdicts['EV3b']} | "
      f"EV3c 80% at n={n80}: {verdicts['EV3c']}")

# ------------------------------------------------ sensitivity: no substitutions
clean = long[~long.set_index(["test", "model"]).index.isin(
    subs_cells[subs_cells].index)]
sp_c, mv_c, sr_c = gstudy(clean, "test", "model", "y")
print(f"\nsensitivity (cells with zero random substitutions, "
      f"{clean.groupby(['test','model']).ngroups} cells): "
      f"sigma_P^2={sp_c:.5f} sigma_M^2={mv_c:.5f} resid={sr_c:.5f}")
pd.DataFrame([dict(sigma_p=sp_c, model_var=mv_c, sigma_resid=sr_c)]
             ).to_csv(OUT / "tab_sensitivity_nosubs.csv", index=False)

# ---------------- secondary (exploratory, labeled): object = model, per test
sec = []
for t in sorted(long.test.unique()):
    sub = long[long.test == t]
    sp, sr = single_facet_components(sub, "model", "y_raw")
    for n in (1, 3, 5, 10):
        sec.append(dict(test=t, n=n, G=round(sp / (sp + sr / n), 3)))
sec_df = pd.DataFrame(sec).pivot(index="test", columns="n", values="G")
sec_df.to_csv(OUT / "tab_secondary_model_ranking_G.csv")
print("\nsecondary (exploratory): G for ranking MODELS by an n-administration mean")
print(sec_df.to_string())

(OUT / "verdicts.json").write_text(json.dumps(verdicts, indent=2))
print("\nC2 VERDICTS:", json.dumps(verdicts))
