# Contributing to @rankfor/dice-roller

Thank you for your interest in contributing to the Dice Roller library. This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Issues

Before creating an issue, please:

1. Search existing issues to avoid duplicates
2. Use the issue templates when available
3. Include relevant details:
   - Node.js version
   - Package version
   - Steps to reproduce
   - Expected vs actual behavior
   - Error messages or logs

### Suggesting Features

We welcome feature suggestions. Please:

1. Check if the feature has already been requested
2. Describe the use case clearly
3. Explain how it benefits the community

### Pull Requests

#### Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/rankfor-open.git
   cd rankfor-open/dice-roller/packages/core
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Development Workflow

1. **Write tests first** (TDD approach)
   ```bash
   npm test -- --watch
   ```

2. **Make your changes**
   - Follow the existing code style
   - Add JSDoc comments to exported functions
   - Keep functions focused and small

3. **Run the test suite**
   ```bash
   npm test
   ```

4. **Run linting**
   ```bash
   npm run lint
   ```

5. **Build the project**
   ```bash
   npm run build
   ```

#### Commit Guidelines

We follow conventional commits:

```
type(scope): description

[optional body]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

Examples:
```
feat(experiment): add support for Claude model
fix(entropy): handle edge case with empty arrays
docs(readme): add browser usage section
test(gini): add test for boundary conditions
```

#### Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md with your changes
5. Create the pull request with a clear description

## Code Style

### TypeScript Guidelines

- Use strict TypeScript (`"strict": true`)
- Never use `any` - use proper types or `unknown`
- Export types alongside implementations
- Add JSDoc comments to all exported functions

```typescript
/**
 * Calculate Shannon entropy for brand distribution
 * Higher entropy = more diverse recommendations
 *
 * @param brandCounts - Array of brand mention counts
 * @returns Entropy value in bits
 *
 * @example
 * ```typescript
 * const entropy = calculateShannonEntropy([5, 5, 5, 5]);
 * // Returns 2 (maximum entropy for 4 equal values)
 * ```
 */
export function calculateShannonEntropy(brandCounts: number[]): number {
  // ...
}
```

### Testing Guidelines

- Write descriptive test names
- Test edge cases (empty arrays, zeros, large values)
- Use `describe` blocks to group related tests
- Aim for high coverage on core logic

```typescript
describe('calculateShannonEntropy', () => {
  it('returns 0 for empty array', () => {
    expect(calculateShannonEntropy([])).toBe(0);
  });

  it('returns maximum entropy for uniform distribution', () => {
    // 4 equal values = log2(4) = 2 bits
    expect(calculateShannonEntropy([5, 5, 5, 5])).toBe(2);
  });

  it('returns lower entropy for skewed distribution', () => {
    const uniform = calculateShannonEntropy([5, 5, 5, 5]);
    const skewed = calculateShannonEntropy([100, 1, 1, 1]);
    expect(skewed).toBeLessThan(uniform);
  });
});
```

## Project Structure

```
packages/core/
  src/
    index.ts        # Main entry point with all exports
    index.test.ts   # Test suite
  dist/             # Built output (generated)
  package.json
  tsconfig.json
  jest.config.js
  README.md
  LICENSE
  CONTRIBUTING.md
  CHANGELOG.md
```

## Adding New Features

### Adding a New Statistical Function

1. Add the function to `src/index.ts`
2. Export it in the exports section
3. Add comprehensive tests
4. Update README.md with usage examples
5. Add to CHANGELOG.md

### Adding a New LLM Provider

1. Add the query function (following `queryGemini`/`queryOpenAI` patterns)
2. Update the `model` type union
3. Add API key handling in experiment mode
4. Update documentation
5. Add integration tests (mocked)

## Questions?

- Open an issue for questions
- Join discussions in GitHub Discussions
- Contact: opensource@rankfor.ai

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
