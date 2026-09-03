"""Saturation analysis per ANALYSIS-PLAN.md (frozen d193c2b). Exact estimators only."""

import json
from math import comb
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)
EXP = Path("/Users/diz/dev/rankfor/ai-territory/dev-specs/research/experiments")


def cell_stats(runs_brands, label_extra=None):
    """runs_brands: list of per-run brand lists. Returns estimators of the plan."""
    n = len(runs_brands)
    sets = [set(b) for b in runs_brands]
    all_brands = set().union(*sets)
    r = {b: sum(b in s for s in sets) for b in all_brands}
    S_obs = len(all_brands)
    Q1 = sum(1 for v in r.values() if v == 1)
    Q2 = sum(1 for v in r.values() if v == 2)
    A = []
    for k in range(1, n + 1):
        miss = sum(comb(n - rb, k) / comb(n, k) if n - rb >= k else 0.0
                   for rb in r.values())
        A.append(S_obs - miss)
    if Q2 > 0:
        chao2 = S_obs + (n - 1) / n * Q1 * Q1 / (2 * Q2)
    else:
        chao2 = S_obs + (n - 1) / n * Q1 * (Q1 - 1) / 2
    out = dict(n=n, S_obs=S_obs, Q1=Q1, Q2=Q2,
               final_run_yield=Q1 / n, chao2=chao2,
               share_seen=S_obs / chao2 if chao2 > 0 else 1.0,
               still_rising=Q1 > 0, A=A)
    if label_extra:
        out.update(label_extra)
    return out


# ---------------------------------------------------------------- C-A breadth
bm = pd.read_parquet(EXP / "category-ownership/category_ownership_2026/data/brand_mentions.parquet")
rows, curves = [], []
excluded = 0
for (q, m), sub in bm.groupby(["query", "model"]):
    iters = sorted(sub.iteration.unique())
    if len(iters) < 4:
        excluded += 1
        continue
    runs = [sub[sub.iteration == it].brand.tolist() for it in iters]
    st = cell_stats(runs, dict(query=q, model=m, industry=sub.industry.iloc[0]))
    A = st.pop("A")
    curves.append(dict(query=q, model=m, **{f"A{k+1}": v for k, v in enumerate(A)}))
    rows.append(st)
ca = pd.DataFrame(rows)
ca_curves = pd.DataFrame(curves)
ca.to_csv(OUT / "ca_cells.csv", index=False)
ca_curves.to_csv(OUT / "ca_curves.csv", index=False)

print(f"C-A: {len(ca)} cells analyzed, {excluded} excluded (<4 iterations)")
print(f"  still rising at final run (Q1>0): {ca.still_rising.sum()}/{len(ca)} "
      f"({ca.still_rising.mean():.1%})")
print(f"  median share of Chao2 repertoire seen at n=5: {ca.share_seen.median():.1%} "
      f"(IQR {ca.share_seen.quantile(.25):.1%}-{ca.share_seen.quantile(.75):.1%})")
print(f"  median S_obs {ca.S_obs.median():.0f}, median Chao2 {ca.chao2.median():.1f}, "
      f"median final-run yield {ca.final_run_yield.median():.2f} new brands")
print("  per model still-rising:", ca.groupby('model').still_rising.mean().round(2).to_dict())
print("  per model share_seen median:", ca.groupby('model').share_seen.median().round(2).to_dict())
# what a single ask sees
a1 = ca_curves[[c for c in ca_curves.columns if c.startswith('A')]].values
print(f"  A(1)/A(5) median (share of 5-run set seen by ONE ask): "
      f"{np.median(a1[:,0]/a1[:,4]):.1%}")

# sensitivity: case-insensitive dedup
rows_ci = []
for (q, m), sub in bm.groupby(["query", "model"]):
    iters = sorted(sub.iteration.unique())
    if len(iters) < 4:
        continue
    runs = [sub[sub.iteration == it].brand.str.lower().str.strip().tolist() for it in iters]
    rows_ci.append(cell_stats(runs)["share_seen"])
print(f"  sensitivity (case-insensitive): median share_seen {np.median(rows_ci):.1%}")

# cross-model union (secondary)
uni_rows = []
for q, sub in bm.groupby("query"):
    per_model = {m: set(s.brand.str.lower()) for m, s in sub.groupby("model")}
    if len(per_model) == 3:
        union = set().union(*per_model.values())
        uni_rows.append(dict(query=q, union=len(union),
                             max_single=max(len(v) for v in per_model.values())))
uni = pd.DataFrame(uni_rows)
print(f"  cross-model: single model shows median {np.median(uni.max_single/uni.union):.1%} "
      f"of the 3-model union ({len(uni)} queries)")
uni.to_csv(OUT / "ca_union.csv", index=False)

# ---------------------------------------------------------------- C-B depth
print("\nC-B depth (n=24):")
cb_rows = []
for name, path in (("uk-supermarkets", EXP / "uk-supermarkets/recall_runs.json"),
                   ("nordic-care", EXP / "nordic-care/recall_runs.json")):
    d = json.load(open(path))
    df = pd.DataFrame(d)
    for m, sub in df.groupby("model"):
        for field in ("brandsNamed", "domains"):
            runs = [list(x) for x in sub[field]]
            st = cell_stats(runs, dict(cell=f"{name}/{m}", field=field))
            A = st.pop("A")
            cb_rows.append({**st, "A_curve": json.dumps([round(a, 2) for a in A])})
            print(f"  {name}/{m} [{field}]: n={st['n']} S_obs={st['S_obs']} "
                  f"Q1={st['Q1']} chao2={st['chao2']:.0f} share={st['share_seen']:.0%} "
                  f"rising={st['still_rising']} | A(1)={A[0]:.1f} A(5)={A[4]:.1f} "
                  f"A(10)={A[9]:.1f} A(24)={A[-1]:.1f}")
pd.DataFrame(cb_rows).to_csv(OUT / "cb_cells.csv", index=False)
print("\ndone")
