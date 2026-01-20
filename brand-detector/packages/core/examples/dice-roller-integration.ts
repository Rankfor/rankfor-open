/**
 * Example: Integrating @rankfor/brand-detector with @rankfor/dice-roller
 * =======================================================================
 *
 * This example shows how to use both packages together for comprehensive
 * AI visibility analysis: stability analysis + brand mention tracking.
 */

import { DiceRoller } from '@rankfor/dice-roller';
import { brandDetector } from '@rankfor/brand-detector';

/**
 * Example 1: Basic Integration - Track Brand Stability
 */
async function example1_BasicIntegration() {
  const roller = new DiceRoller({
    apiKey: process.env.GEMINI_API_KEY!,
  });

  // Run stability analysis
  const result = await roller.roll({
    prompt: "What are the best CRM tools for SMBs?",
    iterations: 5,
    model: 'gemini',
  });

  console.log('=== Stability Analysis ===\n');

  // Analyze brand mentions in each iteration
  const brandsByIteration: Array<{ iteration: number; brands: string[] }> = [];

  for (const response of result.responses) {
    const brands = brandDetector.analyzeLLMResponse(response.text);

    brandsByIteration.push({
      iteration: response.iteration,
      brands: brands.mentions.map((m) => m.brand),
    });

    console.log(`Iteration ${response.iteration}:`, brands.mentions.map((m) => m.brand).join(', '));
  }

  // Calculate brand stability
  console.log('\n=== Brand Stability Scores ===\n');

  const allBrands = new Set(brandsByIteration.flatMap((b) => b.brands));

  for (const brand of allBrands) {
    const appearances = brandsByIteration.filter((b) => b.brands.includes(brand)).length;
    const stability = (appearances / result.responses.length) * 100;

    console.log(`${brand}: ${stability.toFixed(0)}% (${appearances}/${result.responses.length} iterations)`);
  }
}

/**
 * Example 2: Cross-Model Brand Comparison
 */
async function example2_CrossModelComparison() {
  const roller = new DiceRoller({
    apiKey: process.env.GEMINI_API_KEY!,
    openaiApiKey: process.env.OPENAI_API_KEY!,
  });

  const prompt = "What are the best project management tools?";

  console.log('=== Cross-Model Brand Comparison ===\n');

  // Run on Gemini
  const geminiResult = await roller.roll({
    prompt,
    iterations: 3,
    model: 'gemini',
  });

  // Run on OpenAI
  const openaiResult = await roller.roll({
    prompt,
    iterations: 3,
    model: 'openai',
  });

  // Analyze brands in each model's responses
  const geminiBrands = new Map<string, number>();
  const openaiBrands = new Map<string, number>();

  for (const response of geminiResult.responses) {
    const analysis = brandDetector.analyzeLLMResponse(response.text);
    for (const mention of analysis.mentions) {
      geminiBrands.set(mention.brand, (geminiBrands.get(mention.brand) || 0) + mention.count);
    }
  }

  for (const response of openaiResult.responses) {
    const analysis = brandDetector.analyzeLLMResponse(response.text);
    for (const mention of analysis.mentions) {
      openaiBrands.set(mention.brand, (openaiBrands.get(mention.brand) || 0) + mention.count);
    }
  }

  // Display comparison
  const allBrands = new Set([...geminiBrands.keys(), ...openaiBrands.keys()]);

  console.log('Brand          | Gemini | OpenAI | Total');
  console.log('---------------|--------|--------|------');

  for (const brand of allBrands) {
    const gemini = geminiBrands.get(brand) || 0;
    const openai = openaiBrands.get(brand) || 0;
    const total = gemini + openai;

    console.log(`${brand.padEnd(14)} | ${gemini.toString().padStart(6)} | ${openai.toString().padStart(6)} | ${total}`);
  }
}

/**
 * Example 3: Sentiment + Stability Analysis
 */
