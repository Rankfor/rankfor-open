/**
 * @rankfor/dice-roller
 * AI Response Stability Analyzer
 *
 * Analyze how consistently AI models respond to the same prompt.
 * Useful for understanding brand visibility and recommendation patterns.
 *
 * MIT License - https://github.com/Rankfor/rankfor-open
 *
 * @packageDocumentation
 */

// ============================================================================
// Types
// ============================================================================

/**
 * Search mode for LLM queries
 * - 'memory': Use model's training data only (default, faster, no extra cost)
 * - 'search': Enable web search/grounding for real-time information (slower, may incur costs)
 */
export type SearchMode = 'memory' | 'search';

/**
 * Citation/source from web search results
 */
export interface SearchCitation {
  /** URL of the source */
  url: string;
  /** Title of the source page */
  title: string;
  /** Relevant snippet from the source */
  snippet?: string;
}

/**
 * Configuration for text analysis customization
 */
export interface AnalysisConfig {
  /**
   * Custom stop words to exclude from key point comparison.
   * If provided, replaces the default English stop words.
   * Useful for non-English content or domain-specific filtering.
   */
  customStopWords?: string[];

  /**
   * Custom synonym groups for semantic matching.
   * Each group is an array of words considered semantically equivalent.
   * Useful for industry-specific terminology.
   *
   * @example
   * ```typescript
   * customSynonyms: [
   *   ['CRM', 'customer relationship management', 'client management'],
   *   ['AI', 'artificial intelligence', 'machine learning', 'ML']
   * ]
   * ```
   */
  customSynonyms?: string[][];

  /**
   * Custom positive sentiment indicators.
   * If provided, extends the default list.
   */
  customPositiveIndicators?: string[];

  /**
   * Custom negative sentiment indicators.
   * If provided, extends the default list.
   */
  customNegativeIndicators?: string[];
}

/**
 * Error data from a failed iteration
 */
export interface IterationError {
  /** Iteration number that failed (1-indexed) */
  iteration: number;
  /** Error message */
  message: string;
  /** Original error object */
  error: Error;
}

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

  /** Maximum tokens per response (default: 2048) */
  maxTokens?: number;

  /** Optional brand name for focused brand mention analysis */
  brandName?: string;

  /** Delay between iterations in ms (default: 1000) */
  iterationDelayMs?: number;

  /**
   * Search mode: 'memory' (default) or 'search'
   * - 'memory': Uses model's training data only
   * - 'search': Enables web search/grounding for real-time information
   */
  searchMode?: SearchMode;

  /** Callback for progress updates */
  onProgress?: (iteration: number, total: number) => void;

  /**
   * Callback for iteration errors.
   * Called when an individual iteration fails but analysis continues.
   * If not provided, errors are silently logged to console.
   */
  onError?: (error: IterationError) => void;

  /**
   * Custom analysis configuration for stop words, synonyms, etc.
   * Allows tailoring the analysis to specific industries or languages.
   */
  analysisConfig?: AnalysisConfig;
}

/**
 * Brand mention with context
 */
export interface BrandMentionContext {
  /** Character position in response */
  position: number;
  /** Text snippet around the mention */
  snippet: string;
  /** Sentiment of the context (positive, neutral, negative) */
  sentiment: 'positive' | 'neutral' | 'negative';
}

/**
 * A single response from the LLM
 */
export interface ResponseData {
  /** Iteration number (1-indexed) */
  iteration: number;
  /** Response text */
  content: string;
  /** Response length in characters */
  length: number;
  /**
   * Estimated token count (approximation: ~4 chars per token for English).
   * Note: This is an estimate. Actual token count varies by model tokenizer.
   */
  estimatedTokens: number;
  /** Number of brand mentions (if brandName provided) */
  brandMentions: number;
  /** Brand mention contexts with snippets */
  brandMentionContexts: BrandMentionContext[];
  /** Key points extracted from the response */
  keyPoints: string[];
  /** Overall sentiment (positive, neutral, negative) */
  sentiment: 'positive' | 'neutral' | 'negative';
  /** Response latency in ms */
  latencyMs: number;
  /** Timestamp of response */
  timestamp: string;
  /** Search mode used for this response */
  searchMode?: SearchMode;
  /** Citations from web search (only populated when searchMode='search') */
  citations?: SearchCitation[];
}

/**
 * A message that appeared in some but not all responses
 */
export interface VariableMessage {
  /** The message content */
  message: string;
  /** Percentage of responses containing this message (0-100) */
  frequency: number;
  /** Which iterations included this message (1-indexed) */
  appearancePattern: number[];
}

/**
 * Brand mention statistics
 */
export interface BrandMentionStats {
  /** Total mentions across all responses */
  total: number;
  /** Minimum mentions in a single response */
  min: number;
  /** Maximum mentions in a single response */
  max: number;
  /** Average mentions per response */
  average: number;
  /** Variance of mentions */
  variance: number;
  /** Standard deviation of mentions */
  standardDeviation: number;
  /** All mention contexts aggregated */
  allContexts: BrandMentionContext[];
}

/**
 * Sentiment distribution across responses
 */
export interface SentimentDistribution {
  /** Percentage of positive responses */
  positive: number;
  /** Percentage of neutral responses */
  neutral: number;
  /** Percentage of negative responses */
  negative: number;
}

/**
 * Result of stability analysis
 */
export interface StabilityResult {
  /** Overall consistency score (0-100) */
  consistencyScore: number;

  /** Semantic overlap between responses (0-100) */
  semanticOverlap: number;

  /** All individual responses */
  responses: ResponseData[];

  /** Detailed analysis */
  analysis: {
    /** Messages that appeared in 80%+ of responses */
    coreStableMessages: string[];

    /** Messages that appeared in 30-80% of responses */
    variableMessages: VariableMessage[];

    /** Messages that appeared in <30% of responses */
    outliers: string[];

    /** Key point frequency map */
    keyPointFrequency: Record<string, number>;
  };

  /** Brand mention statistics (if brandName provided) */
  brandMentions: BrandMentionStats;

  /** Sentiment distribution */
  sentimentDistribution: SentimentDistribution;

  /** AI-generated recommendations */
  recommendations: {
    /** Messages to add to your content */
    messagesToAdd: string[];
    /** Messages to reinforce */
    messagesToReinforce: string[];
    /** Opportunity gaps to address */
    opportunityGaps: string[];
  };

  /** Execution metadata */
  metadata: {
    prompt: string;
    model: string;
    iterations: number;
    executionTimeMs: number;
    brandName?: string;
    /** Search mode used for this analysis */
    searchMode: SearchMode;
  };
}

// ============================================================================
// Experiment Mode Types
// ============================================================================

/**
 * API keys for different LLM providers
 */
export interface ExperimentApiKeys {
  /** Google Gemini API key */
  geminiApiKey?: string;
  /** OpenAI API key */
  openaiApiKey?: string;
  /** xAI Grok API key */
  grokApiKey?: string;
}

/**
 * Options for running a cross-model experiment
 */
export interface ExperimentOptions {
  /** The prompt to analyze across models */
  prompt: string;

  /** API keys for different providers */
  apiKeys: ExperimentApiKeys;

  /** Number of iterations per model (default: 5, max: 10) */
  iterations?: number;

  /** Model temperature (default: 0.7) */
  temperature?: number;

