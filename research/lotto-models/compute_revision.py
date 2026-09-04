#!/usr/bin/env python3
"""Recomputation pack for the 2026-09-04 revision of the lotto note.

Reads the frozen data package at ../../../scripts/lotto-vs-models/ and writes,
next to this script:

  mc_pvalues.csv           Monte Carlo p-values per source (review item 3)
  prompt_variant_table.csv 6x4 per-(engine, prompt variant) table (item 5)
  deployment_record.csv    per-engine deployment record (item 8)
  prediction_ledger.csv    prediction ledger (item 11)
  floor_spotcheck.csv      fair-floor spot checks vs the reviewer's simulations

Null model: tickets are independent; each ticket is six distinct integers
drawn uniformly from 1..49. Statistic: N_eff = 1 / sum(share_i^2), the
effective diversity of number frequencies, identical to run.py metrics().
p_MC = (1 + #{sim N_eff <= observed N_eff}) / (B + 1), one-sided, ties count.
Everything is seeded; B = 20,000.
"""
import csv
import json
import re
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
SRC = HERE / "../../../scripts/lotto-vs-models"
DATA = SRC / "data"

B = 20000
MASTER_SEED = 20260904

PROMPTS = {  # verbatim from run.py PROMPTS, the four en_* variants used
    "en_base": "Give me six different random numbers between 1 and 49.\nAnswer with the six numbers only, separated by commas.",
    "en_lottery": "Pick six lottery numbers between 1 and 49.",
    "en_terse": "I need 6 random numbers from 1 to 49. Just the numbers.",
    "en_integers": "Generate six unique random integers in the range 1-49.",
}

ENDPOINTS = {  # from run.py call functions
    "gpt-5.6-luna": ("gpt-5.6-luna", "api.openai.com", "none beyond defaults"),
    "claude-sonnet-5": ("claude-sonnet-5", "api.anthropic.com", "max_tokens=128"),
    "gemini-3.7-flash": ("gemini-3.7-flash", "generativelanguage.googleapis.com", "none beyond defaults"),
    "grok-4.5": ("grok-4.5", "api.x.ai", "none beyond defaults"),
    "mistral-large": ("mistral-large-latest", "api.mistral.ai", "none beyond defaults"),
    "sonar": ("sonar", "api.perplexity.ai", "none beyond defaults"),
}


def parse(text):
    """Copied verbatim from run.py so re-parsing matches the published metrics."""
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


def neff_from_counts(counts):
    arr = np.array([counts.get(i, 0) for i in range(1, 50)], float)
    share = arr / arr.sum()
    return float(1.0 / (share ** 2).sum()), arr


def lotto_counts(path):
    c = Counter()
    for tok in path.read_text().split():
        n, k = tok.split(":")
        c[int(n)] = int(k)
    return c


def simulate(tickets, seed, b=B, chunk=500):
    """b simulated datasets of `tickets` independent uniform 6-distinct-of-49
    tickets. Returns (neff, top_count, share_1_31) arrays of length b."""
    rng = np.random.default_rng(seed)
    balls = tickets * 6
    neff = np.empty(b)
    tops = np.empty(b)
    s131 = np.empty(b)
    done = 0
    while done < b:
        m = min(chunk, b - done)
        u = rng.random((m, tickets, 49))
        idx = np.argpartition(u, 6, axis=2)[:, :, :6]        # 6 distinct uniform picks
        flat = (idx + np.arange(m)[:, None, None] * 49).reshape(m, -1)
        counts = np.bincount(flat.ravel(), minlength=m * 49).reshape(m, 49)
        share = counts / balls
        neff[done:done + m] = 1.0 / (share ** 2).sum(axis=1)
        tops[done:done + m] = counts.max(axis=1)
        s131[done:done + m] = counts[:, :31].sum(axis=1) / balls
        done += m
    return neff, tops, s131


def p_low(sim, obs):
    return (1 + int(np.sum(sim <= obs))) / (len(sim) + 1)


def p_two(sim, obs):
    lo = (1 + int(np.sum(sim <= obs))) / (len(sim) + 1)
    hi = (1 + int(np.sum(sim >= obs))) / (len(sim) + 1)
    return min(1.0, 2 * min(lo, hi))


