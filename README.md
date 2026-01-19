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
│       └── 2026-01-dice-roll-stability/
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

All research is available under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

| Paper | Date | Status |
|-------|------|--------|
| [Dice Roll Stability Analysis](./research/papers/2026-01-dice-roll-stability) | Jan 2026 | Published |

Browse all research at [open.rankfor.ai/resources](https://open.rankfor.ai/resources).

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
