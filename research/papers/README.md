# Rankfor.AI Research Papers

Published and submitted research from the Rankfor.AI team. All papers are open-access or preprint-available.

## Papers

### 1. PersonaGen-149K: A Large-Scale Dataset of AI-Generated Buyer Personas for Consumer Information-Seeking Behavior Research

**Authors:** Dmitrij Zatuchin (EUAS), Daniil Dzemesjuk (Rankfor.AI)
**Journal:** Springer Discover Artificial Intelligence
**Status:** Submitted (15.02.2026), under review
**Preprint:** ResearchSquare.com

148,636 AI-generated buyer personas across 122 industries (normalizing to 23 primary verticals), constructed through a multi-stage pipeline combining four publicly available persona corpora (~40M raw descriptions), GPU-accelerated MinHash LSH and semantic deduplication, and structured enrichment via xAI Grok. Each persona includes demographics, typical search queries (744K+), information needs (741K+), goals (450K+), and pain points (449K+).

**Dataset (10% research sample):** [rankfor/PersonaGen-15K on HuggingFace](https://huggingface.co/datasets/rankfor/PersonaGen-15K) (CC BY 4.0, 14,955 personas)

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

## Dataset

The PersonaGen-15K research sample is publicly available:

| | |
|---|---|
| **HuggingFace** | [rankfor/PersonaGen-15K](https://huggingface.co/datasets/rankfor/PersonaGen-15K) |
| **License** | CC BY 4.0 |
| **Personas** | 14,955 (stratified 10% of 148,636) |
| **Industries** | 23 primary verticals |
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
```

## Authors

- **Dmitrij Zatuchin** -- Department of Business Administration, Estonian Entrepreneurship University of Applied Sciences (EUAS), Tallinn, Estonia. [dmitrij.zatuchin@eek.ee](mailto:dmitrij.zatuchin@eek.ee)
- **Daniil Dzemesjuk** -- Rankfor.AI, Tallinn, Estonia. [dd@rankfor.ai](mailto:dd@rankfor.ai)

## License

All research papers are licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
