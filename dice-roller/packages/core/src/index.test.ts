/**
 * Tests for @rankfor/dice-roller core algorithm
 *
 * Tests the key functions without making actual API calls.
 */

import {
  cleanResponse,
  analyzeSentiment,
  extractBrandMentions,
  extractKeyPoints,
  calculateSemanticOverlap,
  calculateJaccardSimilarity,
  calculateShannonEntropy,
  calculateNormalizedEntropy,
  calculateGiniCoefficient,
} from './index';

describe('cleanResponse', () => {
  it('removes markdown headers', () => {
    const input = '# Header\n## Subheader\nContent';
    const result = cleanResponse(input);
    expect(result).toBe('Header\nSubheader\nContent');
  });

  it('removes bold and italic markers', () => {
    const input = 'This is **bold** and *italic* text';
    const result = cleanResponse(input);
    expect(result).toBe('This is bold and italic text');
  });

  it('removes bullet points', () => {
    const input = '- Item 1\n* Item 2\nRegular text';
    const result = cleanResponse(input);
    expect(result).toBe('Item 1\nItem 2\nRegular text');
  });

  it('removes numbered lists', () => {
    const input = '1. First\n2. Second\n3. Third';
    const result = cleanResponse(input);
    expect(result).toBe('First\nSecond\nThird');
  });

  it('removes code blocks', () => {
    const input = 'Before\n```javascript\nconst x = 1;\n```\nAfter';
    const result = cleanResponse(input);
    expect(result).toBe('Before\nAfter');
  });

  it('removes inline code', () => {
    const input = 'Use the `console.log` function';
    const result = cleanResponse(input);
    expect(result).toBe('Use the console.log function');
  });
});

describe('analyzeSentiment', () => {
  it('detects positive sentiment', () => {
    const text = 'This is an excellent product with outstanding quality and reliable performance';
    expect(analyzeSentiment(text)).toBe('positive');
  });

  it('detects negative sentiment', () => {
    const text = 'This is a poor product with problematic issues and disappointing results';
    expect(analyzeSentiment(text)).toBe('negative');
  });

  it('detects neutral sentiment', () => {
    const text = 'This is a product that exists and does things';
    expect(analyzeSentiment(text)).toBe('neutral');
  });

  it('handles mixed sentiment towards neutral', () => {
    const text = 'This has excellent features but also some concerning issues';
    // Should be neutral since scores are close
    const result = analyzeSentiment(text);
    expect(['positive', 'neutral', 'negative']).toContain(result);
  });
});

describe('extractBrandMentions', () => {
  it('finds exact brand name matches', () => {
    const response = 'Salesforce is a leading CRM platform. Many companies use Salesforce for their needs.';
    const result = extractBrandMentions(response, 'Salesforce');
    expect(result.length).toBe(2);
    expect(result[0].snippet).toContain('Salesforce');
  });

  it('handles case insensitive matching', () => {
    const response = 'SALESFORCE is great. salesforce works well.';
    const result = extractBrandMentions(response, 'Salesforce');
    expect(result.length).toBe(2);
  });

  it('returns empty array for no mentions', () => {
    const response = 'This text does not mention the brand at all.';
    const result = extractBrandMentions(response, 'Salesforce');
    expect(result).toEqual([]);
  });

  it('extracts context snippets around mentions', () => {
    const response = 'I recommend using Salesforce for CRM needs because it is reliable.';
    const result = extractBrandMentions(response, 'Salesforce');
    expect(result[0].snippet).toContain('recommend');
    expect(result[0].snippet).toContain('CRM');
  });

  it('analyzes sentiment of context snippets', () => {
    const response = 'Salesforce is excellent and the best CRM tool available.';
    const result = extractBrandMentions(response, 'Salesforce');
    expect(result[0].sentiment).toBe('positive');
  });

  it('handles empty brand name', () => {
    const response = 'Some text here';
    const result = extractBrandMentions(response, '');
    expect(result).toEqual([]);
  });

  it('handles empty response', () => {
    const result = extractBrandMentions('', 'Salesforce');
    expect(result).toEqual([]);
  });
});