  /** Maximum tokens per response (default: 2048) */
  maxTokens?: number;

  /** Optional brand name for focused analysis */
  brandName?: string;

  /** Delay between iterations in ms (default: 1000) */
  iterationDelayMs?: number;

  /**
   * Search mode: 'memory' (default) or 'search'
   * - 'memory': Uses model's training data only
   * - 'search': Enables web search/grounding for real-time information
   */
  searchMode?: SearchMode;

  /** Callback for progress updates */
  onProgress?: (model: string, iteration: number, total: number) => void;

  /**
   * Callback for iteration errors.
   * Called when an individual iteration fails but analysis continues.
   */
  onError?: (error: IterationError & { model: string }) => void;

  /**
   * Custom analysis configuration for stop words, synonyms, etc.
   */
  analysisConfig?: AnalysisConfig;
}

/**
 * Brand frequency data for a single model
 */
export interface BrandFrequency {
  /** Brand name */
  brand: string;
  /** Number of times mentioned */
  count: number;
  /** Percentage of total mentions */
  percentage: number;
}

/**
 * Per-model result in an experiment
 */
export interface ModelExperimentResult {
  /** Model name */
  model: 'gemini' | 'openai' | 'grok';
  /** Full stability result for this model */
  result: StabilityResult;
  /** Unique brands mentioned by this model */
  uniqueBrands: string[];
  /** Brand frequency distribution */
  brandFrequencies: BrandFrequency[];
}

/**
 * Cross-model overlap analysis
 */
export interface CrossModelOverlap {
  /** Model A name */
  modelA: string;
  /** Model B name */
  modelB: string;
  /** Number of shared brands */
  sharedBrands: number;
  /** List of shared brand names */
  sharedBrandNames: string[];
  /** Jaccard similarity index (0-1) */
  jaccardIndex: number;
}

/**
 * Shannon entropy result for a model
 */
export interface EntropyResult {
  /** Model name */
  model: string;
  /** Raw Shannon entropy value */
  entropy: number;
  /** Normalized entropy (0-1) */
  normalizedEntropy: number;
  /** Interpretation of diversity */
  interpretation: 'stereotyped' | 'moderate' | 'diverse';
}

/**
 * Gini coefficient result for brand concentration
 */
export interface GiniResult {
  /** Model name */
  model: string;
  /** Gini coefficient (0=equality, 1=inequality) */
  giniCoefficient: number;
  /** Interpretation */
  interpretation: 'concentrated' | 'moderate' | 'distributed';
}

/**
 * Result of a cross-model experiment
 */
export interface ExperimentResult {
  /** Per-model stability results */
  modelResults: ModelExperimentResult[];

  /** Messages that appeared in ALL models' core messages */
  universalCoreMessages: string[];

  /** Messages that appeared in most (but not all) models */
  crossModelVariableMessages: Array<{
    message: string;
    appearsInModels: string[];
    frequency: number;
  }>;

  /** Cross-model overlap analysis */
  crossModelOverlap: CrossModelOverlap[];

  /** Brands mentioned by ALL models */
  universalBrands: string[];

  /** Statistical analysis */
  statistics: {
    /** Shannon entropy per model */
    shannonEntropy: EntropyResult[];
    /** Gini coefficient per model */
    giniCoefficients: GiniResult[];
    /** Average consistency across models */
    averageConsistency: number;
    /** Cross-model semantic overlap */
    crossModelSemanticOverlap: number;
    /** Response length statistics per model */
    responseLengthStats: Array<{
      model: string;
      avgLength: number;
      minLength: number;
      maxLength: number;
      stdDev: number;
    }>;
  };

  /** Recommendations based on cross-model analysis */
  recommendations: {
    /** Messages reinforced by ALL models */
    universallyReinforced: string[];
    /** Opportunities where only some models mention it */
    differentiationOpportunities: string[];
    /** Gaps where your brand is weak across all models */
    universalGaps: string[];
  };

  /** Execution metadata */
  metadata: {
    prompt: string;
    modelsUsed: string[];
    iterationsPerModel: number;
    totalExecutionTimeMs: number;
    brandName?: string;
    /** Search mode used for this experiment */
    searchMode: SearchMode;
  };
}

// ============================================================================
// Constants
// ============================================================================

/** Threshold for core/stable messages (80%+ of responses) */
const CORE_MESSAGE_THRESHOLD = 0.8;

/** Threshold for variable messages (30-80% of responses) */
const VARIABLE_MESSAGE_THRESHOLD = 0.3;

/** Stop words to exclude from key point comparison */
const STOP_WORDS = new Set([
  'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of',
  'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have',
  'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
  'might', 'must', 'shall', 'can', 'need', 'that', 'which', 'who', 'whom',
  'this', 'these', 'those', 'it', 'its', 'they', 'them', 'their', 'our', 'your',
  'his', 'her', 'we', 'you', 'i', 'me', 'my', 'also', 'more', 'most', 'other',
  'some', 'such', 'than', 'too', 'very', 'just', 'about', 'into', 'through',
  'during', 'before', 'after', 'above', 'below', 'between', 'under', 'again',
  'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
  'all', 'each', 'few', 'any', 'both', 'only', 'own', 'same', 'so', 'because',
  'until', 'while',
]);

/** Domain-specific synonym groups for semantic matching */
const SYNONYM_GROUPS = [
  ['product', 'service', 'solution', 'offering', 'platform'],
  ['customer', 'client', 'user', 'consumer', 'buyer'],
  ['quality', 'excellent', 'superior', 'premium', 'high-end'],
  ['price', 'cost', 'pricing', 'value', 'affordable'],
  ['fast', 'quick', 'rapid', 'speedy', 'efficient'],
  ['reliable', 'dependable', 'trustworthy', 'stable', 'consistent'],
  ['innovative', 'creative', 'novel', 'cutting-edge', 'advanced'],
  ['experience', 'expertise', 'knowledge', 'skill', 'proficiency'],
  ['support', 'help', 'assistance', 'service', 'care'],
  ['leader', 'leading', 'top', 'best', 'premier', 'foremost'],
  ['recommend', 'suggest', 'advise', 'propose'],
  ['benefit', 'advantage', 'strength', 'asset'],
  ['issue', 'problem', 'challenge', 'concern', 'difficulty'],
  ['improve', 'enhance', 'optimize', 'upgrade', 'boost'],
  ['market', 'industry', 'sector', 'field', 'space'],
];

/** Positive sentiment indicators */
const POSITIVE_INDICATORS = [
  'excellent', 'best', 'leading', 'innovative', 'expert', 'trusted',
  'recommend', 'superior', 'outstanding', 'proven', 'reliable', 'quality',
  'effective', 'efficient', 'top', 'premier', 'award', 'recognized',
  'great', 'perfect', 'ideal', 'exceptional', 'remarkable', 'impressive',
];

/** Negative sentiment indicators */
const NEGATIVE_INDICATORS = [
  'poor', 'lacking', 'inadequate', 'failed', 'problematic', 'inferior',
  'weak', 'limited', 'concerning', 'risk', 'expensive', 'difficult',
  'disappointing', 'issue', 'complaint', 'alternative to', 'avoid',
  'outdated', 'slow', 'unreliable', 'buggy', 'confusing', 'frustrating',
];

// ============================================================================
// LLM Client Functions
// ============================================================================

