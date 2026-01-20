#!/usr/bin/env node
/**
 * @rankfor/dice-roller-cli
 * CLI for AI response stability analysis
 *
 * Usage:
 *   npx @rankfor/dice-roller-cli "What are the best CRM tools?" --iterations 5
 *   npx @rankfor/dice-roller-cli --prompt "Best project management software" --brand "Asana"
 *
 * MIT License - https://github.com/Rankfor/rankfor-open
 */

import { program } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import {
  analyzeStability,
  type StabilityOptions,
  type StabilityResult,
} from '@rankfor/dice-roller';

// ============================================================================
// CLI Configuration
// ============================================================================

program
  .name('dice-roller')
  .description('AI Response Stability Analyzer - Test how consistently AI responds to your prompts')
  .version('0.1.0')
  .argument('[prompt]', 'The prompt to analyze')
  .option('-p, --prompt <prompt>', 'The prompt to analyze (alternative to positional argument)')
  .option('-i, --iterations <number>', 'Number of iterations (3-10)', '5')
  .option('-m, --model <model>', 'AI model to use (gemini, openai, grok)', 'gemini')
  .option('-k, --api-key <key>', 'API key for the model (or use GEMINI_API_KEY, OPENAI_API_KEY, GROK_API_KEY env vars)')
  .option('-b, --brand <name>', 'Brand name to track mentions')
  .option('-t, --temperature <number>', 'Model temperature (0-1)', '0.7')
  .option('-o, --output <format>', 'Output format (text, json)', 'text')
  .option('-q, --quiet', 'Suppress progress output')
  .action(async (promptArg: string | undefined, options: Record<string, unknown>) => {
    const prompt = promptArg || (options.prompt as string | undefined);

    if (!prompt) {
      console.error(chalk.red('Error: Please provide a prompt to analyze'));
      console.log('\nUsage:');
      console.log('  dice-roller "What are the best CRM tools?"');
      console.log('  dice-roller --prompt "Best project management software" --brand "Asana"');
      process.exit(1);
    }

    const model = (options.model as string) || 'gemini';
    const iterations = parseInt(options.iterations as string, 10);
    const temperature = parseFloat(options.temperature as string);
    const brandName = options.brand as string | undefined;
    const outputFormat = (options.output as string) || 'text';
    const quiet = options.quiet as boolean;

    // Get API key from options or environment
    let apiKey = options.apiKey as string | undefined;
    if (!apiKey) {
      const envVars: Record<string, string> = {
        gemini: 'GEMINI_API_KEY',
        openai: 'OPENAI_API_KEY',
        grok: 'GROK_API_KEY',
      };
      const envVar = envVars[model] || 'GEMINI_API_KEY';
      apiKey = process.env[envVar] || process.env.GOOGLE_GEMINI_API_KEY;
    }

    if (!apiKey) {
      console.error(chalk.red(`Error: No API key found for ${model}`));
      console.log('\nProvide an API key via:');
      console.log(`  --api-key YOUR_KEY`);
      console.log(`  GEMINI_API_KEY=YOUR_KEY (environment variable)`);
      console.log('\nGet a free Gemini API key at: https://aistudio.google.com/apikey');
      process.exit(1);
    }

    if (iterations < 1 || iterations > 10) {
      console.error(chalk.red('Error: Iterations must be between 1 and 10'));
      process.exit(1);
    }

    // Run analysis
    const spinner = quiet ? null : ora('Analyzing response stability...').start();

    try {
      const stabilityOptions: StabilityOptions = {
        prompt,
        iterations,
        model: model as 'gemini' | 'openai' | 'grok',
        apiKey,
        temperature,
        brandName,
        onProgress: (current, total) => {
          if (spinner) {
            spinner.text = `Running iteration ${current}/${total}...`;
          }
        },
      };

      const result = await analyzeStability(stabilityOptions);

      if (spinner) {
        spinner.succeed('Analysis complete!');
      }

      if (outputFormat === 'json') {
        console.log(JSON.stringify(result, null, 2));
      } else {
        printTextResults(result, prompt, brandName);
      }
    } catch (error) {
      if (spinner) {
        spinner.fail('Analysis failed');
      }
      console.error(chalk.red(`\nError: ${(error as Error).message}`));
      process.exit(1);
    }
  });

// ============================================================================
// Output Formatting
// ============================================================================

