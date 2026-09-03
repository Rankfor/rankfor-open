"""C1 (Motoki) confirmatory analysis, PREREGISTRATION.md items EV1-EV5b.

Reads outputs/c1/c1_long.csv + c1_placebo_long.csv, writes per-item CSVs and
verdicts.json to outputs/c1/. Estimators from dice_roll_estimators.py only.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as sps

sys.path.insert(0, str(Path(__file__).parent))
from dice_roll_estimators import (cliffs_delta, bca_ci, mbb_se, fit_curves,
                                  power_exponent, gstudy, dstudy_G,
                                  single_facet_components, empirical_G,
                                  drift_tests)

HERE = Path(__file__).parent
OUT = HERE / "outputs" / "c1"
long = pd.read_csv(OUT / "c1_long.csv")
placebo = pd.read_csv(OUT / "c1_placebo_long.csv")
PERSONAS = sorted(long.persona.unique())
verdicts = {}

# ---------------------------------------------------------------- EV1
print("== EV1 pooled G-study (question x persona x round) ==")
sigma_p, model_var, sigma_resid = gstudy(long, "question", "persona", "y")
total = sigma_p + model_var + sigma_resid
print(f"sigma_P^2={sigma_p:.4f} ({sigma_p/total:.1%})  "
      f"sigma_M^2={model_var:.4f} ({model_var/total:.1%})  "
      f"sigma_resid^2={sigma_resid:.4f} ({sigma_resid/total:.1%})")
GRID = [2, 3, 5, 7, 10, 15, 20]
rows = []
for n_M in (3, 5):
    row = {"n_M": n_M}
    for n_I in GRID:
        row[f"n_I={n_I}"] = round(dstudy_G(sigma_p, model_var, sigma_resid, n_I, n_M), 3)
    rows.append(row)
dstudy_df = pd.DataFrame(rows)
dstudy_df.to_csv(OUT / "tab_ev1_dstudy.csv", index=False)
print(dstudy_df.to_string(index=False))
g_at_5 = [dstudy_G(sigma_p, model_var, sigma_resid, n, 5) for n in GRID]
# concavity on an uneven grid: slopes per unit n must decrease
inc = np.diff(g_at_5); slopes = inc / np.diff(GRID)
ev1a = bool((inc > 0).all() and (np.diff(slopes) < 0).all())
verdicts["EV1a"] = "replicates" if ev1a else "fails"
print("EV1a monotone+concave:", verdicts["EV1a"])

# single-facet full-data components per persona (used by EV1b and EV2)
sf_full = {}
for p in PERSONAS:
    sp, sr = single_facet_components(long[long.persona == p], "question", "y")
    sf_full[p] = (sp, sr)
g5 = {p: sp / (sp + sr / 5) for p, (sp, sr) in sf_full.items()}
g10 = {p: sp / (sp + sr / 10) for p, (sp, sr) in sf_full.items()}
g15 = {p: sp / (sp + sr / 15) for p, (sp, sr) in sf_full.items()}
ev1b = all(g5[p] < g10[p] < g15[p] for p in PERSONAS) and all(v < 0.80 for v in g5.values())
verdicts["EV1b"] = "replicates" if ev1b else "fails"
pd.DataFrame([{"persona": p, "G5": g5[p], "G10": g10[p], "G15": g15[p]}
              for p in PERSONAS]).to_csv(OUT / "tab_ev1b_singlefacet.csv", index=False)
print("EV1b G(5)<G(10)<G(15), all G(5)<0.80:", verdicts["EV1b"],
      "| G(5) range", round(min(g5.values()), 3), "-", round(max(g5.values()), 3))

# ---------------------------------------------------------------- EV2
print("\n== EV2 out-of-sample D-study prediction (first 10 rounds -> n=20,50) ==")
ev2_rows = []
for p in PERSONAS:
    sub = long[long.persona == p]
    first10 = sub[sub["round"] <= 10]
    sp, sr = single_facet_components(first10, "question", "y")
    for n in (20, 50):
        g_pred = sp / (sp + sr / n)
        g_emp = empirical_G(sub, "question", "round", "y", n, splits=200, seed=2026)
        diff = abs(g_pred - g_emp)
        cell = ("replicates" if diff <= 0.05 else
                "partial" if diff <= 0.10 else "fails")
        ev2_rows.append(dict(persona=p, n=n, G_pred=round(g_pred, 3),
                             G_emp=round(g_emp, 3), abs_diff=round(diff, 3),
                             cell_verdict=cell))
ev2_df = pd.DataFrame(ev2_rows)
ev2_df.to_csv(OUT / "tab_ev2_prediction.csv", index=False)
print(ev2_df.to_string(index=False))
rep_share = (ev2_df.cell_verdict == "replicates").mean()
atleast_partial = (ev2_df.cell_verdict != "fails").mean()
verdicts["EV2"] = ("replicates" if rep_share >= 0.8 else
                   "partial" if atleast_partial >= 0.8 else "fails")
print(f"EV2 corpus verdict: {verdicts['EV2']} "
      f"(replicate share {rep_share:.0%}, at-least-partial {atleast_partial:.0%})")

# ---------------------------------------------------------------- EV3
print("\n== EV3 convergence (mbb block bootstrap, n=2..50) ==")
conv_ns = list(range(2, 51))
best_counts = {k: 0 for k in ["log", "power", "mm", "linear"]}
ses_all = []
for (q, p), sub in long.groupby(["question", "persona"]):
    x = sub.sort_values("round").y.values.astype(float)
    ses = [mbb_se(x, n, block=2, reps=200) for n in conv_ns]
    ses_all.append(ses)
    aics = fit_curves(conv_ns, ses)
    best = min(aics, key=aics.get)
    best_counts[best] += 1
total_cells = sum(best_counts.values())
for k, v in best_counts.items():
    print(f"  {k:8s}: {v}/{total_cells} ({v/total_cells:.0%})")
mean_se = np.mean(ses_all, axis=0)
asym = mean_se[-1]
pct = [(1 - (se - asym) / (mean_se[0] - asym)) * 100 for se in mean_se]
conv_df = pd.DataFrame({"n": conv_ns, "mean_SE": mean_se, "pct_asymptotic": pct})
conv_df.to_csv(OUT / "tab_ev3_convergence.csv", index=False)
pd.DataFrame([best_counts]).to_csv(OUT / "tab_ev3_family_votes.csv", index=False)

share_pl = (best_counts["power"] + best_counts["log"]) / total_cells
verdicts["EV3a"] = "replicates" if share_pl >= 0.5 else "fails"
g_exp = power_exponent(conv_ns, mean_se)
verdicts["EV3b"] = "replicates" if 0.35 <= g_exp <= 0.65 else "fails"
n80 = next((n for n, pc in zip(conv_ns, pct) if pc >= 80), None)
verdicts["EV3c"] = "replicates" if (n80 is not None and n80 <= 10) else "fails"
print(f"EV3a power+log share {share_pl:.0%}: {verdicts['EV3a']}")
print(f"EV3b exponent {g_exp:.3f}: {verdicts['EV3b']}")
print(f"EV3c 80% precision at n={n80}: {verdicts['EV3c']}")

# ---------------------------------------------------------------- EV4
print("\n== EV4 empirical power (democrats vs republicans) ==")
rng = np.random.default_rng(2026)
eff_rows = []
for q, sub in long[long.persona.isin(["democrats", "republicans"])].groupby("question"):
    x = sub[sub.persona == "democrats"].sort_values("round").y.values.astype(float)
    y = sub[sub.persona == "republicans"].sort_values("round").y.values.astype(float)
    d, lo, hi = bca_ci(cliffs_delta, x, y, reps=1000)
    eff_rows.append(dict(question=q, delta=d, ci_low=lo, ci_high=hi))
eff_df = pd.DataFrame(eff_rows)
eff_df.to_csv(OUT / "tab_ev4_delta.csv", index=False)
large = eff_df[eff_df.delta.abs() >= 0.474]
print(f"questions with |delta| >= 0.474: {len(large)}/{len(eff_df)} "
      f"(median |delta| overall {eff_df.delta.abs().median():.3f})")

POWER_NS = [5, 10, 15, 20]
pow_rows = []
for q in large.question:
    sub = long[(long.question == q) & long.persona.isin(["democrats", "republicans"])]
    x = sub[sub.persona == "democrats"].y.values.astype(float)
    y = sub[sub.persona == "republicans"].y.values.astype(float)
    row = {"question": q}
    for n in POWER_NS:
        rej = 0
        for _ in range(500):
            xs = rng.choice(x, n, replace=False)
            ys = rng.choice(y, n, replace=False)
            if len(np.unique(np.concatenate([xs, ys]))) == 1:
                continue
            _, pval = sps.mannwhitneyu(xs, ys, alternative="two-sided",
                                       method="asymptotic")
            if pval < 0.05:
                rej += 1
        row[f"power_n{n}"] = rej / 500
    pow_rows.append(row)
pow_df = pd.DataFrame(pow_rows)
pow_df.to_csv(OUT / "tab_ev4_power.csv", index=False)
med = {n: pow_df[f"power_n{n}"].median() for n in POWER_NS}
print("median power:", {n: round(v, 2) for n, v in med.items()})
verdicts["EV4a"] = "replicates" if med[5] < 0.80 else "fails"
n_hit = next((n for n in POWER_NS if med[n] >= 0.80), None)
verdicts["EV4b"] = "replicates" if (n_hit is None or n_hit >= 10) else "fails"
print(f"EV4a median power(5)={med[5]:.2f}: {verdicts['EV4a']}")
print(f"EV4b first n with median power>=0.80: {n_hit}: {verdicts['EV4b']}")

# ---------------------------------------------------------------- EV5
print("\n== EV5 drift battery + placebo negative control ==")
drift_df = drift_tests(long, "question", "persona", "round", "y", family="gaussian")
drift_df.to_csv(OUT / "tab_ev5a_drift.csv", index=False)
flag_rate = drift_df.flag.mean()
verdicts["EV5a"] = "replicates" if flag_rate <= 0.10 else "fails"
print(f"EV5a flagged {drift_df.flag.sum()}/{len(drift_df)} ({flag_rate:.1%}): "
      f"{verdicts['EV5a']}")

pl_rows = []
for q, sub in placebo[placebo.persona.isin(["democrats", "republicans"])].groupby("question"):
    x = sub[sub.persona == "democrats"].y.values.astype(float)
    y = sub[sub.persona == "republicans"].y.values.astype(float)
    pl_rows.append(dict(question=q, delta=cliffs_delta(x, y)))
pl_df = pd.DataFrame(pl_rows)
pl_df.to_csv(OUT / "tab_ev5b_placebo_delta.csv", index=False)
med_abs = pl_df.delta.abs().median()
pdrift = drift_tests(placebo, "question", "persona", "round", "y", family="gaussian")
pdrift.to_csv(OUT / "tab_ev5b_placebo_drift.csv", index=False)
pflag = pdrift.flag.mean()
verdicts["EV5b"] = ("replicates" if (med_abs < 0.147 and pflag <= 0.10) else "fails")
print(f"EV5b placebo median |delta|={med_abs:.3f}, drift flag rate {pflag:.1%}: "
      f"{verdicts['EV5b']}")

(OUT / "verdicts.json").write_text(json.dumps(verdicts, indent=2))
print("\nC1 VERDICTS:", json.dumps(verdicts))
