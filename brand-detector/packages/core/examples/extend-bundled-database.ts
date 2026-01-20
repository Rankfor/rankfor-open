/**
 * Example: Extending the bundled database with custom brands
 *
 * This example shows how to:
 * 1. Load the bundled database
 * 2. Add your custom brands to it
 * 3. Create a detector with the extended database
 */

import { BrandDetector } from '../src/BrandDetector';
import brandsDb from '../data/brands.json';
import type { BrandDatabase } from '../src/types';

// Extend bundled database with custom brands
const extendedDb: BrandDatabase = {
  ...brandsDb,
  brands: [
    ...brandsDb.brands,
    // Add your custom brands here
    'CustomCRM',
    'OurBrand',
    'CompetitorX',
    'NicheTool'
  ],
  high_confidence: [
    ...brandsDb.high_confidence,
    // Mark high-confidence custom brands
    'CustomCRM',
    'OurBrand'
  ]
};

// Create detector with extended database
const detector = new BrandDetector(extendedDb);

// Test with mixed brands (bundled + custom)
const text = `
For CRM, we recommend Salesforce (bundled) or CustomCRM (custom).
HubSpot (bundled) and OurBrand (custom) are great for marketing.
CompetitorX (custom) offers similar features to Microsoft Dynamics (bundled).
`;

const result = detector.analyzeLLMResponse(text);

console.log('Extended Database Analysis:');
console.log('===========================');
console.log(`Total Brands: ${result.totalBrands}`);
console.log(`Total Mentions: ${result.totalMentions}`);
console.log('\nBrand Mentions:');
for (const mention of result.mentions) {
  const source = brandsDb.brands.includes(mention.brand) ? 'bundled' : 'custom';
  console.log(`  - ${mention.brand}: ${mention.count} mentions (${mention.confidence} confidence, ${source})`);
}

// Check bundled brands
console.log('\nBundled Brands:');
console.log(`Salesforce: ${detector.isBrand('Salesforce')} (${detector.getConfidence('Salesforce')})`);
console.log(`HubSpot: ${detector.isBrand('HubSpot')} (${detector.getConfidence('HubSpot')})`);

// Check custom brands
console.log('\nCustom Brands:');
console.log(`CustomCRM: ${detector.isBrand('CustomCRM')} (${detector.getConfidence('CustomCRM')})`);
console.log(`OurBrand: ${detector.isBrand('OurBrand')} (${detector.getConfidence('OurBrand')})`);
console.log(`CompetitorX: ${detector.isBrand('CompetitorX')} (${detector.getConfidence('CompetitorX')})`);

// Database metadata
const metadata = detector.getMetadata();
console.log('\nDatabase Info:');
console.log(`Total brands in database: ${extendedDb.brands.length}`);
console.log(`High confidence brands: ${extendedDb.high_confidence.length}`);
console.log(`Original bundled brands: ${brandsDb.brands.length}`);
console.log(`Added custom brands: ${extendedDb.brands.length - brandsDb.brands.length}`);
