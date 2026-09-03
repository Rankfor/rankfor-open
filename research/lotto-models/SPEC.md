# Lotto against the models

**What it measures:** a real lottery machine and a language model are both asked
for six numbers from 1 to 49. One of them has no opinion. The other has a
favourite.

**Why this design is strong:** the baseline is not theoretical. Polish Lotto is a
mechanical, audited draw, and we hold two independent summers of it, 27 years
apart. That gives an *empirical* null distribution, so nobody can argue about what
"random enough" looks like at small sample sizes.

**Status:** baseline data collected and verified. Model arm not yet run.

---

## 1. The finding already in hand

Two summers of Polish Lotto, taken from the official draw statistics.

| | draws | balls | chi-square vs uniform | N_eff (of 49) | 42 |
|---|---|---|---|---|---|
| 1 Jun – 31 Aug **1999** | 26 | 156 | chi2=29.9, df=48, **p=0.98** | 41.1 | 1 time, rank **48/49** |
| 1 Jun – 31 Aug **2026** | 39 | 234 | chi2=42.8, df=48, **p=0.68** | 41.4 | 1 time, rank **49/49** |

Both summers are statistically indistinguishable from uniform. The machine is
fair, in 1999 and again in 2026.

**And in both, 42 sat at the bottom.** Least drawn of all 49 numbers in 2026,
second-least in 1999.

Meanwhile 42 is the number language models reach for more than any other.

### Say this correctly

The machine does not *avoid* 42. It has no opinion at all, which is precisely what
p=0.98 and p=0.68 mean. With 49 numbers and a small sample, something has to land
at the bottom, and this time it was 42, twice. That is noise behaving exactly as
noise should.

**The contrast is not "the machine dislikes 42 and the models like it."** It is:
*the machine produces no favourite, and the models produce a strong one.* Write it
that way. The naive version is wrong and a statistician in the comments will say so.

---

## 2. The model arm

### Prompt

```
Give me six different random numbers between 1 and 49.
Answer with the six numbers only, separated by commas.
```

Paraphrases for robustness, ~40 runs each:

```
Pick six lottery numbers between 1 and 49.
I need 6 random numbers from 1 to 49. Just the numbers.
Generate six unique random integers in the range 1-49.
```

### Cells

```
engines (n) x languages (EN, PL) x n_runs (200)
```

200 runs = 1,200 balls per cell, five times the 2026 baseline, so the model's
distribution is far better resolved than the lottery's. That asymmetry is fine and
should be stated: we are giving the models every chance to look random.

### Controls

- **Fresh context every call.** One call, one answer, no conversation carryover.
  This is the easiest way to invalidate the study.
- **Default temperature**, recorded. Never 0: that measures the mode, not the
  distribution, and the distribution is the entire point.
- **Record the exact model version string** and date per call.
- Both arms if the engine supports it: web search off, then on.
- Run cells in randomised order so a mid-run model update does not land on one
  engine.

### What to record

One row per call: `ts, engine, model_version, language, prompt_variant,
raw_answer, parsed[6], n_parsed, invalid_reason, refused, latency_ms`.

Parsing rules, decided before the run:

- Fewer or more than six numbers → keep the row, flag `n_parsed`, exclude from the
  distribution, report the rate.
- Duplicates within one answer → the prompt asked for different numbers, so this
  is a failure mode worth counting. Report `duplicate_rate` separately.
- Out of range (0, 50+) → same treatment.
- Refusals are data. Report them; never drop silently.

---

## 3. Analysis

Compute per cell, and for each Lotto year.

```
counts[1..49]
share_i  = count_i / total_balls
HHI      = sum(share_i ** 2)
N_eff    = 1 / HHI                       # of a possible 49
chi2, p  = chisquare(counts, expected = total/49)
```

### The envelope

A fair source at small n is *lumpy*, and the study lives or dies on accounting for
that. Simulated, 20,000 runs of a fair RNG:

| sample | top number, median | top, 95th pct | N_eff median | N_eff 5th pct |
|---|---|---|---|---|
| 156 balls (1999 size) | 8 | 10 | 37.7 | 34.6 |
| 234 balls (2026 size) | 10 | 13 | 40.8 | 38.3 |

Real Lotto landed at N_eff 41.1 and 41.4, comfortably inside.

**A model is outside the envelope** if, at its own sample size, `N_eff` falls
below the 5th percentile or its top count exceeds the 95th. Re-run the simulation
at the model's actual ball count; do not reuse the numbers above.

### Headline metric

`N_eff` again, on a scale everyone understands because the ceiling is visible:
**49 is the maximum, the machine got 41, the model got X.**

Report also: top-1 share, top-6 share, and the rank of 42 in every source.

### Secondary tests worth running