/**
 * Query Gemini API
 */
/**
 * Query result with optional citations
 */
interface QueryResult {
  response: string;
  latencyMs: number;
  citations?: SearchCitation[];
}

/**
 * Query Gemini API with optional Google Search grounding
 *
 * Search mode uses the google_search tool for real-time web grounding.
 * @see https://ai.google.dev/gemini-api/docs/google-search
 */
async function queryGemini(
  prompt: string,
  apiKey: string,
  temperature: number,
  maxTokens: number,
  searchMode: SearchMode = 'memory',
): Promise<QueryResult> {
  const { GoogleGenerativeAI } = await import('@google/generative-ai');
  const client = new GoogleGenerativeAI(apiKey);

  // Configure model options
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const modelOptions: any = {
    model: 'gemini-3-pro-preview',
  };

  // Add Google Search grounding tool when in search mode
  // The googleSearch tool enables real-time web search grounding
  if (searchMode === 'search') {
    modelOptions.tools = [{ googleSearch: {} }];
  }

  const model = client.getGenerativeModel(modelOptions);

  const start = Date.now();
  const result = await model.generateContent({
    contents: [{ role: 'user', parts: [{ text: prompt }] }],
    generationConfig: {
      temperature,
      maxOutputTokens: maxTokens,
    },
  });

  const latencyMs = Date.now() - start;
  const response = result.response.text();

  // Extract citations from grounding metadata if available
  let citations: SearchCitation[] | undefined;
  if (searchMode === 'search') {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const groundingMetadata = (result.response as any).groundingMetadata;

    if (groundingMetadata?.groundingChunks) {
      citations = groundingMetadata.groundingChunks
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .filter((chunk: any) => chunk.web)
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        .map((chunk: any) => ({
          url: chunk.web.uri,
          title: chunk.web.title,
        }));
    }
  }

  return { response, latencyMs, citations };
}

/**
 * Query OpenAI API (also works for Grok via baseURL)
 */
/**
 * Query OpenAI API with optional web search
 *
 * For OpenAI: Uses the web_search tool via responses API
 * For Grok/xAI: Uses the agentic search tools (web_search, x_search)
 *
 * @see https://platform.openai.com/docs/guides/tools-web-search
 * @see https://docs.x.ai/docs/guides/tools/search-tools
 */
async function queryOpenAI(
  prompt: string,
  apiKey: string,
  temperature: number,
  maxTokens: number,
  model: 'openai' | 'grok',
  searchMode: SearchMode = 'memory',
): Promise<QueryResult> {
  const OpenAI = (await import('openai')).default;

  const config: { apiKey: string; baseURL?: string } = { apiKey };
  let modelName = 'gpt-5.2';

  if (model === 'grok') {
    config.baseURL = 'https://api.x.ai/v1';
    modelName = 'grok-4';
  }

  const client = new OpenAI(config);
  const start = Date.now();

  let response: string;
  let citations: SearchCitation[] | undefined;

  if (searchMode === 'search') {
    // Use web search enabled endpoint
    if (model === 'openai') {
      // OpenAI uses the responses API with web_search tool
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const result = await (client as any).responses.create({
        model: 'gpt-5-search-preview',
        input: prompt,
        tools: [{ type: 'web_search' }],
      });

      response = result.output_text || '';

      // Extract citations from annotations
      if (result.output) {
        citations = [];
        for (const item of result.output) {
          if (item.annotations) {
            for (const annotation of item.annotations) {
              if (annotation.type === 'url_citation') {
                citations.push({
                  url: annotation.url,
                  title: annotation.title || annotation.url,
                });
              }
            }
          }
        }
      }
    } else {
      // Grok/xAI uses agentic search tools
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const result = await (client as any).responses.create({
        model: 'grok-4',
        input: prompt,
        tools: [
          { type: 'web_search' },
          { type: 'x_search' },
        ],
      });

      response = result.output_text || '';

      // Extract citations from xAI response
      if (result.citations) {
        citations = result.citations.map((c: { url: string; title?: string }) => ({
          url: c.url,
          title: c.title || c.url,
        }));
      }
    }
  } else {
    // Standard chat completion without web search
    const result = await client.chat.completions.create({
      model: modelName,
      messages: [{ role: 'user', content: prompt }],
      temperature,
      max_tokens: maxTokens,
    });

    response = result.choices[0]?.message?.content || '';
  }

  const latencyMs = Date.now() - start;
  return { response, latencyMs, citations };
}

// ============================================================================
// Text Analysis Functions
// ============================================================================

/**
 * Clean response text by removing markdown formatting
 */
