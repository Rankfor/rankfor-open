/**
 * Tests for custom brand database support
 */

import { BrandDetector } from '../BrandDetector';
import type { BrandDatabase } from '../types';

describe('BrandDetector - Custom Database', () => {
  const customDb: BrandDatabase = {
    meta: {
      version: '1.0.0',
      generated_at: '2026-01-20T00:00:00.000Z',
      sources: [
        {
          name: 'Test Brands',
          url: 'https://test.com',
          count: 5,
          license: 'CC0',
        },
      ],
      total_raw: 5,
      total_filtered: 5,
      ignored_terms: ['target'],
    },
    brands: ['CustomCRM', 'OurBrand', 'CompetitorX', 'NicheTool', 'Target'],
    high_confidence: ['CustomCRM', 'OurBrand', 'NicheTool'],
  };

  describe('Constructor', () => {
    it('should accept custom brand database', () => {
      const detector = new BrandDetector(customDb);
      expect(detector).toBeInstanceOf(BrandDetector);
    });

    it('should use bundled database by default (even if empty placeholder)', () => {
      const detector = new BrandDetector();
      expect(detector).toBeInstanceOf(BrandDetector);
      // Note: bundled DB is placeholder until scripts/fetch-brands.py is run
    });
  });

  describe('Custom Brands Detection', () => {
    let detector: BrandDetector;

    beforeEach(() => {
      detector = new BrandDetector(customDb);
    });

    it('should detect custom brands', () => {
      expect(detector.isBrand('CustomCRM')).toBe(true);
      expect(detector.isBrand('OurBrand')).toBe(true);
      expect(detector.isBrand('CompetitorX')).toBe(true);
      expect(detector.isBrand('NicheTool')).toBe(true);
    });

    it('should not detect brands not in custom database', () => {
      expect(detector.isBrand('Salesforce')).toBe(false);
      expect(detector.isBrand('HubSpot')).toBe(false);
      expect(detector.isBrand('UnknownBrand')).toBe(false);
    });

    it('should return correct confidence levels', () => {
      expect(detector.getConfidence('CustomCRM')).toBe('high');
      expect(detector.getConfidence('OurBrand')).toBe('high');
      expect(detector.getConfidence('NicheTool')).toBe('high');
      expect(detector.getConfidence('CompetitorX')).toBe('medium');
      expect(detector.getConfidence('Target')).toBe('low'); // in ignored_terms
    });
  });

  describe('analyzeLLMResponse with Custom Database', () => {
    let detector: BrandDetector;

    beforeEach(() => {
      detector = new BrandDetector(customDb);
    });

    it('should analyze text with custom brands', () => {
      const text = 'I recommend CustomCRM and OurBrand for this use case.';
      const result = detector.analyzeLLMResponse(text);

      expect(result.totalBrands).toBe(2);
      expect(result.totalMentions).toBe(2);
      expect(result.topBrand).toBe('CustomCRM');
      expect(result.mentions).toEqual([
        { brand: 'CustomCRM', count: 1, confidence: 'high' },
        { brand: 'OurBrand', count: 1, confidence: 'high' },
      ]);
    });

    it('should count multiple mentions correctly', () => {
      const text = 'CustomCRM is great. CustomCRM offers many features. Try CustomCRM today.';
      const result = detector.analyzeLLMResponse(text);

      expect(result.totalBrands).toBe(1);
      expect(result.totalMentions).toBe(3);
      expect(result.mentions[0]).toEqual({
        brand: 'CustomCRM',
        count: 3,
        confidence: 'high',
      });
    });

    it('should filter by minConfidence', () => {
      const text = 'Use CustomCRM, CompetitorX, or NicheTool.';

      // High confidence only (CustomCRM, NicheTool)
      const highOnly = detector.analyzeLLMResponse(text, { minConfidence: 'high' });
      expect(highOnly.totalBrands).toBe(2);
      expect(highOnly.mentions.map(m => m.brand).sort()).toEqual(['CustomCRM', 'NicheTool']);

      // Medium and above (adds CompetitorX)
      const mediumUp = detector.analyzeLLMResponse(text, { minConfidence: 'medium' });
      expect(mediumUp.totalBrands).toBe(3);

      // Test with low confidence brand (Target)
      const textWithLow = 'Use CustomCRM or Target.';
      const all = detector.analyzeLLMResponse(textWithLow, { minConfidence: 'low' });
      expect(all.totalBrands).toBe(2); // CustomCRM (high) + Target (low)
    });

    it('should extract context in extended mode', () => {
      const text = 'For CRM solutions, CustomCRM is the best choice available.';
      const result = detector.analyzeLLMResponse(text, {
        extended: true,
        contextRadius: 30,
      });

      expect(result.mentions[0].contexts).toBeDefined();
      expect(result.mentions[0].contexts![0]).toContain('CustomCRM');
    });
  });

  describe('Extended Database (Bundled + Custom)', () => {
    it('should detect both bundled and custom brands', () => {
      const bundledDb = {
        meta: {
          version: '1.0.0',
          generated_at: '2026-01-20T00:00:00.000Z',
          sources: [],
          total_raw: 2,
          total_filtered: 2,
          ignored_terms: [],
        },
        brands: ['Salesforce', 'HubSpot'],
        high_confidence: ['Salesforce', 'HubSpot'],
      };

      const extendedDb: BrandDatabase = {
        ...bundledDb,
        brands: [...bundledDb.brands, 'CustomCRM', 'OurBrand'],
        high_confidence: [...bundledDb.high_confidence, 'CustomCRM', 'OurBrand'],
      };

      const detector = new BrandDetector(extendedDb);

      // Bundled brands
      expect(detector.isBrand('Salesforce')).toBe(true);
      expect(detector.isBrand('HubSpot')).toBe(true);

      // Custom brands
      expect(detector.isBrand('CustomCRM')).toBe(true);
      expect(detector.isBrand('OurBrand')).toBe(true);

      const text = 'Salesforce and CustomCRM are both great CRM tools.';
      const result = detector.analyzeLLMResponse(text);
      expect(result.totalBrands).toBe(2);
    });
  });

  describe('Metadata', () => {
    it('should return custom database metadata', () => {
      const detector = new BrandDetector(customDb);
      const metadata = detector.getMetadata();

      expect(metadata.version).toBe('1.0.0');
      expect(metadata.sources).toHaveLength(1);
      expect(metadata.sources[0].name).toBe('Test Brands');
      expect(metadata.total_filtered).toBe(5);
      expect(metadata.ignored_terms).toContain('target');
    });
  });
});
