#!/usr/bin/env python3
"""The same question as probe.py, asked of 66 real companies from 11 European markets.

WHY REAL BRANDS. The fictional-name study establishes that an LLM reads a company name as a
word and describes the word, and that the leak is lexical (a pseudoword one letter away keeps
only a quarter of it) and survives translation (a Polish name carries its Polish meaning into
an English answer, on Gemini). Peec AI's finding on 904 real brands adds the boundary
condition: the effect only appears on brands the model does not recognise.

That boundary is the interesting claim and it has not been tested where it matters most, on
real companies whose names are ordinary words in their own language. Skoda is the case that
makes the question concrete: `skoda` means a pity, a shame, damage in Czech, and Skoda Auto is
a household name across Europe. If recognition protects a brand, nothing of that meaning should
reach the description. If anything leaks on a brand that famous, the protection is partial and
every smaller company in the region is exposed.

TWO MEASUREMENTS PER BRAND, from the same answers.

  description  ten attributes, scored on Warriner, Kuperman and Brysbaert (2013), the same
               norms Peec used, so the numbers stay comparable across all three studies.
  recognition  whether the model produces a specific, checkable fact about the company. A
               model that knows Kesko names groceries and Finland; a model that does not
               describes the word or hedges. Recognition is the moderator the whole question
               turns on, so it is measured rather than assumed from brand fame.

The name's own valence comes from a separate step (gloss.py) that asks three models what the
name means in its home language and keeps only what they agree on, with the model under
measurement excluded from its own gloss.

    export GEMINI_API_KEY=... ANTHROPIC_API_KEY=... OPENAI_API_KEY=...
    python3 probe_real.py --iterations 10
"""
import argparse, concurrent.futures, json, os, re, sys, threading, time
import urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

PROMPT = ("Describe the company {brand} in exactly 10 single-word attributes, then state one "
          "specific fact about what it does.\n"
          "Return only JSON: {{\"attributes\": [10 lowercase English words], \"fact\": \"one sentence\"}}")

# Latest generally-available model from each vendor as of 12 August 2026. Both tiers of brand
# are run on the same three, because the comparison this study turns on is recognised against
# unrecognised, and a model change between the two arms would confound exactly that.
MODELS = [("gemini", "google", "gemini-3.6-flash"),
          ("claude", "anthropic", "claude-sonnet-5"),
          ("gpt", "openai", "gpt-4.1")]


class Failed(Exception):
    """The call did not return a usable object."""


def _post(url, payload, headers, timeout=90):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json", **headers})
    with urllib.request.urlopen(req, timeout=timeout) as fh:
        return json.load(fh)


def _parse(text):
    if not text:
        raise Failed("empty")
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise Failed("no complete object")
    try:
        d = json.loads(m.group(0))
    except json.JSONDecodeError as e:
        raise Failed(f"unparseable: {e}")
    attrs = [re.sub(r"[^a-z]", "", str(x).lower()) for x in (d.get("attributes") or [])]
    attrs = [a for a in attrs if a]
    if len(attrs) < 5:
        raise Failed(f"only {len(attrs)} usable attributes")
    return attrs, str(d.get("fact") or "")


def call_google(model, brand):
    key = os.environ["GEMINI_API_KEY"]
    d = _post(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}",
              {"contents": [{"parts": [{"text": PROMPT.format(brand=brand)}]}],
               "generationConfig": {"maxOutputTokens": 2048}}, {})
    cand = (d.get("candidates") or [None])[0]
    if not cand:
        raise Failed("no candidate")
    if cand.get("finishReason") not in (None, "STOP"):
        raise Failed(f"finishReason={cand['finishReason']}")
    return _parse("".join(p.get("text", "") for p in cand.get("content", {}).get("parts", [])))


def call_anthropic(model, brand):
    d = _post("https://api.anthropic.com/v1/messages",
              {"model": model, "max_tokens": 2048,
               "messages": [{"role": "user", "content": PROMPT.format(brand=brand)}]},
              {"x-api-key": os.environ["ANTHROPIC_API_KEY"], "anthropic-version": "2023-06-01"})
    if d.get("stop_reason") not in (None, "end_turn", "stop_sequence"):
        raise Failed(f"stop_reason={d['stop_reason']}")
    return _parse("".join(b.get("text", "") for b in d.get("content", []) if b.get("type") == "text"))


def call_openai(model, brand):
    d = _post("https://api.openai.com/v1/chat/completions",
              {"model": model, "max_tokens": 2048,
               "messages": [{"role": "user", "content": PROMPT.format(brand=brand)}]},
              {"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}"})
    ch = d["choices"][0]
    if ch.get("finish_reason") not in (None, "stop"):
        raise Failed(f"finish_reason={ch['finish_reason']}")
    return _parse(ch["message"]["content"])


VENDOR = {"google": call_google, "anthropic": call_anthropic, "openai": call_openai}


def ask(vendor, model, brand):
    """Temperature left at the vendor default: the spread of repeated answers is part of what
    this measures. A failed call is recorded as a failure, never as an empty result."""
    last = ""
    for attempt in range(3):
        try:
            attrs, fact = VENDOR[vendor](model, brand)
            return attrs, fact, "ok"
        except Failed as e:
            last = str(e)
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, TimeoutError) as e:
            last = f"{type(e).__name__}: {str(e)[:90]}"
        time.sleep(1.5 * (attempt + 1))
    return [], "", f"failed: {last}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--iterations", type=int, default=10)
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--brands", default="brands-combined.json")
    ap.add_argument("--out", default="responses-real-v2.jsonl")
    a = ap.parse_args()
    for k in ("GEMINI_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_API_KEY"):
        if not os.environ.get(k):
            sys.exit(f"missing {k}")

    brands = json.load(open(os.path.join(DATA, a.brands), encoding="utf-8"))
    jobs = [{**b, "model": mid, "vendor": v, "model_id": m, "iteration": i}
            for b in brands for mid, v, m in MODELS for i in range(a.iterations)]
    print(f"{len(brands)} brands x {len(MODELS)} models x {a.iterations} iterations = {len(jobs)} calls",
          flush=True)

    cache = os.path.join(DATA, a.out)
    done = set()
    if os.path.exists(cache):
        for ln in open(cache, encoding="utf-8"):
            if ln.strip():
                r = json.loads(ln)
                done.add((r["brand"], r["model"], r["iteration"]))
        print(f"  resuming, {len(done)} already collected")
    todo = [j for j in jobs if (j["brand"], j["model"], j["iteration"]) not in done]

    lock = threading.Lock(); n = {"d": 0, "f": 0}

    def work(j, fh):
        attrs, fact, status = ask(j["vendor"], j["model_id"], j["brand"])
        with lock:
            fh.write(json.dumps({**j, "attributes": attrs, "fact": fact, "status": status},
                                ensure_ascii=False) + "\n")
            fh.flush()
            n["d"] += 1; n["f"] += status != "ok"
            print(f"  {n['d']}/{len(todo)}  failures {n['f']}", end="\r", flush=True)

    if todo:
        with open(cache, "a", encoding="utf-8") as fh:
            with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:
                list(pool.map(lambda j: work(j, fh), todo))
        print()
    print(f"wrote {cache}")


if __name__ == "__main__":
    main()