export function cleanResponse(text: string): string {
  let cleaned = text;

  // Remove markdown headers
  cleaned = cleaned.replace(/^#{1,6}\s*/gm, '');

  // Remove bold/italic markers
  cleaned = cleaned.replace(/\*\*(.+?)\*\*/g, '$1');
  cleaned = cleaned.replace(/\*(.+?)\*/g, '$1');
  cleaned = cleaned.replace(/__(.+?)__/g, '$1');
  cleaned = cleaned.replace(/_(.+?)_/g, '$1');

  // Remove bullet points
  cleaned = cleaned.replace(/^\s*[-*]\s*/gm, '');

  // Remove numbered lists
  cleaned = cleaned.replace(/^\s*\d+\.\s*/gm, '');

  // Remove code blocks
  cleaned = cleaned.replace(/```[\s\S]*?```/g, '');

  // Remove inline code
  cleaned = cleaned.replace(/`([^`]+)`/g, '$1');

  // Normalize whitespace
  cleaned = cleaned.replace(/\n{2,}/g, '\n');
  cleaned = cleaned.replace(/ {2,}/g, ' ');

  return cleaned.trim();
}

/**
 * Analyze sentiment of text
 */
export function analyzeSentiment(text: string): 'positive' | 'neutral' | 'negative' {
  const lower = text.toLowerCase();

  let positiveScore = 0;
  let negativeScore = 0;

  for (const word of POSITIVE_INDICATORS) {
    const regex = new RegExp(`\\b${word}\\b`, 'gi');
    const matches = lower.match(regex);
    if (matches) positiveScore += matches.length;
  }

  for (const word of NEGATIVE_INDICATORS) {
    const regex = new RegExp(`\\b${word}\\b`, 'gi');
    const matches = lower.match(regex);
    if (matches) negativeScore += matches.length;
  }

  if (positiveScore > negativeScore * 1.5) return 'positive';
  if (negativeScore > positiveScore * 1.5) return 'negative';
  return 'neutral';
}

/**
 * Analyze sentiment of a short snippet
 */
function analyzeSnippetSentiment(snippet: string): 'positive' | 'neutral' | 'negative' {
  const lower = snippet.toLowerCase();

  let positiveScore = 0;
  let negativeScore = 0;

  for (const word of POSITIVE_INDICATORS) {
    if (lower.includes(word)) positiveScore++;
  }

  for (const word of NEGATIVE_INDICATORS) {
    if (lower.includes(word)) negativeScore++;
  }

  if (positiveScore > negativeScore) return 'positive';
  if (negativeScore > positiveScore) return 'negative';
  return 'neutral';
}

/**
 * Generate brand name variations for comprehensive detection
 */
function generateBrandVariations(brandName: string): string[] {
  const variations = new Set<string>();
  const normalized = brandName.trim();

  if (!normalized) return [];

  variations.add(normalized);

  // Split by separators
  const words = normalized.split(/[\s\-_&]+/).filter((w) => w.length > 0);
  for (const word of words) {
    if (word.length >= 2) {
      variations.add(word);
    }
  }

  // Common abbreviation expansions
  const abbreviationMap: Record<string, string[]> = {
    vw: ['volkswagen', 'volkswagen group', 'vw group'],
    volkswagen: ['vw', 'vw group', 'volkswagen group'],
    bmw: ['bayerische motoren werke'],
    gm: ['general motors'],
    hp: ['hewlett packard', 'hewlett-packard'],
    ibm: ['international business machines'],
    ge: ['general electric'],
  };

  for (const word of words) {
    const lowerWord = word.toLowerCase();
    if (abbreviationMap[lowerWord]) {
      for (const expansion of abbreviationMap[lowerWord]) {
        variations.add(expansion);
      }
    }
  }

  // Handle suffixes
  const suffixPatterns = [
    / group$/i, / corp$/i, / inc$/i, / ltd$/i, / llc$/i,
    / sa$/i, / ag$/i, / gmbh$/i,
  ];

  for (const pattern of suffixPatterns) {
    if (pattern.test(normalized)) {
      const withoutSuffix = normalized.replace(pattern, '').trim();
      if (withoutSuffix.length >= 2) {
        variations.add(withoutSuffix);
      }
    }
  }

  return Array.from(variations).filter((v) => v.length >= 2);
}

/**
 * Extract brand mentions with context
 */
export function extractBrandMentions(
  response: string,
  brandName: string,
): BrandMentionContext[] {
  if (!brandName || !response) return [];

  const contexts: BrandMentionContext[] = [];
  const snippetRadius = 80;
  const foundPositions = new Set<number>();

  const variations = generateBrandVariations(brandName);

  for (const variation of variations) {
    const escaped = variation.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`\\b${escaped}\\b`, 'gi');

    let match: RegExpExecArray | null;
    while ((match = regex.exec(response)) !== null) {
      const position = match.index;

      // Skip nearby duplicates
      let isDuplicate = false;
      for (const existingPos of foundPositions) {
        if (Math.abs(existingPos - position) < 10) {
          isDuplicate = true;
          break;
        }
      }

      if (isDuplicate) continue;
      foundPositions.add(position);

      // Extract snippet
      const matchLength = match[0].length;
      const start = Math.max(0, position - snippetRadius);
      const end = Math.min(response.length, position + matchLength + snippetRadius);

      let snippet = response.substring(start, end).trim();
      if (start > 0) snippet = '...' + snippet;
      if (end < response.length) snippet = snippet + '...';

      const sentiment = analyzeSnippetSentiment(snippet);

      contexts.push({ position, snippet, sentiment });
    }
  }

  return contexts.sort((a, b) => a.position - b.position);
}

/**
 * Extract key points from a response using simple NLP
 * (No AI call - pure algorithmic extraction for open-source version)
 */
export function extractKeyPoints(response: string): string[] {
  // Split into sentences
  const sentences = response
    .split(/[.!?]+/)
    .map((s) => s.trim())
    .filter((s) => s.length > 20 && s.length < 300);

  // Score sentences by importance indicators
  const scored = sentences.map((sentence) => {
    let score = 0;
    const lower = sentence.toLowerCase();

    // Important phrases
    if (lower.includes('important')) score += 2;
    if (lower.includes('key')) score += 2;
    if (lower.includes('critical')) score += 2;
    if (lower.includes('essential')) score += 2;
    if (lower.includes('recommend')) score += 3;
    if (lower.includes('should')) score += 1;
    if (lower.includes('must')) score += 2;
    if (lower.includes('benefit')) score += 1;
    if (lower.includes('advantage')) score += 1;
    if (lower.includes('best')) score += 2;
    if (lower.includes('leading')) score += 2;
    if (lower.includes('top')) score += 1;
    if (/\d+%/.test(sentence)) score += 2; // Contains percentages
    if (/\$[\d,]+/.test(sentence)) score += 2; // Contains money

    return { sentence, score };
  });

  // Sort by score and take top 10
  return scored
    .sort((a, b) => b.score - a.score)
    .slice(0, 10)
    .map((item) => item.sentence);
}

/**
 * Normalize a key point for comparison (preserves international characters)
 */
function normalizeKeyPoint(keyPoint: string): string {
  return keyPoint
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s-]/gu, '')
    .replace(/\s+/g, ' ')
    .trim();
}

/**
 * Get significant words from text (excluding stop words)
 */
function getSignificantWords(text: string): Set<string> {
  return new Set(
    text
      .split(' ')
      .map((w) => w.toLowerCase())
      .filter((w) => w.length > 2 && !STOP_WORDS.has(w)),
  );
}

/**
 * Check if two words share a common stem
 */
function shareWordStem(a: string, b: string): boolean {
  const minLen = Math.min(a.length, b.length);
  if (minLen < 5) return false;

  const prefixLen = Math.min(5, Math.floor(minLen * 0.6));
  return a.substring(0, prefixLen) === b.substring(0, prefixLen);
}

/**
 * Check if two words are synonyms
 */
function areSynonyms(a: string, b: string): boolean {
  for (const group of SYNONYM_GROUPS) {
    if (group.includes(a) && group.includes(b)) {
      return true;
    }
  }
  return false;
}

/**
 * Check if two key points are semantically similar
 */
function areSimilarKeyPoints(a: string, b: string): boolean {
  const wordsA = getSignificantWords(a);
  const wordsB = getSignificantWords(b);

  if (wordsA.size === 0 || wordsB.size === 0) return false;

  let directOverlap = 0;
  for (const word of wordsA) {
    if (wordsB.has(word)) directOverlap++;
  }

  let stemOverlap = 0;
  for (const wordA of wordsA) {
    for (const wordB of wordsB) {
      if (wordA !== wordB && shareWordStem(wordA, wordB)) {
        stemOverlap++;
        break;
      }
    }
  }

  let conceptOverlap = 0;
  for (const wordA of wordsA) {
    for (const wordB of wordsB) {
      if (wordA !== wordB && areSynonyms(wordA, wordB)) {
        conceptOverlap++;
        break;
      }
    }
  }

  const totalOverlap = directOverlap + stemOverlap * 0.8 + conceptOverlap * 0.7;
  const minWords = Math.min(wordsA.size, wordsB.size);
  const similarity = totalOverlap / minWords;

  return similarity >= 0.3;
}

// ============================================================================
// Statistical Functions
// ============================================================================

/**
 * Estimate token count for a text string.
 * Uses approximation of ~4 characters per token for English text.
 * This is a rough estimate - actual tokenization varies by model.
 *
 * @param text - The text to estimate tokens for
 * @returns Estimated token count
 */
export function estimateTokenCount(text: string): number {
  if (!text) return 0;
  // Approximation: ~4 characters per token for English
  // This accounts for spaces, punctuation, and common word lengths
  return Math.ceil(text.length / 4);
}

/**
 * Calculate mean of an array
 */
function calculateMean(values: number[]): number {
  if (values.length === 0) return 0;
  return values.reduce((a, b) => a + b, 0) / values.length;
}

/**
 * Calculate variance of an array
 */
function calculateVariance(values: number[]): number {
  if (values.length === 0) return 0;
  const mean = calculateMean(values);
  return values.reduce((sum, v) => sum + Math.pow(v - mean, 2), 0) / values.length;
}

/**
 * Calculate standard deviation of an array
 */
function calculateStdDev(values: number[]): number {
  return Math.sqrt(calculateVariance(values));
}

/**
 * Calculate Jaccard similarity between two sets of strings
 */
export function calculateJaccardSimilarity(a: string[], b: string[]): number {
  const setA = new Set(a.map((s) => s.toLowerCase()));
  const setB = new Set(b.map((s) => s.toLowerCase()));

  if (setA.size === 0 && setB.size === 0) return 1;
  if (setA.size === 0 || setB.size === 0) return 0;

  const intersection = new Set([...setA].filter((x) => setB.has(x)));
  const union = new Set([...setA, ...setB]);

  return intersection.size / union.size;
}

/**
 * Calculate word-based semantic overlap between two texts
 */
export function calculateSemanticOverlap(text1: string, text2: string): number {
  const words1 = getSignificantWords(text1);
  const words2 = getSignificantWords(text2);

  if (words1.size === 0 || words2.size === 0) return 0;

  const intersection = new Set([...words1].filter((w) => words2.has(w)));
  const union = new Set([...words1, ...words2]);

  return Math.round((intersection.size / union.size) * 100);
}

/**
 * Calculate average pairwise overlap between multiple responses
 */
function calculateAverageOverlap(responses: ResponseData[]): number {
  if (responses.length < 2) return 100;

  let totalOverlap = 0;
  let comparisons = 0;

  for (let i = 0; i < responses.length; i++) {
    for (let j = i + 1; j < responses.length; j++) {
      totalOverlap += calculateSemanticOverlap(
        responses[i].content,
        responses[j].content,
      );
      comparisons++;
    }
  }

  return comparisons > 0 ? Math.round(totalOverlap / comparisons) : 0;
}

// ============================================================================
// Analysis Functions
// ============================================================================

/**
 * Classify key points into stable, variable, and outlier categories
 * Uses Union-Find clustering approach from Python implementation
 */
function classifyKeyMessages(
  responses: ResponseData[],
): {
  coreStableMessages: string[];
  variableMessages: VariableMessage[];
  outliers: string[];
  keyPointFrequency: Record<string, number>;
} {
  const totalIterations = responses.length;

  // Count key point frequency with similarity matching
  const keyPointFrequency = new Map<string, Set<number>>();

  for (let i = 0; i < responses.length; i++) {
    for (const keyPoint of responses[i].keyPoints) {
      const normalized = normalizeKeyPoint(keyPoint);

      let foundMatch = false;
      for (const [existing, iterations] of keyPointFrequency) {
        if (areSimilarKeyPoints(normalized, existing)) {
          iterations.add(i + 1);
          foundMatch = true;
          break;
        }
      }

      if (!foundMatch) {
        keyPointFrequency.set(normalized, new Set([i + 1]));
      }
    }
  }

  const coreStableMessages: string[] = [];
  const variableMessages: VariableMessage[] = [];
  const outliers: string[] = [];
  const frequencyRecord: Record<string, number> = {};

  for (const [keyPoint, iterations] of keyPointFrequency) {
    const count = iterations.size;
    const frequency = count / totalIterations;
    frequencyRecord[keyPoint] = count;

    if (frequency >= CORE_MESSAGE_THRESHOLD) {
      coreStableMessages.push(keyPoint);
    } else if (frequency >= VARIABLE_MESSAGE_THRESHOLD) {
      variableMessages.push({
        message: keyPoint,
        frequency: Math.round(frequency * 100),
        appearancePattern: Array.from(iterations).sort((a, b) => a - b),
      });
    } else {
      outliers.push(keyPoint);
    }
  }

  return {
    coreStableMessages,
    variableMessages,
    outliers,
    keyPointFrequency: frequencyRecord,
  };
}

/**
 * Calculate brand mention statistics
 */
function calculateBrandMentionStats(responses: ResponseData[]): BrandMentionStats {
  const mentions = responses.map((r) => r.brandMentions);
  const allContexts = responses.flatMap((r) => r.brandMentionContexts || []);

  if (mentions.length === 0) {
    return {
      total: 0,
      min: 0,
      max: 0,
      average: 0,
      variance: 0,
      standardDeviation: 0,
      allContexts: [],
    };
  }

  const total = mentions.reduce((a, b) => a + b, 0);
  const min = Math.min(...mentions);
  const max = Math.max(...mentions);
  const average = calculateMean(mentions);
  const variance = calculateVariance(mentions);
  const standardDeviation = calculateStdDev(mentions);

  return {
    total,
    min,
    max,
    average: Math.round(average * 100) / 100,
    variance: Math.round(variance * 100) / 100,
    standardDeviation: Math.round(standardDeviation * 100) / 100,
    allContexts,
  };
}

/**
 * Calculate sentiment distribution
 */
function calculateSentimentDistribution(
  responses: ResponseData[],
): SentimentDistribution {
  const total = responses.length;
  if (total === 0) {
    return { positive: 0, neutral: 0, negative: 0 };
  }

  const counts = responses.reduce(
    (acc, r) => {
      acc[r.sentiment]++;
      return acc;
    },
    { positive: 0, neutral: 0, negative: 0 },
  );

  return {
    positive: Math.round((counts.positive / total) * 100),
    neutral: Math.round((counts.neutral / total) * 100),
    negative: Math.round((counts.negative / total) * 100),
  };
}

/**
 * Calculate overall confidence score
 */
function calculateConfidenceScore(
  semanticOverlap: number,
  brandStats: BrandMentionStats,
  coreMessagesCount: number,
): number {
  // Weighted scoring:
  // - 40% from semantic overlap
  // - 30% from brand mention consistency (low variance = high score)
  // - 30% from having core messages

  const overlapScore = semanticOverlap;

  const maxVariance = 5;
  const varianceScore = Math.max(0, 100 - (brandStats.variance / maxVariance) * 100);

  const coreScore = Math.min(100, coreMessagesCount * 20);

  const confidence = Math.round(
    overlapScore * 0.4 + varianceScore * 0.3 + coreScore * 0.3,
  );

  return Math.min(100, Math.max(0, confidence));
}

/**
 * Generate recommendations based on analysis
 */
function generateRecommendations(
  analysis: {
    coreStableMessages: string[];
    variableMessages: VariableMessage[];
    outliers: string[];
  },
  brandStats: BrandMentionStats,
  sentimentDistribution: SentimentDistribution,
  brandName?: string,
): {
  messagesToAdd: string[];
  messagesToReinforce: string[];
  opportunityGaps: string[];
} {
  const messagesToReinforce: string[] = [];
  const messagesToAdd: string[] = [];
  const opportunityGaps: string[] = [];

  // Core messages should be reinforced
  for (const message of analysis.coreStableMessages) {
    messagesToReinforce.push(
      `Reinforce: "${message}" - This appears consistently across AI responses`,
    );
  }

  // Variable messages need attention
  for (const vm of analysis.variableMessages) {
    messagesToAdd.push(
      `Strengthen: "${vm.message}" - Appears ${vm.frequency}% of the time, could be more consistent`,
    );
  }

  // Outliers represent opportunities
  for (const message of analysis.outliers.slice(0, 5)) {
    opportunityGaps.push(
      `Opportunity: "${message}" - Unique insight that competitors may be missing`,
    );
  }

  // Brand mention recommendations
  if (brandName && brandStats.average < 1) {
    messagesToAdd.push(
      `Low brand visibility: ${brandName} is mentioned less than once on average. Strengthen brand positioning.`,
    );
  }

  if (brandStats.variance > 2) {
    messagesToAdd.push(
      `Inconsistent brand mentions: High variance (${brandStats.variance.toFixed(1)}) suggests unpredictable AI perception.`,
    );
  }

  // Sentiment recommendations
  if (sentimentDistribution.negative > 20) {
    messagesToAdd.push(
      `Negative sentiment detected in ${sentimentDistribution.negative}% of responses. Review content for reputation issues.`,
    );
  }

  return {
    messagesToAdd,
    messagesToReinforce,
    opportunityGaps,
  };
}

// ============================================================================
// Main Entry Point
// ============================================================================

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
 *   brandName: 'Salesforce',
 * });
 *
 * console.log(`Consistency: ${result.consistencyScore}%`);
 * console.log('Always mentioned:', result.analysis.coreStableMessages);
 * ```
 */
export async function analyzeStability(
  options: StabilityOptions,
): Promise<StabilityResult> {
  const {
    prompt,
    iterations = 5,
    model = 'gemini',
    apiKey,
    temperature = 0.7,
    maxTokens = 2048,
    brandName,
    iterationDelayMs = 1000,
    searchMode = 'memory',
    onProgress,
    onError,
  } = options;

  if (!apiKey) {
    throw new Error('API key is required');
  }

  if (iterations < 1 || iterations > 10) {
    throw new Error('Iterations must be between 1 and 10');
  }

  const startTime = Date.now();
  const responses: ResponseData[] = [];

  // Run iterations
  for (let i = 1; i <= iterations; i++) {
    try {
      let result: QueryResult;

      if (model === 'gemini') {
        result = await queryGemini(prompt, apiKey, temperature, maxTokens, searchMode);
      } else {
        result = await queryOpenAI(prompt, apiKey, temperature, maxTokens, model, searchMode);
      }

      const cleanedResponse = cleanResponse(result.response);
      const keyPoints = extractKeyPoints(cleanedResponse);
      const sentiment = analyzeSentiment(cleanedResponse);
      const brandMentionContexts = brandName
        ? extractBrandMentions(cleanedResponse, brandName)
        : [];

      responses.push({
        iteration: i,
        content: result.response,
        length: result.response.length,
        estimatedTokens: estimateTokenCount(result.response),
        brandMentions: brandMentionContexts.length,
        brandMentionContexts,
        keyPoints,
        sentiment,
        latencyMs: result.latencyMs,
        timestamp: new Date().toISOString(),
        searchMode,
        citations: result.citations,
      });

      if (onProgress) {
        onProgress(i, iterations);
      }

      // Delay between iterations (except last)
      if (i < iterations) {
        await new Promise((resolve) => setTimeout(resolve, iterationDelayMs));
      }
    } catch (error) {
      const iterationError: IterationError = {
        iteration: i,
        message: error instanceof Error ? error.message : 'Unknown error',
        error: error instanceof Error ? error : new Error(String(error)),
      };

      if (onError) {
        onError(iterationError);
      } else {
        console.error(`Error in iteration ${i}:`, error);
      }
      // Continue with remaining iterations
    }
  }

  if (responses.length === 0) {
    throw new Error('All iterations failed - unable to complete analysis');
  }

  // Analyze responses
  const semanticOverlap = calculateAverageOverlap(responses);
  const classification = classifyKeyMessages(responses);
  const brandStats = calculateBrandMentionStats(responses);
  const sentimentDist = calculateSentimentDistribution(responses);
  const confidenceScore = calculateConfidenceScore(
    semanticOverlap,
    brandStats,
    classification.coreStableMessages.length,
  );
  const recommendations = generateRecommendations(
    classification,
    brandStats,
    sentimentDist,
    brandName,
  );

  const executionTimeMs = Date.now() - startTime;

  return {
    consistencyScore: confidenceScore,
    semanticOverlap,
    responses,
    analysis: {
      coreStableMessages: classification.coreStableMessages,
      variableMessages: classification.variableMessages,
      outliers: classification.outliers,
      keyPointFrequency: classification.keyPointFrequency,
    },
    brandMentions: brandStats,
    sentimentDistribution: sentimentDist,
    recommendations,
    metadata: {
      prompt,
      model,
      iterations: responses.length,
      executionTimeMs,
      brandName,
      searchMode,
    },
  };
}

// ============================================================================
// Cross-Model Statistical Functions
// ============================================================================

/**
 * Calculate Shannon entropy for brand distribution
 * Higher entropy = more diverse recommendations
 * Lower entropy = more stereotyped (few dominant brands)
 */
export function calculateShannonEntropy(brandCounts: number[]): number {
  const total = brandCounts.reduce((a, b) => a + b, 0);
  if (total === 0) return 0;

  let entropy = 0;
  for (const count of brandCounts) {
    if (count > 0) {
      const probability = count / total;
      entropy -= probability * Math.log2(probability);
    }
  }

  return Math.round(entropy * 1000) / 1000;
}

/**
 * Calculate normalized Shannon entropy (0-1 scale)
 */
export function calculateNormalizedEntropy(
  brandCounts: number[],
): { entropy: number; normalized: number } {
  const entropy = calculateShannonEntropy(brandCounts);
  const uniqueBrands = brandCounts.filter((c) => c > 0).length;

  if (uniqueBrands <= 1) {
    return { entropy, normalized: 0 };
  }

  const maxEntropy = Math.log2(uniqueBrands);
  const normalized = maxEntropy > 0 ? entropy / maxEntropy : 0;

  return {
    entropy,
    normalized: Math.round(normalized * 1000) / 1000,
  };
}

/**
 * Calculate Gini coefficient for brand concentration
 * 0 = perfect equality (all brands mentioned equally)
 * 1 = perfect inequality (one brand dominates)
 */
export function calculateGiniCoefficient(values: number[]): number {
  const sorted = [...values].sort((a, b) => a - b);
  const n = sorted.length;

  if (n === 0) return 0;

  const sum = sorted.reduce((a, b) => a + b, 0);
  if (sum === 0) return 0;

  let cumulativeSum = 0;
  let giniSum = 0;

  for (let i = 0; i < n; i++) {
    cumulativeSum += sorted[i];
    giniSum += (2 * (i + 1) - n - 1) * sorted[i];
  }

  const gini = giniSum / (n * sum);
  return Math.round(Math.max(0, Math.min(1, gini)) * 1000) / 1000;
}

/**
 * Extract all brand names from responses using NER-like pattern matching
 */
function extractBrandsFromResponses(responses: ResponseData[]): Map<string, number> {
  const brandCounts = new Map<string, number>();

  // Common brand patterns (capitalized words, often with TM indicators)
  const brandPatterns = [
    // Technology brands
    /\b(Google|Microsoft|Apple|Amazon|Meta|Facebook|Tesla|Netflix|Spotify|Adobe|Salesforce|Oracle|IBM|Intel|AMD|Nvidia|Samsung|Sony|LG|Huawei|Xiaomi)\b/gi,
    // E-commerce
    /\b(Shopify|WooCommerce|Magento|BigCommerce|Etsy|eBay|Alibaba|Walmart|Target|Best Buy)\b/gi,
    // CRM/Marketing
    /\b(HubSpot|Mailchimp|Marketo|Pardot|ActiveCampaign|Klaviyo|Braze|Intercom|Zendesk|Freshdesk)\b/gi,
    // Analytics
    /\b(Tableau|Power BI|Looker|Mixpanel|Amplitude|Heap|Segment|Snowflake|Databricks)\b/gi,
    // Cloud
    /\b(AWS|Azure|GCP|Google Cloud|Cloudflare|DigitalOcean|Heroku|Vercel|Netlify)\b/gi,
    // Finance
    /\b(Stripe|PayPal|Square|Adyen|Braintree|Plaid|Wise|Revolut)\b/gi,
    // HR/Productivity
    /\b(Slack|Teams|Zoom|Notion|Asana|Monday|Trello|Jira|Confluence|Figma|Miro)\b/gi,
    // General capitalized brand-like patterns
    /\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?(?:\s+(?:Inc|Corp|Ltd|LLC|Co)\.?)?)\b/g,
  ];

  for (const response of responses) {
    const content = response.content;
    const foundBrands = new Set<string>();

    for (const pattern of brandPatterns) {
      const matches = content.matchAll(pattern);
      for (const match of matches) {
        const brand = match[1] || match[0];
        // Normalize brand name
        const normalized = brand.trim().replace(/\s+(Inc|Corp|Ltd|LLC|Co)\.?$/i, '');
        if (normalized.length >= 2 && !STOP_WORDS.has(normalized.toLowerCase())) {
          foundBrands.add(normalized);
        }
      }
    }

    for (const brand of foundBrands) {
      brandCounts.set(brand, (brandCounts.get(brand) || 0) + 1);
    }
  }

  return brandCounts;
}

