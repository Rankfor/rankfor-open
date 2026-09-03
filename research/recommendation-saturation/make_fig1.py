"""Figure 1, reviewer-corrected: per-cell colours consistent across panels,
matched dashed Chao2 lines, ticks to 24, within-sample language, split dates."""

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager

HERE = Path(__file__).parent
try:
    font_manager.fontManager.addfont("/Users/diz/Library/Fonts/Fustat-VariableFont_wght.ttf")
except Exception:
    pass
plt.rcParams["font.family"] = ["Fustat", "Helvetica Neue", "Arial"]

INK = "#1A1B1E"; GREY = "#D0D6DC"; SUB = "#676F79"; TEAL = "#006875"
CELL_COLORS = {  # Okabe-Ito, colourblind-safe, fixed order
    "uk-supermarkets/gemini": "#0072B2",
    "uk-supermarkets/openai": "#E69F00",
    "nordic-care/gemini": "#009E73",
    "nordic-care/openai": "#CC79A7",
}
CELL_LABELS = {
    "uk-supermarkets/gemini": "UK supermarkets / Gemini 3.5 Flash",
    "uk-supermarkets/openai": "UK supermarkets / GPT-5.4",
    "nordic-care/gemini": "Nordic care / Gemini 3.5 Flash",
    "nordic-care/openai": "Nordic care / GPT-5.4",
}
TICKS = [1, 5, 10, 15, 20, 24]

cbc = pd.read_csv(HERE / "outputs" / "cb_cells_corrected.csv")
cb = pd.read_csv(HERE / "outputs" / "cb_cells.csv")
ca_curves = pd.read_csv(HERE / "outputs" / "ca_curves.csv")

fig, axes = plt.subplots(1, 2, figsize=(12.5, 5.4), facecolor="white")
for ax in axes:
    ax.set_facecolor("white")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GREY)
    ax.tick_params(colors=SUB)
    ax.grid(axis="y", color=GREY, lw=0.6, alpha=0.5)
    ax.set_xticks(TICKS)
    ax.set_xlim(1, 24)
    ax.set_xlabel("repeated runs of the same prompt", color=SUB)

ax = axes[0]
c5 = ca_curves.dropna(subset=["A5"])
for _, r in c5.sample(min(300, len(c5)), random_state=0).iterrows():
    ax.plot(range(1, 6), [r.A1, r.A2, r.A3, r.A4, r.A5], color=GREY, lw=0.5,
            alpha=0.35, zorder=1)
med = [c5[f"A{k}"].median() for k in range(1, 6)]
ax.plot(range(1, 6), med, color=TEAL, lw=3, zorder=3,
        label="median, 684 complete breadth cells (n=5, roster-based)")
for _, r in cbc.iterrows():
    A = json.loads(r.A_curve)
    ax.plot(range(1, len(A) + 1), A, color=CELL_COLORS[r.cell], lw=2.2, zorder=2,
            label=CELL_LABELS[r.cell])
ax.set_title("Brands: discovery approaches a plateau", fontsize=16,
             fontweight="bold", color=INK, loc="left", pad=12)
ax.set_ylabel("distinct brands seen (expected)", color=SUB)
ax.set_ylim(0, 14.5)
ax.legend(frameon=False, fontsize=8.2, loc="lower right", labelcolor=SUB)

ax = axes[1]
for _, r in cb[cb.field == "domains"].iterrows():
    A = json.loads(r.A_curve)
    col = CELL_COLORS[r.cell]
    ax.plot(range(1, len(A) + 1), A, color=col, lw=2.4, zorder=2)
    ax.axhline(r.chao2, color=col, lw=1.1, ls="--", alpha=0.55, zorder=1)
    ax.annotate(f"Chao2 ~{r.chao2:.0f}", (24.2, r.chao2), fontsize=8.2, color=col,
                va="center", annotation_clip=False)
ax.set_title("Cited domains: discovery continues at 24 runs", fontsize=16,
             fontweight="bold", color=INK, loc="left", pad=12)
ax.set_ylabel("distinct cited domains seen (expected)", color=SUB)
ax.set_ylim(0, 175)
ax.plot([], [], color=SUB, lw=1.1, ls="--",
        label="Chao2 richness estimate (lower bound), matched colour")
ax.legend(frameon=False, fontsize=8.6, loc="upper left", labelcolor=SUB)

fig.suptitle("Brand discovery slows sooner than citation discovery in four deep probes",
             fontsize=18, fontweight="bold", color=INK, x=0.02, ha="left", y=1.02)
fig.text(0.02, -0.05,
         "Exact rarefaction A(k), averaged over run subsets; Chao2 richness (lower-bound "
         "estimator). 684 complete breadth cells (n=5, brands, 50-brand roster) and 4 deep "
         "cells (n=24, open-extended rosters + cited domains).\n"
         "Engines: GPT and Gemini families, Perplexity sonar-pro (breadth). "
         "Data collected June 2026; analysis September 2026.",
         fontsize=8.6, color=SUB)
fig.tight_layout()
fig.savefig(HERE / "outputs" / "fig1_saturation.png", dpi=200, bbox_inches="tight",
            facecolor="white")
print("figure written")
