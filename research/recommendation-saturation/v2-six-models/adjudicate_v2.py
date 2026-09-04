#!/usr/bin/env python3
"""Open-arm adjudication per PREREGISTRATION-V2.md: pooled per query, blind to
engine, one written rule. Keeps only organizations offering the queried
category; canonical = organization (product lines collapse to it). Output:
data/adjudicated.json {query_key: {candidate: canonical}}.
"""
import json
import re
import sys
import time
from pathlib import Path

import requests

HERE = Path(__file__).parent
ENV_FILES = [Path("/Users/diz/dev/rankfor/ai-territory/open-site/.env"),
             Path("/Users/diz/dev/rankfor/backend/.env")]


def env(key):
    for p in ENV_FILES:
        for line in p.read_text().splitlines():
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise KeyError(key)


RULE = """A candidate counts only if it names an ORGANIZATION that offers the queried product
or service category. Excluded: loyalty programs, information sources, regulators, media
outlets, generic phrases, people, places, technologies, and product lines of an organization
that is itself in the list (a product line maps to its organization: canonical for "Zoho CRM"
is "Zoho"). Operating brands collapse to the parent organization only when one is a documented
subsidiary of the other; otherwise keep the brand as its own canonical."""


def call_gemini(prompt, retries=5):
    for a in range(retries):
        try:
            r = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.7-flash:generateContent",
                headers={"x-goog-api-key": env("GEMINI_API_KEY1")},
                json={"contents": [{"parts": [{"text": prompt}]}],
                      "generationConfig": {"temperature": 0,
                                           "responseMimeType": "application/json"}},
                timeout=180)
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            if a == retries - 1:
                raise
            time.sleep(2 ** a)


def main():
    cands = json.load(open(HERE / "data" / "candidates_raw.json"))
    out_path = HERE / "data" / "adjudicated.json"
    out = json.load(open(out_path)) if out_path.exists() else {}
    for qkey, cmap in cands.items():
        if qkey in out:
            continue
        industry, qidx, qtext = qkey.split("|", 2)
        pool = sorted(
            (t for t, c in cmap.items()
             if c >= 2 or len(t.split()) >= 2 or re.search(r"[&\d]", t)),
            key=lambda t: -cmap[t])
        keep = {}
        CH = 900
        for i in range(0, len(pool), CH):
            chunk = pool[i:i + CH]
            prompt = (f"Buying question (industry: {industry}): \"{qtext}\"\n\n"
                      f"Rule:\n{RULE}\n\n"
                      "From the candidate strings below (mined from AI answers to this "
                      "question), return ONLY the ones that satisfy the rule, as a JSON "
                      "array of objects {\"candidate\": str, \"canonical\": str} where "
                      "canonical is the offering organization's name. Include every "
                      "distinct string variant that refers to a kept organization "
                      "(e.g. both \"HubSpot\" and \"HubSpot CRM\" map to \"HubSpot\"). "
                      "Return [] if none qualify. No commentary.\n\nCANDIDATES:\n"
                      + "\n".join(chunk))
            txt = call_gemini(prompt)
            try:
                arr = json.loads(txt)
            except json.JSONDecodeError:
                m = re.search(r"\[.*\]", txt, re.S)
                arr = json.loads(m.group(0)) if m else []
            for o in arr:
                c, can = o.get("candidate"), o.get("canonical")
                if c and can and c in cmap:
                    keep[c] = can.strip()
        out[qkey] = keep
        json.dump(out, open(out_path, "w"), ensure_ascii=False, indent=0)
        print(f"{industry}/{qidx}: {len(keep)} accepted of {len(pool)} pooled "
              f"({len(set(keep.values()))} organizations)", flush=True)
    print("adjudication complete")


if __name__ == "__main__":
    main()
