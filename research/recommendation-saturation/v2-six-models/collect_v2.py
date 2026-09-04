#!/usr/bin/env python3
"""Six-engine saturation v2 collector per PREREGISTRATION-V2.md (frozen 56d62de).

Engine layer copied from scripts/lotto-vs-models/run.py (same keys, same HTTP
shapes). Usage:
  python3 collect_v2.py smoke          # one discarded call per engine
  python3 collect_v2.py collect        # full 4,500-call run, resumable
"""
import json
import random
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import requests

HERE = Path(__file__).parent
OUT = HERE / "data"
OUT.mkdir(exist_ok=True)
RAW = OUT / "raw_responses.jsonl"
QDIR = Path("/Users/diz/dev/rankfor/ai-territory/dev-specs/research/experiments/"
            "category-ownership/category_ownership_2026/queries")
ENV_FILES = [Path("/Users/diz/dev/rankfor/ai-territory/open-site/.env"),
             Path("/Users/diz/dev/rankfor/backend/.env")]
N_RUNS = 15
WORKERS = 8
RETRIES = 5


def env(key):
    for path in ENV_FILES:
        for line in path.read_text().splitlines():
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise KeyError(key)


def call_openai(model, prompt):
    r = requests.post("https://api.openai.com/v1/chat/completions",
                      headers={"Authorization": f"Bearer {env('OPENAI_API_KEY')}"},
                      json={"model": model, "messages": [{"role": "user", "content": prompt}]},
                      timeout=180)
    r.raise_for_status()
    j = r.json()
    return j["choices"][0]["message"]["content"], j.get("model", model), None


def call_anthropic(model, prompt):
    r = requests.post("https://api.anthropic.com/v1/messages",
                      headers={"x-api-key": env("CLAUDE_API_KEY"),
                               "anthropic-version": "2023-06-01"},
                      json={"model": model, "max_tokens": 1024,
                            "messages": [{"role": "user", "content": prompt}]},
                      timeout=180)
    r.raise_for_status()
    j = r.json()
    return "".join(b.get("text", "") for b in j["content"]), j.get("model", model), None


def call_gemini(model, prompt):
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": env("GEMINI_API_KEY1")},
        json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=180)
    r.raise_for_status()
    j = r.json()
    parts = j["candidates"][0]["content"].get("parts", [])
    return "".join(p.get("text", "") for p in parts), j.get("modelVersion", model), None


def call_perplexity(model, prompt):
    r = requests.post("https://api.perplexity.ai/chat/completions",
                      headers={"Authorization": f"Bearer {env('PERPLEXITY_API_KEY')}"},
                      json={"model": model, "messages": [{"role": "user", "content": prompt}]},
                      timeout=180)
    r.raise_for_status()
    j = r.json()
    cits = j.get("citations") or j.get("search_results")
    return j["choices"][0]["message"]["content"], j.get("model", model), cits


def call_grok(model, prompt):
    r = requests.post("https://api.x.ai/v1/chat/completions",
                      headers={"Authorization": f"Bearer {env('GROK_DEV')}"},
                      json={"model": model, "messages": [{"role": "user", "content": prompt}]},
                      timeout=180)
    r.raise_for_status()
    j = r.json()
    return j["choices"][0]["message"]["content"], j.get("model", model), None


def call_mistral(model, prompt):
    r = requests.post("https://api.mistral.ai/v1/chat/completions",
                      headers={"Authorization": f"Bearer {env('MISTRAL_API_DEV')}"},
                      json={"model": model, "messages": [{"role": "user", "content": prompt}]},
                      timeout=180)
    r.raise_for_status()
    j = r.json()
    return j["choices"][0]["message"]["content"], j.get("model", model), None


ENGINES = {
    "gpt-5.6-luna": (call_openai, "gpt-5.6-luna"),
    "claude-sonnet-5": (call_anthropic, "claude-sonnet-5"),
    "gemini-3.7-flash": (call_gemini, "gemini-3.7-flash"),
    "grok-4.5": (call_grok, "grok-4.5"),
    "mistral-large": (call_mistral, "mistral-large-latest"),
    "sonar": (call_perplexity, "sonar"),
}


def load_queries():
    qs = []
    for ind in ("saas", "consulting", "fintech", "ecommerce", "healthtech"):
        data = json.loads((QDIR / f"{ind}_queries.json").read_text())
        items = data if isinstance(data, list) else data.get("queries", data)
        for i, q in enumerate(items[:10]):
            text = q if isinstance(q, str) else (q.get("query") or q.get("text"))
            qs.append(dict(industry=ind, query_idx=i, query=text))
    assert len(qs) == 50, f"expected 50 queries, got {len(qs)}"
    return qs


def done_keys():
    if not RAW.exists():
        return set()
    keys = set()
    for line in RAW.read_text().splitlines():
        try:
            r = json.loads(line)
            keys.add((r["industry"], r["query_idx"], r["engine"], r["iteration"]))
        except Exception:
            pass
    return keys


def one(task):
    fn, model = ENGINES[task["engine"]]
    last = None
    for attempt in range(RETRIES):
        try:
            text, version, cits = fn(model, task["query"])
            return {**task, "response": text, "model_version": version,
                    "citations": cits, "error": None,
                    "ts": datetime.now(timezone.utc).isoformat()}
        except Exception as e:
            last = str(e)[:200]
            time.sleep(2 ** attempt + random.random())
    return {**task, "response": None, "model_version": None, "citations": None,
            "error": last, "ts": datetime.now(timezone.utc).isoformat()}


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "collect"
    qs = load_queries()
    if mode == "smoke":
        for eng in ENGINES:
            t = dict(industry="smoke", query_idx=-1, engine=eng, iteration=-1,
                     query="Name one European capital city. One word.")
            r = one(t)
            ok = "OK" if r["error"] is None else f"FAIL {r['error']}"
            print(f"{eng:18s} {ok}  ({(r.get('response') or '')[:40]!r}, {r.get('model_version')})")
        return
    done = done_keys()
    tasks = [dict(**q, engine=eng, iteration=it)
             for q in qs for eng in ENGINES for it in range(1, N_RUNS + 1)
             if (q["industry"], q["query_idx"], eng, it) not in done]
    random.Random(2026).shuffle(tasks)
    print(f"{len(done)} done, {len(tasks)} to go", flush=True)
    n_ok = n_err = 0
    with RAW.open("a") as f, ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = [ex.submit(one, t) for t in tasks]
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            if r["error"] is None:
                n_ok += 1
            else:
                n_err += 1
            if i % 100 == 0:
                print(f"{i}/{len(tasks)} ok={n_ok} err={n_err}", flush=True)
    print(f"DONE ok={n_ok} err={n_err}", flush=True)


if __name__ == "__main__":
    main()
