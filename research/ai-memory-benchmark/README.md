# AI Memory Benchmark: SECI Extraction vs Raw Storage

Structured knowledge extraction vs raw verbatim storage on the [LongMemEval](https://github.com/xiaowu0162/longmemeval) benchmark (Wu et al., ICLR 2025).

## Results

**LongMemEval_S, 500 questions, all 6 task types, session-level retrieval:**

| Approach | R@5 | R@10 | NDCG@5 | NDCG@10 |
|----------|-----|------|--------|---------|
| Raw all turns | 85.9% | 92.8% | 80.3% | 83.0% |
| Raw user-only (MemPalace method) | 92.1% | 96.3% | 86.8% | 88.5% |
| **SECI extraction** | **93.7%** | **96.7%** | 89.1% | 90.3% |
| **SECI hybrid + keyword** | **93.9%** | 96.6% | **89.7%** | **90.8%** |

### Per-Task R@5

| Approach | Knowledge Update | Multi-Session | SS-Assistant | SS-Preference | SS-User | Temporal |
|----------|---|---|---|---|---|---|
| Raw user-only | **98.6%** | 90.6% | 96.4% | **96.7%** | 92.2% | 86.9% |
| SECI extraction | 95.8% | 93.2% | **98.2%** | **96.7%** | **96.9%** | **88.8%** |
| SECI hybrid+kw | 96.5% | **93.7%** | **98.2%** | **96.7%** | **96.9%** | 88.4% |

## Key Finding

The embedding model (all-MiniLM-L6-v2) truncates at **256 tokens**. LongMemEval sessions average **10,000 characters**. Raw storage embeds only the first ~1,000 characters, losing 90% of session content at the embedding layer.

SECI extraction condenses the full session into ~500 characters that fit within the embedding window. The retrieval advantage comes from fitting the window, not from extraction quality per se.

## Quick Start

```bash
pip install chromadb sentence-transformers

# Download LongMemEval data
mkdir -p data && cd data
curl -L -o longmemeval_s_cleaned.json \
  https://huggingface.co/datasets/xiaowu0162/longmemeval-cleaned/resolve/main/longmemeval_s_cleaned.json
cd ..

# Run full benchmark (500 questions, ~4 hours)
python seci_vs_mempalace.py --dataset s --mode retrieval

# Quick test (20 questions, ~10 min)
python seci_vs_mempalace.py --dataset s --mode retrieval --limit 20
```

## Four Retrieval Approaches

1. **Raw all turns**: Store full session text (user + assistant turns), embed as one document.
2. **Raw user-only**: Store only user turns per session. This is the approach used by [MemPalace](https://github.com/milla-jovovich/mempalace).
3. **SECI extraction**: Condense each session into ~500 chars of structured facts (topic from first user message, follow-up from last user message, resolution from last assistant message). Based on the Externalization phase of Nonaka & Takeuchi's SECI model (1995).
4. **SECI hybrid + keyword**: Fuse raw user-only and SECI extraction scores via Reciprocal Rank Fusion (RRF, k=60), plus keyword overlap boost (up to 30%).

All approaches use ChromaDB with all-MiniLM-L6-v2 embeddings (384-dim, cosine similarity). No LLM is used in retrieval.

## Caveats

- **Top-10 retrieval.** MemPalace benchmarks with top-50 retrieval depth. Our top-10 is more constrained. The 92.1% vs MemPalace's published 96.6% gap is likely attributable to this difference.
- **Rule-based extraction.** The extraction is a positional heuristic (first/last messages), not LLM summarization. LLM-based extraction would likely improve quality.
- **Single embedding model.** With longer-context models (bge-large at 512 tokens, nomic at 8192), the raw storage gap would narrow as truncation decreases.
- **Knowledge-update weakness.** Raw user-only scores 98.6% vs SECI's 96.5% on knowledge-update questions. Original wording matters when facts change.

## Theoretical Background

The extraction approach is based on the SECI knowledge management model (Nonaka & Takeuchi, 1995), adapted for AI agent memory:

| Phase | Original (KM) | AI Agent Adaptation |
|-------|---------------|---------------------|
| Socialization | Tacit to tacit | Conversation session occurs |
| Externalization | Tacit to explicit | Extract structured facts from session |
| Combination | Explicit to explicit | Merge, deduplicate, consolidate |
| Internalization | Explicit to tacit | Load context into next session |

This benchmark tests the Externalization phase. A paper describing the full adaptation is under preparation for Knowledge and Information Systems (Springer).

## Files

```
seci_vs_mempalace.py          # Benchmark runner
results/
  s_raw_all_turns_retrieval.jsonl
  s_mempalace_faithful_retrieval.jsonl
  s_seci_extracted_retrieval.jsonl
  s_seci_hybrid_kw_retrieval.jsonl
```

Each JSONL file contains per-question results with `question_id`, `question_type`, `metrics`, `retrieved_ids`, and `gold_ids`.

## Citation

If you use this benchmark in your work:

```
@misc{zatuchin2026secimemory,
  title={From Organizational Knowledge to AI Agent Memory: Empirical Validation of the SECI Model on the LongMemEval Benchmark},
  author={Żatuchin, Dmitrij},
  year={2026},
  howpublished={\url{https://github.com/Rankfor/rankfor-open/tree/main/research/ai-memory-benchmark}}
}
```

## Related

- [LongMemEval](https://github.com/xiaowu0162/longmemeval) (Wu et al., ICLR 2025)
- [MemPalace](https://github.com/milla-jovovich/mempalace)
- [Żatuchin (2024) SECI in Digital Education](https://doi.org/10.1007/s44217-024-00229-0)
- [Full writeup on open.rankfor.ai](https://open.rankfor.ai/resources/ai-memory-benchmark-seci-vs-raw-2026)

## License

MIT. See [LICENSE](../../LICENSE).
