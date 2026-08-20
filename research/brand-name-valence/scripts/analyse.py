#!/usr/bin/env python3
"""Score the descriptions against the same valence norms Peec used, then ask the three
questions their design cannot answer.

    python3 analyse.py
"""
import collections, csv, json, math, os, random, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
SEED = 20260808
B = 2000

W = {r["Word"]: float(r["V.Mean.Sum"])
     for r in csv.DictReader(open(os.path.join(DATA, "warriner-2013-valence.csv"), encoding="utf-8"))
     if r["V.Mean.Sum"]}

COND = {"en_word": "English word", "pseudo": "pseudoword", "pl_word": "Polish word"}


def score(attrs):
    """Mean valence of the attributes that appear in the norms. Attributes outside the norms
    are dropped and counted, because scoring them as neutral would pull every description
    toward the scale midpoint and shrink exactly the effect being measured."""
    v = [W[a] for a in attrs if a in W]
    return (statistics.fmean(v) if v else float("nan")), len(v), len(attrs)


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return float("nan")
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs)); dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    return num / (dx * dy) if dx and dy else float("nan")


def slope(xs, ys):
    mx, my = statistics.fmean(xs), statistics.fmean(ys)
    den = sum((x - mx) ** 2 for x in xs)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den if den else float("nan")


def main():
    rng = random.Random(SEED)
    rows = [json.loads(l) for l in open(os.path.join(DATA, "responses.jsonl"), encoding="utf-8") if l.strip()]
    ok = [r for r in rows if r["status"] == "ok"]
    print(f"responses: {len(rows):,} collected, {len(rows)-len(ok)} failed calls, {len(ok):,} usable")

    cov_in = cov_tot = 0
    for r in ok:
        s, k, t = score(r["attributes"])
        r["desc_valence"], r["n_scored"], r["n_attrs"] = s, k, t
        cov_in += k; cov_tot += t
    ok = [r for r in ok if not math.isnan(r["desc_valence"])]
    print(f"attribute coverage by the norms: {cov_in:,}/{cov_tot:,} = {cov_in/cov_tot:.1%}")

    # ── 1. the effect, per condition and model ────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("1. DOES NAME VALENCE MOVE DESCRIPTION VALENCE?")
    print("   slope is scale points of description valence per scale point of name valence")
    print(f"\n  {'condition':14} {'model':8} {'names':>5} {'slope':>7} {'r':>6} {'low band':>9} {'high band':>10} {'gap':>7}")
    effects = {}
    for cond in ("en_word", "pseudo", "pl_word"):
        for model in ("gemini", "claude", "ALL"):
            sub = [r for r in ok if r["condition"] == cond and (model == "ALL" or r["model"] == model)]
            if not sub:
                continue
            by = collections.defaultdict(list)
            for r in sub:
                by[(r["concept"], r["name_valence"])].append(r["desc_valence"])
            xs = [k[1] for k in by]; ys = [statistics.fmean(v) for v in by.values()]
            lo = statistics.fmean([statistics.fmean(v) for k, v in by.items() if k[1] < 3.2])
            hi = statistics.fmean([statistics.fmean(v) for k, v in by.items() if k[1] > 5.6])
            effects[(cond, model)] = {"slope": slope(xs, ys), "r": pearson(xs, ys),
                                      "lo": lo, "hi": hi, "gap": hi - lo, "by": by}
            print(f"  {COND[cond]:14} {model:8} {len(by):>5} {slope(xs,ys):>7.3f} {pearson(xs,ys):>6.2f} "
                  f"{lo:>9.2f} {hi:>10.2f} {hi-lo:>7.2f}")

    # ── 2. the noise floor ────────────────────────────────────────────────────────────────
    print("\n" + "=" * 78)
    print("2. THE NOISE FLOOR: how much does one answer move on its own?")
    per_name = collections.defaultdict(list)
    for r in ok:
        per_name[(r["company"], r["model"])].append(r["desc_valence"])
    sds = [statistics.stdev(v) for v in per_name.values() if len(v) > 2]
    sd = statistics.fmean(sds)
    print(f"  within one company and model, across repeated answers:")
    print(f"    mean SD of description valence : {sd:.3f} scale points")
    print(f"    median SD                      : {statistics.median(sds):.3f}")
    print(f"    range of SD across the {len(sds)} cells  : {min(sds):.3f} to {max(sds):.3f}")

    gap = effects[("en_word", "ALL")]["gap"]
    print(f"\n  the between-band effect we are trying to see (English word condition): {gap:.3f}")
    print(f"  one answer carries a standard deviation of                             : {sd:.3f}")
    if sd:
        print(f"  so a single answer is {sd/abs(gap):.1f}x the size of the effect" if gap else "")
        for n in (1, 3, 5, 10, 15, 20, 30, 50):
            se = sd / math.sqrt(n)
            print(f"    n={n:<3} standard error {se:.3f}   effect/SE = {abs(gap)/se:>5.1f}"
                  f"{'   <- detectable at 95%' if abs(gap)/se >= 1.96 else ''}")

    # ── 3. does the real word or the pseudoword leak more? ────────────────────────────────
    print("\n" + "=" * 78)
    print("3. REAL WORD AGAINST PSEUDOWORD: which one leaks its valence?")
    print(f"\n  {'concept':12} {'name val':>8} {'english':>8} {'pseudo':>8} {'polish':>8}   pseudo-minus-english")
    design = json.load(open(os.path.join(DATA, "name-design.json"), encoding="utf-8"))
    diffs = []
    for d in sorted(design, key=lambda x: x["valence"]):
        cell = {}
        for cond in ("en_word", "pseudo", "pl_word"):
            v = [r["desc_valence"] for r in ok if r["concept"] == d["en_word"] and r["condition"] == cond]
            cell[cond] = statistics.fmean(v) if v else float("nan")
        dd = cell["pseudo"] - cell["en_word"]
        diffs.append((d["valence"], dd))
        print(f"  {d['en_word']:12} {d['valence']:>8.2f} {cell['en_word']:>8.2f} {cell['pseudo']:>8.2f} "
              f"{cell['pl_word']:>8.2f}   {dd:>+8.2f}")

    print("\n  If the real word leaked more, low-valence concepts would show pseudo minus english > 0")
    lo_d = [d for v, d in diffs if v < 3.2]; hi_d = [d for v, d in diffs if v > 5.6]
    print(f"    low-valence concepts  mean difference {statistics.fmean(lo_d):+.3f}")
    print(f"    high-valence concepts mean difference {statistics.fmean(hi_d):+.3f}")

    # permutation test on the slope, English word condition, pooled
    e = effects[("en_word", "ALL")]
    xs = [k[1] for k in e["by"]]; ys = [statistics.fmean(v) for v in e["by"].values()]
    obs = abs(slope(xs, ys)); ge = 0
    for _ in range(B):
        sh = ys[:]; rng.shuffle(sh)
        if abs(slope(xs, sh)) >= obs:
            ge += 1
    print(f"\n  permutation test on the English-word slope: p = {(ge+1)/(B+1):.4f} ({B} shuffles)")

    json.dump({"noise_sd": sd,
               "effects": {f"{c}|{m}": {k: v for k, v in d.items() if k != "by"}
                           for (c, m), d in effects.items()}},
              open(os.path.join(DATA, "analysis.json"), "w"), indent=1)
    print(f"\nwrote {os.path.join(DATA,'analysis.json')}")


if __name__ == "__main__":
    main()
