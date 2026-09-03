"""C3 (llm-stability) ingestion + confirmatory analysis: EV1, EV2(reduced),
EV3, EV5c, EV6 per PREREGISTRATION.md.

Outcome: per-run accuracy from the repo's own published evaluation
(stability_eval.csv, column correct_count_per_run / num_questions). Unit is the
prompt cell (task, shots); model facet = model; iteration = run index (files
are numbered 0..9 in collection order). Where a (model, task, shots) cell was
re-collected on several dates, the latest date is kept (logged as an
implementation note; the prereg did not anticipate duplicate collections).
"""

import ast
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as sps

sys.path.insert(0, str(Path(__file__).parent))
from dice_roll_estimators import (mbb_se, fit_curves, power_exponent, gstudy,
                                  dstudy_G, single_facet_components,
                                  empirical_G, drift_tests)

HERE = Path(__file__).parent
OUT = HERE / "outputs" / "c3"
OUT.mkdir(parents=True, exist_ok=True)
REPO = HERE / "corpora" / "llm-stability"
verdicts = {}


def load_eval(path):
    df = pd.read_csv(path)
    df["shots"] = df.task_config.map(lambda s: str(ast.literal_eval(s)["shots"]))
    df["temperature"] = df.model_config.map(lambda s: ast.literal_eval(s)["temperature"])
    df["top_p_k"] = df.model_config.map(lambda s: ast.literal_eval(s).get("top_p_k"))
    df = (df.sort_values("date")
            .groupby(["model", "task", "shots", "temperature", "top_p_k"], as_index=False)
            .tail(1))
    rows = []
    for _, r in df.iterrows():
        counts = ast.literal_eval(r.correct_count_per_run)
        for run, c in enumerate(counts):
            rows.append(dict(model=r.model, task=r.task, shots=r.shots,
                             temperature=r.temperature, top_p_k=r.top_p_k,
                             unit=f"{r.task}|{r.shots}", run=run,
                             correct=c, nq=r.num_questions, acc=c / r.num_questions))
    return pd.DataFrame(rows)


v3_all = load_eval(REPO / "experiments" / "v3" / "stability_eval.csv")
# v3 holds two decoding arms; top_p_k=1.0 is the complete 80-cell factorial
# with N=10 everywhere, top_p_k=0.0 covers 34 cells. Primary = the complete
# arm (deviation note: the prereg did not anticipate two arms inside v3).
long = v3_all[v3_all.top_p_k == 1.0].copy()
print(f"C3 v3: {len(long)} run rows, {long.unit.nunique()} units, "
      f"{long.model.nunique()} models, runs per cell "
      f"{long.groupby(['unit','model']).size().min()}-{long.groupby(['unit','model']).size().max()}")
long.to_csv(OUT / "c3_long.csv", index=False)

# ---------------------------------------------------------------- EV1
print("\n== EV1 pooled G-study (unit x model x run) ==")
sigma_p, model_var, sigma_resid = gstudy(long, "unit", "model", "acc")
total = sigma_p + model_var + sigma_resid
print(f"sigma_P^2={sigma_p:.5f} ({sigma_p/total:.1%})  sigma_M^2={model_var:.5f} "
      f"({model_var/total:.1%})  resid={sigma_resid:.5f} ({sigma_resid/total:.1%})")
GRID = [2, 3, 5, 7, 10]
rows = []
for n_M in (3, long.model.nunique()):
    row = {"n_M": n_M}
    for n_I in GRID:
        row[f"n_I={n_I}"] = round(dstudy_G(sigma_p, model_var, sigma_resid, n_I, n_M), 3)
    rows.append(row)
dstudy_df = pd.DataFrame(rows)
dstudy_df.to_csv(OUT / "tab_ev1_dstudy.csv", index=False)
print(dstudy_df.to_string(index=False))
g_grid = [dstudy_G(sigma_p, model_var, sigma_resid, n, long.model.nunique()) for n in GRID]
# concavity on an uneven grid: slopes per unit n must decrease
inc = np.diff(g_grid); slopes = inc / np.diff(GRID)
verdicts["EV1a"] = "replicates" if ((inc > 0).all() and (np.diff(slopes) < 0).all()) else "fails"
print("EV1a monotone+concave:", verdicts["EV1a"])

MODELS = sorted(long.model.unique())
sf = {}
for m in MODELS:
    sp, sr = single_facet_components(long[long.model == m], "unit", "acc")
    sf[m] = (sp, sr)
g5 = {m: sp / (sp + sr / 5) for m, (sp, sr) in sf.items()}
g10 = {m: sp / (sp + sr / 10) for m, (sp, sr) in sf.items()}
g15 = {m: sp / (sp + sr / 15) for m, (sp, sr) in sf.items()}
ev1b = all(g5[m] < g10[m] < g15[m] for m in MODELS) and all(v < 0.80 for v in g5.values())
verdicts["EV1b"] = "replicates" if ev1b else "fails"
pd.DataFrame([{"model": m, "G5": g5[m], "G10": g10[m], "G15": g15[m]} for m in MODELS]
             ).to_csv(OUT / "tab_ev1b_singlefacet.csv", index=False)
print("EV1b:", verdicts["EV1b"], "| G(5):",
      {m: round(v, 3) for m, v in g5.items()})

