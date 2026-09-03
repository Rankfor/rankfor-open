#!/usr/bin/env python3
"""Lotto against the models. See SPEC.md.

  python3 run.py collect --runs 200      # model arm -> data/raw_answers.jsonl
  python3 run.py analyse                 # both arms -> counts.csv, metrics.csv

ponytail: one file, plain requests, no client SDKs. Four HTTP shapes is less
code than four vendor packages and their version drift.
"""
import argparse, json, os, random, re, sys, time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import requests
from scipy.stats import chisquare

HERE = Path(__file__).parent
DATA = HERE / "data"
ENV_FILES = [HERE / ".env", Path.cwd() / ".env"]  # put your provider keys here

PROMPTS = {
    "en_base": "Give me six different random numbers between 1 and 49.\nAnswer with the six numbers only, separated by commas.",
    "en_lottery": "Pick six lottery numbers between 1 and 49.",
    "en_terse": "I need 6 random numbers from 1 to 49. Just the numbers.",
    "en_integers": "Generate six unique random integers in the range 1-49.",
    "pl_base": "Podaj sześć różnych losowych liczb od 1 do 49.\nOdpowiedz samymi liczbami, oddzielonymi przecinkami.",
}


def env(key):
    for path in ENV_FILES:
        for line in path.read_text().splitlines():
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise KeyError(key)


# --- engines: each returns (text, model_version_string) -------------------

def call_openai(model, prompt):
    r = requests.post("https://api.openai.com/v1/chat/completions",
                      headers={"Authorization": f"Bearer {env('OPENAI_API_KEY')}"},
                      json={"model": model, "messages": [{"role": "user", "content": prompt}]},
                      timeout=120)
    r.raise_for_status()
    j = r.json()
    return j["choices"][0]["message"]["content"], j.get("model", model)


def call_anthropic(model, prompt):
    r = requests.post("https://api.anthropic.com/v1/messages",
                      headers={"x-api-key": env("CLAUDE_API_KEY"), "anthropic-version": "2023-06-01"},
                      json={"model": model, "max_tokens": 128,
                            "messages": [{"role": "user", "content": prompt}]},
                      timeout=120)
    r.raise_for_status()
    j = r.json()
    text = "".join(b.get("text", "") for b in j["content"])
    return text, j.get("model", model)


def call_gemini(model, prompt):
    r = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": env("GEMINI_API_KEY1")},
        json={"contents": [{"parts": [{"text": prompt}]}]}, timeout=120)
    r.raise_for_status()
    j = r.json()
    parts = j["candidates"][0]["content"].get("parts", [])
    return "".join(p.get("text", "") for p in parts), j.get("modelVersion", model)


def call_perplexity(model, prompt):
    r = requests.post("https://api.perplexity.ai/chat/completions",
                      headers={"Authorization": f"Bearer {env('PERPLEXITY_API_KEY')}"},
                      json={"model": model, "messages": [{"role": "user", "content": prompt}]},
                      timeout=120)
    r.raise_for_status()
    j = r.json()
    return j["choices"][0]["message"]["content"], j.get("model", model)


def call_grok(model, prompt):
    r = requests.post("https://api.x.ai/v1/chat/completions",
                      headers={"Authorization": f"Bearer {env('GROK_DEV')}"},
                      json={"model": model, "messages": [{"role": "user", "content": prompt}]},
                      timeout=180)
    r.raise_for_status()
    j = r.json()
    return j["choices"][0]["message"]["content"], j.get("model", model)


def call_mistral(model, prompt):
    r = requests.post("https://api.mistral.ai/v1/chat/completions",
                      headers={"Authorization": f"Bearer {env('MISTRAL_API_DEV')}"},
                      json={"model": model, "messages": [{"role": "user", "content": prompt}]},
                      timeout=180)
    r.raise_for_status()
    j = r.json()
    return j["choices"][0]["message"]["content"], j.get("model", model)


ENGINES = {
    "gpt-5.6-luna": (call_openai, "gpt-5.6-luna"),
    "claude-sonnet-5": (call_anthropic, "claude-sonnet-5"),
    "gemini-3.7-flash": (call_gemini, "gemini-3.7-flash"),
    "grok-4.5": (call_grok, "grok-4.5"),
    "mistral-large": (call_mistral, "mistral-large-latest"),
    "sonar": (call_perplexity, "sonar"),          # web search on by design
}


