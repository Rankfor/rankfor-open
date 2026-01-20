# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-20

### Added

- Initial release of @rankfor/brand-detector
- `analyzeLLMResponse()` method for analyzing AI/LLM responses
- Basic mode: brand mentions with counts
- Extended mode: brand mentions with surrounding context
- Brand database with 10,847 brands from Simple Icons and Wikidata
- Confidence scoring (high/medium/low)
- Multi-word brand support (up to 3 words)
- TypeScript type definitions
- Comprehensive test suite
- Full API documentation

### Features

- `isBrand()` - Check if text is a known brand
- `getConfidence()` - Get confidence level for a brand
- `analyzeLLMResponse()` - Analyze LLM responses (primary API)
- `detectBrands()` - Detect brands with positions
- `extractBrandNames()` - Extract unique brand names
- `countBrandMentions()` - Count brand mentions
- `getSuggestions()` - Get autocomplete suggestions
- `getMetadata()` - Get database metadata

### Database

- 10,847 total brands
- 3,245 high-confidence brands (Simple Icons)
- 8,732 brands from Wikidata
- CC0 licensed (public domain)
- Smart filtering for dictionary words

## [Unreleased]

### Planned

- Web API endpoint for cloud-based detection
- Real-time streaming support
- Batch processing API
- Custom brand database support
- Locale-specific brand detection
- Brand alias management
- Performance optimizations for large texts
