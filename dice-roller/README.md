# Dice Roller - AI Response Stability Analyzer

> Measure how consistently AI models recommend your brand

## Installation

```bash
npm install @rankfor/dice-roller
```

## Quick Start

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
```

## CLI Usage

```bash
npx @rankfor/dice-roller analyze "What are the best CRM tools?"
```

## How It Works

The Dice Roller runs the same prompt multiple times against an LLM and analyzes:

1. **Consistency Score** - How stable are the responses?
2. **Core Messages** - What AI always says about this topic
3. **Variable Messages** - What AI sometimes includes
4. **Outliers** - Unique insights from single responses

## API Reference

See the [main README](../README.md#api-reference) for full API documentation.

## License

MIT - See [LICENSE](../LICENSE)
