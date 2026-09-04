#!/usr/bin/env python3
"""Six-engine saturation analysis per PREREGISTRATION-V2.md (56d62de).
Open arm primary, roster arm for v1 comparability, sonar domain curves.
Outputs to outputs/.
"""
import json
import re
from collections import defaultdict
from math import comb
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd

HERE = Path(__file__).parent
OUT = HERE / "outputs"
OUT.mkdir(exist_ok=True)

rows = []
for line in open(HERE / "data" / "raw_responses.jsonl"):
    r = json.loads(line)
    if r.get("iteration") == -1:
        continue
    rows.append(r)

adj = json.load(open(HERE / "data" / "adjudicated.json"))

# roster arm: deposit aliases
import sys
sys.path.append(str(Path("/Users/diz/dev/rankfor/ai-territory/dev-specs/research/experiments/"
                          "category-ownership/category_ownership_2026")))
roster_aliases = json.load(open("/Users/diz/dev/rankfor/ai-territory/dev-specs/research/"
                                "experiments/category-ownership/category_ownership_2026/"
                                "brands/brand_aliases.json"))


def cell_stats(sets):
    n = len(sets)
    allb = set().union(*sets) if sets else set()
    r = {b: sum(b in s for s in sets) for b in allb}
    S = len(allb)
    Q1 = sum(1 for v in r.values() if v == 1)
    Q2 = sum(1 for v in r.values() if v == 2)
    A = [S - sum(comb(n - rb, k) / comb(n, k) if n - rb >= k else 0.0
                 for rb in r.values()) for k in range(1, n + 1)]
    chao2 = (S + (n - 1) / n * Q1 * Q1 / (2 * Q2)) if Q2 > 0 else \
        (S + (n - 1) / n * Q1 * (Q1 - 1) / 2)
    return S, Q1, chao2, A


# per-query alias regex (open arm), longest alias first, word boundaries
open_maps = {}
for qkey, kept in adj.items():
    industry, qidx, qtext = qkey.split("|", 2)
    pairs = sorted(kept.items(), key=lambda kv: -len(kv[0]))
    open_maps[(industry, int(qidx))] = [(re.compile(
        r"(?<![A-Za-z0-9])" + re.escape(a) + r"(?![A-Za-z0-9])", re.I), can)
        for a, can in pairs]

ros_pairs = sorted(roster_aliases.items(), key=lambda kv: -len(kv[0]))
ros_rx = [(re.compile(r"(?<![A-Za-z0-9])" + re.escape(a) + r"(?![A-Za-z0-9])", re.I), can)
          for a, can in ros_pairs]


def domains_of(cits):
    out = set()
    for c in cits or []:
        u = c.get("url") if isinstance(c, dict) else c
        if not u:
            continue
        try:
            host = urlparse(u).netloc.lower()
        except Exception:
            continue
        host = host[4:] if host.startswith("www.") else host
        if host:
            out.add(host)
    return out


cells = defaultdict(lambda: defaultdict(dict))  # arm -> (q,e) -> it -> set
for r in rows:
    key = (r["industry"], r["query_idx"])
    text = r.get("response") or ""
    ob = {can for rx, can in open_maps.get(key, []) if rx.search(text)}
    rb = {can for rx, can in ros_rx if rx.search(text)}
    cells["open"][(key, r["engine"])][r["iteration"]] = ob
    cells["roster"][(key, r["engine"])][r["iteration"]] = rb
    if r["engine"] == "sonar":
        cells["domains"][(key, "sonar")][r["iteration"]] = domains_of(r.get("citations"))

results = {}
for arm in ("open", "roster", "domains"):
    recs = []
    for (key, eng), runs in cells[arm].items():
        sets = [runs[i] for i in sorted(runs)]
        if len(sets) < 12:
            continue
        S, Q1, chao2, A = cell_stats(sets)
        recs.append(dict(industry=key[0], query_idx=key[1], engine=eng,
                         n=len(sets), S_obs=S, Q1=Q1,
                         chao2=round(chao2, 2), rising=Q1 > 0,
                         A1=round(A[0], 2), A5=round(A[4], 2),
                         A10=round(A[9], 2), A15=round(A[-1], 2),
                         share5=round(A[4] / chao2, 3) if chao2 else 1.0,
                         share10=round(A[9] / chao2, 3) if chao2 else 1.0,
                         share15=round(S / chao2, 3) if chao2 else 1.0,
                         a1_over_a5=round(A[0] / A[4], 3) if A[4] else None))
    df = pd.DataFrame(recs)
    df.to_csv(OUT / f"v2_cells_{arm}.csv", index=False)
    results[arm] = df

print("=" * 70)
print("OPEN ARM (primary), per engine:")
df = results["open"]
per = df.groupby("engine").agg(
    cells=("rising", "size"), rising=("rising", "mean"),
    med_S=("S_obs", "median"), med_share5=("share5", "median"),
    med_share10=("share10", "median"), med_share15=("share15", "median"),
    med_a1a5=("a1_over_a5", "median")).round(3)
print(per.to_string())
print("\nv1 claims under test:")
print("(a) median A(10)/Chao2 >= 0.90 per engine:",
      {e: bool(v >= 0.90) for e, v in per.med_share10.items()})
print("(b) A(1)/A(5) near 0.80 per engine:", per.med_a1a5.to_dict())

print("\nROSTER ARM, per engine (v1 comparability):")
print(results["roster"].groupby("engine").agg(
    med_S=("S_obs", "median"), rising=("rising", "mean"),
    med_a1a5=("a1_over_a5", "median")).round(3).to_string())

print("\nSONAR DOMAIN CURVES (the citation-breadth replication):")
dd = results["domains"]
print(f"cells: {len(dd)} | rising at n=15: {dd.rising.sum()} ({dd.rising.mean():.0%})")
print(f"median S_obs {dd.S_obs.median():.0f}, median share15 {dd.share15.median():.1%}, "
      f"median A(1)/A(15) {(dd.A1/dd.A15).median():.1%}")

# cross-engine union (open arm)
uni = []
for key, grp in results["open"].groupby(["industry", "query_idx"]):
    engs = grp.engine.unique()
    if len(engs) < 6:
        continue
    # repertoire per engine = union of canonicals over runs
    reps = {}
    for e in engs:
        runs = cells["open"][((key[0], key[1]), e)]
        reps[e] = set().union(*runs.values())
    union = set().union(*reps.values())
    best = max(len(v) for v in reps.values())
    excl = sum(1 for b in union if sum(b in v for v in reps.values()) == 1)
    uni.append(dict(industry=key[0], query_idx=key[1], union=len(union),
                    best_single=best, best_share=round(best / len(union), 3),
                    engine_exclusive=excl))
u = pd.DataFrame(uni)
u.to_csv(OUT / "v2_union.csv", index=False)
print(f"\nCROSS-ENGINE (open): median best-single/union {u.best_share.median():.0%} "
      f"(p25 {u.best_share.quantile(.25):.0%}); median union {u.union.median():.0f} orgs; "
      f"median engine-exclusive brands per query {u.engine_exclusive.median():.0f}")

excl_counts = (results['open'].groupby('engine')
               .apply(lambda g: g.n.count(), include_groups=False))
json.dump({
    "open_per_engine": per.reset_index().to_dict("records"),
    "sonar_domains": dict(cells=int(len(dd)), rising=int(dd.rising.sum()),
                          med_share15=float(dd.share15.median())),
    "union": dict(med_best_share=float(u.best_share.median()),
                  med_union=float(u.union.median())),
}, open(OUT / "v2_verdicts.json", "w"), indent=1)
print("\nsaved outputs/")
