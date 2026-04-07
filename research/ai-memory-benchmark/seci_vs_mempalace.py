#!/usr/bin/env python3
"""
SECI vs MemPalace benchmark on LongMemEval.

Tests three retrieval approaches:
  1. RAW_CHROMADB: MemPalace's approach - store verbatim sessions, search with embeddings
  2. SECI_EXTRACTED: Our approach - extract structured knowledge, search extracted files
  3. SECI_HYBRID: Store both raw + extracted, search both

Outputs:
  - Retrieval metrics (R@5, R@10) per approach
  - QA hypothesis files for LongMemEval evaluation
"""

import json
import os
import sys
import time
import hashlib
import re
from pathlib import Path
from collections import defaultdict
from typing import Optional

import chromadb
from chromadb.utils import embedding_functions
import numpy as np

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
BENCHMARK_DIR = Path(__file__).parent
DATA_DIR = BENCHMARK_DIR / "longmemeval-repo" / "data"
RESULTS_DIR = BENCHMARK_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Use oracle (small, fits context) for initial testing
ORACLE_FILE = DATA_DIR / "longmemeval_oracle.json"
S_FILE = DATA_DIR / "longmemeval_s_cleaned.json"

# Gemini for extraction + QA (our available key)
GEMINI_API_KEY = None
GEMINI_MODEL = "gemini-2.5-flash"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def load_data(path: Path) -> list:
    with open(path) as f:
        return json.load(f)


def session_to_text(session: list[dict], user_only: bool = False) -> str:
    """Convert a session (list of turns) to plain text."""
    lines = []
    for turn in session:
        if user_only and turn["role"] != "user":
            continue
        role = turn["role"].capitalize()
        lines.append(f"{role}: {turn['content']}")
    return "\n".join(lines)


def session_to_user_text(session: list[dict]) -> str:
    """MemPalace style: join only user turns."""
    user_turns = [t["content"] for t in session if t["role"] == "user"]
    return "\n".join(user_turns)


def deduplicate_ids(session_ids: list[str]) -> list[str]:
    """Make session IDs unique by appending a suffix for duplicates."""
    seen = {}
    unique = []
    for sid in session_ids:
        if sid in seen:
            seen[sid] += 1
            unique.append(f"{sid}__dup{seen[sid]}")
        else:
            seen[sid] = 0
            unique.append(sid)
    return unique


def session_to_markdown_distill(session: list[dict], date: str, session_id: str) -> str:
    """Simulate /distill: extract structured knowledge from a session.
    This is a simplified version that extracts key facts without an LLM.
    """
    user_lines = []
    assistant_lines = []
    for turn in session:
        if turn["role"] == "user":
            user_lines.append(turn["content"])
        else:
            assistant_lines.append(turn["content"])
    
    user_text = " ".join(user_lines)
    
    # Extract: decisions, preferences, facts, events
    md = f"# Session {session_id}\n"
    md += f"**Date**: {date}\n\n"
    md += f"## User Context\n{user_text[:500]}\n\n"
    md += f"## Key Points\n"
    
    # Simple extraction: first and last user messages often contain the core info
    if user_lines:
        md += f"- Topic: {user_lines[0][:200]}\n"
        if len(user_lines) > 1:
            md += f"- Follow-up: {user_lines[-1][:200]}\n"
    
    # Assistant conclusions
    if assistant_lines:
        md += f"- Resolution: {assistant_lines[-1][:200]}\n"
    
    return md


def strip_dedup_suffix(sid: str) -> str:
    """Remove __dupN suffix added by deduplicate_ids."""
    if "__dup" in sid:
        return sid.split("__dup")[0]
    return sid


