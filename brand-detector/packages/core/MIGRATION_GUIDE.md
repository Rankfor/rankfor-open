# Migration Guide: Custom Brand Databases

## Version 1.1.0 - Custom Database Support

### What's New

Version 1.1.0 adds support for custom brand databases. You can now:
- Provide your own brand database to detect niche/custom brands
- Extend the bundled database with your brands
- Switch between different brand databases at runtime

### Breaking Changes

**None!** This is a backward-compatible feature. All existing code continues to work without changes.

### Migrating to Custom Databases

#### Before (v1.0.x)

```typescript
import { BrandDetector } from '@rankfor/brand-detector';

// Only bundled database available
const detector = new BrandDetector();
```

#### After (v1.1.0+)

**Option 1: Use bundled database (no changes required)**

```typescript
import { BrandDetector } from '@rankfor/brand-detector';

const detector = new BrandDetector();
```

**Option 2: Use custom database**

```typescript
import { BrandDetector } from '@rankfor/brand-detector';
import myBrands from './my-brands.json';

const detector = new BrandDetector(myBrands);
```

**Option 3: Extend bundled database**

```typescript
import { BrandDetector } from '@rankfor/brand-detector';
import brandsDb from '@rankfor/brand-detector/data/brands.json';
import type { BrandDatabase } from '@rankfor/brand-detector';

const extendedDb: BrandDatabase = {
  ...brandsDb,
  brands: [...brandsDb.brands, 'CustomCRM', 'OurBrand'],
  high_confidence: [...brandsDb.high_confidence, 'CustomCRM']
};

const detector = new BrandDetector(extendedDb);
```

### Use Cases

#### 1. Industry-Specific Detection

If you're analyzing a specific industry (e.g., healthcare SaaS), create a focused database:

```typescript
const healthcareBrands: BrandDatabase = {
  meta: {
    version: '1.0.0',
    generated_at: new Date().toISOString(),
    sources: [{ name: 'Healthcare Brands', url: '', count: 50, license: 'CC0' }],
    total_raw: 50,
    total_filtered: 50,
    ignored_terms: []
  },
  brands: ['Epic', 'Cerner', 'Allscripts', 'Meditech', /* ... */],
  high_confidence: ['Epic', 'Cerner', 'Allscripts']
};

const detector = new BrandDetector(healthcareBrands);
```

#### 2. Competitive Intelligence

Track your brand and direct competitors only:

```typescript
const competitorBrands: BrandDatabase = {
  meta: { /* metadata */ },
  brands: ['OurBrand', 'CompetitorA', 'CompetitorB', 'CompetitorC'],
  high_confidence: ['OurBrand', 'CompetitorA', 'CompetitorB']
};

const detector = new BrandDetector(competitorBrands);
```

#### 3. Multi-Region Brands

Detect regional brands not in the bundled database:

```typescript
const regionalBrands: BrandDatabase = {
  meta: { /* metadata */ },
  brands: [
    // APAC brands
    'Tokopedia', 'Lazada', 'Grab',
    // MEA brands
    'Careem', 'Noon', 'Talabat',
    // LATAM brands
    'MercadoLibre', 'Rappi', 'Nubank'
  ],
  high_confidence: ['Tokopedia', 'MercadoLibre', 'Careem']
};

const detector = new BrandDetector(regionalBrands);
```

### Custom Database Format

```json
{
  "meta": {
    "version": "1.0.0",
    "generated_at": "2026-01-20T00:00:00.000Z",
    "sources": [
      {
        "name": "Your Source Name",
        "url": "https://source-url.com",
        "count": 100,
        "license": "CC0"
      }
    ],
    "total_raw": 100,
    "total_filtered": 100,
    "ignored_terms": ["apple", "target", "orange"]
  },
  "brands": [
    "BrandName1",
    "BrandName2",
    "Multi Word Brand"
  ],
  "high_confidence": [
    "BrandName1",
    "BrandName2"
  ]
}
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `meta.version` | string | Database version (semantic versioning) |
| `meta.generated_at` | string | ISO 8601 timestamp |
| `meta.sources` | array | Data sources with name, url, count, license |
| `meta.total_raw` | number | Total brands before filtering |
| `meta.total_filtered` | number | Total brands after filtering |
| `meta.ignored_terms` | string[] | Dictionary words to mark as low confidence |
| `brands` | string[] | All brand names (case-sensitive) |
| `high_confidence` | string[] | Subset of brands with high confidence |

### Best Practices

1. **High Confidence Brands**: Use for unique brand names that don't conflict with dictionary words
   ```typescript
   high_confidence: ['Salesforce', 'HubSpot', 'CustomCRM']
   ```

2. **Medium Confidence**: Brands not in `high_confidence` but also not in `ignored_terms`
   ```typescript
   brands: ['Salesforce', 'Target', 'Apple']
   // Target and Apple are dictionary words, so mark them:
   ignored_terms: ['target', 'apple']
   ```

3. **Ignored Terms**: Common words that happen to be brand names
   ```typescript
   ignored_terms: ['apple', 'orange', 'target', 'go', 'uber']
   ```

4. **Multi-word Brands**: Supported up to 3 words
   ```typescript
   brands: ['Salesforce Marketing Cloud', 'Adobe Experience Manager']
   ```

5. **Case Sensitivity**: Brand names are case-sensitive in the database but detection is case-insensitive
   ```typescript
   brands: ['HubSpot'] // Will detect 'hubspot', 'HubSpot', 'HUBSPOT'
   ```

### Performance Notes

- Custom databases have the same O(1) lookup performance as the bundled database
- Larger databases use more memory (~10MB per 10,000 brands)
- Detection speed is O(n) where n = word count in text

### FAQ

**Q: Can I load multiple databases?**
A: No, you can only use one database per `BrandDetector` instance. However, you can merge multiple databases:

```typescript
const mergedDb: BrandDatabase = {
  meta: { /* combined metadata */ },
  brands: [...db1.brands, ...db2.brands, ...db3.brands],
  high_confidence: [...db1.high_confidence, ...db2.high_confidence]
};
```

**Q: Can I update the database at runtime?**
A: No, databases are immutable after initialization. Create a new `BrandDetector` instance with the updated database.

**Q: What happens to the bundled database?**
A: It's still included in the package. If you don't provide a custom database, it's used by default.

**Q: How do I generate a custom database?**
A: You can:
1. Create it manually in JSON format (see template above)
2. Modify the included `scripts/fetch-brands.py` script
3. Export data from your own sources and format as JSON

### Support

- [GitHub Issues](https://github.com/Rankfor/rankfor-open/issues)
- [Documentation](https://github.com/Rankfor/rankfor-open/tree/main/brand-detector)
- [Examples](/examples)
