# rankfor-open
Open-source tools for AI Visibility. Measure brand stability, detect hallucinations, and quantify how LLMs reason about your brand.
Take control of how AI sees your brand.

# Rankfor Open

> Open-source algorithms and research for AI visibility intelligence.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![npm version](https://img.shields.io/npm/v/@rankfor/dice-roller.svg)](https://www.npmjs.com/package/@rankfor/dice-roller)

## What is Rankfor Open?

Rankfor Open is the open-source arm of [Rankfor.AI](https://rankfor.ai), providing:

- **Dice Roller Algorithm** - Analyze AI response stability and consistency
- **Research Papers** - Peer-reviewed studies on AI visibility and brand recommendations
- **AI Visibility Glossary** - Standardized terminology for the emerging GEO field

## Quick Start

### Dice Roller CLI

```bash
npx @rankfor/dice-roller analyze "What are the best CRM tools for small businesses?"
```

### Dice Roller as Library

```bash
npm install @rankfor/dice-roller
```

```typescript
import { analyzeStability } from '@rankfor/dice-roller';

const result = await analyzeStability({
  prompt: 'What are the best CRM tools for small businesses?',
  iterations: 5,
  model: 'gemini',
  apiKey: process.env.GEMINI_API_KEY,
});

console.log(`Consistency Score: ${result.consistencyScore}%`);
console.log('Stable Messages:', result.analysis.coreStableMessages);
console.log('Variable Messages:', result.analysis.variableMessages);
```

## Repository Structure

```
rankfor-open/
├── dice-roller/              # MIT licensed algorithm
│   ├── packages/
│   │   ├── core/             # analyzeStability() - pure algorithm
│   │   │   ├── src/
│   │   │   └── package.json  # @rankfor/dice-roller
│   │   └── cli/              # npx @rankfor/dice-roller
│   └── README.md
├── research/                 # Published research (CC BY 4.0)
│   └── papers/
├── glossary/                 # AI visibility terminology
│   └── terms.json
├── LICENSE                   # MIT
├── CONTRIBUTING.md
└── README.md
```

## Packages

| Package | Description | License |
|---------|-------------|---------|
| [@rankfor/dice-roller](./dice-roller) | AI response stability analyzer | MIT |

## Research

Everything below is public and citable. Preprints are on arXiv, datasets are on
Zenodo under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), and each
DOI resolves to the archived files, not to this repository.

### Preprints

| Paper | arXiv | Date |
|---|---|---|
| Who Owns the AI Recommendation? A Multi-Industry Empirical Map of Brand Category Ownership Across Large Language Models | [2606.23057](https://arxiv.org/abs/2606.23057) | Jun 2026 |
| The Language Blind Spot: How Query Language and Brand Recognition Tier Shape AI-Constructed Brand Reputation Across Twelve European Languages | [2606.23165](https://arxiv.org/abs/2606.23165) | Jun 2026 |
| How Large Language Models Source Brand Reputation Across Languages and Markets | [2606.25787](https://arxiv.org/abs/2606.25787) | Jun 2026 |
| Where Does the Noise Come From? A Variance-Components Decomposition of Non-Determinism in LLM Brand Answers | [2607.13304](https://arxiv.org/abs/2607.13304) | Jul 2026 |
| Who Gets Named: Citation Type Predicts Individual Naming by Grounded Language Models, and a Roster Instrument Captures 0.5% of It | [2607.23893](https://arxiv.org/abs/2607.23893) | Jul 2026 |

### Datasets

| Dataset | DOI | Date |
|---|---|---|
| Does an AI describe your company, or your company's name? 9,600 model answers about invented and real companies | [10.5281/zenodo.21904654](https://doi.org/10.5281/zenodo.21904654) | Aug 2026 |
| Supplementary Materials: Measuring Corporate Reputation in the Age of AI | [10.5281/zenodo.19225834](https://doi.org/10.5281/zenodo.19225834) | Aug 2026 |
| Individual Professional Visibility in Grounded LLM Answers: 2,400 buyer-intent responses across four European markets | [10.5281/zenodo.21612690](https://doi.org/10.5281/zenodo.21612690) | Jul 2026 |
| How LLMs Source Brand Reputation Across Languages and Markets: a cross-market citation dataset | [10.5281/zenodo.20829524](https://doi.org/10.5281/zenodo.20829524) | Jun 2026 |
| Cross-Language AI Brand Reputation: a 66-brand, 12-language dataset | [10.5281/zenodo.20794390](https://doi.org/10.5281/zenodo.20794390) | Jun 2026 |
| Category Ownership Map (COI/CVI/DS): a multi-industry dataset of brand recommendations | [10.5281/zenodo.20788142](https://doi.org/10.5281/zenodo.20788142) | Jun 2026 |
| Supplementary Materials: How LLMs Source Brand Reputation Knowledge, cross-industry | [10.5281/zenodo.19225835](https://doi.org/10.5281/zenodo.19225835) | Mar 2026 |

[PersonaGen-15K](https://huggingface.co/datasets/rankfor/PersonaGen-15K) is on
Hugging Face: 14,955 AI-generated buyer personas, a stratified 10% of the
149K set, Parquet, CC BY 4.0.

### Studies in this repository

Code and the small tables needed to check a number. Large data stays on Zenodo,
which is the archive of record.

| Study | What it measures |
|---|---|
| [brand-name-valence](./research/brand-name-valence) | Whether a model judges the company or only the sound of its name: 9,600 answers, 264 real companies and 150 invented ones, 21 markets, 3 models |
| [dice-roll-method](./research/dice-roll-method) | Stability of LLM brand answers under repeated identical prompts |
| [ai-memory-benchmark](./research/ai-memory-benchmark) | SECI-structured extraction against raw storage on LongMemEval |

Papers under peer review, with abstracts and current venue, are listed in
[research/papers](./research/papers).

To cite the repository or any of the work above, use the "Cite this repository"
button, which reads [CITATION.cff](./CITATION.cff).

## How It Works

### Dice Roller Algorithm

The Dice Roller analyzes AI response consistency by:

1. **Running Multiple Iterations** - Sends the same prompt 5+ times to an LLM
2. **Extracting Key Messages** - Identifies brand mentions, recommendations, and key points
3. **Calculating Semantic Overlap** - Measures consistency across responses
4. **Classifying Messages** - Separates stable vs. variable content

```
┌─────────────────────────────────────────────────────────────┐
│                    STABILITY ANALYSIS                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Prompt: "Best project management tools?"                   │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ Iteration 1: "Asana, Monday, Notion..."             │    │
│  │ Iteration 2: "Monday, Asana, ClickUp..."            │    │
│  │ Iteration 3: "Asana, Notion, Monday..."             │    │
│  │ Iteration 4: "Asana, Monday, Trello..."             │    │
│  │ Iteration 5: "Monday, Asana, Notion..."             │    │
│  └─────────────────────────────────────────────────────┘    │
│                          │                                  │
│                          ▼                                  │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ RESULTS                                             │    │
│  │ • Consistency Score: 78%                            │    │
│  │ • Core Stable: "Asana", "Monday" (100%)             │    │
│  │ • Variable: "Notion" (60%), "ClickUp" (20%)         │    │
│  │ • Outliers: "Trello" (appeared once)                │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Use Cases

- **Brand Monitoring** - Track how often AI recommends your brand
- **Competitive Intelligence** - Compare your AI visibility vs. competitors
- **Content Strategy** - Identify which messages are consistently associated with your brand
- **Research** - Academic study of LLM recommendation patterns

## API Reference

### `analyzeStability(options)`

```typescript
interface StabilityOptions {
  prompt: string;           // The prompt to analyze
  iterations?: number;      // Number of runs (default: 5, max: 10)
  model?: 'gemini' | 'openai' | 'grok';  // LLM to use
  apiKey: string;           // Your API key for the chosen model
  temperature?: number;     // Model temperature (default: 0.7)
}

interface StabilityResult {
  consistencyScore: number; // 0-100 percentage
  responses: ResponseData[];
  analysis: {
    semanticOverlap: number;
    coreStableMessages: string[];
    variableMessages: VariableMessage[];
    outliers: string[];
  };
  brandMentions: {
    total: number;
    min: number;
    max: number;
    average: number;
  };
}
```

## Contributing

We welcome contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/Rankfor/rankfor-open.git
cd rankfor-open/dice-roller
npm install
npm run build
npm test
```

## License

- **Code**: [MIT License](LICENSE)
- **Research**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)
- **Glossary**: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)

## Links

- [Rankfor.AI](https://rankfor.ai) - Full AI visibility platform
- [open.rankfor.ai](https://open.rankfor.ai) - Free tools and research
- [Documentation](https://open.rankfor.ai/resources)
- [Report Issues](https://github.com/Rankfor/rankfor-open/issues)

---

Built with care by the [Rankfor.AI](https://rankfor.ai) team.