/**
 * Calculate cross-model overlap using Jaccard index
 */
function calculateCrossModelOverlapStats(
  modelResults: ModelExperimentResult[],
): CrossModelOverlap[] {
  const overlaps: CrossModelOverlap[] = [];

  for (let i = 0; i < modelResults.length; i++) {
    for (let j = i + 1; j < modelResults.length; j++) {
      const modelA = modelResults[i];
      const modelB = modelResults[j];

      const setA = new Set(modelA.uniqueBrands.map((b) => b.toLowerCase()));
      const setB = new Set(modelB.uniqueBrands.map((b) => b.toLowerCase()));

      const intersection = new Set([...setA].filter((x) => setB.has(x)));
      const union = new Set([...setA, ...setB]);

      const sharedBrandNames = [...intersection].map((b) => {
        // Find original casing
        return (
          modelA.uniqueBrands.find((x) => x.toLowerCase() === b) ||
          modelB.uniqueBrands.find((x) => x.toLowerCase() === b) ||
          b
        );
      });

      overlaps.push({
        modelA: modelA.model,
        modelB: modelB.model,
        sharedBrands: intersection.size,
        sharedBrandNames,
        jaccardIndex:
          union.size > 0
            ? Math.round((intersection.size / union.size) * 1000) / 1000
            : 0,
      });
    }
  }

  return overlaps;
}

