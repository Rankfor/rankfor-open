import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  format: ['cjs', 'esm'],
  dts: true,
  clean: true,
  minify: true,
  sourcemap: true,
  splitting: false,
  treeshake: true,
  outDir: 'dist',
  // Mark peer dependencies as external
  external: ['@google/generative-ai', 'openai'],
});