def parse(text):
    """-> (numbers, invalid_reason). Keeps the row either way, per SPEC §2.

    Models often wrap the answer in prose that repeats the range ("between 1
    and 49"), so a whole-text scan finds eight numbers where the model gave
    six. When exactly one line holds six numbers, that line is the answer.
    Anything less clear-cut falls through to the whole-text scan and is
    flagged, never quietly repaired.
    """
    text = text or ""
    for spans in (re.findall(r"\*\*(.+?)\*\*", text), text.splitlines()):
        sixes = [g for g in ([int(n) for n in re.findall(r"\d+", sp)] for sp in spans)
                 if len(g) == 6]
        if len(sixes) == 1:
            nums = sixes[0]
            break
    else:
        nums = [int(n) for n in re.findall(r"\d+", text)]
    if len(nums) != 6:
        return nums, f"n_parsed={len(nums)}"
    if any(n < 1 or n > 49 for n in nums):
        return nums, "out_of_range"
    if len(set(nums)) != 6:
        return nums, "duplicates"
    return nums, None


def one_call(engine, prompt_variant, lang):
    fn, model = ENGINES[engine]
    prompt = PROMPTS[prompt_variant]
    t0 = time.time()
    row = {"ts": datetime.now(timezone.utc).isoformat(), "engine": engine,
           "language": lang, "prompt_variant": prompt_variant, "temperature": "default"}
    try:
        try:
            text, version = fn(model, prompt)
        except Exception:                        # one retry, transient 429 / 5xx / socket
            time.sleep(3)
            text, version = fn(model, prompt)
        nums, reason = parse(text)
        row.update(model_version=version, raw_answer=text.strip(), parsed=nums,
                   n_parsed=len(nums), invalid_reason=reason, refused=False)
    except Exception as e:                      # network / 4xx / refusal
        row.update(model_version=model, raw_answer=f"ERROR: {e}"[:400], parsed=[],
                   n_parsed=0, invalid_reason="call_failed", refused=True)
    row["latency_ms"] = round((time.time() - t0) * 1000)
    return row


def collect(runs, langs, workers):
    jobs = []
    for engine in ENGINES:
        for lang in langs:
            variants = ([k for k in PROMPTS if k.startswith("en_")] if lang == "EN"
                        else [k for k in PROMPTS if k.startswith("pl_")])
            for i in range(runs):
                jobs.append((engine, variants[i % len(variants)], lang))
    random.shuffle(jobs)                         # SPEC §2: randomised cell order
    out = DATA / "raw_answers.jsonl"
    done = 0
    with out.open("a") as f, ThreadPoolExecutor(workers) as pool:
        futures = [pool.submit(one_call, *j) for j in jobs]
        for fut in as_completed(futures):        # write as they land, no head-of-line block
            row = fut.result()
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()
            done += 1
            if done % 25 == 0:
                print(f"  {done}/{len(jobs)}", file=sys.stderr)
    print(f"wrote {done} rows -> {out}")


# --- analysis ------------------------------------------------------------

def lotto_counts(path):
    c = Counter()
    for tok in path.read_text().split():
        n, k = tok.split(":")
        c[int(n)] = int(k)
    return c


def metrics(counts, label, n_units, extra=None):
    arr = np.array([counts.get(i, 0) for i in range(1, 50)], float)
    total = arr.sum()
    share = arr / total
    hhi = float((share ** 2).sum())
    chi2, p = chisquare(arr, f_exp=np.full(49, total / 49))
    order = np.argsort(-arr, kind="stable")
    rank42 = int(np.where(order == 41)[0][0]) + 1
    top = order[:6] + 1
    m = {"source": label, "units": n_units, "balls": int(total),
         "N_eff": round(1 / hhi, 1), "chi2": round(float(chi2), 1), "df": 48,
         "p": round(float(p), 4),
         "top1_share_pct": round(100 * share.max(), 1),
         "top6_share_pct": round(100 * float(np.sort(share)[-6:].sum()), 1),
         "top6_numbers": " ".join(str(int(t)) for t in top),
         "rank_of_42": f"{rank42}/49", "count_42": int(arr[41]),
         "share_1_31_pct": round(100 * arr[:31].sum() / total, 1),
         "mean_ball": round(float((np.arange(1, 50) * arr).sum() / total), 2)}
    m["_top_count"] = int(arr.max())
    m.update(extra or {})
    return m


def envelope(tickets, sims=20000, seed=7):
    """Fair-draw envelope, sampling the way the game actually works.

    V07: a ticket is six DISTINCT numbers, so the null must draw six without
    replacement within a ticket and treat tickets as independent. The earlier
    version drew every ball independently with replacement, which is a different
    process and gives a wrong envelope.
    """
    rng = np.random.default_rng(seed)
    balls = tickets * 6
    neff, tops = np.empty(sims), np.empty(sims)
    for i in range(sims):
        c = np.zeros(49)
        for _ in range(tickets):
            c[rng.choice(49, size=6, replace=False)] += 1
        neff[i] = 1 / ((c / balls) ** 2).sum()
        tops[i] = c.max()
    return {"neff_p5": round(float(np.percentile(neff, 5)), 1),
            "neff_median": round(float(np.median(neff)), 1),
            "top_median": int(np.median(tops)),
            "top_p95": int(np.percentile(tops, 95))}