function printTextResults(
  result: StabilityResult,
  prompt: string,
  brandName?: string,
): void {
  console.log('\n' + chalk.bold('=' .repeat(60)));
  console.log(chalk.bold.cyan('  AI Response Stability Analysis'));
  console.log(chalk.bold('=' .repeat(60)) + '\n');

  // Prompt
  console.log(chalk.gray('Prompt:'));
  console.log(chalk.white(`  "${prompt}"`));
  if (brandName) {
    console.log(chalk.gray('Brand:'), chalk.white(brandName));
  }
  console.log(chalk.gray('Iterations:'), chalk.white(result.metadata.iterations));
  console.log(chalk.gray('Model:'), chalk.white(result.metadata.model));
  console.log('');

  // Scores
  console.log(chalk.bold('SCORES'));
  console.log(chalk.gray('-'.repeat(40)));

  const consistencyColor = getScoreColor(result.consistencyScore);
  const overlapColor = getScoreColor(result.semanticOverlap);

  console.log(
    `  Consistency Score:  ${consistencyColor(result.consistencyScore + '%')}`,
  );
  console.log(
    `  Semantic Overlap:   ${overlapColor(result.semanticOverlap + '%')}`,
  );
  console.log('');

  // Sentiment
  console.log(chalk.bold('SENTIMENT DISTRIBUTION'));
  console.log(chalk.gray('-'.repeat(40)));
  console.log(
    `  ${chalk.green('Positive:')} ${result.sentimentDistribution.positive}%  ` +
    `${chalk.gray('Neutral:')} ${result.sentimentDistribution.neutral}%  ` +
    `${chalk.red('Negative:')} ${result.sentimentDistribution.negative}%`,
  );
  console.log('');

  // Brand mentions (if applicable)
  if (brandName && result.brandMentions.total > 0) {
    console.log(chalk.bold(`BRAND MENTIONS: ${brandName}`));
    console.log(chalk.gray('-'.repeat(40)));
    console.log(`  Total: ${result.brandMentions.total}`);
    console.log(`  Average: ${result.brandMentions.average.toFixed(1)}/response`);
    console.log(`  Range: ${result.brandMentions.min}-${result.brandMentions.max}`);
    console.log(`  Variance: ${result.brandMentions.variance.toFixed(2)}`);
    console.log('');
  }

  // Core stable messages
  console.log(chalk.bold.green('WHAT AI ALWAYS SAYS (80%+ of responses)'));
  console.log(chalk.gray('-'.repeat(40)));
  if (result.analysis.coreStableMessages.length > 0) {
    for (const msg of result.analysis.coreStableMessages) {
      console.log(chalk.green('  - ') + truncate(msg, 70));
    }
  } else {
    console.log(chalk.gray('  (No consistent messages found)'));
  }
  console.log('');

  // Variable messages
  console.log(chalk.bold.yellow('WHAT AI SOMETIMES SAYS (30-80%)'));
  console.log(chalk.gray('-'.repeat(40)));
  if (result.analysis.variableMessages.length > 0) {
    for (const vm of result.analysis.variableMessages) {
      console.log(
        chalk.yellow('  - ') + truncate(vm.message, 60) + chalk.gray(` (${vm.frequency}%)`),
      );
    }
  } else {
    console.log(chalk.gray('  (No variable messages found)'));
  }
  console.log('');

  // Outliers
  console.log(chalk.bold.magenta('UNIQUE INSIGHTS (appeared once)'));
  console.log(chalk.gray('-'.repeat(40)));
  if (result.analysis.outliers.length > 0) {
    for (const msg of result.analysis.outliers.slice(0, 5)) {
      console.log(chalk.magenta('  - ') + truncate(msg, 70));
    }
    if (result.analysis.outliers.length > 5) {
      console.log(chalk.gray(`  ... and ${result.analysis.outliers.length - 5} more`));
    }
  } else {
    console.log(chalk.gray('  (No unique outliers found)'));
  }
  console.log('');

  // Footer
  console.log(chalk.gray('=' .repeat(60)));
  console.log(chalk.gray('  Generated by Rankfor.AI Dice Roller'));
  console.log(chalk.gray('  https://open.rankfor.ai/dice-roller'));
  console.log(chalk.gray('=' .repeat(60)) + '\n');
}

function getScoreColor(score: number): (text: string) => string {
  if (score >= 70) return chalk.green;
  if (score >= 40) return chalk.yellow;
  return chalk.red;
}

function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
}

// ============================================================================
// Run CLI
// ============================================================================

program.parse();
