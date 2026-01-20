# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.0] - 2026-01-20

### Added

- **Multilingual Stop Word Filtering**: Dynamic language-aware brand extraction
  - `stopword` package integration supporting 50+ languages
  - `AnalysisConfig.language` - ISO 639-1 language code (en, pl, de, fr, es, it, nl, pt, ru, uk)
  - `getStopWords()` - Dynamic stop word generation (English + Target Language + User Custom)
  - Automatic filtering of capitalized sentence starters (German "Die", Polish "O", "W", etc.)
  - Zero-config multilingual support - just set the language code
- **Enhanced Business Jargon Filtering**: 80+ ignore terms
  - Expanded `IGNORED_TERMS` set for marketing/tech/AI jargon
  - Website UI terms (login, signup, dashboard, etc.)
  - Pricing/plan terminology (free, pro, enterprise, etc.)
  - Generic descriptors and sentence starters
- **Improved Brand Extraction**: Two-pass pattern matching
  - **Pass 1**: High-confidence known brands (Salesforce, HubSpot, etc.)
  - **Pass 2**: General capitalized patterns with strict filtering
  - Special case handling (e.g., "Teams" alone vs "Microsoft Teams")
  - Brand name normalization with case-insensitive deduplication
- **Language-Aware Cross-Model Experiments**: `runExperiment()` now respects language settings
  - Passes `AnalysisConfig.language` to brand extraction
  - Consistent multilingual filtering across all models

### Changed

- Brand extraction now requires minimum 3-character length (was 2) for safety
- `extractBrandsFromResponses()` signature updated to accept language and config
- Known brands pattern expanded with Rankfor.ai, SEO tools (Semrush, Ahrefs, Moz, etc.)

### Fixed

- Brand extraction no longer falsely detects German/Polish prepositions as brands
- Polish "W" (In), "Z" (With), "O" (About) properly filtered
- German "Die" (The), "Der" (The), "Das" (The) properly filtered
- Single-letter capitalized words no longer detected as brands

---

## [1.2.0] - 2026-01-20

### Added

- **Configuration Injection**: Customize analysis for different industries/languages
  - `AnalysisConfig` interface for stop words, synonyms, sentiment indicators
  - `customStopWords` - Override default English stop words
  - `customSynonyms` - Add industry-specific synonym groups
  - `customPositiveIndicators` / `customNegativeIndicators` - Extend sentiment detection
- **Error Callbacks**: Better error handling for production use
  - `onError` callback option for `analyzeStability()` and `runExperiment()`
  - `IterationError` type with iteration number, message, and error object
  - Errors no longer silently logged to console (unless no callback provided)
- **Token Estimation**: Response metadata now includes token count
  - `ResponseData.estimatedTokens` - Approximate token count (~4 chars/token)
  - `estimateTokenCount()` utility function exported for custom use
- **Build Improvements**: Proper npm package bundling
  - tsup for dual CJS/ESM output with sourcemaps
  - Minified production builds
  - Tree-shakeable exports

### Changed

- Package version bumped to 1.2.0
- Build system changed from tsc to tsup

---

## [1.1.0] - 2026-01-20

### Added

- **Search Mode**: Compare AI "memory" (training data) vs "search" (live web) responses
  - `searchMode: 'memory' | 'search'` option for `analyzeStability()` and `runExperiment()`
  - Gemini: Uses Google Search Grounding
  - OpenAI: Uses Web Search Tool via Responses API
  - Grok/xAI: Uses Agentic Search (web_search + x_search)
- **Citations Support**: When using search mode, responses include source URLs
  - New `SearchCitation` type with `url`, `title`, and optional `snippet`
  - `ResponseData.citations` populated in search mode
- **SearchMode Type**: Exported `SearchMode` type for TypeScript users

### Changed

- Updated model versions:
  - Gemini: `gemini-3-pro-preview`
  - OpenAI: `gpt-5.2` (memory), `gpt-5-search-preview` (search)
  - Grok: `grok-4`
- `StabilityResult.metadata` now includes `searchMode`
- `ExperimentResult.metadata` now includes `searchMode`

---

## [1.0.0] - 2026-01-19

### Added

- **Core Analysis Functions**
  - `analyzeStability()` - Single-model response stability analysis
  - `runExperiment()` - Cross-model experiment with statistical analysis
  - `cleanResponse()` - Markdown formatting removal
  - `analyzeSentiment()` - Positive/neutral/negative detection
  - `extractBrandMentions()` - Brand mention extraction with context
  - `extractKeyPoints()` - Key point extraction from responses

- **Statistical Functions**
  - `calculateShannonEntropy()` - Brand diversity measurement
  - `calculateNormalizedEntropy()` - Normalized entropy (0-1 scale)
  - `calculateGiniCoefficient()` - Concentration inequality measurement
  - `calculateJaccardSimilarity()` - Set-based similarity calculation
  - `calculateSemanticOverlap()` - Word-based text similarity

- **Multi-Model Support**
  - Google Gemini 3 Pro (`gemini-3-pro-preview`)
  - OpenAI GPT-5.2 (`gpt-5.2`)
  - xAI Grok 4 (`grok-4`)

- **Message Classification**
  - Core stable messages (80%+ appearance rate)
  - Variable messages (30-80% appearance rate)
  - Outliers (<30% appearance rate)

- **Cross-Model Analysis**
  - Universal core messages (appear in ALL models)
  - Cross-model variable messages with frequency tracking
  - Cross-model brand overlap with Jaccard index
  - Universal brands (mentioned by ALL models)

- **Statistical Analysis Output**
  - Shannon entropy per model with interpretation
  - Gini coefficient per model with interpretation
  - Response length statistics (avg, min, max, stdDev)
  - Average consistency across models
  - Cross-model semantic overlap percentage

- **Recommendations Engine**
  - Messages to reinforce (core stable)
  - Messages to add (low frequency)
  - Opportunity gaps (outliers)
  - Brand visibility recommendations
  - Cross-model differentiation opportunities

- **TypeScript Support**
  - Full type definitions for all interfaces
  - Strict mode compatible
  - ESM and CommonJS exports

### Documentation

- Comprehensive README with examples
- JSDoc comments on all exported functions
- API reference with parameter tables
- Use case examples (brand monitoring, content strategy, competitive intelligence)

### Testing

- 45 unit tests covering all core functionality
- Edge case handling (empty arrays, zeros, single elements)
- Statistical function accuracy tests

---

## [Unreleased]

### Planned

- CLI wrapper for command-line usage
- Additional LLM providers (Claude, Llama, Mistral)
- Streaming response support
- Response caching options
- Export to CSV/JSON formats
