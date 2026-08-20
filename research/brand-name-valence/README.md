# Does an AI describe your company, or your company's name?

Ask a model to describe a company and it answers on the evidence it has. Ask it
about a company whose name happens to sound unpleasant, and part of the answer
turns out to be about the name.

This study measures how much. It scores how pleasant a brand name *sounds*
independently of the company, then measures how far the model's description of
the company moves with it.

**Dataset:** [10.5281/zenodo.21904654](https://doi.org/10.5281/zenodo.21904654) (CC BY 4.0)
**Published:** August 2026

## Design

9,600 model answers, no failures.

| | |
|---|---|
| Real companies | 264, across 21 home markets |
| Invented companies | pseudoword names matched to the real ones for length and phonology |
| Answers about invented names | 1,350 |
| Answers about real companies | 8,250 |
| Models | Gemini, Claude, GPT |
| Name conditions | English word, pseudoword, Polish word |

Every brand name carries a valence score for the *word*, judged without the
company attached. The outcome is the valence of the model's description of the
*company*. Names scoring below 3.2 form the low band, above 5.6 the high band,
and the gap between the two bands is the effect: scale points of description
that come from the name rather than the firm.

## What it found

The noise floor first, because nothing below it counts: asking the same model
about the same company repeatedly moves the description by **0.28 scale points**
on average. That is the bar every number below has to clear.

Gap between unpleasant-sounding and pleasant-sounding names, in scale points:

| Model | English word | Pseudoword | Polish word |
|---|---:|---:|---:|
| Gemini | **+3.10** | +0.95 | +2.93 |
| Claude | +1.81 | +0.42 | +0.73 |
| GPT | +0.89 | −0.00 | −0.04 |

Gemini's description of a company moves **3.10 points** on a seven-point scale
with nothing changing but how agreeable its name sounds in English, eleven times
the noise floor. GPT shows nothing outside English: −0.00 on pseudowords and
−0.04 on Polish words, both inside the noise.

Two secondary results:

- **Refusal is not evenly distributed.** Claude declines or hedges on 19% of
  invented companies. Gemini and GPT hedge on 0%: they describe a company that
  does not exist as readily as one that does.
- **Knowing the sector is not the same as knowing the company.** Asked to name
  the industry of a real company, Gemini is right 75.1% of the time, GPT 67.9%,
  Claude 67.4%, over 175 scored answers.

## Reproducing it

```bash
export GEMINI_API_KEY=...  ANTHROPIC_API_KEY=...  OPENAI_API_KEY=...

python scripts/probe.py        # invented companies, three name conditions
python scripts/probe_real.py   # the 264 real companies
python scripts/recognition.py  # sector-recall check
python scripts/analyse.py      # bands, gaps, noise floor
```

The scripts read only from environment variables and write their raw output
next to themselves. `data/` here holds the analysed results, small enough to
read in a diff; the raw answers are in the Zenodo deposit.

| File | What it is |
|---|---|
| `data/analysis.json` | slopes, correlations and band means per condition and model |
| `data/deck-numbers.json` | the figures quoted above |
| `data/wordname-summary.json` | per-brand name valence, description valence, recognition and hedge rate |
| `data/industry-accuracy-by-company.csv` | sector-recall scoring, per company |

## Citing

```bibtex
@dataset{zatuchin2026namevalence,
  author    = {{\.Z}atuchin, Dmitrij},
  title     = {Does an AI describe your company, or your company's name?
               9,600 model answers about invented and real companies},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.21904654}
}
```