/**
 * Find messages that appear across all models
 */
function findUniversalMessages(
  modelResults: ModelExperimentResult[],
): {
  universalCore: string[];
  crossModelVariable: Array<{
    message: string;
    appearsInModels: string[];
    frequency: number;
  }>;
} {
  if (modelResults.length === 0) {
    return { universalCore: [], crossModelVariable: [] };
  }

  // Collect all core messages from all models
  const messageModelMap = new Map<string, Set<string>>();

  for (const mr of modelResults) {
    for (const message of mr.result.analysis.coreStableMessages) {
      const normalized = message.toLowerCase().trim();

      // Find similar existing messages
      let foundSimilar = false;
      for (const [existing, models] of messageModelMap) {
        if (areSimilarKeyPoints(normalized, existing)) {
          models.add(mr.model);
          foundSimilar = true;
          break;
        }
      }

      if (!foundSimilar) {
        messageModelMap.set(normalized, new Set([mr.model]));
      }
    }
  }

  const totalModels = modelResults.length;
  const universalCore: string[] = [];
  const crossModelVariable: Array<{
    message: string;
    appearsInModels: string[];
    frequency: number;
  }> = [];

  for (const [message, models] of messageModelMap) {
    const frequency = models.size / totalModels;

    if (models.size === totalModels) {
      universalCore.push(message);
    } else if (models.size > 1) {
      crossModelVariable.push({
        message,
        appearsInModels: Array.from(models),
        frequency: Math.round(frequency * 100),
      });
    }
  }

  // Sort by frequency
  crossModelVariable.sort((a, b) => b.frequency - a.frequency);

  return { universalCore, crossModelVariable };
}

