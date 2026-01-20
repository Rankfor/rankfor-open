# Brand Detector Examples

This directory contains examples demonstrating how to use custom brand databases with `@rankfor/brand-detector`.

## Examples

### 1. Custom Database (`custom-database.ts`)

Shows how to use a completely custom brand database instead of the bundled one.

**Use case:** You only need to detect a specific set of brands (e.g., your company's products and direct competitors).

```bash
npx ts-node examples/custom-database.ts
```

### 2. Extend Bundled Database (`extend-bundled-database.ts`)

Shows how to extend the bundled database (10,000+ brands) with your custom brands.

**Use case:** You want to detect both common brands AND your niche/custom brands.

```bash
npx ts-node examples/extend-bundled-database.ts
```

## Custom Brands JSON Format

The `custom-brands.json` file demonstrates the required structure for custom brand databases:

```json
{
  "meta": {
    "version": "1.0.0",
    "generated_at": "2026-01-20T00:00:00.000Z",
    "sources": [
      {
        "name": "Custom Brands Example",
        "url": "https://example.com",
        "count": 10,
        "license": "CC0"
      }
    ],
    "total_raw": 10,
    "total_filtered": 10,
    "ignored_terms": ["the", "it"]
  },
  "brands": [
    "CustomCRM",
    "OurBrand",
    "CompetitorX"
  ],
  "high_confidence": [
    "CustomCRM",
    "OurBrand"
  ]
}
```

### Field Descriptions

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `meta.version` | string | Yes | Database version (semantic versioning) |
| `meta.generated_at` | string | Yes | ISO 8601 timestamp of generation |
| `meta.sources` | array | Yes | Data sources (name, url, count, license) |
| `meta.total_raw` | number | Yes | Total brands before filtering |
| `meta.total_filtered` | number | Yes | Total brands after filtering |
| `meta.ignored_terms` | string[] | Yes | Dictionary words to mark as low confidence |
| `brands` | string[] | Yes | List of all brand names |
| `high_confidence` | string[] | Yes | Subset of brands with high confidence |

## Running Examples

### Prerequisites

```bash
npm install
npm run build
```

### Run Examples

```bash
# Custom database example
npx ts-node examples/custom-database.ts

# Extend bundled database example
npx ts-node examples/extend-bundled-database.ts
```

## Creating Your Own Custom Database

1. **Copy the template:**
   ```bash
   cp examples/custom-brands.json my-brands.json
   ```

2. **Edit your brands:**
   ```json
   {
     "brands": ["YourBrand", "Competitor1", "Competitor2"],
     "high_confidence": ["YourBrand"]
   }
   ```

3. **Use in your code:**
   ```typescript
   import { BrandDetector } from '@rankfor/brand-detector';
   import myBrands from './my-brands.json';

   const detector = new BrandDetector(myBrands);
   ```

## Tips

- **High Confidence**: Use for brands that are unambiguous (unique names, not dictionary words)
- **Medium Confidence**: Brands that might have common word meanings (e.g., "Target", "Apple")
- **Ignored Terms**: Add common words that happen to be brand names (e.g., "apple", "orange", "target")
- **Multi-word Brands**: Supported up to 3 words (e.g., "Salesforce Marketing Cloud")

## Integration with Research

These examples are particularly useful for:

- **Competitive Intelligence**: Track which brands AI recommends
- **Gender Bias Research**: Detect brand mentions in gender-framed queries
- **Stability Analysis**: Analyze brand consistency across multiple AI responses
- **Industry-Specific Analysis**: Focus on brands in your niche/industry
