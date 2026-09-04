"""Figures for the two-study saturation note.
fig1: median brand accumulation per engine (open arm, n=15), retrieval marked.
fig2: cited domains: four deep web-search cells (n=24) + sonar breadth median (n=15).
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager

HERE = Path(__file__).parent
NOTE = HERE.parent / "note"
try:
    font_manager.fontManager.addfont("/Users/diz/Library/Fonts/Fustat-VariableFont_wght.ttf")
except Exception:
    pass
plt.rcParams["font.family"] = ["Fustat", "Helvetica Neue", "Arial"]
INK = "#1A1B1E"; GREY = "#D0D6DC"; SUB = "#676F79"

ENG_COL = {
    "gpt-5.6-luna": "#0072B2", "claude-sonnet-5": "#E69F00",
    "gemini-3.7-flash": "#009E73", "grok-4.5": "#CC79A7",
    "mistral-large": "#56B4E9", "sonar": "#D55E00",
}
ENG_LAB = {
    "gpt-5.6-luna": "GPT-5.6", "claude-sonnet-5": "Claude Sonnet 5",
    "gemini-3.7-flash": "Gemini 3.7 Flash", "grok-4.5": "Grok 4.5",
    "mistral-large": "Mistral Large", "sonar": "Perplexity sonar (web search)",
}
RISING = {"gpt-5.6-luna": 92, "claude-sonnet-5": 90, "gemini-3.7-flash": 90,
          "grok-4.5": 86, "mistral-large": 92, "sonar": 64}

df = pd.read_csv(HERE / "outputs" / "v2_cells_open.csv")
# median A(k): we stored A1,A5,A10,A15; recompute full curves from cells? use stored grid
GRID = [1, 5, 10, 15]

fig, ax = plt.subplots(figsize=(8.6, 5.4), facecolor="white")
ax.set_facecolor("white")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(GREY)
ax.tick_params(colors=SUB)
ax.grid(axis="y", color=GREY, lw=0.6, alpha=0.5)
ends = []
for eng, grp in df.groupby("engine"):
    med = [grp[f"A{k}"].median() for k in GRID]
    ls = "--" if eng == "sonar" else "-"
    ax.plot(GRID, med, color=ENG_COL[eng], lw=2.6, ls=ls, marker="o", ms=4)
    ends.append((med[-1], eng))
# space end labels at least 1.8 units apart, bottom-up
ends.sort()
ys = []
for y, eng in ends:
    y_lab = y if not ys else max(y, ys[-1] + 1.8)
    ys.append(y_lab)
    ax.annotate(f"{ENG_LAB[eng]}  ({RISING[eng]}% of cells still adding at 15)",
                (15.2, y_lab), fontsize=9, color=ENG_COL[eng], va="center",
                annotation_clip=False)
ax.set_xticks(GRID)
ax.set_xlim(1, 15)
ax.set_ylim(0, 34)
ax.set_xlabel("repeated runs of the same prompt", color=SUB)
ax.set_ylabel("distinct organizations named (median cell, expected)", color=SUB)
ax.set_title("Five engines keep adding brands; the searching engine stops",
             fontsize=16, fontweight="bold", color=INK, loc="left", pad=12)
fig.text(0.02, -0.06,
         "Median exact rarefaction per engine, open extraction (1,470 adjudicated "
         "organizations), 50 buying questions x 15 runs.\nDashed: retrieval-enabled. "
         "Data September 2026.", fontsize=8.6, color=SUB)
fig.tight_layout()
fig.savefig(NOTE / "fig1_engines.png", dpi=200, bbox_inches="tight", facecolor="white")
fig.savefig(HERE / "outputs" / "fig1_engines.png", dpi=200, bbox_inches="tight",
            facecolor="white")

# fig2: domains
cb = pd.read_csv(HERE.parent / "outputs" / "cb_cells.csv")
dd = pd.read_csv(HERE / "outputs" / "v2_cells_domains.csv")
CELL_COLORS = {"uk-supermarkets/gemini": "#0072B2", "uk-supermarkets/openai": "#E69F00",
               "nordic-care/gemini": "#009E73", "nordic-care/openai": "#CC79A7"}
CELL_LABELS = {"uk-supermarkets/gemini": "UK supermarkets / Gemini 3.5 (24 runs)",
               "uk-supermarkets/openai": "UK supermarkets / GPT-5.4 (24 runs)",
               "nordic-care/gemini": "Nordic care / Gemini 3.5 (24 runs)",
               "nordic-care/openai": "Nordic care / GPT-5.4 (24 runs)"}
fig, ax = plt.subplots(figsize=(8.6, 5.2), facecolor="white")
ax.set_facecolor("white")
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
for s in ("left", "bottom"):
    ax.spines[s].set_color(GREY)
ax.tick_params(colors=SUB)
ax.grid(axis="y", color=GREY, lw=0.6, alpha=0.5)
for _, r in cb[cb.field == "domains"].iterrows():
    A = json.loads(r.A_curve)
    ax.plot(range(1, len(A) + 1), A, color=CELL_COLORS[r.cell], lw=2.2,
            label=CELL_LABELS[r.cell])
med = [dd[f"A{k}"].median() for k in GRID]
ax.plot(GRID, med, color="#D55E00", lw=2.6, ls="--", marker="o", ms=4,
        label="Perplexity sonar, median of 50 cells (15 runs)")
ax.set_xticks([1, 5, 10, 15, 20, 24])
ax.set_xlim(1, 24)
ax.set_xlabel("repeated runs of the same prompt", color=SUB)
ax.set_ylabel("distinct cited domains seen (expected)", color=SUB)
ax.set_title("Cited domains: still accumulating at every horizon tested",
             fontsize=16, fontweight="bold", color=INK, loc="left", pad=12)
ax.legend(frameon=False, fontsize=8.6, loc="upper left", labelcolor=SUB)
fig.text(0.02, -0.05, "Exact rarefaction. Deep cells June 2026; sonar breadth "
         "September 2026.", fontsize=8.6, color=SUB)
fig.tight_layout()
fig.savefig(NOTE / "fig2_domains.png", dpi=200, bbox_inches="tight", facecolor="white")
print("figures written")
