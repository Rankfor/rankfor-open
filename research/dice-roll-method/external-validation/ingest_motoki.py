"""C1 ingestion (PREREGISTRATION.md §3): Motoki gpt-dados.xlsx to long format.

Primary source is sheet `quadrant_calculation` (explicit `round` column, five
personas' Likert answers plus economic/social axis scores). Placebo from
`dataset_placebo` with round derived from question cycling, verified by assert.
Outputs (never redistributed, ND clause): outputs/c1/c1_long.csv,
outputs/c1/c1_placebo_long.csv.
"""

from pathlib import Path
import pandas as pd

HERE = Path(__file__).parent
OUT = HERE / "outputs" / "c1"
OUT.mkdir(parents=True, exist_ok=True)

PERSONAS = {
    "chatGPT": ("chatGPT", "e_chatGPT", "s_chatGPT"),
    "democrats": ("democrats", "e_democrat", "s_democrat"),
    "republicans": ("republicans", "e_republican", "s_republican"),
    "radDemocrat": ("radDemocrat", "e_radDemocrat", "s_radDemocrat"),
    "radRepublican": ("radRepublican", "e_radRepublican", "s_radRepublican"),
}

# Ordinal coding of the 5-level Likert labels. Monotone, neutral mid-scale;
# rank-based estimators (Cliff's delta, MW, KS) are invariant to the choice.
LIKERT = {"strongly disagree": 0, "disagree": 1, "neutral": 2,
          "agree": 3, "strongly agree": 4}

qc = pd.read_excel(HERE / "motoki-gpt-dados.xlsx", sheet_name="quadrant_calculation")
qc.columns = [c.strip() for c in qc.columns]

rows = []
for persona, (ycol, ecol, scol) in PERSONAS.items():
    sub = qc[["round", "i_question", ycol, ecol, scol]].copy()
    sub.columns = ["round", "question", "y", "e", "s"]
    sub["persona"] = persona
    rows.append(sub)
long = pd.concat(rows, ignore_index=True)
long = long.dropna(subset=["y"])
long["y"] = long["y"].str.strip().str.lower().map(LIKERT)
assert long["y"].notna().all(), "unmapped Likert label"
long["round"] = long["round"].astype(int)
long["question"] = long["question"].astype(int)

n_q = long.question.nunique(); n_r = long["round"].nunique()
print(f"C1 primary: {len(long)} rows, {n_q} questions, {n_r} rounds, "
      f"{long.persona.nunique()} personas")
assert n_q == 62 and n_r == 100, "unexpected design size"
cell_sizes = long.groupby(["question", "persona"]).size()
print("iterations per question x persona: "
      f"min {cell_sizes.min()}, max {cell_sizes.max()}")
assert long["y"].between(0, 4).all(), "Likert answers outside 0..4"
long.to_csv(OUT / "c1_long.csv", index=False)

# Placebo: no round column; verify question cycling, derive round positionally.
pl = pd.read_excel(HERE / "motoki-gpt-dados.xlsx", sheet_name="dataset_placebo")
pl.columns = [c.strip() for c in pl.columns]
qs = pl["i_question"].astype(int).values
n_pq = pl["i_question"].nunique()
period = len(qs) // n_pq
assert len(qs) % n_pq == 0, "placebo rows do not tile evenly"
block_ok = all((qs[i * n_pq:(i + 1) * n_pq] == qs[:n_pq]).all() for i in range(period))
assert block_ok, "placebo question order not cyclic; cannot derive round"
pl["round"] = [i // n_pq + 1 for i in range(len(pl))]
plong = pl.melt(id_vars=["round", "i_question"],
                value_vars=["chatGPT", "democrats", "republicans"],
                var_name="persona", value_name="y").dropna(subset=["y"])
plong = plong.rename(columns={"i_question": "question"})
plong["y"] = plong["y"].str.strip().str.lower().map(LIKERT)
assert plong["y"].notna().all(), "unmapped placebo Likert label"
plong["question"] = plong["question"].astype(int)
print(f"C1 placebo: {len(plong)} rows, {plong.question.nunique()} questions, "
      f"{plong['round'].nunique()} rounds")
plong.to_csv(OUT / "c1_placebo_long.csv", index=False)
print("ingest OK")
