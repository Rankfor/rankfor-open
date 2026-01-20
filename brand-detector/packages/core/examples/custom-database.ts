/**
 * Example: Using a custom brand database
 *
 * This example shows how to:
 * 1. Load a custom brand database from JSON
 * 2. Create a BrandDetector with custom brands
 * 3. Analyze text for your custom brands
 */

import { BrandDetector } from '../src/BrandDetector';
import customBrands from './custom-brands.json';

// Create detector with custom brands
const detector = new BrandDetector(customBrands);

// Analyze text containing custom brands
const text = `
We recommend using CustomCRM for customer management,
OurBrand for marketing automation, and CompetitorX as an alternative.
For niche use cases, consider NicheTool or StartupY.
`;

const result = detector.analyzeLLMResponse(text);

console.log('Analysis Results:');
console.log('=================');
console.log(`Total Brands: ${result.totalBrands}`);
console.log(`Total Mentions: ${result.totalMentions}`);
console.log(`Top Brand: ${result.topBrand}`);
console.log('\nBrand Mentions:');
for (const mention of result.mentions) {
  console.log(`  - ${mention.brand}: ${mention.count} mentions (${mention.confidence} confidence)`);
}

// Check if specific brands are recognized
console.log('\nBrand Recognition:');
console.log(`Is "CustomCRM" a brand? ${detector.isBrand('CustomCRM')}`);
console.log(`Is "OurBrand" a brand? ${detector.isBrand('OurBrand')}`);
console.log(`Is "UnknownBrand" a brand? ${detector.isBrand('UnknownBrand')}`);

// Get confidence levels
console.log('\nConfidence Levels:');
console.log(`CustomCRM: ${detector.getConfidence('CustomCRM')}`);
console.log(`CompetitorX: ${detector.getConfidence('CompetitorX')}`);
console.log(`RegionalBrand: ${detector.getConfidence('RegionalBrand')}`);
