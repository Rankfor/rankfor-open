# The Dice Roll Method

**Monte Carlo simulation code and convergence analysis for:**

> Zatuchin, D. (2026). *The Dice Roll Method: A Standardized Protocol for Measuring
> Stochastic Bias in Large Language Model Outputs.*
> International Journal of Data Science and Analytics, Springer. (submitted)

---

## Overview

This directory contains the complete, self-contained analysis pipeline for the paper.
All results reported in the paper are reproducible from the notebook using only the
data files described in `DATA_SCHEMA.md`.

**What the notebook produces:**

| Output | Description |
|---|---|
| Power analysis table | Empirical power by effect size and iteration count (10,000 Monte Carlo replications) |
| Convergence table | Mean brand count and precision at $n = 2, \ldots, 10$ (bootstrap, $B = 1{,}000$) |
| Metric correlations | $5 \times 5$ Spearman matrix (CV, Gini, Shannon, mean, SD) |
| ICC reliability | Split-half ICC(2,1) at $n = 4, 6, 8, 10$ |
| Cost-efficiency table | Precision gain vs. API cost at each iteration count |
| 4 publication figures | Power curves, convergence plots, correlation heatmap, cost-precision frontier |

---

## Quick Start

### Google Colab (recommended)

```python
# 1. Clone the repository
!git clone https://github.com/Rankfor/rankfor-open.git
%cd rankfor-open

# 2. (Optional) Restore study data from Google Drive
from google.colab import drive
drive.mount('/content/drive')
!cp -r "/content/drive/MyDrive/research/dice-roll-method/data" \
        research/dice-roll-method/

# 3. Open the notebook via File -> Open
#    research/dice-roll-method/dice_roll_method_study.ipynb
```

> The notebook runs fully without external data files. S1 reference data
> (Valentine's Day subset, n=10, from Zatuchin 2026a) is embedded directly
> in the notebook. S2/S4/S5 unlock additional analyses when present.

### Local

```bash
git clone https://github.com/Rankfor/rankfor-open.git
cd rankfor-open
pip install numpy pandas scipy scikit-learn matplotlib seaborn plotly pingouin \
    statsmodels sentence-transformers torch
jupyter notebook research/dice-roll-method/dice_roll_method_study.ipynb
```

---

## Files

```
dice-roll-method/
├── README.md                       ← this file
├── DATA_SCHEMA.md                  ← canonical data format specifications
├── dice_roll_method_study.ipynb    ← self-contained Google Colab notebook
│
├── data/
│   ├── s1_gender_bias/             ← Study S1 (Zatuchin 2026a)
│   ├── s2_reputation/              ← Study S2 (Zatuchin 2026b)
│   ├── s4_cross_language/          ← Study S4 (Zatuchin 2026e)
│   └── s5_category_ownership/      ← Study S5 (Zatuchin 2026c)
│
└── results/                        ← generated at runtime (gitignored)
    ├── figures/
    └── tables/
```

Data files are not committed to the repository. See `DATA_SCHEMA.md` for
the expected format and contact dmitrij.zatuchin@eek.ee to request the datasets.

---

## Citation

```bibtex
@article{zatuchin2026diceroll,
  title={The Dice Roll Method: A Standardized Protocol for Measuring
         Stochastic Bias in Large Language Model Outputs},
  author={\.{Z}atuchin, Dmitrij},
  journal={International Journal of Data Science and Analytics},
  year={2026},
  publisher={Springer Nature},
  note={Submitted}
}
```

---

## License

Code: MIT. See [LICENSE](../../LICENSE).
Paper: CC BY 4.0 upon publication.