def main():
    # ---- load and re-parse the raw model answers (raw_answer is truth) ----
    rows = [json.loads(l) for l in (DATA / "raw_answers.jsonl").read_text().splitlines() if l.strip()]
    for r in rows:
        if not r["refused"]:
            r["parsed"], r["invalid_reason"] = parse(r["raw_answer"])
    assert len(rows) == 1200, len(rows)
    assert {r["prompt_variant"] for r in rows} == set(PROMPTS), "unexpected prompt variants"
    assert {r["language"] for r in rows} == {"EN"}

    engines = sorted({r["engine"] for r in rows})
    per_engine = {}
    for e in engines:
        cell = [r for r in rows if r["engine"] == e]
        valid = [r for r in cell if not r["refused"] and not r["invalid_reason"]]
        c = Counter(n for r in valid for n in r["parsed"])
        tickets = Counter(tuple(sorted(r["parsed"])) for r in valid)
        per_engine[e] = dict(attempted=len(cell), valid=valid, counts=c, tickets=tickets)

    # ---- physical samples: verify shape and totals ----
    lot99 = lotto_counts(DATA / "lotto_1999.txt")
    lot26 = lotto_counts(DATA / "lotto_2026.txt")
    assert sum(lot99.values()) == 156 and sum(lot99.values()) // 6 == 26
    assert sum(lot26.values()) == 234 and sum(lot26.values()) // 6 == 39
    assert 44 not in lot99, "1999 file should hold a true zero for 44"
    print("physical samples verified: 1999 = 26 draws / 156 balls (44 absent), "
          "2026 = 39 draws / 234 balls")

    # ---- (a) Monte Carlo p-values per source ----
    sources = [("Polish Lotto summer 1999", 26, lot99),
               ("Polish Lotto summer 2026", 39, lot26)]
    for e in engines:
        sources.append((e, len(per_engine[e]["valid"]), per_engine[e]["counts"]))

    sizes = sorted({t for _, t, _ in sources})
    sims = {}
    for i, t in enumerate(sizes):
        sims[t] = simulate(t, seed=MASTER_SEED + i)
        print(f"simulated {B} datasets at {t} tickets "
              f"(seed {MASTER_SEED + i}): 5th pct Neff {np.percentile(sims[t][0], 5):.4f}, "
              f"median {np.median(sims[t][0]):.4f}")

    mc_rows = []
    for label, t, c in sources:
        obs_neff, arr = neff_from_counts(c)
        sim_neff, sim_top, sim_131 = sims[t]
        obs_131 = arr[:31].sum() / arr.sum()
        mc_rows.append({
            "source": label, "tickets": t, "balls": t * 6,
            "neff_obs": round(obs_neff, 4), "neff_obs_rounded": round(obs_neff, 1),
            "fair_floor_p5": round(float(np.percentile(sim_neff, 5)), 4),
            "sim_median": round(float(np.median(sim_neff)), 4),
            "p_mc_neff_low": f"{p_low(sim_neff, obs_neff):.7f}",
            "exceedances": int(np.sum(sim_neff <= obs_neff)),
            "top_count_obs": int(arr.max()),
            "top_count_p95": int(np.percentile(sim_top, 95)),
            "share_1_31_pct": round(100 * obs_131, 1),
            "p_mc_share131_two_sided": f"{p_two(sim_131, obs_131):.7f}",
            "B": B, "seed": MASTER_SEED + sizes.index(t),
        })
    write_csv(HERE / "mc_pvalues.csv", mc_rows)

    # ---- (b) 6x4 prompt-variant table ----
    pv_rows = []
    for e in engines:
        for v in ["en_base", "en_lottery", "en_terse", "en_integers"]:
            cell = [r for r in rows if r["engine"] == e and r["prompt_variant"] == v]
            valid = [r for r in cell if not r["refused"] and not r["invalid_reason"]]
            tickets = Counter(tuple(sorted(r["parsed"])) for r in valid)
            c = Counter(n for r in valid for n in r["parsed"])
            neff, _ = neff_from_counts(c) if valid else (float("nan"), None)
            modal_share = 100 * tickets.most_common(1)[0][1] / len(valid) if valid else float("nan")
            pv_rows.append({
                "engine": e, "variant": v, "attempted": len(cell), "valid": len(valid),
                "distinct_tickets": len(tickets),
                "modal_share_pct": round(modal_share, 1),
                "neff": round(neff, 1),
            })
    write_csv(HERE / "prompt_variant_table.csv", pv_rows)

    # ---- (c) deployment record ----
    dep_rows = []
    for e in engines:
        cell = [r for r in rows if r["engine"] == e]
        returned = sorted({r["model_version"] for r in cell if not r["refused"]})
        ts = sorted(r["ts"] for r in cell)
        dep_rows.append({
            "engine": e,
            "requested_model_id": ENDPOINTS[e][0],
            "returned_model_id": "; ".join(returned),
            "endpoint_host": ENDPOINTS[e][1],
            "collection_utc": f"{ts[0][:16]} to {ts[-1][:16]}",
            "request_parameters": ENDPOINTS[e][2] + "; no temperature, seed, or top_p sent",
            "web_search": ("retrieval-enabled by default" if e == "sonar"
                           else "no search parameters sent; none observed"),
        })
    write_csv(HERE / "deployment_record.csv", dep_rows)

    # ---- (d) prediction ledger ----
    neff_of = {e: round(neff_from_counts(per_engine[e]["counts"])[0], 1) for e in engines}
    ledger = [
        {"item": "claude-sonnet-5 N_eff", "predicted": "20 to 30, below floor",
         "observed": f"{neff_of['claude-sonnet-5']}, below floor",
         "status": "direction supported, interval missed"},
        {"item": "gpt-5.6-luna N_eff", "predicted": "25 to 35, below floor",
         "observed": f"{neff_of['gpt-5.6-luna']}, below floor",
         "status": "direction supported, interval missed"},
        {"item": "gemini-3.6-flash N_eff (ran: gemini-3.7-flash)",
         "predicted": "25 to 35, below floor",
         "observed": f"{neff_of['gemini-3.7-flash']}, below floor",
         "status": "direction supported, interval missed; model drifted 3.6 to 3.7"},
        {"item": "grok-4.5 N_eff", "predicted": "25 to 35, below floor",
         "observed": f"{neff_of['grok-4.5']}, below floor",
         "status": "direction supported, interval missed"},
        {"item": "mistral-large N_eff", "predicted": "not predicted",
         "observed": f"{neff_of['mistral-large']}, below floor", "status": "engine added post-freeze"},
        {"item": "sonar N_eff", "predicted": "not predicted",
         "observed": f"{neff_of['sonar']}, below floor", "status": "engine added post-freeze"},
        {"item": "7 and 42 top-5 in at least 3 engines", "predicted": "yes",
         "observed": "both top-5 in gemini-3.7-flash, grok-4.5, mistral-large",
         "status": "supported"},
        {"item": "share of numbers 1-31", "predicted": "68 to 78%",
         "observed": "63.8 to 68.0%", "status": "interval missed"},
        {"item": "mean number below 25.0", "predicted": "yes",
         "observed": "24.42 to 27.00; two engines below 25.0",
         "status": "not consistently observed"},
        {"item": "ascending order in over half of answers", "predicted": "yes, plausibly over 90%",
         "observed": "87.0 to 100% in five engines; 27.7% in mistral-large",
         "status": "supported in five of six"},
        {"item": "invalid rows under 5%", "predicted": "yes",
         "observed": "0 to 6.0% (mistral-large 6.0%, all HTTP 429)",
         "status": "supported in five of six"},
    ]
    write_csv(HERE / "prediction_ledger.csv", ledger)

    # 7-and-42 rank verification for the ledger row
    for e in ["gemini-3.7-flash", "grok-4.5", "mistral-large"]:
        _, arr = neff_from_counts(per_engine[e]["counts"])
        order = np.argsort(-arr, kind="stable") + 1
        r7 = int(np.where(order == 7)[0][0]) + 1
        r42 = int(np.where(order == 42)[0][0]) + 1
        print(f"rank check {e}: 7 at {r7}/49, 42 at {r42}/49")
        assert r7 <= 5 and r42 <= 5

    # ---- (e) fair-floor spot checks vs reviewer values ----
    reviewer = {26: 35.6833, 39: 39.1674, 188: 46.5802, 196: 46.6875, 200: 46.7168}
    spot = []
    for t in sizes:
        p5 = float(np.percentile(sims[t][0], 5))
        spot.append({"tickets": t, "our_p5": round(p5, 4),
                     "reviewer_p5": reviewer[t], "abs_diff": round(abs(p5 - reviewer[t]), 4),
                     "paper_floor": {26: 35.7, 39: 39.3, 188: 46.6, 196: 46.7, 200: 46.7}[t]})
    write_csv(HERE / "floor_spotcheck.csv", spot)

    # ---- summary print ----
    print("\n--- Monte Carlo p-values ---")
    for r in mc_rows:
        print(f"{r['source']:<28} tickets={r['tickets']:>3} Neff={r['neff_obs']:>8.4f} "
              f"floor={r['fair_floor_p5']:>7.4f} p_MC={r['p_mc_neff_low']} "
              f"1-31={r['share_1_31_pct']}% (p2s={r['p_mc_share131_two_sided']})")
    print("\n--- floor spot checks ---")
    for r in spot:
        print(r)


def write_csv(path, rows):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {path.name} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
