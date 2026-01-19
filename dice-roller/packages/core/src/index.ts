/**
 * @rankfor/dice-roller
 * AI Response Stability Analyzer
 *
 * Analyze how consistently AI models respond to the same prompt.
 * Useful for understanding brand visibility and recommendation patterns.
 *
 * @packageDocumentation
 */

/**
 * Options for stability analysis
 */
export interface StabilityOptions {
  /** The prompt to analyze */
  prompt: string;

  /** Number of iterations to run (default: 5, max: 10) */
  iterations?: number;

  /** LLM model to use */
  model?: 'gemini' | 'openai' | 'grok';

  /** API key for the chosen model */
  apiKey: string;

  /** Model temperature (default: 0.7) */
  temperature?: number;

  /** Optional brand context for focused analysis */
  brandContext?: {
    name: string;
    url?: string;
    industry?: string;
  };
}

/**
 * A single response from the LLM
 */
export interface ResponseData {
  /** Response text */
  content: string;

  /** Brands mentioned in the response */
  brandMentions: string[];

  /** Key points extracted from the response */
  keyPoints: string[];

  /** Overall sentiment (positive, neutral, negative) */
  sentiment: 'positive' | 'neutral' | 'negative';

  /** Response latency in ms */
  latencyMs: number;
}

/**
 * A message that appeared in some but not all responses
 */
export interface VariableMessage {
  /** The message content */
  message: string;

  /** Percentage of responses containing this message */
  frequency: number;

  /** Which iterations included this message */
  appearancePattern: number[];
}

/**
 * Result of stability analysis
 */
export interface StabilityResult {
  /** Overall consistency score (0-100) */
  consistencyScore: number;

  /** All individual responses */
  responses: ResponseData[];

  /** Detailed analysis */
  analysis: {
    /** Semantic overlap between responses (0-100) */
    semanticOverlap: number;

    /** Messages that appeared in all/most responses */
    coreStableMessages: string[];

    /** Messages that appeared in some responses */
    variableMessages: VariableMessage[];

    /** Messages that appeared only once */
    outliers: string[];
  };

  /** Brand mention statistics */
  brandMentions: {
    /** Total mentions across all responses */
    total: number;

    /** Minimum mentions in a single response */
    min: number;

    /** Maximum mentions in a single response */
    max: number;

    /** Average mentions per response */
    average: number;

    /** Standard deviation of mentions */
    variance: number;
  };

  /** AI-generated recommendations */
  recommendations: {
    /** Messages to add to your content */
    messagesToAdd: string[];

    /** Messages to reinforce */
    messagesToReinforce: string[];

    /** Opportunity gaps to address */
    opportunityGaps: string[];
  };
}

/**
 * Analyze AI response stability for a given prompt
 *
 * @param options - Configuration options
 * @returns Promise resolving to stability analysis results
 *
 * @example
 * ```typescript
 * const result = await analyzeStability({
 *   prompt: 'What are the best CRM tools for small businesses?',
 *   iterations: 5,
 *   model: 'gemini',
 *   apiKey: process.env.GEMINI_API_KEY,
 * });
 *
 * console.log(`Consistency: ${result.consistencyScore}%`);
 * console.log('Always mentioned:', result.analysis.coreStableMessages);
 * ```
 */
export async function analyzeStability(
  options: StabilityOptions
): Promise<StabilityResult> {
  const { prompt, iterations = 5, model = 'gemini', apiKey, temperature = 0.7 } = options;

  if (!apiKey) {
    throw new Error('API key is required');
  }

  if (iterations < 1 || iterations > 10) {
    throw new Error('Iterations must be between 1 and 10');
  }

  // TODO: Implement actual LLM calls
  // This is a placeholder that will be implemented in Phase 4
  throw new Error(
    'Not yet implemented. Full implementation coming in @rankfor/dice-roller v1.0.0. ' +
    'For now, use the Rankfor.AI platform at https://app.rankfor.ai for stability analysis.'
  );
}

/**
 * Calculate semantic overlap between two texts
 *
 * @param text1 - First text
 * @param text2 - Second text
 * @returns Overlap score (0-100)
 */
export function calculateSemanticOverlap(text1: string, text2: string): number {
  // Simple word-based overlap for initial version
  const words1 = new Set(text1.toLowerCase().split(/\s+/).filter(w => w.length > 3));
  const words2 = new Set(text2.toLowerCase().split(/\s+/).filter(w => w.length > 3));

  if (words1.size === 0 || words2.size === 0) {
    return 0;
  }

  const intersection = new Set([...words1].filter(w => words2.has(w)));
  const union = new Set([...words1, ...words2]);

  return Math.round((intersection.size / union.size) * 100);
}

/**
 * Extract brand mentions from text
 *
 * @param text - Text to analyze
 * @param knownBrands - Optional list of known brand names to look for
 * @returns Array of mentioned brands
 */
export function extractBrandMentions(
  text: string,
  knownBrands?: string[]
): string[] {
  const mentions: string[] = [];

  if (knownBrands) {
    for (const brand of knownBrands) {
      const regex = new RegExp(`\\b${brand}\\b`, 'gi');
      if (regex.test(text)) {
        mentions.push(brand);
      }
    }
  }

  // Also extract capitalized words that might be brands
  const capitalizedPattern = /\b[A-Z][a-zA-Z]+(?:\.[A-Z][a-zA-Z]+)?\b/g;
  const matches = text.match(capitalizedPattern) || [];

  // Filter common non-brand words
  const commonWords = new Set([
    'The', 'This', 'That', 'These', 'Those', 'What', 'When', 'Where', 'Which',
    'How', 'Why', 'Who', 'Here', 'There', 'Some', 'Many', 'Most', 'Best',
    'Good', 'Great', 'First', 'Last', 'New', 'Old', 'High', 'Low',
  ]);

  for (const match of matches) {
    if (!commonWords.has(match) && !mentions.includes(match)) {
      mentions.push(match);
    }
  }

  return mentions;
}

export default analyzeStability;
