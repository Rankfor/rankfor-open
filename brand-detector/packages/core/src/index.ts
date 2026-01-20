/**
 * @rankfor/brand-detector
 * ======================
 *
 * Detect and analyze brand mentions in LLM/AI responses.
 *
 * @packageDocumentation
 */

export { BrandDetector } from './BrandDetector';
export type {
  BrandConfidence,
  DetectedBrand,
  BrandMention,
  BrandAnalysisResult,
  BrandDetectorOptions,
  BrandDatabase,
  BrandDatabaseMeta,
  BrandDatabaseSource,
} from './types';

// Convenience export: singleton instance
import { BrandDetector } from './BrandDetector';
export const brandDetector = new BrandDetector();
