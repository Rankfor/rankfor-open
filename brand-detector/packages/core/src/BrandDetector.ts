/**
 * Brand Detector
 * ==============
 *
 * Detect and analyze brand mentions in LLM/AI responses.
 *
 * @packageDocumentation
 */

import brandsDb from '../data/brands.json';
import type { BrandDatabase, BrandDetectorOptions, DetectedBrand, BrandMention, BrandAnalysisResult } from './types';

/**
 * Brand Detector Service
 *
 * Detects brand mentions in text using a comprehensive database of 10,000+ brands
 * from Simple Icons (curated tech/SaaS) and Wikidata (global brands).
 *
 * @example
 * ```typescript
 * import { BrandDetector } from '@rankfor/brand-detector';
 *
 * const detector = new BrandDetector();
 *
 * // Analyze LLM response
 * const result = detector.analyzeLLMResponse(
 *   "I recommend Salesforce, HubSpot, or Pipedrive for CRM."
 * );
 *
 * console.log(result.totalBrands);    // 3
 * console.log(result.topBrand);       // 'Salesforce'
 * ```
 */
export class BrandDetector {
  private highConfidenceSet: Set<string>;
  private ignoredTermsSet: Set<string>;
  private normalizedMap: Map<string, string>; // lowercase -> original

  constructor() {
    const db = brandsDb as BrandDatabase;

    // Create lookup sets for O(1) access
    this.highConfidenceSet = new Set(db.high_confidence);
    this.ignoredTermsSet = new Set(db.meta.ignored_terms);

    // Create normalized map (lowercase to original)
    this.normalizedMap = new Map();
    for (const brand of db.brands) {
      this.normalizedMap.set(brand.toLowerCase(), brand);
    }
  }

  /**
   * Check if a string is a known brand
   *
   * @param text - Text to check
   * @returns True if text is a known brand
   *
   * @example
   * ```typescript
   * detector.isBrand('Salesforce');  // true
   * detector.isBrand('foobar');      // false
   * ```
   */
  isBrand(text: string): boolean {
    const normalized = this.normalizedMap.get(text.toLowerCase());
    return normalized !== undefined;
  }

  /**
   * Get confidence level for a brand
   *
   * @param text - Brand name
   * @returns Confidence level or null if not a brand
   *
   * @example
   * ```typescript
   * detector.getConfidence('HubSpot');  // 'high'
   * detector.getConfidence('Oracle');   // 'low' (dictionary word)
   * detector.getConfidence('unknown');  // null
   * ```
   */
  getConfidence(text: string): 'high' | 'medium' | 'low' | null {
    const normalized = this.normalizedMap.get(text.toLowerCase());
    if (!normalized) return null;

    if (this.highConfidenceSet.has(normalized)) {
      return 'high';
    }

    // Check if in ignored terms (dictionary words)
    if (this.ignoredTermsSet.has(text.toLowerCase())) {
      return 'low';
    }

    return 'medium';
  }

  /**
   * Analyze LLM response for brand mentions
   *
   * PRIMARY API for analyzing AI/LLM responses.
   *
   * @param llmResponse - Text response from LLM (ChatGPT, Claude, Gemini, etc.)
   * @param options - Analysis options
   * @returns Brand analysis with counts and optional contexts
   *
   * @example Basic mode (counts only):
   * ```typescript
   * const result = detector.analyzeLLMResponse(
   *   "I recommend Salesforce for CRM. Salesforce has great features."
   * );
   * // {
   * //   totalBrands: 1,
   * //   totalMentions: 2,
   * //   mentions: [
   * //     { brand: 'Salesforce', count: 2, confidence: 'high' }
   * //   ],
   * //   topBrand: 'Salesforce'
   * // }
   * ```
   *
   * @example Extended mode (with context):
   * ```typescript
   * const result = detector.analyzeLLMResponse(
   *   "I recommend Salesforce for CRM. Salesforce has great features.",
   *   { extended: true, contextRadius: 30 }
   * );
   * // {
   * //   totalBrands: 1,
   * //   totalMentions: 2,
   * //   mentions: [
   * //     {
   * //       brand: 'Salesforce',
   * //       count: 2,
   * //       confidence: 'high',
   * //       contexts: [
   * //         'I recommend Salesforce for CRM.',
   * //         'CRM. Salesforce has great features.'
   * //       ]
   * //     }
   * //   ],
   * //   topBrand: 'Salesforce'
   * // }
   * ```
   */
  analyzeLLMResponse(
    llmResponse: string,
    options: BrandDetectorOptions = {}
  ): BrandAnalysisResult {
    const { extended = false, contextRadius = 50, minConfidence = 'low' } = options;

    // Detect all brands in the response
    const detectedBrands = this.detectBrands(llmResponse, { minConfidence });

    // Group by normalized brand name
    const brandGroups = new Map<string, DetectedBrand[]>();
    for (const brand of detectedBrands) {
      const existing = brandGroups.get(brand.normalized) || [];
      existing.push(brand);
      brandGroups.set(brand.normalized, existing);
    }

    // Build mentions array
    const mentions: BrandMention[] = [];
    for (const [brandName, brandOccurrences] of brandGroups) {
      const mention: BrandMention = {
        brand: brandName,
        count: brandOccurrences.length,
        confidence: brandOccurrences[0].confidence,
      };

      // Add contexts if extended mode
      if (extended) {
        mention.contexts = brandOccurrences.map((occurrence) =>
          this.extractContextWindow(
            llmResponse,
            occurrence.startIndex,
            occurrence.endIndex,
            contextRadius
          )
        );
      }

      mentions.push(mention);
    }

    // Sort by count (descending)
    mentions.sort((a, b) => b.count - a.count);

    // Calculate metrics
    const totalBrands = mentions.length;
    const totalMentions = mentions.reduce((sum, m) => sum + m.count, 0);
    const topBrand = mentions.length > 0 ? mentions[0].brand : null;

    return {
      totalBrands,
      totalMentions,
      mentions,
      topBrand,
    };
  }