async function example3_SentimentStability() {
  const roller = new DiceRoller({
    apiKey: process.env.GEMINI_API_KEY!,
  });

  const result = await roller.roll({
    prompt: "Compare Salesforce, HubSpot, and Pipedrive for CRM",
    iterations: 5,
    model: 'gemini',
  });

  console.log('=== Sentiment + Stability Analysis ===\n');

  const positiveWords = /excellent|great|best|recommended|leading|robust|powerful/i;
  const negativeWords = /expensive|complex|difficult|lacking|limited|steep learning curve/i;

  const brandSentiments = new Map<string, { positive: number; negative: number; mentions: number }>();

  // Analyze each response with context
  for (const response of result.responses) {
    const analysis = brandDetector.analyzeLLMResponse(response.text, {
      extended: true,
      contextRadius: 60,
    });

    for (const mention of analysis.mentions) {
      const existing = brandSentiments.get(mention.brand) || { positive: 0, negative: 0, mentions: 0 };

      if (mention.contexts) {
        for (const context of mention.contexts) {
          if (positiveWords.test(context)) existing.positive += 1;
          if (negativeWords.test(context)) existing.negative += 1;
        }
      }

      existing.mentions += mention.count;
      brandSentiments.set(mention.brand, existing);
    }
  }

  // Display results
  console.log('Brand          | Mentions | Positive | Negative | Net Sentiment');
  console.log('---------------|----------|----------|----------|---------------');

  for (const [brand, sentiment] of brandSentiments) {
    const net = sentiment.positive - sentiment.negative;
    const netLabel = net > 0 ? `+${net}` : net.toString();

    console.log(
      `${brand.padEnd(14)} | ${sentiment.mentions.toString().padStart(8)} | ${sentiment.positive.toString().padStart(8)} | ${sentiment.negative.toString().padStart(8)} | ${netLabel.padStart(13)}`
    );
  }
}

/**
 * Example 4: Gender Bias Detection with Stability
 */
async function example4_GenderBiasStability() {
  const roller = new DiceRoller({
    apiKey: process.env.GEMINI_API_KEY!,
  });

  console.log('=== Gender Bias Detection with Stability ===\n');

  // Run for "husband" queries
  const husbandResult = await roller.roll({
    prompt: "Gift ideas for my husband who loves tech",
    iterations: 5,
    model: 'gemini',
  });

  // Run for "wife" queries
  const wifeResult = await roller.roll({
    prompt: "Gift ideas for my wife who loves tech",
    iterations: 5,
    model: 'gemini',
  });

  // Analyze brands
  const husbandBrands = new Map<string, number>();
  const wifeBrands = new Map<string, number>();

  for (const response of husbandResult.responses) {
    const analysis = brandDetector.analyzeLLMResponse(response.text);
    for (const mention of analysis.mentions) {
      husbandBrands.set(mention.brand, (husbandBrands.get(mention.brand) || 0) + 1);
    }
  }

  for (const response of wifeResult.responses) {
    const analysis = brandDetector.analyzeLLMResponse(response.text);
    for (const mention of analysis.mentions) {
      wifeBrands.set(mention.brand, (wifeBrands.get(mention.brand) || 0) + 1);
    }
  }

  // Find gender-locked brands
  const allBrands = new Set([...husbandBrands.keys(), ...wifeBrands.keys()]);

  console.log('Brand          | Husband | Wife | Gender Lock');
  console.log('---------------|---------|------|-------------');

  for (const brand of allBrands) {
    const husband = husbandBrands.get(brand) || 0;
    const wife = wifeBrands.get(brand) || 0;

    let genderLock = 'Neutral';
    if (husband > 0 && wife === 0) genderLock = 'Husband';
    if (wife > 0 && husband === 0) genderLock = 'Wife';

    console.log(
      `${brand.padEnd(14)} | ${husband.toString().padStart(7)} | ${wife.toString().padStart(4)} | ${genderLock}`
    );
  }
}

// Run examples
async function main() {
  try {
    // await example1_BasicIntegration();
    // await example2_CrossModelComparison();
    // await example3_SentimentStability();
    await example4_GenderBiasStability();
  } catch (error) {
    console.error('Error:', error);
  }
}

// Uncomment to run
// main();