def compute_retrieval_metrics(
    retrieved_ids: list[str],
    gold_ids: list[str],
    k_values: list[int] = [5, 10]
) -> dict:
    """Compute recall@K and NDCG@K."""
    metrics = {}
    gold_set = set(gold_ids)
    
    for k in k_values:
        top_k = retrieved_ids[:k]
        hits = sum(1 for rid in top_k if strip_dedup_suffix(rid) in gold_set)
        recall = hits / len(gold_set) if gold_set else 0.0
        
        # NDCG: any relevant doc in top-k
        dcg = sum(
            (1.0 / np.log2(i + 2)) for i, rid in enumerate(top_k) if strip_dedup_suffix(rid) in gold_set
        )
        idcg = sum(1.0 / np.log2(i + 2) for i in range(min(len(gold_set), k)))
        ndcg = dcg / idcg if idcg > 0 else 0.0
        
        metrics[f"recall_all@{k}"] = recall
        metrics[f"ndcg_any@{k}"] = ndcg
    
    return metrics


# ---------------------------------------------------------------------------
# Approach 1: Raw ChromaDB (MemPalace baseline)
# ---------------------------------------------------------------------------
class RawChromaDBRetriever:
    """Store verbatim session text, retrieve by embedding similarity."""
    
    def __init__(self, name: str = "raw"):
        self.client = chromadb.Client()  # ephemeral
        self.ef = embedding_functions.DefaultEmbeddingFunction()  # all-MiniLM-L6-v2
        self.name = name
    
    def index(self, sessions: list[list[dict]], dates: list[str], session_ids: list[str]):
        """Index all sessions for one question instance."""
        col_name = f"raw_{hashlib.md5(str(session_ids).encode()).hexdigest()[:12]}"
        
        # Delete if exists
        try:
            self.client.delete_collection(col_name)
        except:
            pass
        
        self.collection = self.client.create_collection(
            name=col_name,
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"}
        )
        
        docs = []
        ids = []
        metadatas = []
        for session, date, sid in zip(sessions, dates, session_ids):
            text = session_to_text(session)
            docs.append(text)
            ids.append(str(sid))
            metadatas.append({"date": date, "session_id": str(sid)})
        
        # ChromaDB has batch limits, chunk if needed
        batch_size = 100
        for i in range(0, len(docs), batch_size):
            self.collection.add(
                documents=docs[i:i+batch_size],
                ids=ids[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )
    
    def retrieve(self, question: str, top_k: int = 10) -> list[str]:
        """Return session IDs ranked by relevance."""
        results = self.collection.query(
            query_texts=[question],
            n_results=min(top_k, self.collection.count())
        )
        return results["ids"][0] if results["ids"] else []


# ---------------------------------------------------------------------------
# Approach 1b: Raw ChromaDB user-only (MemPalace faithful reproduction)
# ---------------------------------------------------------------------------
class RawUserOnlyRetriever:
    """MemPalace's actual method: index only user turns per session."""
    
    def __init__(self, name: str = "mempalace_faithful"):
        self.client = chromadb.Client()
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.name = name
    
    def index(self, sessions, dates, session_ids):
        col_name = f"mpf_{hashlib.md5(str(session_ids).encode()).hexdigest()[:12]}"
        try:
            self.client.delete_collection(col_name)
        except:
            pass
        
        self.collection = self.client.create_collection(
            name=col_name,
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"}
        )
        
        docs, ids, metadatas = [], [], []
        for session, date, sid in zip(sessions, dates, session_ids):
            text = session_to_user_text(session)
            if text.strip():
                docs.append(text)
                ids.append(str(sid))
                metadatas.append({"date": date})
        
        if docs:
            batch_size = 100
            for i in range(0, len(docs), batch_size):
                self.collection.add(
                    documents=docs[i:i+batch_size],
                    ids=ids[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size]
                )
    
    def retrieve(self, question: str, top_k: int = 10) -> list[str]:
        n = min(top_k, self.collection.count())
        if n == 0:
            return []
        results = self.collection.query(query_texts=[question], n_results=n)
        return results["ids"][0] if results["ids"] else []


# ---------------------------------------------------------------------------
# Approach 2: SECI Extracted (our approach)
# ---------------------------------------------------------------------------
class SECIExtractedRetriever:
    """Extract structured knowledge per session, search extracted text."""
    
    def __init__(self, name: str = "seci"):
        self.client = chromadb.Client()
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.name = name
    
    def index(self, sessions: list[list[dict]], dates: list[str], session_ids: list[str]):
        col_name = f"seci_{hashlib.md5(str(session_ids).encode()).hexdigest()[:12]}"
        try:
            self.client.delete_collection(col_name)
        except:
            pass
        
        self.collection = self.client.create_collection(
            name=col_name,
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"}
        )
        
        docs = []
        ids = []
        metadatas = []
        for session, date, sid in zip(sessions, dates, session_ids):
            # Simulate /distill extraction
            extracted = session_to_markdown_distill(session, date, str(sid))
            docs.append(extracted)
            ids.append(str(sid))
            metadatas.append({"date": date, "session_id": str(sid)})
        
        batch_size = 100
        for i in range(0, len(docs), batch_size):
            self.collection.add(
                documents=docs[i:i+batch_size],
                ids=ids[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size]
            )
    
    def retrieve(self, question: str, top_k: int = 10) -> list[str]:
        results = self.collection.query(
            query_texts=[question],
            n_results=min(top_k, self.collection.count())
        )
        return results["ids"][0] if results["ids"] else []


# ---------------------------------------------------------------------------
# Approach 3: SECI Hybrid (raw + extracted)
# ---------------------------------------------------------------------------
class SECIHybridRetriever:
    """Store both raw text and extracted knowledge, fuse retrieval scores."""
    
    def __init__(self, name: str = "hybrid"):
        self.client = chromadb.Client()
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.name = name
    
    def index(self, sessions: list[list[dict]], dates: list[str], session_ids: list[str]):
        h = hashlib.md5(str(session_ids).encode()).hexdigest()[:12]
        
        for col_name in [f"hybrid_raw_{h}", f"hybrid_ext_{h}"]:
            try:
                self.client.delete_collection(col_name)
            except:
                pass
        
        self.raw_col = self.client.create_collection(
            name=f"hybrid_raw_{h}",
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"}
        )
        self.ext_col = self.client.create_collection(
            name=f"hybrid_ext_{h}",
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"}
        )
        
        for session, date, sid in zip(sessions, dates, session_ids):
            raw_text = session_to_text(session)
            ext_text = session_to_markdown_distill(session, date, str(sid))
            
            self.raw_col.add(
                documents=[raw_text],
                ids=[str(sid)],
                metadatas=[{"date": date}]
            )
            self.ext_col.add(
                documents=[ext_text],
                ids=[str(sid)],
                metadatas=[{"date": date}]
            )
    
    def retrieve(self, question: str, top_k: int = 10) -> list[str]:
        n = min(top_k * 2, self.raw_col.count())
        
        raw_results = self.raw_col.query(query_texts=[question], n_results=n)
        ext_results = self.ext_col.query(query_texts=[question], n_results=n)
        
        # Fuse: reciprocal rank fusion
        scores = defaultdict(float)
        k_rrf = 60  # standard RRF constant
        
        for rank, sid in enumerate(raw_results["ids"][0]):
            scores[sid] += 1.0 / (k_rrf + rank + 1)
        
        for rank, sid in enumerate(ext_results["ids"][0]):
            scores[sid] += 1.0 / (k_rrf + rank + 1)
        
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        return [sid for sid, _ in ranked[:top_k]]


# ---------------------------------------------------------------------------
# Approach 4: SECI Hybrid + Keyword Boost (closer to MemPalace hybrid v1)
# ---------------------------------------------------------------------------
class SECIHybridKeywordRetriever:
    """Hybrid retrieval + keyword overlap boost + temporal boost."""
    
    def __init__(self, name: str = "hybrid_kw"):
        self.client = chromadb.Client()
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.name = name
        self._sessions_text = {}  # sid -> raw text for keyword matching
        self._sessions_dates = {}  # sid -> date
    
    def index(self, sessions, dates, session_ids):
        h = hashlib.md5(str(session_ids).encode()).hexdigest()[:12]
        
        for col_name in [f"hkw_raw_{h}", f"hkw_ext_{h}"]:
            try:
                self.client.delete_collection(col_name)
            except:
                pass
        
        self.raw_col = self.client.create_collection(
            name=f"hkw_raw_{h}",
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"}
        )
        self.ext_col = self.client.create_collection(
            name=f"hkw_ext_{h}",
            embedding_function=self.ef,
            metadata={"hnsw:space": "cosine"}
        )
        
        self._sessions_text = {}
        self._sessions_dates = {}
        
        for session, date, sid in zip(sessions, dates, session_ids):
            raw_text = session_to_text(session)
            ext_text = session_to_markdown_distill(session, date, str(sid))
            sid_str = str(sid)
            
            self._sessions_text[sid_str] = raw_text.lower()
            self._sessions_dates[sid_str] = date
            
            self.raw_col.add(documents=[raw_text], ids=[sid_str], metadatas=[{"date": date}])
            self.ext_col.add(documents=[ext_text], ids=[sid_str], metadatas=[{"date": date}])
    
    def retrieve(self, question: str, top_k: int = 10, question_date: str = None) -> list[str]:
        n = min(top_k * 2, self.raw_col.count())
        
        raw_results = self.raw_col.query(query_texts=[question], n_results=n)
        ext_results = self.ext_col.query(query_texts=[question], n_results=n)
        
        # RRF base scores
        scores = defaultdict(float)
        k_rrf = 60
        for rank, sid in enumerate(raw_results["ids"][0]):
            scores[sid] += 1.0 / (k_rrf + rank + 1)
        for rank, sid in enumerate(ext_results["ids"][0]):
            scores[sid] += 1.0 / (k_rrf + rank + 1)
        
        # Keyword boost
        q_words = set(re.findall(r'\b\w{3,}\b', question.lower()))
        for sid in scores:
            text = self._sessions_text.get(sid, "")
            overlap = sum(1 for w in q_words if w in text)
            keyword_boost = min(overlap / max(len(q_words), 1), 1.0) * 0.3
            scores[sid] *= (1.0 + keyword_boost)
        
        # Temporal boost (if question_date available)
        if question_date:
            try:
                from datetime import datetime
                q_date = datetime.strptime(question_date, "%Y-%m-%d")
                for sid in scores:
                    s_date_str = self._sessions_dates.get(sid, "")
                    try:
                        s_date = datetime.strptime(s_date_str, "%Y-%m-%d")
                        days_diff = abs((q_date - s_date).days)
                        # Closer sessions get a boost (up to 20%)
                        temporal_boost = max(0, 0.2 * (1 - days_diff / 365))
                        scores[sid] *= (1.0 + temporal_boost)
                    except:
                        pass
            except:
                pass
        
        ranked = sorted(scores.items(), key=lambda x: -x[1])
        return [sid for sid, _ in ranked[:top_k]]


# ---------------------------------------------------------------------------
# Main benchmark runner
# ---------------------------------------------------------------------------
def run_retrieval_benchmark(data: list, retrievers: list, dataset_name: str):
    """Run retrieval evaluation across all approaches."""
    
    results_by_approach = {r.name: [] for r in retrievers}
    type_results = {r.name: defaultdict(list) for r in retrievers}
    
    n = len(data)
    skip_abs = 0
    
    for i, instance in enumerate(data):
        qid = instance["question_id"]
        
        # Skip abstention questions (no ground truth retrieval target)
        if "_abs" in qid:
            skip_abs += 1
            continue
        
        question = instance["question"]
        question_date = instance.get("question_date", None)
        qtype = instance["question_type"]
        gold_session_ids = [str(x) for x in instance["answer_session_ids"]]
        sessions = instance["haystack_sessions"]
        dates = instance["haystack_dates"]
        raw_session_ids = [str(x) for x in instance["haystack_session_ids"]]
        session_ids = deduplicate_ids(raw_session_ids)
        
        # Also map gold IDs to the same dedup scheme
        raw_to_dedup = dict(zip(raw_session_ids, session_ids))
        # For gold, use first occurrence (original ID)
        gold_session_ids = [str(x) for x in instance["answer_session_ids"]]
        
        if (i + 1) % 50 == 0 or i == 0:
            print(f"  Processing {i+1}/{n} (skipped {skip_abs} abstention)...", flush=True)
        
        for retriever in retrievers:
            # Index
            retriever.index(sessions, dates, session_ids)
            
            # Retrieve
            if hasattr(retriever, '_sessions_text'):
                retrieved = retriever.retrieve(question, top_k=10, question_date=question_date)
            else:
                retrieved = retriever.retrieve(question, top_k=10)
            
            # Compute metrics
            metrics = compute_retrieval_metrics(retrieved, gold_session_ids, k_values=[5, 10])
            
            results_by_approach[retriever.name].append({
                "question_id": qid,
                "question_type": qtype,
                "metrics": {"session": metrics},
                "retrieved_ids": retrieved,
                "gold_ids": gold_session_ids
            })
            
            type_results[retriever.name][qtype].append(metrics)
    
    # Print results
    print(f"\n{'='*70}")
    print(f"RETRIEVAL RESULTS on {dataset_name} ({n - skip_abs} questions, {skip_abs} abstention skipped)")
    print(f"{'='*70}\n")
    
    for approach_name in results_by_approach:
        all_metrics = [r["metrics"]["session"] for r in results_by_approach[approach_name]]
        
        r5 = np.mean([m["recall_all@5"] for m in all_metrics])
        r10 = np.mean([m["recall_all@10"] for m in all_metrics])
        n5 = np.mean([m["ndcg_any@5"] for m in all_metrics])
        n10 = np.mean([m["ndcg_any@10"] for m in all_metrics])
        
        print(f"  {approach_name.upper():20s}  R@5={r5:.4f}  R@10={r10:.4f}  NDCG@5={n5:.4f}  NDCG@10={n10:.4f}")
        
        # Per-type breakdown
        for qtype in sorted(type_results[approach_name].keys()):
            type_m = type_results[approach_name][qtype]
            tr5 = np.mean([m["recall_all@5"] for m in type_m])
            tr10 = np.mean([m["recall_all@10"] for m in type_m])
            print(f"    {qtype:30s}  R@5={tr5:.4f}  R@10={tr10:.4f}  (n={len(type_m)})")
        print()
    
    # Save detailed results
    for approach_name, results in results_by_approach.items():
        out_path = RESULTS_DIR / f"{dataset_name}_{approach_name}_retrieval.jsonl"
        with open(out_path, "w") as f:
            for r in results:
                f.write(json.dumps(r) + "\n")
        print(f"  Saved: {out_path}")
    
    return results_by_approach


# ---------------------------------------------------------------------------
# QA generation (using Gemini)
# ---------------------------------------------------------------------------
def generate_qa_with_gemini(data: list, retriever, dataset_name: str, top_k: int = 5):
    """Generate answers using Gemini with retrieved context."""
    global GEMINI_API_KEY
    
    if not GEMINI_API_KEY:
        GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
        if not GEMINI_API_KEY:
            # Try .env file
            env_path = Path(__file__).parent.parent / ".env"
            if env_path.exists():
                for line in env_path.read_text().splitlines():
                    if line.startswith("GEMINI_API_KEY="):
                        GEMINI_API_KEY = line.split("=", 1)[1].strip()
                        break
    
    if not GEMINI_API_KEY:
        print("WARNING: No GEMINI_API_KEY found. Skipping QA generation.")
        return None
    
    try:
        import google.generativeai as genai
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
    except ImportError:
        print("WARNING: google-generativeai not installed. Run: pip3 install google-generativeai")
        return None
    
    hypotheses = []
    n = len(data)
    
    for i, instance in enumerate(data):
        qid = instance["question_id"]
        question = instance["question"]
        question_date = instance.get("question_date", None)
        sessions = instance["haystack_sessions"]
        dates = instance["haystack_dates"]
        session_ids = [str(x) for x in instance["haystack_session_ids"]]
        
        if (i + 1) % 25 == 0 or i == 0:
            print(f"  QA: {i+1}/{n}...", flush=True)
        
        # Index and retrieve
        retriever.index(sessions, dates, session_ids)
        if hasattr(retriever, '_sessions_text'):
            retrieved_ids = retriever.retrieve(question, top_k=top_k, question_date=question_date)
        else:
            retrieved_ids = retriever.retrieve(question, top_k=top_k)
        
        # Build context from retrieved sessions
        id_to_idx = {str(sid): idx for idx, sid in enumerate(session_ids)}
        context_parts = []
        for rid in retrieved_ids:
            if rid in id_to_idx:
                idx = id_to_idx[rid]
                date = dates[idx]
                text = session_to_text(sessions[idx])
                context_parts.append(f"[Session from {date}]\n{text}")
        
        context = "\n\n---\n\n".join(context_parts)
        
        prompt = f"""You are a helpful chat assistant with access to past conversation history.
Based on the following past conversation sessions, answer the user's question.
If the information is not available in the provided sessions, say "I don't have that information."

Past conversations:
{context}

Question (asked on {question_date}): {question}

Answer concisely and directly."""
        
        try:
            response = model.generate_content(prompt)
            answer = response.text.strip()
        except Exception as e:
            answer = f"Error: {e}"
            print(f"  WARNING: Gemini error on {qid}: {e}")
        
        hypotheses.append({
            "question_id": qid,
            "hypothesis": answer
        })
        
        # Rate limit: Gemini free tier
        time.sleep(0.5)
    
    # Save
    out_path = RESULTS_DIR / f"{dataset_name}_{retriever.name}_qa.jsonl"
    with open(out_path, "w") as f:
        for h in hypotheses:
            f.write(json.dumps(h) + "\n")
    print(f"  Saved QA hypotheses: {out_path}")
    
    return out_path


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SECI vs MemPalace benchmark")
    parser.add_argument("--dataset", choices=["oracle", "s"], default="oracle",
                       help="Which dataset: oracle (small, ~3 sessions/q) or s (~40 sessions/q)")
    parser.add_argument("--mode", choices=["retrieval", "qa", "both"], default="retrieval",
                       help="What to run: retrieval only, qa only, or both")
    parser.add_argument("--limit", type=int, default=0,
                       help="Limit number of questions (0 = all)")
    args = parser.parse_args()
    
    # Load data
    data_file = ORACLE_FILE if args.dataset == "oracle" else S_FILE
    print(f"Loading {data_file}...")
    data = load_data(data_file)
    
    if args.limit > 0:
        data = data[:args.limit]
        print(f"  Limited to {args.limit} questions")
    
    print(f"  Loaded {len(data)} questions")
    
    # Initialize retrievers
    retrievers = [
        RawChromaDBRetriever("raw_all_turns"),
        RawUserOnlyRetriever("mempalace_faithful"),
        SECIExtractedRetriever("seci_extracted"),
        SECIHybridKeywordRetriever("seci_hybrid_kw"),
    ]
    
    if args.mode in ("retrieval", "both"):
        print(f"\n--- RETRIEVAL BENCHMARK ({args.dataset}) ---\n")
        run_retrieval_benchmark(data, retrievers, args.dataset)
    
    if args.mode in ("qa", "both"):
        print(f"\n--- QA BENCHMARK ({args.dataset}) ---\n")
        # Use the best retriever from retrieval phase for QA
        best_retriever = SECIHybridKeywordRetriever("seci_hybrid_kw")
        generate_qa_with_gemini(data, best_retriever, args.dataset)
        
        # Also run raw ChromaDB for comparison
        raw_retriever = RawChromaDBRetriever("raw_chromadb")
        generate_qa_with_gemini(data, raw_retriever, args.dataset)
