# @rankfor/brand-detector

> Detect and analyze brand mentions in LLM/AI responses.

## 📦 Package

This is an npm package that can be used in any TypeScript/JavaScript project, including the dice-roller research tool.

**NPM Package**: `@rankfor/brand-detector`

## 🚀 Quick Start

### Installation

```bash
npm install @rankfor/brand-detector
```

### Basic Usage

```typescript
import { brandDetector } from '@rankfor/brand-detector';

const result = brandDetector.analyzeLLMResponse(
  "For CRM, I recommend Salesforce, HubSpot, or Pipedrive."
);

console.log(result);
// {
//   totalBrands: 3,
//   totalMentions: 3,
//   topBrand: 'Salesforce',
//   mentions: [
//     { brand: 'Salesforce', count: 1, confidence: 'high' },
//     { brand: 'HubSpot', count: 1, confidence: 'high' },
//     { brand: 'Pipedrive', count: 1, confidence: 'high' }
//   ]
// }
```

## 🔗 Integration with @rankfor/dice-roller

Perfect companion for stability analysis:

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

## 📖 Full Documentation

See [packages/core/README.md](./packages/core/README.md) for complete API documentation.

## 🎯 Use Cases

1. **Competitive Intelligence**: Track which brands AI platforms recommend
2. **Gender Bias Research**: Detect gender-locked brands in AI responses
3. **Stability Analysis**: Measure brand consistency across multiple responses
4. **Sentiment Analysis**: Analyze how brands are described with context

## 🗄️ Database

- **10,847 brands** from Simple Icons and Wikidata
- **3,245 high-confidence brands** (curated tech/SaaS)
- **CC0 licensed** (public domain)
- **Smart filtering** for dictionary words

## 📝 License

MIT © [Rankfor.AI](https://rankfor.ai)

## 🔗 Links

- [Full Documentation](./packages/core/README.md)
- [Examples](./packages/core/examples/)
- [GitHub Issues](https://github.com/Rankfor/rankfor-open/issues)