/**
 * Find brands mentioned by all models
 */
function findUniversalBrands(modelResults: ModelExperimentResult[]): string[] {
  if (modelResults.length === 0) return [];

  // Start with first model's brands
  let commonBrands = new Set(
    modelResults[0].uniqueBrands.map((b) => b.toLowerCase()),
  );

  // Intersect with other models
  for (let i = 1; i < modelResults.length; i++) {
    const modelBrands = new Set(
      modelResults[i].uniqueBrands.map((b) => b.toLowerCase()),
    );
    commonBrands = new Set([...commonBrands].filter((b) => modelBrands.has(b)));
  }

  // Return with original casing from first model
  return [...commonBrands].map((b) => {
    for (const mr of modelResults) {
      const found = mr.uniqueBrands.find((x) => x.toLowerCase() === b);
      if (found) return found;
    }
    return b;
  });
}

/**
 * Generate cross-model recommendations
 */
function generateExperimentRecommendations(
  modelResults: ModelExperimentResult[],
  universalMessages: string[],
  crossModelVariable: Array<{ message: string; appearsInModels: string[] }>,
  universalBrands: string[],
  brandName?: string,
): ExperimentResult['recommendations'] {
  const universallyReinforced: string[] = [];
  const differentiationOpportunities: string[] = [];
  const universalGaps: string[] = [];

  // Universal messages are strongly reinforced
  for (const message of universalMessages) {
    universallyReinforced.push(
      `All models agree: "${message}" - This is a core message across all AI systems`,
    );
  }

  // Messages appearing in some models are differentiation opportunities
  for (const vm of crossModelVariable.slice(0, 5)) {
    differentiationOpportunities.push(
      `Partial coverage: "${vm.message}" - Only mentioned by ${vm.appearsInModels.join(', ')}`,
    );
  }

  // Check if brand is universally mentioned
  if (brandName) {
    const brandLower = brandName.toLowerCase();
    const isUniversal = universalBrands.some((b) => b.toLowerCase() === brandLower);

    if (isUniversal) {
      universallyReinforced.push(
        `${brandName} is mentioned by ALL models - strong cross-model visibility`,
      );
    } else {
      // Check which models mention it
      const mentioningModels = modelResults
        .filter((mr) =>
          mr.uniqueBrands.some((b) => b.toLowerCase() === brandLower),
        )
        .map((mr) => mr.model);

      if (mentioningModels.length > 0) {
        differentiationOpportunities.push(
          `${brandName} only mentioned by: ${mentioningModels.join(', ')} - opportunity for broader visibility`,
        );
      } else {
        universalGaps.push(
          `${brandName} not mentioned by any model - critical visibility gap`,
        );
      }
    }
  }

  // Check for low consistency across models
  const avgConsistency =
    modelResults.reduce((sum, mr) => sum + mr.result.consistencyScore, 0) /
    modelResults.length;

  if (avgConsistency < 50) {
    universalGaps.push(
      `Low average consistency (${Math.round(avgConsistency)}%) across models - AI perception is highly variable`,
    );
  }

  return {
    universallyReinforced,
    differentiationOpportunities,
    universalGaps,
  };
}

