# Data Schema — The Dice Roll Method

This document specifies the canonical data formats for all source studies used in the
meta-methodology analysis described in:

> Zatuchin, D. (2026). *The Dice Roll Method: A Standardized Protocol for Measuring
> Stochastic Bias in Large Language Model Outputs.* International Journal of Data
> Science and Analytics, Springer. (submitted)

All raw data files must be placed in the corresponding subdirectories of `data/` before
running the analysis notebook. Original datasets are available from the corresponding
author upon reasonable request.

---

## Repository Layout

```
research/dice-roll-method/
├── DATA_SCHEMA.md               ← this file
├── README.md                    ← study overview and citation
├── dice_roll_method_study.ipynb ← self-contained Google Colab notebook
│
├── data/
│   ├── s1_gender_bias/          ← Study S1: Gender bias in brand recommendations
│   │   ├── iterations.json          required
│   │   ├── gini_coefficients.json   optional (pre-computed)
│   │   └── entropy_scores.json      optional (pre-computed)
│   │
│   ├── s2_reputation/           ← Study S2: Corporate reputation sourcing
│   │   └── consistency_scores.csv   required
│   │
│   ├── s4_cross_language/       ← Study S4: Cross-language reputation
│   │   ├── raw_responses.json       required
│   │   ├── embeddings.npy           required (BGE-M3, float32)
│   │   └── stability_scores.csv     optional (pre-computed)
│   │
│   └── s5_category_ownership/   ← Study S5: Category ownership map
│       ├── raw_responses.json       required
│       └── embeddings.npy           required (BGE-M3, float32)
│
└── results/
    ├── figures/                 ← generated PNG figures (gitignored)
    └── tables/                  ← generated CSV tables (gitignored)
```

---

## S1 — Gender Bias in Brand Recommendations

**Source study:** Zatuchin (2026a), submitted to Human-Centric Intelligent Systems, Springer.
**Subset used:** Valentine's Day subset ($n = 10$ iterations per prompt-model combination).

### `data/s1_gender_bias/iterations.json`

Per-iteration brand count array for each prompt-model pair.

```json
{
  "schema_version": "1.0",
  "study": "S1_valentines",
  "temperature": 0.3,
  "max_tokens": 1024,
  "description": "Brand counts per LLM iteration for Valentine's Day gift prompts",
  "combinations": [
    {
      "prompt": "boyfriend",
      "model": "gemini",
      "iterations": [13, 11, 15, 13, 12, 7, 13, 10, 11, 13]
    },
    {
      "prompt": "girlfriend",
      "model": "gemini",
      "iterations": [17, 13, 10, 15, 14, 18, 13, 12, 11, 19]
    }
  ]
}
```

**Fields:**

| Field | Type | Description |
|---|---|---|
| `prompt` | string | Recipient label: `boyfriend`, `girlfriend`, `husband`, `wife`, `partner` |
| `model` | string | Model identifier: `gemini`, `grok`, `openai` |
| `iterations` | int[] | Brand count per iteration run, ordered 1..n |

### `data/s1_gender_bias/gini_coefficients.json` (optional)

Pre-computed Gini coefficients from the original analysis.

```json
{
  "schema_version": "1.0",
  "combinations": [
    {
      "prompt": "husband",
      "model": "grok",
      "gini": 0.56
    }
  ]
}
```

### `data/s1_gender_bias/entropy_scores.json` (optional)

Pre-computed normalized Shannon entropy values.

```json
{
  "schema_version": "1.0",
  "combinations": [
    {
      "prompt": "husband",
      "model": "all",
      "h_norm": 0.86
    }
  ]
}
```

---

## S2 — Corporate Reputation Sourcing

**Source study:** Zatuchin (2026b), submitted to Human-Centric Intelligent Systems, Springer.
**Observations:** 1,311 responses across 24 companies, 8 industries, $n = 5$ iterations.

### `data/s2_reputation/consistency_scores.csv`

Pre-computed cosine similarity stability scores from the original study.

```csv
brand,industry,model,iteration_group,cosine_similarity,sentiment,source_type
"Spotify","Technology","gemini","1-5",0.72,"positive","direct_answer"
"Spotify","Technology","gpt","1-5",0.54,"neutral","list_format"
```