  /**
   * Detect all brands in text with positions
   *
   * @param text - Text to search for brands
   * @param options - Detection options
   * @returns Array of detected brands with positions
   */
  detectBrands(
    text: string,
    options: {
      minConfidence?: 'high' | 'medium' | 'low';
      maxResults?: number;
    } = {}
  ): DetectedBrand[] {
    const { minConfidence = 'low', maxResults = Infinity } = options;

    const detected: DetectedBrand[] = [];

    // Split text into words, preserving positions
    const words = this.tokenize(text);

    // Check each word and multi-word combinations
    for (let i = 0; i < words.length; i++) {
      // Try 1-word, 2-word, 3-word combinations
      for (let len = 1; len <= Math.min(3, words.length - i); len++) {
        const candidate = words
          .slice(i, i + len)
          .map((w) => w.text)
          .join(' ');
        const normalized = this.normalizedMap.get(candidate.toLowerCase());

        if (normalized) {
          const confidence = this.getConfidence(normalized);

          // Skip if below minimum confidence
          if (confidence && this.meetsMinConfidence(confidence, minConfidence)) {
            // Check if not already detected (avoid duplicates)
            const startIndex = words[i].startIndex;
            const endIndex = words[i + len - 1].endIndex;

            const alreadyDetected = detected.some(
              (d) => d.startIndex === startIndex && d.endIndex === endIndex
            );

            if (!alreadyDetected) {
              detected.push({
                name: candidate,
                normalized,
                confidence,
                startIndex,
                endIndex,
              });
            }
          }
        }
      }
    }

    // Sort by position
    detected.sort((a, b) => a.startIndex - b.startIndex);

    // Limit results
    return detected.slice(0, maxResults);
  }

  /**
   * Extract unique brand names from text
   *
   * @param text - Text to search
   * @param minConfidence - Minimum confidence level
   * @returns Array of unique brand names
   */
  extractBrandNames(
    text: string,
    minConfidence: 'high' | 'medium' | 'low' = 'medium'
  ): string[] {
    const brands = this.detectBrands(text, { minConfidence });
    const uniqueNames = new Set(brands.map((b) => b.normalized));
    return Array.from(uniqueNames);
  }

  /**
   * Count brand mentions in text
   *
   * @param text - Text to search
   * @param brandName - Specific brand to count (optional)
   * @returns Count of brand mentions
   */
  countBrandMentions(text: string, brandName?: string): number {
    const brands = this.detectBrands(text);

    if (brandName) {
      const normalized = this.normalizedMap.get(brandName.toLowerCase());
      return brands.filter((b) => b.normalized === normalized).length;
    }

    return brands.length;
  }

  /**
   * Get database metadata
   */
  getMetadata(): BrandDatabase['meta'] {
    return (brandsDb as BrandDatabase).meta;
  }

  /**
   * Get autocomplete suggestions for brand names
   *
   * @param partial - Partial brand name
   * @param limit - Maximum suggestions
   * @returns Array of matching brand names
   */
  getSuggestions(partial: string, limit: number = 10): string[] {
    const lowerPartial = partial.toLowerCase();
    const suggestions: string[] = [];

    for (const [lowercase, original] of this.normalizedMap) {
      if (lowercase.startsWith(lowerPartial)) {
        suggestions.push(original);

        if (suggestions.length >= limit) {
          break;
        }
      }
    }

    return suggestions.sort();
  }

  /**
   * Tokenize text into words with positions
   */
  private tokenize(text: string): Array<{ text: string; startIndex: number; endIndex: number }> {
    const tokens: Array<{ text: string; startIndex: number; endIndex: number }> = [];

    // Match words (including hyphenated words and dots)
    const regex = /[\w.-]+/g;
    let match: RegExpExecArray | null;

    while ((match = regex.exec(text)) !== null) {
      tokens.push({
        text: match[0],
        startIndex: match.index,
        endIndex: match.index + match[0].length,
      });
    }

    return tokens;
  }

  /**
   * Check if confidence meets minimum threshold
   */
  private meetsMinConfidence(
    confidence: 'high' | 'medium' | 'low',
    minConfidence: 'high' | 'medium' | 'low'
  ): boolean {
    const levels: Record<'high' | 'medium' | 'low', number> = {
      high: 3,
      medium: 2,
      low: 1,
    };

    return levels[confidence] >= levels[minConfidence];
  }

  /**
   * Extract context window around a brand mention
   */
  private extractContextWindow(
    text: string,
    startIndex: number,
    endIndex: number,
    radius: number
  ): string {
    const contextStart = Math.max(0, startIndex - radius);
    const contextEnd = Math.min(text.length, endIndex + radius);

    let context = text.slice(contextStart, contextEnd);

    // Add ellipsis if truncated
    if (contextStart > 0) {
      context = '...' + context;
    }
    if (contextEnd < text.length) {
      context = context + '...';
    }

    return context;
  }
}
