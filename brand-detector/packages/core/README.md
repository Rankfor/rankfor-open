# @rankfor/brand-detector

> Detect and analyze brand mentions in LLM/AI responses with 10,000+ brand database from Simple Icons and Wikidata.

[![npm version](https://img.shields.io/npm/v/@rankfor/brand-detector.svg)](https://www.npmjs.com/package/@rankfor/brand-detector)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **10,847 brands** from Simple Icons (curated tech/SaaS) and Wikidata (global brands)
- **Fast O(1) lookups** using optimized data structures
- **Multi-word brand support** (e.g., "Salesforce Marketing Cloud")
- **Confidence scoring** (high/medium/low) to filter ambiguous brands
- **Context extraction** to analyze surrounding text for each brand mention
- **TypeScript-first** with full type definitions
- **Zero dependencies** (except bundled data)

## Installation

```bash
npm install @rankfor/brand-detector
```

## Quick Start

```typescript
import { brandDetector } from '@rankfor/brand-detector';

// Analyze LLM response
const result = brandDetector.analyzeLLMResponse(
  "For CRM, I recommend Salesforce, HubSpot, or Pipedrive. Salesforce is best for enterprise."
);

console.log(result);
// {
//   totalBrands: 3,
//   totalMentions: 4,
//   topBrand: 'Salesforce',
//   mentions: [
//     { brand: 'Salesforce', count: 2, confidence: 'high' },
//     { brand: 'HubSpot', count: 1, confidence: 'high' },
//     { brand: 'Pipedrive', count: 1, confidence: 'high' }
//   ]
// }
```

## API Reference

### `analyzeLLMResponse(llmResponse, options?)`

**Primary API** for analyzing AI/LLM responses.

```typescript
brandDetector.analyzeLLMResponse(llmResponse: string, options?: {
  extended?: boolean;          // Include context around each mention
  contextRadius?: number;      // Characters before/after (default: 50)
  minConfidence?: 'high' | 'medium' | 'low';
}): BrandAnalysisResult
```

#### Basic Mode (counts only)

```typescript
const result = brandDetector.analyzeLLMResponse(
  "I recommend Salesforce and HubSpot."
);

// {
//   totalBrands: 2,
//   totalMentions: 2,
//   topBrand: 'Salesforce',
//   mentions: [
//     { brand: 'Salesforce', count: 1, confidence: 'high' },
//     { brand: 'HubSpot', count: 1, confidence: 'high' }
//   ]
// }
```

#### Extended Mode (with context)

```typescript
const result = brandDetector.analyzeLLMResponse(
  "Salesforce offers robust features but HubSpot has better UX.",
  {
    extended: true,
    contextRadius: 30,
  }
);

// {
//   totalBrands: 2,
//   totalMentions: 2,
//   mentions: [
//     {
//       brand: 'Salesforce',
//       count: 1,
//       confidence: 'high',
//       contexts: ['Salesforce offers robust features but...']
//     },
//     {
//       brand: 'HubSpot',
//       count: 1,
//       confidence: 'high',
//       contexts: ['...features but HubSpot has better UX.']
//     }
//   ]
// }
```

### Other Methods

```typescript
// Check if text is a brand
brandDetector.isBrand('Salesforce');  // true

// Get confidence level
brandDetector.getConfidence('HubSpot');  // 'high'
brandDetector.getConfidence('Oracle');   // 'low' (dictionary word)

// Extract unique brand names
brandDetector.extractBrandNames(text, 'medium');  // ['Salesforce', 'HubSpot']

// Count mentions
brandDetector.countBrandMentions(text);             // 5
brandDetector.countBrandMentions(text, 'Salesforce');  // 2

// Get autocomplete suggestions
brandDetector.getSuggestions('Sales', 10);  // ['Salesforce', 'Salesforce Marketing Cloud', ...]

// Get database metadata
brandDetector.getMetadata();  // { version, sources, total_brands, ... }
```

## Use Cases

### 1. Competitive Intelligence

Track which brands AI platforms recommend:

```typescript
const chatGPT = brandDetector.analyzeLLMResponse(chatGPTResponse);
const claude = brandDetector.analyzeLLMResponse(claudeResponse);
const gemini = brandDetector.analyzeLLMResponse(geminiResponse);

// Compare recommendation share across models
for (const brand of allBrands) {
  console.log(`${brand}:`, {
    chatGPT: chatGPT.mentions.find(m => m.brand === brand)?.count || 0,
    claude: claude.mentions.find(m => m.brand === brand)?.count || 0,
    gemini: gemini.mentions.find(m => m.brand === brand)?.count || 0,
  });
}
```

### 2. Gender Bias Research

Detect brand mentions in gender-framed queries:

```typescript
const husbandGifts = brandDetector.analyzeLLMResponse(husbandResponse);
const wifeGifts = brandDetector.analyzeLLMResponse(wifeResponse);

// Find gender-locked brands
const onlyHusband = husbandGifts.mentions.filter(
  m => !wifeGifts.mentions.some(w => w.brand === m.brand)
).map(m => m.brand);

console.log('Husband-only brands:', onlyHusband);
```

### 3. Stability Analysis (Dice Roll)

Analyze brand consistency across multiple responses:

```typescript
const results = [];
for (let i = 0; i < 5; i++) {
  const response = await getChatGPTResponse(prompt);
  results.push(brandDetector.analyzeLLMResponse(response));
}

// Calculate stability
const allBrands = new Set(results.flatMap(r => r.mentions.map(m => m.brand)));

for (const brand of allBrands) {
  const appearances = results.filter(r =>
    r.mentions.some(m => m.brand === brand)
  ).length;

  const stability = (appearances / results.length) * 100;
  console.log(`${brand}: ${stability}% stability`);
}
```

### 4. Sentiment Analysis

Use extended mode to analyze how brands are described:

```typescript
const result = brandDetector.analyzeLLMResponse(llmResponse, {
  extended: true,
});

const positiveWords = /excellent|great|best|recommended/i;
const negativeWords = /expensive|complex|difficult/i;

for (const mention of result.mentions) {
  if (mention.contexts) {
    const sentiment = mention.contexts.reduce((score, context) => {
      if (positiveWords.test(context)) score += 1;
      if (negativeWords.test(context)) score -= 1;
      return score;
    }, 0);

    console.log(`${mention.brand}: sentiment score ${sentiment}`);
  }
}
```

## Confidence Levels

| Level | Source | Examples | Use Case |
|-------|--------|----------|----------|
| **High** | Simple Icons | Salesforce, HubSpot, Microsoft | Primary detection |
| **Medium** | Wikidata | Regional brands, B2B companies | Comprehensive analysis |
| **Low** | Dictionary words | Target, Apple, Oracle | Contextual only |

Filter by confidence:

```typescript
// High-confidence only (curated tech/SaaS brands)
const result = brandDetector.analyzeLLMResponse(llmResponse, {
  minConfidence: 'high',
});

// Include all brands (including dictionary words)
const result = brandDetector.analyzeLLMResponse(llmResponse, {
  minConfidence: 'low',
});
```

## TypeScript Types

```typescript
interface BrandAnalysisResult {
  totalBrands: number;
  totalMentions: number;
  mentions: BrandMention[];
  topBrand: string | null;
}

interface BrandMention {
  brand: string;
  count: number;
  confidence: 'high' | 'medium' | 'low';
  contexts?: string[];  // Only in extended mode
}
```

## Database

The package includes a pre-generated database of 10,847 brands from:

- **Simple Icons** (3,245 brands): Curated tech/SaaS brands with logos
- **Wikidata** (8,732 brands): Global brands with verified logos

Both sources are **CC0 licensed** (public domain), making them safe for commercial use.

### Regenerating the Database

To update the brand database with latest data:

```bash
cd node_modules/@rankfor/brand-detector
python scripts/fetch-brands.py
```

## Integration with @rankfor/dice-roller

Perfect companion to [@rankfor/dice-roller](https://www.npmjs.com/package/@rankfor/dice-roller) for comprehensive AI visibility analysis:

```typescript
import { DiceRoller } from '@rankfor/dice-roller';
import { brandDetector } from '@rankfor/brand-detector';

const roller = new DiceRoller({ apiKey: process.env.GEMINI_API_KEY });

// Run stability analysis
const result = await roller.roll({
  prompt: "What are the best CRM tools?",
  iterations: 5,
  model: 'gemini',
});

// Analyze brand mentions in each response
for (const response of result.responses) {
  const brands = brandDetector.analyzeLLMResponse(response.text);
  console.log(`Iteration ${response.iteration}:`, brands.mentions);
}
```

## Performance

- **Lookups**: O(1) using Set and Map
- **Memory**: ~10MB (bundled database)
- **Multi-word**: Supports up to 3-word brand names
- **Detection**: O(n) where n = word count

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](../../CONTRIBUTING.md).

## License

MIT © [Rankfor.AI](https://rankfor.ai)

Brand database sources (Simple Icons, Wikidata) are CC0 (public domain).

## Related Packages

- [@rankfor/dice-roller](https://www.npmjs.com/package/@rankfor/dice-roller) - AI response stability analyzer

## Support

- [Documentation](https://github.com/Rankfor/rankfor-open/tree/main/brand-detector)
- [Issues](https://github.com/Rankfor/rankfor-open/issues)
- [Discord](https://discord.gg/rankfor) (coming soon)

## Changelog

See [CHANGELOG.md](./CHANGELOG.md) for release history.
