#!/usr/bin/env python3
"""Does the model actually know the company, or is it writing fluent filler?

An earlier version of this analysis counted an answer as recognition when it carried a fact
longer than forty characters. That measures verbosity. A model will write a confident sentence
about a company it has never seen, and on the FT 1000 arm it does so constantly, so the length
rule scored 100 per cent recognition everywhere and told us nothing.

This scores recognition against ground truth instead. The FT 1000 record carries each company's
sector, and the model's ten attributes plus its one stated fact either land in that sector or
they do not. The mapping from FT sector label to accepted terms is written out below so a reader
can disagree with a specific line rather than with a black box.

The rule is deliberately generous: one matching term anywhere in the attributes or the fact
counts as a hit. A generous rule that still separates the two tiers is stronger evidence than a
strict one that might be separating them by strictness.

What this cannot do: verify that a fact is true in detail. A model that says a Lithuanian
payments firm does payments scores a hit whether or not the rest of the sentence is invented.
So read this as topical recognition, the weakest useful form, and treat it as an upper bound on
how much these models really know about a company of this size.

    python3 recognition.py
"""
import collections, csv, json, math, os, re, statistics

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# FT sector label -> terms that count as landing in that sector.
SECTOR_TERMS = {
    "IT & Software": ["software", "saas", "it", "tech", "technology", "platform", "digital",
                      "cloud", "data", "app", "developer", "automation", "ai", "computing"],
    "Fintech, Financial Services & Insurance": ["fintech", "financial", "finance", "payments",
                                                "payment", "banking", "bank", "insurance",
                                                "lending", "credit", "card", "invoice", "wealth"],
    "Professional, Scientific & Technical Services": ["consulting", "consultancy", "advisory",
                                                      "engineering", "research", "professional",
                                                      "services", "scientific", "technical"],
    "Energy & Utilities": ["energy", "power", "electricity", "solar", "renewable", "utilities",
                           "utility", "grid", "heating", "gas", "battery", "charging"],
    "Wholesale": ["wholesale", "distribution", "distributor", "supply", "trading", "supplier"],
    "Advertising & Marketing": ["advertising", "marketing", "agency", "brand", "media", "creative",
                                "campaign", "seo", "communications"],
    "Electrical Manufacturing": ["manufacturing", "manufacturer", "electrical", "electronics",
                                 "industrial", "hardware", "equipment", "components", "production"],
    "Media & Telecommunications": ["media", "telecom", "telecommunications", "broadcasting",
                                   "publishing", "content", "network", "connectivity"],
    "Health Care & Life Sciences": ["health", "healthcare", "medical", "clinical", "pharma",
                                    "pharmaceutical", "biotech", "life", "patient", "care",
                                    "diagnostics", "wellness"],
    "Automotive": ["automotive", "car", "vehicle", "cars", "mobility", "motor", "fleet"],
    "Logistics & Transportation": ["logistics", "transport", "transportation", "shipping",
                                   "delivery", "freight", "courier", "warehousing", "supply"],
    "Ecommerce": ["ecommerce", "commerce", "online", "retail", "marketplace", "shop", "shopping",
                  "store", "dtc"],
    "Retail": ["retail", "retailer", "store", "shop", "consumer", "shopping", "grocery"],
    "Apparel & Fashion": ["apparel", "fashion", "clothing", "wear", "textile", "footwear",
                          "garments", "style"],
    "Waste Management & Recycling": ["waste", "recycling", "circular", "environmental",
                                     "sustainability", "sustainable", "reuse"],
    "Education & Social Services": ["education", "learning", "training", "school", "edtech",
                                    "students", "social", "courses"],
    "Food & Beverages": ["food", "beverage", "drinks", "restaurant", "catering", "grocery",
                         "nutrition", "brewing", "coffee"],
    "Hospitality & Travel": ["hospitality", "travel", "tourism", "hotel", "booking", "leisure",
                             "flights", "accommodation"],
}

W = {r["Word"]: float(r["V.Mean.Sum"])
     for r in csv.DictReader(open(os.path.join(DATA, "warriner-2013-valence.csv"), encoding="utf-8"))
     if r["V.Mean.Sum"]}

HEDGE = re.compile(r"\b(fictional|unknown|not (?:a )?(?:widely |publicly )?(?:known|recognis|recognized)"
                   r"|no (?:public|specific|verifiable) information|unverified|nonexistent|hypothetical"
                   r"|does not appear to (?:exist|be)|unable to (?:find|verify|confirm)|i (?:do not|don't) have"
                   r"|little(?: publicly available)? information|obscure|undocumented)\b", re.I)