1. **The 1-31 tell.** Humans over-pick the birthday range. Do models? Compare the
   share of balls in 1–31 against the 31/49 = 63.3% expected. A model well above
   that has inherited the human bias; the Lotto years give the fair baseline.
2. **Low-number bias.** Mean of drawn numbers, model against 25.0 expected.
3. **Ascending order.** How often the six come back already sorted. A machine has
   no order; a model that always sorts is revealing template behaviour, not
   randomness.
4. **English against Polish.** Same engine, translated prompt. Bootstrap the
   difference in `N_eff`, 10,000 resamples, report the 95% interval.

---

## 4. Interpretation rules

**What this shows.** That the mechanical draw is indistinguishable from uniform in
two separate decades, and whether the models are.

**What it does not show.** *Why* a model favours a number. 42 has an obvious
cultural source, but this design does not measure training-data frequency and
cannot attribute cause. Say "appears in N% of answers", never "because of
Hitchhiker's".

**Do not claim the lottery is a perfect RNG.** Claim what was tested: two summers,
one game, consistent with uniform at p=0.98 and p=0.68. That is a strong, narrow,
defensible statement.

**If a model comes out random**, that is the headline for that model. AI Mode came
close in the prior number study; if one engine passes here, name it and say so.

---

## 5. Publication guardrails

1. **Numbers, not people.** No lottery player is identified, no company is
   characterised. This study has almost no ethical surface, which is part of why
   it is a good one to publish.
2. **Every visual carries the method line**: draws, balls, engines, runs, arm,
   language, date.
3. **Publish the counts.** Both Lotto tables are public record and the model counts
   should be too, so anyone can recompute.
4. **State the coincidence explicitly.** 42 landing lowest twice is chance, and the
   post must say so. Letting a reader believe the machine dislikes 42 would be
   letting them believe something false in our favour.
5. **Do not present the Lotto data as our own collection.** It is the operator's
   published draw statistics; cite it as such with the date range.

---

## 6. The visual

Brand tokens from `rankfor-ops/brand/visual-system.md`: ink `#010101`, mint
`#00DDC7`, Fustat for headline, DM Sans for body. Mint is signal, never
decoration. A number is a headline. Ink ground, because the card competes in a
light feed.

**Canvas 1200x1500 (4:5).** Maximum column height on LinkedIn mobile and desktop.

### The chart

Three stacked strips, 1 to 49 on a shared axis, one row per source:

```
POLISH LOTTO, SUMMER 1999      26 draws   ....bars....
POLISH LOTTO, SUMMER 2026      39 draws   ....bars....
[ENGINE], ASKED 200 TIMES                 ....bars....
```

The first two rows read as flat noise. The third should visibly spike. Mark 42 on
all three rows with a single mint rule running the full height, so the eye lands on
the same column in every strip and does the comparison itself.

```
headline   "A lottery machine has no favourite number. The models do."
big number "49 → 41 → X"  labelled "effective numbers, out of 49"
footnote   "Lotto: official draw statistics, 1 Jun–31 Aug 1999 and 2026.
            Models: 200 runs each, web search off, September 2026."
```

### Build notes

- Render at 2x and downsample; LinkedIn recompresses hard.
- Measure text width against its box before drawing. Overflow is the most common
  defect in these cards.
- Check at 25% zoom. If the spike and the headline do not survive, simplify.
- Do not colour the Lotto rows mint. They are the baseline; grey them and let mint
  mark only the model spike and the 42 rule.

---

## 7. Run order

1. Write `PREDICTION.md`: which engines will fail, and what N_eff you expect.
2. Pilot one engine, 30 runs, inspect raw answers by hand. Fix parsing before scaling.
3. Full run, all engines, EN first.
4. Recompute the envelope at the actual ball counts.
5. Compute metrics, bootstrap the language difference.
6. Build the chart, check the method line against real run counts.
7. Add Polish.

## 8. Deliverables

```
data/lotto_1999.txt, lotto_2026.txt    verified: 156 and 234 balls
data/raw_answers.jsonl                 every model call, verbatim
data/counts.csv                        1..49 per source
data/metrics.csv                       N_eff, chi2, p, top1, rank_of_42
PREDICTION.md                          before the run
FINDINGS.md                            with the coincidence stated plainly
visuals/                               1200x1500, method line on each
```

## 9. Known ways this goes wrong

| Symptom | Cause |
|---|---|
| model looks random | too few runs; the envelope is wide at small n, re-check against the simulation at your actual count |
| lots of invalid rows | the model is returning prose; tighten the prompt, do not silently parse around it |
| duplicates inside one answer | a real failure mode, count it rather than dedupe it away |
| 1999 has 48 numbers, not 49 | 44 was never drawn that summer; that is a true zero, keep it |
| results shift mid-run | model version changed; that is why the version is logged per call |
