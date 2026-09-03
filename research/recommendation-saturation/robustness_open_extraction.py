"""Post-freeze robustness check (2026-09-04, labeled as such in RESULTS-SUMMARY.md).

The frozen plan took brand sets as recorded. Both deep probes recorded brands
against fixed rosters (10 UK, 6 Nordic), and the observed plateaus sat one
brand under those ceilings, so the flat curves could have been dictionary
artifacts. This check mines open capitalized-candidate strings from the raw
responses, adjudicates genuine providers by reading their contexts (documented
in git history), extends the rosters (UK +M&S; Nordic +Ersta Diakoni,
+Blomsterfonden, +Stora Skondal, +Aleris, +Bracke Diakoni), and recomputes the
frozen estimators. Output: outputs/cb_cells_corrected.csv.
"""

import json
from collections import defaultdict
from math import comb
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
EXP = Path("/Users/diz/dev/rankfor/ai-territory/dev-specs/research/experiments")

ROSTERS = {
    "uk-supermarkets": {
        "Tesco": ["tesco"], "Sainsbury's": ["sainsbury"], "Asda": ["asda"],
        "Morrisons": ["morrisons"], "Ocado": ["ocado"], "Waitrose": ["waitrose"],
        "Aldi": ["aldi"], "Lidl": ["lidl"], "Iceland": ["iceland"],
        "Amazon Fresh": ["amazon fresh", "amazon"],
        "M&S": ["m&s", "marks & spencer", "marks and spencer", "marks &amp; spencer"],
    },
    "nordic-care": {
        "Ambea": ["ambea", "vardaga", "nytida"], "Humana": ["humana"],
        "Attendo": ["attendo"], "Dedicare": ["dedicare"], "Norlandia": ["norlandia"],
        "Förenede Care": ["förenede", "forenede"],
        "Ersta Diakoni": ["ersta"], "Blomsterfonden": ["blomsterfonden"],
        "Stora Sköndal": ["stora sköndal", "stora skondal", "stiftelsen stora"],
        "Aleris": ["aleris"], "Bräcke Diakoni": ["bräcke", "bracke"],
    },
}


def stats(sets):
    n = len(sets)
    allb = set().union(*sets)
    r = {b: sum(b in s for s in sets) for b in allb}
    S = len(allb)
    Q1 = sum(1 for v in r.values() if v == 1)
    Q2 = sum(1 for v in r.values() if v == 2)
    A = [S - sum(comb(n - rb, k) / comb(n, k) if n - rb >= k else 0
                 for rb in r.values()) for k in range(1, n + 1)]
    chao2 = S + (n - 1) / n * Q1 * Q1 / (2 * Q2) if Q2 > 0 else \
        S + (n - 1) / n * Q1 * (Q1 - 1) / 2
    return S, Q1, Q2, chao2, A


rows = []
for name, roster in ROSTERS.items():
    d = json.load(open(EXP / name / "recall_runs.json"))
    by = defaultdict(list)
    for row in d:
        by[row["model"]].append(row.get("response", ""))
    for m, texts in sorted(by.items()):
        sets = [{b for b, al in roster.items() if any(a in t.lower() for a in al)}
                for t in texts]
        S, Q1, Q2, chao2, A = stats(sets)
        rows.append(dict(cell=f"{name}/{m}", n=len(sets), S_obs=S, Q1=Q1, Q2=Q2,
                         chao2=round(chao2, 2), still_rising=Q1 > 0,
                         A_curve=json.dumps([round(a, 2) for a in A])))
        print(f"{name}/{m}: S_obs={S} Q1={Q1} chao2={chao2:.1f} "
              f"A(10)={A[9]:.1f} A(24)={A[-1]:.1f}")
out = HERE / "outputs" / "cb_cells_corrected.csv"
pd.DataFrame(rows).to_csv(out, index=False)
print("wrote", out)