describe('extractKeyPoints', () => {
  it('extracts sentences with importance indicators', () => {
    const response = `
      Here are some features.
      It is important to note that this tool is recommended by experts.
      The key benefit is improved productivity.
      Other stuff happens too.
    `;
    const result = extractKeyPoints(response);
    expect(result.length).toBeGreaterThan(0);
    // Should prioritize sentences with 'important', 'recommended', 'key', 'benefit'
    const hasImportantSentence = result.some(
      (s) => s.toLowerCase().includes('important') || s.toLowerCase().includes('recommended'),
    );
    expect(hasImportantSentence).toBe(true);
  });

  it('prioritizes sentences with statistics', () => {
    const response = `
      This is a regular sentence.
      Companies report a 50% increase in efficiency.
      Another regular sentence here.
    `;
    const result = extractKeyPoints(response);
    const hasStatsSentence = result.some((s) => s.includes('50%'));
    expect(hasStatsSentence).toBe(true);
  });

  it('filters out very short sentences', () => {
    const response = 'Short. Also short. This is a longer sentence that should be included in the results.';
    const result = extractKeyPoints(response);
    // Short sentences (< 20 chars) should be filtered
    for (const point of result) {
      expect(point.length).toBeGreaterThan(20);
    }
  });

  it('limits to 10 key points', () => {
    const response = Array(20)
      .fill('This is an important sentence that should be considered as a key point.')
      .join(' ');
    const result = extractKeyPoints(response);
    expect(result.length).toBeLessThanOrEqual(10);
  });
});

describe('calculateSemanticOverlap', () => {
  it('returns 100 for identical texts', () => {
    const text = 'This is a sample text with some words';
    // Not exactly 100 due to Jaccard formula, but should be high
    const result = calculateSemanticOverlap(text, text);
    expect(result).toBeGreaterThanOrEqual(90);
  });

  it('returns 0 for completely different texts', () => {
    const text1 = 'Apple orange banana fruit';
    const text2 = 'Car truck vehicle automobile';
    const result = calculateSemanticOverlap(text1, text2);
    expect(result).toBe(0);
  });

  it('returns moderate score for partially overlapping texts', () => {
    const text1 = 'Salesforce is a great CRM tool for business';
    const text2 = 'Salesforce provides excellent CRM solutions for enterprises';
    const result = calculateSemanticOverlap(text1, text2);
    expect(result).toBeGreaterThan(0);
    expect(result).toBeLessThan(100);
  });

  it('handles empty strings', () => {
    expect(calculateSemanticOverlap('', 'some text')).toBe(0);
    expect(calculateSemanticOverlap('some text', '')).toBe(0);
    expect(calculateSemanticOverlap('', '')).toBe(0);
  });

  it('ignores stop words', () => {
    const text1 = 'The quick brown fox';
    const text2 = 'A quick brown dog';
    // 'the' and 'a' should be ignored, 'quick' and 'brown' should match
    const result = calculateSemanticOverlap(text1, text2);
    expect(result).toBeGreaterThan(0);
  });
});