# ---------------------------------------------------------------- EV2 (reduced)
print("\n== EV2 reduced: predicted vs empirical G at n=5 (split-half) ==")
ev2_rows = []
for m in MODELS:
    sub = long[long.model == m]
    cells = sub.groupby("unit")["run"].count()
    if cells.min() < 10:
        sub = sub[sub.unit.isin(cells[cells >= 10].index)]
    sp, sr = single_facet_components(sub, "unit", "acc")
    g_pred = sp / (sp + sr / 5)
    g_emp = empirical_G(sub, "unit", "run", "acc", 5, splits=200, seed=2026)
    diff = abs(g_pred - g_emp)
    cell = "replicates" if diff <= 0.05 else "partial" if diff <= 0.10 else "fails"
    ev2_rows.append(dict(model=m, G_pred=round(g_pred, 3), G_emp=round(g_emp, 3),
                         abs_diff=round(diff, 3), cell_verdict=cell))
ev2_df = pd.DataFrame(ev2_rows)
ev2_df.to_csv(OUT / "tab_ev2_prediction.csv", index=False)
print(ev2_df.to_string(index=False))
rep = (ev2_df.cell_verdict == "replicates").mean()
alp = (ev2_df.cell_verdict != "fails").mean()
verdicts["EV2"] = ("replicates" if rep >= 0.8 else "partial" if alp >= 0.8 else "fails")
print(f"EV2 verdict: {verdicts['EV2']}")

# ---------------------------------------------------------------- EV3
print("\n== EV3 convergence (n=2..10) ==")
conv_ns = list(range(2, 11))
best_counts = {k: 0 for k in ["log", "power", "mm", "linear"]}
ses_all = []
excluded = 0
for (u, m), sub in long.groupby(["unit", "model"]):
    x = sub.sort_values("run").acc.values.astype(float)
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
print(f"excluded cells (<4 runs): {excluded}")
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

# ---------------------------------------------------------------- EV5c
print("\n== EV5c drift battery across ordered runs ==")
drift_df = drift_tests(long, "unit", "model", "run", "acc", family="binomial")
drift_df.to_csv(OUT / "tab_ev5c_drift.csv", index=False)
flag_rate = drift_df.flag.mean() if len(drift_df) else 0.0
verdicts["EV5c"] = "replicates" if flag_rate <= 0.10 else "fails"
print(f"flagged {drift_df.flag.sum()}/{len(drift_df)} ({flag_rate:.1%}): "
      f"{verdicts['EV5c']}")

# ---------------------------------------------------------------- EV6
print("\n== EV6 temperature-0 boundary ==")
var0 = (long.groupby(["unit", "model"])["acc"].var()
        .rename("var_t0").reset_index())
nonzero_share = (var0.var_t0 > 0).mean()
per_model_det = var0.groupby("model")["var_t0"].apply(lambda v: (v == 0).all())
verdicts["EV6a"] = ("replicates"
                    if nonzero_share >= 0.5 and not per_model_det.any() else "fails")
var0.to_csv(OUT / "tab_ev6a_var_t0.csv", index=False)
print(f"EV6a nonzero-variance share {nonzero_share:.0%}, "
      f"fully deterministic models: {per_model_det.sum()}: {verdicts['EV6a']}")

t1 = load_eval(REPO / "experiments" / "temperature_1.0" / "stability_eval.csv")
tp = load_eval(REPO / "experiments" / "top_p_k_0_vs_1" / "stability_eval.csv")
# temp-0 / top_p_k=0 pool: whole cells only, dedicated experiment preferred,
# v3's 0.0 arm fills cells the experiment lacks (never mixing runs per cell).
tp0 = tp[(tp.temperature == 0.0) & (tp.top_p_k == 0.0)]
v30 = v3_all[v3_all.top_p_k == 0.0]
have = set(map(tuple, tp0[["model", "unit"]].drop_duplicates().values))
fill = v30[~v30.set_index(["model", "unit"]).index.isin(have)]
t0_match = pd.concat([tp0, fill], ignore_index=True)
v1 = (t1.groupby(["model", "unit"])["acc"].var().rename("var_t1"))
v0 = (t0_match.groupby(["model", "unit"])["acc"].var().rename("var_t0"))
pairs = pd.concat([v0, v1], axis=1).dropna()
pairs.to_csv(OUT / "tab_ev6b_pairs.csv")
print(f"paired cells: {len(pairs)}")
if len(pairs) >= 5:
    try:
        stat, pval = sps.wilcoxon(pairs.var_t1, pairs.var_t0, alternative="greater")
    except ValueError:
        pval = 1.0
    verdicts["EV6b"] = "replicates" if pval < 0.05 else "fails"
    print(f"EV6b Wilcoxon one-sided p={pval:.4f} "
          f"(median var t1={pairs.var_t1.median():.5f} vs t0={pairs.var_t0.median():.5f}): "
          f"{verdicts['EV6b']}")
else:
    verdicts["EV6b"] = "not evaluable (too few pairs)"
    print("EV6b:", verdicts["EV6b"])

(OUT / "verdicts.json").write_text(json.dumps(verdicts, indent=2))
print("\nC3 VERDICTS:", json.dumps(verdicts))