def analyse():
    rows = [json.loads(l) for l in (DATA / "raw_answers.jsonl").read_text().splitlines() if l.strip()]
    for r in rows:                       # re-parse: raw_answer is the source of truth
        if not r["refused"]:
            r["parsed"], r["invalid_reason"] = parse(r["raw_answer"])
            r["n_parsed"] = len(r["parsed"])
    sources, counts_out, mets = {}, [], []

    for year, path in (("1999", DATA / "lotto_1999.txt"), ("2026", DATA / "lotto_2026.txt")):
        c = lotto_counts(path)
        draws = sum(c.values()) // 6
        sources[f"lotto_{year}"] = c
        mets.append(metrics(c, f"Polish Lotto summer {year}", f"{draws} draws"))

    for engine in sorted({r["engine"] for r in rows}):
        for lang in sorted({r["language"] for r in rows if r["engine"] == engine}):
            cell = [r for r in rows if r["engine"] == engine and r["language"] == lang]
            valid = [r for r in cell if not r["invalid_reason"]]
            if not valid:
                continue
            c = Counter(n for r in valid for n in r["parsed"])
            key = f"{engine}_{lang}"
            sources[key] = c
            sorted_rate = sum(r["parsed"] == sorted(r["parsed"]) for r in valid) / len(valid)
            tickets = Counter(tuple(sorted(r["parsed"])) for r in valid)
            modal, modal_n = tickets.most_common(1)[0]
            mets.append(metrics(c, f"{engine} ({lang})", f"{len(valid)} runs", {
                "invalid_pct": round(100 * (1 - len(valid) / len(cell)), 1),
                "duplicate_pct": round(100 * sum(r["invalid_reason"] == "duplicates" for r in cell) / len(cell), 1),
                "failed_pct": round(100 * sum(r["refused"] for r in cell) / len(cell), 1),
                "ascending_pct": round(100 * sorted_rate, 1),
                "distinct_tickets": len(tickets),
                "modal_ticket": " ".join(map(str, modal)),
                "modal_ticket_pct": round(100 * modal_n / len(valid), 1)}))

    for m in mets:
        e = envelope(m["balls"] // 6)
        m["fair_N_eff_p5"] = e["neff_p5"]
        m["fair_top_p95"] = e["top_p95"]
        m["outside_envelope"] = ("yes" if m["N_eff"] < e["neff_p5"]
                                 or m.pop("_top_count") > e["top_p95"] else "no")
        m.pop("_top_count", None)

    with (DATA / "counts.csv").open("w") as f:
        f.write("number," + ",".join(sources) + "\n")
        for n in range(1, 50):
            f.write(f"{n}," + ",".join(str(sources[s].get(n, 0)) for s in sources) + "\n")

    cols = list(dict.fromkeys(k for m in mets for k in m))   # union, lotto rows lack model-only keys
    with (DATA / "metrics.csv").open("w") as f:
        f.write(",".join(cols) + "\n")
        for m in mets:
            f.write(",".join(str(m.get(c, "")).replace(",", ";") for c in cols) + "\n")

    for m in mets:
        print(f"{m['source']:<34} {m['units']:>10}  N_eff={m['N_eff']:>5}  "
              f"p={m['p']:<8} 1-31={m['share_1_31_pct']}%  42 rank {m['rank_of_42']}  "
              f"outside={m['outside_envelope']}")
    print(f"\n-> {DATA/'counts.csv'}\n-> {DATA/'metrics.csv'}")


def selfcheck():
    assert parse("3, 14, 15, 22, 33, 41")[0] == [3, 14, 15, 22, 33, 41]
    assert parse("3, 14, 15, 22, 33, 41")[1] is None
    assert parse("7 7 12 19 30 44")[1] == "duplicates"
    assert parse("0, 5, 12, 19, 30, 44")[1] == "out_of_range"
    assert parse("Sure! Here are five: 1 2 3 4 5")[1] == "n_parsed=5"
    assert parse("six between 1 and 49: **7, 14, 23, 28, 35, 46**.")[0] == [7, 14, 23, 28, 35, 46]
    assert parse("**1, 2, 3, 4, 5, 6**\n\nWait:\n\n**7, 8, 9, 10, 11, 12**")[1] == "n_parsed=12"
    c = Counter({i: 10 for i in range(1, 50)})
    m = metrics(c, "uniform", "test")
    assert m["N_eff"] == 49.0 and m["p"] > 0.99
    skew = Counter({i: 1 for i in range(1, 50)}); skew[42] = 100
    assert metrics(skew, "skew", "t")["rank_of_42"] == "1/49"
    print("selfcheck ok")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["collect", "analyse", "selfcheck"])
    ap.add_argument("--runs", type=int, default=200)
    ap.add_argument("--langs", default="EN")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args()
    if a.cmd == "collect":
        collect(a.runs, a.langs.split(","), a.workers)
    elif a.cmd == "analyse":
        analyse()
    else:
        selfcheck()
