/**
 * Type definitions for Brand Detector
 */

export type BrandConfidence = 'high' | 'medium' | 'low';

/**
 * Detected brand with position in text
 */
export interface DetectedBrand {
  /** Original brand name (as it appears in text) */
  name: string;

  /** Normalized brand name (as it appears in database) */
  normalized: string;

  /** Confidence level */
  confidence: BrandConfidence;

  /** Position in text (start index) */
  startIndex: number;

  /** Position in text (end index) */
  endIndex: number;
}

/**
 * Brand mention with count and optional context
 * Used for analyzing LLM responses
 */
export interface BrandMention {
  /** Brand name (normalized) */
  brand: string;

  /** Number of times mentioned */
  count: number;

  /** Confidence level */
  confidence: BrandConfidence;

  /** Surrounding context for each mention (if extended mode) */
  contexts?: string[];
}

/**
 * Result of analyzing LLM response for brand mentions
 */
export interface BrandAnalysisResult {
  /** Total unique brands found */
  totalBrands: number;

  /** Total brand mentions across all brands */
  totalMentions: number;

  /** Brand mentions with counts (and optionally contexts) */
  mentions: BrandMention[];

  /** Most mentioned brand */
  topBrand: string | null;
}

/**
 * Options for brand detection
 */
export interface BrandDetectorOptions {
  /** Include surrounding text context for each mention */
  extended?: boolean;

  /** Number of characters before/after brand mention (default: 50) */
  contextRadius?: number;

  /** Minimum confidence level to include */
  minConfidence?: BrandConfidence;
}

/**
 * Brand database source metadata
 */
export interface BrandDatabaseSource {
  name: string;
  url: string;
  count: number;
  license: string;
}

/**
 * Brand database metadata
 */
export interface BrandDatabaseMeta {
  version: string;
  generated_at: string;
  sources: BrandDatabaseSource[];
  total_raw: number;
  total_filtered: number;
  ignored_terms: string[];
}

/**
 * Brand database structure
 */
export interface BrandDatabase {
  meta: BrandDatabaseMeta;
  brands: string[];
  high_confidence: string[];
}
