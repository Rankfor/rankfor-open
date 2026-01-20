# Integration Guide: Using @rankfor/brand-detector with Dice Roller

## Overview

This guide shows how to use `@rankfor/brand-detector` alongside `@rankfor/dice-roller` for comprehensive AI visibility research.

## Installation

```bash
cd rankfor-open/dice-roller
npm install @rankfor/brand-detector
```

## Basic Integration

### Example 1: Brand Stability Analysis

```typescript
import { DiceRoller } from '@rankfor/dice-roller';
import { brandDetector } from '@rankfor/brand-detector';

async function analyzeBrandStability() {
  const roller = new DiceRoller({
    apiKey: process.env.GEMINI_API_KEY!,
  });

  // Run 5 iterations
  const result = await roller.roll({
    prompt: "What are the best CRM tools for SMBs?",
    iterations: 5,
    model: 'gemini',
  });

  // Analyze brand mentions in each response
  const allBrands = new Set<string>();
  const brandAppearances = new Map<string, number>();

  for (const response of result.responses) {
    const analysis = brandDetector.analyzeLLMResponse(response.text);

    for (const mention of analysis.mentions) {
      allBrands.add(mention.brand);
      brandAppearances.set(
        mention.brand,
        (brandAppearances.get(mention.brand) || 0) + 1
      );
    }
  }

  // Calculate stability for each brand
  console.log('Brand Stability:\n');
  for (const brand of allBrands) {
    const appearances = brandAppearances.get(brand) || 0;
    const stability = (appearances / result.responses.length) * 100;

    console.log(`${brand}: ${stability.toFixed(0)}% (${appearances}/${result.responses.length})`);
  }
}
```

### Example 2: Cross-Model Brand Comparison

```typescript
async function compareModels() {
  const roller = new DiceRoller({
    apiKey: process.env.GEMINI_API_KEY!,
    openaiApiKey: process.env.OPENAI_API_KEY!,
  });

  const prompt = "What are the best project management tools?";

  // Run on both models
  const [gemini, openai] = await Promise.all([
    roller.roll({ prompt, iterations: 3, model: 'gemini' }),
    roller.roll({ prompt, iterations: 3, model: 'openai' }),
  ]);

  // Analyze brands per model
  const geminiAnalysis = gemini.responses.map(r =>
    brandDetector.analyzeLLMResponse(r.text)
  );
  const openaiAnalysis = openai.responses.map(r =>
    brandDetector.analyzeLLMResponse(r.text)
  );

  // Aggregate results
  const geminiBrands = new Set(
    geminiAnalysis.flatMap(a => a.mentions.map(m => m.brand))
  );
  const openaiBrands = new Set(
    openaiAnalysis.flatMap(a => a.mentions.map(m => m.brand))
  );

  console.log('Gemini-only brands:', [...geminiBrands].filter(b => !openaiBrands.has(b)));
  console.log('OpenAI-only brands:', [...openaiBrands].filter(b => !geminiBrands.has(b)));
  console.log('Both models:', [...geminiBrands].filter(b => openaiBrands.has(b)));
}
```

## Advanced Integration

### Example 3: Sentiment Analysis with Stability

```typescript
async function sentimentStability() {
  const roller = new DiceRoller({
    apiKey: process.env.GEMINI_API_KEY!,
  });

  const result = await roller.roll({
    prompt: "Compare Salesforce, HubSpot, and Pipedrive",
    iterations: 5,
    model: 'gemini',
  });

  const positiveWords = /excellent|great|best|leading/i;
  const negativeWords = /expensive|complex|difficult/i;

  const brandSentiments = new Map<string, { pos: number; neg: number }>();

  // Analyze with context
  for (const response of result.responses) {
    const analysis = brandDetector.analyzeLLMResponse(response.text, {
      extended: true,
      contextRadius: 50,
    });

    for (const mention of analysis.mentions) {
      const sentiment = brandSentiments.get(mention.brand) || { pos: 0, neg: 0 };

      if (mention.contexts) {
        for (const context of mention.contexts) {
          if (positiveWords.test(context)) sentiment.pos += 1;
          if (negativeWords.test(context)) sentiment.neg += 1;
        }
      }

      brandSentiments.set(mention.brand, sentiment);
    }
  }

  // Display results
  for (const [brand, sentiment] of brandSentiments) {
    const net = sentiment.pos - sentiment.neg;
    console.log(`${brand}: net sentiment ${net > 0 ? '+' : ''}${net}`);
  }
}
```

### Example 4: Gender Bias Detection

```typescript
async function detectGenderBias() {
  const roller = new DiceRoller({
    apiKey: process.env.GEMINI_API_KEY!,
  });

  // Run for both genders
  const [husbandResult, wifeResult] = await Promise.all([
    roller.roll({
      prompt: "Gift ideas for my husband who loves tech",
      iterations: 5,
      model: 'gemini',
    }),
    roller.roll({
      prompt: "Gift ideas for my wife who loves tech",
      iterations: 5,
      model: 'gemini',
    }),
  ]);

  // Analyze brands
  const husbandBrands = new Set(
    husbandResult.responses.flatMap(r => {
      const analysis = brandDetector.analyzeLLMResponse(r.text);
      return analysis.mentions.map(m => m.brand);
    })
  );

  const wifeBrands = new Set(
    wifeResult.responses.flatMap(r => {
      const analysis = brandDetector.analyzeLLMResponse(r.text);
      return analysis.mentions.map(m => m.brand);
    })
  );

  // Find gender-locked brands
  const husbandOnly = [...husbandBrands].filter(b => !wifeBrands.has(b));
  const wifeOnly = [...wifeBrands].filter(b => !husbandBrands.has(b));

  console.log('Husband-only brands:', husbandOnly);
  console.log('Wife-only brands:', wifeOnly);
  console.log('Gender bias:', ((husbandOnly.length + wifeOnly.length) / (husbandBrands.size + wifeBrands.size)) * 100, '%');
}
```

