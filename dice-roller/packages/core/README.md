# @rankfor/dice-roller

**AI Response Stability Analyzer** - Measure how consistently LLMs recommend your brand.

[![npm version](https://img.shields.io/npm/v/@rankfor/dice-roller.svg)](https://www.npmjs.com/package/@rankfor/dice-roller)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3-blue.svg)](https://www.typescriptlang.org/)

---

## What is AI Response Stability?

When you ask an AI "What are the best CRM tools?", the answer varies each time. This variability matters for brand visibility:

- **Stable mentions** = Your brand is consistently recommended
- **Variable mentions** = Your brand appears sometimes, but not reliably
- **Missing mentions** = Opportunity gap to address

This library helps you understand how AI models perceive your brand by running the same prompt multiple times and analyzing patterns.

---

## Features

- **Multi-Model Support**: Analyze responses from Gemini, OpenAI GPT, and Grok
- **Search Mode**: Compare "memory" (training data) vs "search" (live web) responses
- **Experiment Mode**: Run cross-model comparisons with statistical analysis
- **Shannon Entropy**: Measure diversity of brand recommendations
- **Gini Coefficient**: Detect concentration bias toward specific brands
- **Jaccard Similarity**: Calculate cross-model overlap in recommendations
- **Brand Mention Tracking**: Count and analyze sentiment around your brand
- **Message Classification**: Identify core (stable), variable, and outlier messages
- **Citations Support**: Get source URLs when using search mode
- **Zero Dependencies**: Only peer dependencies for the LLM SDKs you use

---

## Installation

```bash
npm install @rankfor/dice-roller
```

Install the LLM SDK(s) you plan to use:

```bash
# For Gemini
npm install @google/generative-ai

# For OpenAI or Grok
npm install openai
```

---

## Quick Start

### Single Model Analysis

```typescript
import { analyzeStability } from '@rankfor/dice-roller';

const result = await analyzeStability({
  prompt: 'What are the best CRM tools for small businesses?',
  iterations: 5,
  model: 'gemini',
  apiKey: process.env.GEMINI_API_KEY,
  brandName: 'Salesforce', // Optional: track specific brand mentions
});

console.log(`Consistency Score: ${result.consistencyScore}%`);
console.log('Core Messages:', result.analysis.coreStableMessages);
console.log('Brand Mentions:', result.brandMentions.average);
```

### Cross-Model Experiment

```typescript
import { runExperiment } from '@rankfor/dice-roller';

const result = await runExperiment({
  prompt: 'What project management tools do you recommend?',
  apiKeys: {
    geminiApiKey: process.env.GEMINI_API_KEY,
    openaiApiKey: process.env.OPENAI_API_KEY,
    grokApiKey: process.env.GROK_API_KEY,
  },
  iterations: 5,
  brandName: 'Asana',
});

// Messages ALL models agree on
console.log('Universal Messages:', result.universalCoreMessages);

// Brands mentioned by ALL models
console.log('Universal Brands:', result.universalBrands);

// Statistical analysis
console.log('Shannon Entropy:', result.statistics.shannonEntropy);
console.log('Gini Coefficients:', result.statistics.giniCoefficients);
console.log('Cross-Model Overlap:', result.crossModelOverlap);
```

---

## API Reference

### `analyzeStability(options)`

Analyze response stability for a single model.

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `prompt` | `string` | required | The prompt to analyze |
| `iterations` | `number` | `5` | Number of iterations (1-10) |
| `model` | `'gemini' \| 'openai' \| 'grok'` | `'gemini'` | LLM to use |
| `apiKey` | `string` | required | API key for the chosen model |
| `temperature` | `number` | `0.7` | Model temperature |
| `maxTokens` | `number` | `2048` | Max tokens per response |
| `brandName` | `string` | optional | Brand to track mentions for |
| `iterationDelayMs` | `number` | `1000` | Delay between iterations |
| `searchMode` | `'memory' \| 'search'` | `'memory'` | Use training data or live web search |
| `onProgress` | `function` | optional | Progress callback |
| `onError` | `function` | optional | Error callback for failed iterations |
| `analysisConfig` | `AnalysisConfig` | optional | Custom stop words, synonyms, indicators |

**Returns:** `Promise<StabilityResult>`

### `runExperiment(options)`

Run cross-model analysis with statistical comparisons.

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `prompt` | `string` | required | The prompt to analyze |
| `apiKeys` | `ExperimentApiKeys` | required | API keys for each provider |
| `iterations` | `number` | `5` | Iterations per model |
| `temperature` | `number` | `0.7` | Model temperature |
| `maxTokens` | `number` | `2048` | Max tokens per response |
| `brandName` | `string` | optional | Brand for focused analysis |
| `iterationDelayMs` | `number` | `1000` | Delay between iterations |
| `searchMode` | `'memory' \| 'search'` | `'memory'` | Use training data or live web search |
| `onProgress` | `function` | optional | Progress callback `(model, iteration, total)` |
| `onError` | `function` | optional | Error callback with model name |
| `analysisConfig` | `AnalysisConfig` | optional | Custom stop words, synonyms, indicators |

**Returns:** `Promise<ExperimentResult>`

---

## Understanding the Results

### Consistency Score (0-100)

A weighted score combining:
- **40%**: Semantic overlap between responses
- **30%**: Brand mention consistency (low variance = higher score)
- **30%**: Presence of core stable messages

### Message Classification

| Category | Threshold | Meaning |
|----------|-----------|---------|
| Core Stable | 80%+ appearances | Always mentioned - reliable AI perception |
| Variable | 30-80% appearances | Sometimes mentioned - needs reinforcement |
| Outliers | <30% appearances | Rarely mentioned - potential opportunities |

### Statistical Metrics

#### Shannon Entropy
Measures diversity of brand recommendations:
- **Low (<0.5)**: Stereotyped - few dominant brands
- **Moderate (0.5-0.8)**: Balanced recommendations
- **High (>0.8)**: Diverse - many brands recommended equally

#### Gini Coefficient
Measures concentration inequality:
- **0**: Perfect equality (all brands mentioned equally)
- **1**: Perfect inequality (one brand dominates)
- **>0.6**: High concentration - market dominated by few players

#### Jaccard Index
Measures cross-model overlap:
- **1**: Perfect overlap (models recommend same brands)
- **0**: No overlap (completely different recommendations)
- **>0.5**: High agreement between models

---

## Search Mode: Memory vs Live Web

A key feature of this library is comparing how AI responds using its **training data** versus **live web search**.

### Why This Matters

- **Memory mode** (`searchMode: 'memory'`): Shows what the AI "believes" based on training
- **Search mode** (`searchMode: 'search'`): Shows what AI finds via real-time web search

Comparing both reveals:
- Whether your brand appears in AI's "memory" (training data)
- Whether your brand is discoverable via web search
- Gaps between perceived vs actual brand presence

### Using Search Mode

```typescript
// Memory mode (default) - uses training data only
const memoryResult = await analyzeStability({
  prompt: 'Best CRM tools for startups',
  model: 'gemini',
  apiKey: process.env.GEMINI_API_KEY,
  searchMode: 'memory', // or omit - it's the default
});

// Search mode - uses live web search with citations
const searchResult = await analyzeStability({
  prompt: 'Best CRM tools for startups',
  model: 'gemini',
  apiKey: process.env.GEMINI_API_KEY,
  searchMode: 'search',
});

// Compare results
console.log('Memory mentions:', memoryResult.brandMentions.average);
console.log('Search mentions:', searchResult.brandMentions.average);

// Search mode includes citations
for (const response of searchResult.responses) {
  if (response.citations) {
    console.log('Sources:', response.citations.map(c => c.url));
  }
}
```

### Cross-Model Experiment with Search

```typescript
const experiment = await runExperiment({
  prompt: 'What analytics tools do enterprises use?',
  apiKeys: {
    geminiApiKey: process.env.GEMINI_API_KEY,
    openaiApiKey: process.env.OPENAI_API_KEY,
    grokApiKey: process.env.GROK_API_KEY,
  },
  searchMode: 'search', // All models will use web search
  iterations: 5,
});

// See what each model finds via web search
for (const modelResult of experiment.modelResults) {
  console.log(`${modelResult.model} found:`, modelResult.uniqueBrands);
}
```

### Search Mode by Provider

| Provider | Memory Mode | Search Mode |
|----------|-------------|-------------|
| Gemini | Standard generation | [Google Search Grounding](https://ai.google.dev/gemini-api/docs/google-search) |
| OpenAI | Chat completions | [Web Search Tool](https://platform.openai.com/docs/guides/tools-web-search) |
| Grok/xAI | Standard generation | [Agentic Search](https://docs.x.ai/docs/guides/tools/search-tools) (web + X) |

### Pricing Considerations

Search mode may incur additional costs:
- **Gemini**: First 1,500 grounding queries/day free, then $35/1,000 queries
- **OpenAI**: Uses search-enabled models (check current pricing)
- **Grok/xAI**: Free during beta, check current pricing

---

## Models Supported

| Provider | Model | Model ID |
|----------|-------|----------|
| Google | Gemini 3 Pro | `gemini-3-pro-preview` |
| OpenAI | GPT-5.2 | `gpt-5.2` |
| xAI | Grok 4 | `grok-4` |

---

## Configuration

Customize the analysis for different industries or languages:

```typescript
const result = await analyzeStability({
  prompt: 'What CRM tools do you recommend?',
  model: 'gemini',
  apiKey: process.env.GEMINI_API_KEY,
  analysisConfig: {
    // Replace default English stop words (for non-English content)
    customStopWords: ['der', 'die', 'das', 'und', 'oder', ...],

    // Add industry-specific synonym groups
    customSynonyms: [
      ['CRM', 'customer relationship management', 'client management'],
      ['SaaS', 'cloud software', 'software as a service'],
    ],

    // Extend sentiment detection
    customPositiveIndicators: ['enterprise-grade', 'scalable'],
    customNegativeIndicators: ['legacy', 'clunky'],
  },

  // Error handling
  onError: (error) => {
    console.error(`Iteration ${error.iteration} failed: ${error.message}`);
  },
});
```

---

## Helper Functions

The library exports several utility functions for custom analysis:

```typescript
import {
  cleanResponse,           // Remove markdown formatting
  analyzeSentiment,        // Detect positive/neutral/negative
  extractBrandMentions,    // Find brand mentions with context
  extractKeyPoints,        // Extract key points from text
  calculateSemanticOverlap, // Word-based similarity (0-100)
  calculateJaccardSimilarity, // Set-based similarity (0-1)
  calculateShannonEntropy,    // Brand diversity metric
  calculateGiniCoefficient,   // Concentration inequality
  estimateTokenCount,         // Approximate token count (~4 chars/token)
} from '@rankfor/dice-roller';
```

---

## Use Cases

### Brand Monitoring
Track how consistently AI recommends your brand vs competitors:

```typescript
const result = await analyzeStability({
  prompt: 'What email marketing tools do you recommend?',
  brandName: 'Mailchimp',
  iterations: 10,
  model: 'gemini',
  apiKey: process.env.GEMINI_API_KEY,
});

if (result.brandMentions.average < 1) {
  console.log('Low visibility - brand rarely mentioned');
}
```

### Content Strategy
Identify messages to reinforce in your content:

```typescript
const result = await runExperiment({
  prompt: 'What are the benefits of cloud storage?',
  apiKeys: { geminiApiKey, openaiApiKey },
  iterations: 5,
});

// Use these in your content
console.log('Messages to reinforce:', result.universalCoreMessages);

// Gaps to address
console.log('Opportunities:', result.recommendations.differentiationOpportunities);
```

### Competitive Intelligence
Compare how AI perceives you vs competitors:

```typescript
const yourBrand = await analyzeStability({
  prompt: 'Best project management tools',
  brandName: 'Asana',
  ...
});

const competitor = await analyzeStability({
  prompt: 'Best project management tools',
  brandName: 'Monday.com',
  ...
});

console.log(`Your visibility: ${yourBrand.brandMentions.average}`);
console.log(`Competitor visibility: ${competitor.brandMentions.average}`);
```

---

## Browser Usage

For browser environments (e.g., React apps), you can use this library client-side. The OpenAI SDK requires a flag:

```typescript
// The library handles this internally for browser environments
const OpenAI = new OpenAI({
  apiKey: userProvidedKey,
  dangerouslyAllowBrowser: true, // Required for client-side
});
```

Note: Never expose API keys in production client-side code. This is suitable for tools where users provide their own keys.

---

## TypeScript Support

Full TypeScript support with exported types:

```typescript
import type {
  // Core types
  StabilityOptions,
  StabilityResult,
  ExperimentOptions,
  ExperimentResult,
  ResponseData,
  // Search mode
  SearchMode,
  SearchCitation,
  // Brand analysis
  BrandMentionContext,
  BrandMentionStats,
  // Statistical analysis
  EntropyResult,
  GiniResult,
  CrossModelOverlap,
} from '@rankfor/dice-roller';
```

---

## Contributing

We welcome contributions. Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

---

## License

MIT License - see [LICENSE](./LICENSE) for details.

---

## About Rankfor.AI

[Rankfor.AI](https://rankfor.ai) helps brands understand and improve their visibility in AI-powered recommendations. This library is part of our open-source toolkit for AI visibility analysis.

---

## Related

- [Live Demo](https://open.rankfor.ai/dice-roller) - Try the Dice Roller tool online
- [Rankfor.AI](https://rankfor.ai) - AI Brand Visibility Platform
- [Research Papers](https://open.rankfor.ai/resources) - Our published research on AI recommendation patterns