**Columns:**

| Column | Type | Description |
|---|---|---|
| `brand` | string | Company name (24 companies across 8 industries) |
| `industry` | string | Industry label |
| `model` | string | Model identifier |
| `iteration_group` | string | Iteration range, e.g. `1-5` |
| `cosine_similarity` | float | Mean pairwise cosine similarity across iterations (BGE-M3) |
| `sentiment` | string | `positive`, `negative`, `neutral` |
| `source_type` | string | Response format classification |

---

## S4 — Cross-Language Reputation

**Source study:** Zatuchin (2026e), submitted to AI & Society, Springer.
**Observations:** 9,577 responses across 20 brands, 6 languages, 3 models, $n = 5$ iterations.

### `data/s4_cross_language/raw_responses.json`

```json
[
  {
    "id": "s4_001",
    "brand": "Spotify",
    "language": "en",
    "model": "gemini",
    "iteration": 1,
    "prompt": "What do you know about the reputation of Spotify?",
    "response": "Spotify is widely regarded as...",
    "response_length": 312,
    "is_error": false,
    "timestamp": "2026-01-15T10:23:41Z"
  }
]
```

**Fields:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique response identifier |
| `brand` | string | Company name (20 Nordic/European companies) |
| `language` | string | ISO 639-1 code: `en`, `de`, `fi`, `et`, `sv`, `no` |
| `model` | string | Model identifier: `gemini`, `gpt`, `perplexity` |
| `iteration` | int | Iteration index, 1..5 |
| `prompt` | string | Full prompt text |
| `response` | string | Full LLM response text |
| `response_length` | int | Character count of response |
| `is_error` | bool | True if the API call failed |
| `timestamp` | string | ISO 8601 UTC timestamp |

### `data/s4_cross_language/embeddings.npy`

NumPy array of shape `(N, 1024)`, dtype `float32`. Row indices correspond to rows in
`raw_responses.json` (error rows included; filter with `is_error == false` before use).
Embeddings computed with `BAAI/bge-m3` at the sentence level.

### `data/s4_cross_language/stability_scores.csv` (optional)

Pre-computed stability metrics per brand-language-model combination.

```csv
brand,language,model,cosine_stability,n_iterations,semantic_drift
"Spotify","en","gemini",0.91,5,0.09
```

---

## S5 — Category Ownership Map

**Source study:** Zatuchin (2026c), submitted to Electronic Markets, Springer.
**Observations:** 3,750 responses across 50 brands, 5 industries, 3 models, $n = 5$ iterations.

### `data/s5_category_ownership/raw_responses.json`

Same schema as S4 `raw_responses.json`, with the following differences:

| Field | Notes |
|---|---|
| `brand` | 50 brands across 5 industries |
| `language` | Always `en` (English-only study) |
| `query_type` | Additional field: `category_ownership`, `brand_comparison`, `recommendation` |
| `category` | Industry category: `cloud`, `crm`, `ecommerce`, `fintech`, `hr_tech` |

### `data/s5_category_ownership/embeddings.npy`

NumPy array of shape `(N, 1024)`, dtype `float32`. Same conventions as S4.

---

## Shared Experimental Parameters

All studies used the following parameters, which define the Dice Roll Method protocol:

| Parameter | Value |
|---|---|
| Temperature | 0.3 |
| Max tokens | 1,024 |
| System prompt | "You are a helpful assistant with broad knowledge of businesses and technology." |
| Models | GPT-5.2 (OpenAI), Gemini 3 Flash (Google), Grok-4-1 (xAI) or Perplexity sonar-pro |
| Embedding model | `BAAI/bge-m3` (1,024-dimensional, multilingual) |
| Similarity metric | Cosine similarity on L2-normalized vectors |

---

## Data Availability

Original datasets are available from the corresponding author upon reasonable request:
dmitrij.zatuchin@eek.ee

The Monte Carlo simulation code, convergence analysis, and all derived tables are fully
reproducible from the notebook `dice_roll_method_study.ipynb` using only the data files
described above.
