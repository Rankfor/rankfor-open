# Contributing to Rankfor Open

Thank you for your interest in contributing to Rankfor Open. This document provides guidelines for contributions.

## Code of Conduct

Be respectful, inclusive, and constructive. We're building tools for the AI visibility community.

## How to Contribute

### Reporting Issues

1. Check existing issues first
2. Use the issue templates
3. Include reproduction steps for bugs
4. For security issues, email security@rankfor.ai instead

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Write tests for new functionality
4. Ensure all tests pass (`npm test`)
5. Follow the code style (run `npm run lint`)
6. Commit with clear messages
7. Open a PR against `main`

### Commit Messages

Use conventional commits:

```
feat: add semantic overlap calculation
fix: handle empty response arrays
docs: update API reference
test: add coverage for edge cases
```

## Development Setup

```bash
# Clone the repo
git clone https://github.com/Rankfor/rankfor-open.git
cd rankfor-open

# Install dependencies
cd dice-roller
npm install

# Run tests
npm test

# Build
npm run build

# Lint
npm run lint
```

## Code Style

- TypeScript with strict mode
- ESLint + Prettier
- JSDoc comments for public APIs
- 100% test coverage for core algorithms

## Testing

```bash
# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test file
npm test -- --grep "analyzeStability"
```

## Documentation

- Update README.md for user-facing changes
- Add JSDoc comments for new functions
- Include examples in documentation

## Research Contributions

For research paper contributions:

1. Follow the paper template in `research/papers/_template/`
2. Include methodology, data, and reproducibility steps
3. All data must be anonymized
4. License: CC BY 4.0

## Glossary Contributions

For glossary term additions:

1. Edit `glossary/terms.json`
2. Include: term, definition, related terms, sources
3. Terms must be AI visibility specific
4. License: CC BY 4.0

## Questions?

- Open a GitHub Discussion
- Email: opensource@rankfor.ai

## License

By contributing, you agree that your contributions will be licensed under:
- Code: MIT License
- Research/Glossary: CC BY 4.0
