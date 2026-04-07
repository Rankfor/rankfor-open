# Rankfor.AI Research Papers

Published and submitted research from the Rankfor.AI team. All papers are open-access or preprint-available.

## Papers

### 1. PersonaGen-149K: A Large-Scale Dataset of AI-Generated Buyer Personas for Consumer Information-Seeking Behavior Research

**Authors:** Dmitrij Zatuchin (EUAS), Daniil Dzemesjuk (Rankfor.AI)
**Journal:** Springer Discover Artificial Intelligence
**Status:** Submitted (15.02.2026), under review
**Preprint:** ResearchSquare.com

The submitted paper describes the original 148,636-persona dataset (PersonaGen-149K). The full dataset has since been expanded to **PersonaGen-593K** (593,181 personas across 339 industries, normalizing to ~25 primary verticals), constructed through the same multi-stage pipeline combining four publicly available persona corpora (~40M raw descriptions), GPU-accelerated MinHash LSH and semantic deduplication, and structured enrichment via xAI Grok. The expanded dataset includes ~3M search queries, ~3M information needs, ~1.8M goals, ~1.8M pain points, plus 3 new behavioral dimensions: top uncovered needs (~1.7M), search triggers (~2.2M), and preferred sources (~2.5M) -- totaling ~15.9M behavioral attributes.

**Dataset (10% research sample):** [rankfor/PersonaGen-15K on HuggingFace](https://huggingface.co/datasets/rankfor/PersonaGen-15K) (CC BY 4.0, 14,955 personas -- sampled from original 149K)

**Key findings:**
- Distinct industry-specific patterns in information-seeking behavior
- EdTech personas exhibit highest query volume (24.3% of dataset)
- Work-life balance is the dominant pain point across segments (107K mentions)
- Normalized Shannon entropy H/H_max = 0.94 for gender (near-uniform distribution)
- Significant industry-intent associations (chi-square = 26,641, Cramer's V = 0.300, p < 0.001)

---

### 2. Gender Bias in Large Language Model Brand Recommendations: A Three-Study Analysis of Prompt-Induced Disparities Across Seasonal and Recipient Contexts

**Authors:** Dmitrij Zatuchin (EUAS), Daniil Dzemesjuk (Rankfor.AI)
**Journal:** Springer Human-Centric Intelligent Systems
**Status:** Submitted, under review

Three-study analysis of how LLMs (GPT-4o, Gemini 2.5 Flash, Grok 3) exhibit gender bias in brand recommendations across gift-giving scenarios. Examines prompt-induced disparities when varying recipient gender pronouns.

**Key findings:**
- 70% of recommended brands appear in gender-specific contexts only
- Gemini acts as a "personal shopper" (11 brands/response), GPT as a "gift consultant" (1 brand/response), Grok splits the difference (3-5 brands)
- Only 2 brands (Away, Ember) appear consistently regardless of gender context
- Platform-specific recommendation patterns create systematic brand visibility disparities

---

### 3. The Dice Roll Method: A Standardized Protocol for Measuring Stochastic Bias in Large Language Model Outputs

**Author:** Dmitrij Zatuchin (EUAS, Rankfor.AI)
**Journal:** International Journal of Data Science and Analytics (Springer)
**Status:** Submitted (February 2026), under review

A meta-methodology study formalizing the *Dice Roll Method* as a reusable audit protocol
for measuring stochastic bias in LLM outputs. Combines reanalysis of five empirical studies
(approximately 190,000 observations across three to five LLMs, 270+ brands, six languages,
and iteration counts from 5 to 40) with Monte Carlo power simulation (10,000 replications
per condition).

**Key findings:**

- $n = 5$ iterations achieves adequate statistical power ($>0.80$) only for very large effects ($d > 1.2$); large effects ($d \approx 0.8$) require $n \geq 15$
- Metric convergence follows a logarithmic trajectory: 80% of asymptotic precision is achieved at $n = 7$, 90% at $n = 10$
- Test-retest reliability (ICC) crosses the 0.70 acceptability threshold at $n \geq 8$
- Count-based metrics (CV, Gini) and embedding-based metrics (cosine similarity) capture partially orthogonal information, supporting complementary metric batteries
- Cost-efficiency knee point at $n = 7$; a 250-query study at $n = 10$ costs approximately $37.50 in API fees

**Code and data:** [`research/dice-roll-method/`](../dice-roll-method/)

---

### 4. From Organizational Knowledge to AI Agent Memory: Empirical Validation of the SECI Model on the LongMemEval Benchmark

**Author:** Dmitrij Zatuchin (EUAS, Rankfor.AI)
**Journal:** Knowledge and Information Systems (Springer)
**Status:** In preparation

Adapts Nonaka & Takeuchi's SECI knowledge management model (1995) to AI agent memory systems and benchmarks it on LongMemEval (Wu et al., ICLR 2025). Tests structured extraction against raw verbatim storage across 500 questions and six memory task types.

**Key findings:**
- SECI hybrid extraction: 93.9% R@5 vs raw user-only (MemPalace method): 92.1%
- Embedding truncation at 256 tokens is the dominant factor; raw storage loses 90% of 10K-char sessions
- Extraction leads on 4/6 task types; raw wins on knowledge-update questions
- User-only indexing (stripping assistant turns) adds +6.2pp for free

**Code and data:** [`research/ai-memory-benchmark/`](../ai-memory-benchmark/)

---

## Dataset

The PersonaGen-15K research sample is publicly available:

| | |
|---|---|
| **HuggingFace** | [rankfor/PersonaGen-15K](https://huggingface.co/datasets/rankfor/PersonaGen-15K) |
| **License** | CC BY 4.0 |
| **Personas** | 14,955 (stratified 10% of original 148,636; full dataset now 593,181) |
| **Industries** | ~25 primary verticals (339 raw in full dataset) |
| **Market Contexts** | B2C, B2B, B2B2C, B2G |
| **Format** | Parquet (ZSTD compressed) |

## Code

Analysis pipelines and notebooks: [github.com/Rankfor/rankfor-open](https://github.com/Rankfor/rankfor-open)

## Citation

```bibtex
@article{zatuchin2026personagen149k,
  title={PersonaGen-149K: A Large-Scale Dataset of AI-Generated Buyer Personas
         for Consumer Information-Seeking Behavior Research},
  author={\.{Z}atuchin, Dmitrij and Dzemesjuk, Daniil},
  journal={Discover Artificial Intelligence},
  year={2026},
  publisher={Springer Nature}
}

@article{zatuchin2026genderbias,
  title={Gender Bias in Large Language Model Brand Recommendations:
         A Three-Study Analysis of Prompt-Induced Disparities
         Across Seasonal and Recipient Contexts},
  author={\.{Z}atuchin, Dmitrij and Dzemesjuk, Daniil},
  journal={Human-Centric Intelligent Systems},
  year={2026},
  publisher={Springer Nature}
}

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

## Authors

- **Dmitrij Zatuchin** -- Department of Business Administration, Estonian Entrepreneurship University of Applied Sciences (EUAS), Tallinn, Estonia. [dmitrij.zatuchin@eek.ee](mailto:dmitrij.zatuchin@eek.ee)
- **Daniil Dzemesjuk** -- Rankfor.AI, Tallinn, Estonia. [dd@rankfor.ai](mailto:dd@rankfor.ai)

## License

All research papers are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