def valence(attrs):
    v = [W[a] for a in attrs if a in W]
    return statistics.fmean(v) if v else float("nan")


def sector_hit(row):
    """Generous topical match: one accepted term anywhere in the attributes or the fact."""
    terms = SECTOR_TERMS.get(row.get("sector") or "")
    if not terms:
        return None
    blob = " ".join(row["attributes"]) + " " + (row.get("fact") or "").lower()
    return any(re.search(rf"\b{re.escape(t)}\b", blob) for t in terms)


def main():
    rows = [json.loads(l) for l in open(os.path.join(DATA, "responses-real-v2.jsonl"), encoding="utf-8")
            if l.strip()]
    ok = [r for r in rows if r["status"] == "ok"]
    for r in ok:
        r["dv"] = valence(r["attributes"])
        r["hedged"] = bool(HEDGE.search(r.get("fact") or ""))
        r["sector_ok"] = sector_hit(r)
    ok = [r for r in ok if not math.isnan(r["dv"])]
    print(f"{len(rows):,} answers, {len(rows)-len(ok)} unusable, {len(ok):,} scored")

    print("\n" + "=" * 76)
    print("1. RECOGNITION, MEASURED THREE WAYS")
    print(f"\n  {'tier':8} {'model':7} {'answers':>8} {'has a fact':>11} {'hedges':>8} {'sector correct':>15}")
    for tier in ("leader", "ft1000"):
        for m in ("gemini", "claude", "gpt"):
            s = [r for r in ok if r.get("tier") == tier and r["model"] == m]
            if not s:
                continue
            fact = sum(1 for r in s if len(r.get("fact") or "") > 40) / len(s)
            hedge = sum(1 for r in s if r["hedged"]) / len(s)
            sec = [r for r in s if r["sector_ok"] is not None]
            secr = (sum(1 for r in sec if r["sector_ok"]) / len(sec)) if sec else float("nan")
            print(f"  {tier:8} {m:7} {len(s):>8} {fact:>10.1%} {hedge:>8.1%} "
                  f"{'n/a' if math.isnan(secr) else f'{secr:>14.1%}'}")
    print("\n  'has a fact' is the length rule the first pass used. It saturates at 100% and")
    print("  separates nothing, which is why sector correctness replaced it.")

    print("\n" + "=" * 76)
    print("2. DESCRIPTION VALENCE BY TIER")
    for tier in ("leader", "ft1000"):
        s = [r for r in ok if r.get("tier") == tier]
        by = collections.defaultdict(list)
        for r in s:
            by[(r["brand"], r["model"])].append(r["dv"])
        sd = [statistics.stdev(v) for v in by.values() if len(v) > 2]
        print(f"  {tier:8} n={len(s):>5}  mean valence {statistics.fmean(r['dv'] for r in s):.2f}  "
              f"within-brand SD {statistics.fmean(sd):.3f}")

    print("\n" + "=" * 76)
    print("3. THE QUESTION: does valence depend on whether the model knows the company?")
    ft = [r for r in ok if r.get("tier") == "ft1000" and r["sector_ok"] is not None]
    for lab, sub in (("model got the sector right", [r for r in ft if r["sector_ok"]]),
                     ("model got the sector wrong", [r for r in ft if not r["sector_ok"]])):
        if sub:
            print(f"  {lab:28} n={len(sub):>5}  valence {statistics.fmean(r['dv'] for r in sub):.2f}  "
                  f"hedged {sum(1 for r in sub if r['hedged'])/len(sub):.1%}")

    print("\n" + "=" * 76)
    print("4. THE COMPANIES THE MODELS DO NOT KNOW")
    per = collections.defaultdict(list)
    for r in ft:
        per[r["brand"]].append(r)
    unknown = sorted(((sum(1 for x in v if x["sector_ok"]) / len(v), b, v) for b, v in per.items()))
    print(f"  {'brand':26} {'market':12} {'sector correct':>14} {'valence':>8}  sector")
    for rate, b, v in unknown[:18]:
        print(f"  {b[:25]:26} {v[0]['market'][:11]:12} {rate:>13.0%} "
              f"{statistics.fmean(x['dv'] for x in v):>8.2f}  {v[0]['sector'][:28]}")
    known = [x for x in unknown if x[0] >= 0.9]
    print(f"\n  {len(known)} of {len(per)} FT 1000 companies are placed in the right sector "
          f"by 90% or more of answers")

    json.dump([{k: v for k, v in r.items() if k != "attributes"} for r in ok],
              open(os.path.join(DATA, "scored-real-v2.json"), "w"), indent=0)
    print(f"\nwrote {os.path.join(DATA,'scored-real-v2.json')}")


if __name__ == "__main__":
    main()