## Data Export

### Example 5: Export Results for Research Paper

```typescript
async function exportResearchData() {
  const roller = new DiceRoller({
    apiKey: process.env.GEMINI_API_KEY!,
  });

  const result = await roller.roll({
    prompt: "What are the best work management tools?",
    iterations: 10,
    model: 'gemini',
  });

  // Analyze all responses
  const researchData = {
    metadata: {
      prompt: result.prompt,
      model: result.model,
      iterations: result.iterations,
      timestamp: new Date().toISOString(),
    },
    responses: result.responses.map(response => {
      const brandAnalysis = brandDetector.analyzeLLMResponse(response.text, {
        extended: true,
      });

      return {
        iteration: response.iteration,
        text: response.text,
        brands: brandAnalysis.mentions,
        totalBrands: brandAnalysis.totalBrands,
        totalMentions: brandAnalysis.totalMentions,
      };
    }),
    aggregatedBrands: aggregateBrands(result.responses),
  };

  // Save to JSON
  const fs = require('fs');
  fs.writeFileSync(
    'research-data.json',
    JSON.stringify(researchData, null, 2)
  );

  console.log('Research data exported to research-data.json');
}

function aggregateBrands(responses: any[]) {
  const brandStats = new Map<string, {
    appearances: number;
    totalMentions: number;
    stability: number;
  }>();

  for (const response of responses) {
    const analysis = brandDetector.analyzeLLMResponse(response.text);

    for (const mention of analysis.mentions) {
      const stats = brandStats.get(mention.brand) || {
        appearances: 0,
        totalMentions: 0,
        stability: 0,
      };

      stats.appearances += 1;
      stats.totalMentions += mention.count;
      brandStats.set(mention.brand, stats);
    }
  }

  // Calculate stability
  for (const [brand, stats] of brandStats) {
    stats.stability = (stats.appearances / responses.length) * 100;
  }

  return Object.fromEntries(brandStats);
}
```

## CLI Integration

### Example 6: Command-Line Tool

```typescript
#!/usr/bin/env node

import { DiceRoller } from '@rankfor/dice-roller';
import { brandDetector } from '@rankfor/brand-detector';

const [prompt, iterations, model] = process.argv.slice(2);

async function main() {
  const roller = new DiceRoller({
    apiKey: process.env.GEMINI_API_KEY!,
  });

  console.log(`Running ${iterations} iterations for: "${prompt}"\n`);

  const result = await roller.roll({
    prompt,
    iterations: parseInt(iterations),
    model: model as any,
  });

  // Analyze brands
  const allBrands = new Map<string, number>();

  for (const response of result.responses) {
    const analysis = brandDetector.analyzeLLMResponse(response.text);

    for (const mention of analysis.mentions) {
      allBrands.set(mention.brand, (allBrands.get(mention.brand) || 0) + 1);
    }
  }

  // Display results
  console.log('Brand Stability:\n');
  console.log('Brand          | Appearances | Stability');
  console.log('---------------|-------------|----------');

  for (const [brand, appearances] of allBrands) {
    const stability = (appearances / result.responses.length) * 100;
    console.log(
      `${brand.padEnd(14)} | ${appearances}/${result.responses.length}         | ${stability.toFixed(0)}%`
    );
  }
}

main().catch(console.error);
```

Usage:
```bash
./analyze-brands.ts "What are the best CRM tools?" 5 gemini
```

## TypeScript Configuration

Ensure your `tsconfig.json` includes:

```json
{
  "compilerOptions": {
    "esModuleInterop": true,
    "resolveJsonModule": true
  }
}
```

## Testing

```typescript
import { describe, it, expect } from 'jest';
import { brandDetector } from '@rankfor/brand-detector';

describe('Brand Detection', () => {
  it('should detect brands in LLM response', () => {
    const result = brandDetector.analyzeLLMResponse(
      'I recommend Salesforce and HubSpot.'
    );

    expect(result.totalBrands).toBe(2);
    expect(result.mentions).toHaveLength(2);
  });

  it('should provide context in extended mode', () => {
    const result = brandDetector.analyzeLLMResponse(
      'Salesforce is great.',
      { extended: true }
    );

    expect(result.mentions[0].contexts).toBeDefined();
  });
});
```

## Next Steps

1. **Install**: `npm install @rankfor/brand-detector`
2. **Integrate**: Add to your dice-roller research scripts
3. **Analyze**: Run stability analysis with brand tracking
4. **Export**: Generate research data for papers

## Support

- [Documentation](./packages/core/README.md)
- [Examples](./packages/core/examples/)
- [Issues](https://github.com/Rankfor/rankfor-open/issues)