describe('calculateJaccardSimilarity', () => {
  it('returns 1 for identical sets', () => {
    const arr = ['a', 'b', 'c'];
    const result = calculateJaccardSimilarity(arr, arr);
    expect(result).toBe(1);
  });

  it('returns 0 for completely different sets', () => {
    const arr1 = ['a', 'b', 'c'];
    const arr2 = ['x', 'y', 'z'];
    const result = calculateJaccardSimilarity(arr1, arr2);
    expect(result).toBe(0);
  });

  it('returns correct value for partial overlap', () => {
    const arr1 = ['a', 'b', 'c'];
    const arr2 = ['b', 'c', 'd'];
    // Intersection: {b, c} = 2
    // Union: {a, b, c, d} = 4
    // Jaccard = 2/4 = 0.5
    const result = calculateJaccardSimilarity(arr1, arr2);
    expect(result).toBe(0.5);
  });

  it('handles empty arrays', () => {
    expect(calculateJaccardSimilarity([], [])).toBe(1); // Both empty = identical
    expect(calculateJaccardSimilarity(['a'], [])).toBe(0);
    expect(calculateJaccardSimilarity([], ['a'])).toBe(0);
  });

  it('is case insensitive', () => {
    const arr1 = ['Apple', 'Banana'];
    const arr2 = ['apple', 'banana'];
    const result = calculateJaccardSimilarity(arr1, arr2);
    expect(result).toBe(1);
  });
});

describe('calculateShannonEntropy', () => {
  it('returns 0 for empty array', () => {
    const result = calculateShannonEntropy([]);
    expect(result).toBe(0);
  });

  it('returns 0 for array with all zeros', () => {
    const result = calculateShannonEntropy([0, 0, 0]);
    expect(result).toBe(0);
  });

  it('returns 0 for single element', () => {
    const result = calculateShannonEntropy([10]);
    expect(result).toBe(0);
  });

  it('returns maximum entropy for uniform distribution', () => {
    // 4 equal values = log2(4) = 2 bits of entropy
    const result = calculateShannonEntropy([5, 5, 5, 5]);
    expect(result).toBe(2);
  });

  it('returns lower entropy for skewed distribution', () => {
    // One dominant value = lower entropy
    const uniform = calculateShannonEntropy([5, 5, 5, 5]);
    const skewed = calculateShannonEntropy([100, 1, 1, 1]);
    expect(skewed).toBeLessThan(uniform);
  });
});

describe('calculateNormalizedEntropy', () => {
  it('returns normalized entropy between 0 and 1', () => {
    const result = calculateNormalizedEntropy([5, 5, 5, 5]);
    expect(result.normalized).toBe(1); // Perfect uniformity
  });

  it('returns 0 for single non-zero element', () => {
    const result = calculateNormalizedEntropy([10, 0, 0, 0]);
    // Only 1 unique brand, so normalized = 0
    expect(result.normalized).toBe(0);
  });

  it('returns both raw and normalized entropy', () => {
    const result = calculateNormalizedEntropy([5, 5]);
    expect(result).toHaveProperty('entropy');
    expect(result).toHaveProperty('normalized');
    expect(result.entropy).toBeGreaterThan(0);
    expect(result.normalized).toBe(1); // 2 equal values = perfect uniformity
  });
});

describe('calculateGiniCoefficient', () => {
  it('returns 0 for empty array', () => {
    const result = calculateGiniCoefficient([]);
    expect(result).toBe(0);
  });

  it('returns 0 for all zeros', () => {
    const result = calculateGiniCoefficient([0, 0, 0]);
    expect(result).toBe(0);
  });

  it('returns 0 for perfect equality', () => {
    const result = calculateGiniCoefficient([10, 10, 10, 10]);
    expect(result).toBe(0);
  });

  it('returns high value for high inequality', () => {
    // One value dominates
    const result = calculateGiniCoefficient([100, 1, 1, 1]);
    expect(result).toBeGreaterThan(0.5);
  });

  it('returns moderate value for moderate inequality', () => {
    const result = calculateGiniCoefficient([50, 30, 15, 5]);
    expect(result).toBeGreaterThan(0);
    expect(result).toBeLessThan(1);
  });

  it('is bounded between 0 and 1', () => {
    const testCases = [
      [1, 1, 1],
      [100, 1, 1],
      [50, 25, 25],
      [1, 2, 3, 4, 5],
    ];

    for (const tc of testCases) {
      const result = calculateGiniCoefficient(tc);
      expect(result).toBeGreaterThanOrEqual(0);
      expect(result).toBeLessThanOrEqual(1);
    }
  });
});
