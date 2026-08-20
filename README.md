# Rankfor Open

> Code and data for measuring what AI models say about a brand: whether they name
> it, which sources they ground the answer in, and how much of the answer is noise.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![npm version](https://img.shields.io/npm/v/@rankfor/dice-roller.svg)](https://www.npmjs.com/package/@rankfor/dice-roller)

## What is Rankfor Open?

Rankfor Open is the public half of [Rankfor.AI](https://rankfor.ai). It holds:

- **Dice Roller**: measures whether a model says the same thing when asked again
- **Research**: five arXiv preprints and seven open datasets, listed below with their identifiers
- **Glossary**: the terms this field uses, defined once so they can be argued with

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

Ask a model the same question once and you learn what it said that time. The Dice
Roller asks five or more times and reports what held.

It sends the prompt repeatedly, pulls the brands and claims out of each answer,
measures how much the answers overlap, and splits what it finds into the part that
appeared every time and the part that came and went.

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

- **Brand monitoring**: how often a model recommends you, and how steadily
- **Competitive comparison**: the same measurement run against the brands you lose to
- **Content strategy**: which of your claims survive repeated asking, and which do not
- **Research**: the datasets and code behind the preprints

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

Pull requests are welcome. [CONTRIBUTING.md](CONTRIBUTING.MD) has the details.

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

- [Rankfor.AI](https://rankfor.ai): the commercial platform
- [open.rankfor.ai](https://open.rankfor.ai): free tools, studies and the publications index
- [Documentation](https://open.rankfor.ai/resources)
- [Report Issues](https://github.com/Rankfor/rankfor-open/issues)

---

Maintained by [Rankfor.AI](https://rankfor.ai), Tallinn and Wrocław.