// ============================================================================
// Experiment Mode Entry Point
// ============================================================================

/**
 * Run a cross-model experiment analyzing AI response stability across multiple LLMs
 *
 * @param options - Experiment configuration with API keys for multiple providers
 * @returns Promise resolving to comprehensive cross-model analysis
 *
 * @example
 * ```typescript
 * const result = await runExperiment({
 *   prompt: 'What are the best CRM tools for small businesses?',
 *   apiKeys: {
 *     geminiApiKey: process.env.GEMINI_API_KEY,
 *     openaiApiKey: process.env.OPENAI_API_KEY,
 *     grokApiKey: process.env.GROK_API_KEY,
 *   },
 *   iterations: 5,
 *   brandName: 'Salesforce',
 * });
 *
 * console.log('Universal messages:', result.universalCoreMessages);
 * console.log('Cross-model overlap:', result.crossModelOverlap);
 * console.log('Shannon entropy:', result.statistics.shannonEntropy);
 * ```
 */
export async function runExperiment(
  options: ExperimentOptions,
): Promise<ExperimentResult> {
  const {
    prompt,
    apiKeys,
    iterations = 5,
    temperature = 0.7,
    maxTokens = 2048,
    brandName,
    iterationDelayMs = 1000,
    searchMode = 'memory',
    onProgress,
  } = options;

  const startTime = Date.now();
  const modelResults: ModelExperimentResult[] = [];
  const modelsToRun: Array<{ model: 'gemini' | 'openai' | 'grok'; apiKey: string }> = [];

  // Determine which models to run based on provided API keys
  if (apiKeys.geminiApiKey) {
    modelsToRun.push({ model: 'gemini', apiKey: apiKeys.geminiApiKey });
  }
  if (apiKeys.openaiApiKey) {
    modelsToRun.push({ model: 'openai', apiKey: apiKeys.openaiApiKey });
  }
  if (apiKeys.grokApiKey) {
    modelsToRun.push({ model: 'grok', apiKey: apiKeys.grokApiKey });
  }

  if (modelsToRun.length === 0) {
    throw new Error('At least one API key must be provided');
  }

  // Run analysis for each model
  for (const { model, apiKey } of modelsToRun) {
    try {
      const result = await analyzeStability({
        prompt,
        iterations,
        model,
        apiKey,
        temperature,
        maxTokens,
        brandName,
        iterationDelayMs,
        searchMode,
        onProgress: onProgress
          ? (iteration, total) => onProgress(model, iteration, total)
          : undefined,
      });

      // Extract brands from responses
      const brandCounts = extractBrandsFromResponses(result.responses);
      const uniqueBrands = Array.from(brandCounts.keys());

      // Calculate brand frequencies
      const totalMentions = Array.from(brandCounts.values()).reduce((a, b) => a + b, 0);
      const brandFrequencies: BrandFrequency[] = Array.from(brandCounts.entries())
        .map(([brand, count]) => ({
          brand,
          count,
          percentage: totalMentions > 0 ? Math.round((count / totalMentions) * 100) : 0,
        }))
        .sort((a, b) => b.count - a.count);

      modelResults.push({
        model,
        result,
        uniqueBrands,
        brandFrequencies,
      });
    } catch (error) {
      console.error(`Error running ${model} analysis:`, error);
      // Continue with other models
    }
  }

  if (modelResults.length === 0) {
    throw new Error('All model analyses failed');
  }

  // Cross-model analysis
  const crossModelOverlap = calculateCrossModelOverlapStats(modelResults);
  const { universalCore, crossModelVariable } = findUniversalMessages(modelResults);
  const universalBrands = findUniversalBrands(modelResults);

  // Calculate Shannon entropy for each model
  const shannonEntropy: EntropyResult[] = modelResults.map((mr) => {
    const counts = mr.brandFrequencies.map((bf) => bf.count);
    const { entropy, normalized } = calculateNormalizedEntropy(counts);

    let interpretation: 'stereotyped' | 'moderate' | 'diverse';
    if (normalized < 0.5) interpretation = 'stereotyped';
    else if (normalized < 0.8) interpretation = 'moderate';
    else interpretation = 'diverse';

    return {
      model: mr.model,
      entropy,
      normalizedEntropy: normalized,
      interpretation,
    };
  });

  // Calculate Gini coefficient for each model
  const giniCoefficients: GiniResult[] = modelResults.map((mr) => {
    const counts = mr.brandFrequencies.map((bf) => bf.count);
    const gini = calculateGiniCoefficient(counts);

    let interpretation: 'concentrated' | 'moderate' | 'distributed';
    if (gini > 0.6) interpretation = 'concentrated';
    else if (gini > 0.3) interpretation = 'moderate';
    else interpretation = 'distributed';

    return {
      model: mr.model,
      giniCoefficient: gini,
      interpretation,
    };
  });

  // Response length statistics
  const responseLengthStats = modelResults.map((mr) => {
    const lengths = mr.result.responses.map((r) => r.length);
    return {
      model: mr.model,
      avgLength: Math.round(calculateMean(lengths)),
      minLength: Math.min(...lengths),
      maxLength: Math.max(...lengths),
      stdDev: Math.round(calculateStdDev(lengths)),
    };
  });

  // Average consistency across models
  const averageConsistency = Math.round(
    modelResults.reduce((sum, mr) => sum + mr.result.consistencyScore, 0) /
      modelResults.length,
  );

  // Cross-model semantic overlap (average of all pairwise Jaccard indices)
  const crossModelSemanticOverlap =
    crossModelOverlap.length > 0
      ? Math.round(
          (crossModelOverlap.reduce((sum, co) => sum + co.jaccardIndex, 0) /
            crossModelOverlap.length) *
            100,
        )
      : 0;

  // Generate recommendations
  const recommendations = generateExperimentRecommendations(
    modelResults,
    universalCore,
    crossModelVariable,
    universalBrands,
    brandName,
  );

  const executionTimeMs = Date.now() - startTime;

  return {
    modelResults,
    universalCoreMessages: universalCore,
    crossModelVariableMessages: crossModelVariable,
    crossModelOverlap,
    universalBrands,
    statistics: {
      shannonEntropy,
      giniCoefficients,
      averageConsistency,
      crossModelSemanticOverlap,
      responseLengthStats,
    },
    recommendations,
    metadata: {
      prompt,
      modelsUsed: modelResults.map((mr) => mr.model),
      iterationsPerModel: iterations,
      totalExecutionTimeMs: executionTimeMs,
      brandName,
      searchMode,
    },
  };
}

export default analyzeStability;
