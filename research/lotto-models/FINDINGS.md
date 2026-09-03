# Lotto against the models: results

**Run date:** 2026-09-01. **Arm:** English, web search off except Perplexity
(`sonar` searches by design). **Temperature:** provider default, never 0.
**Runs:** 200 per engine, four prompt paraphrases rotated, fresh context per
call, cells in randomised order.

Method and pre-registered expectations: `SPEC.md`, `PREDICTION.md`.
Every call verbatim in `data/raw_answers.jsonl`; counts in `data/counts.csv`;
metrics in `data/metrics.csv`.

---

## 1. Headline

**A lottery machine has no favourite number. Every model tested has several.**

`N_eff` is how many of the 49 numbers a source effectively uses. 49 is perfect
spread. The fair-RNG floor at this sample size is 46.

| source | balls | N_eff (of 49) | top number's share | outside the fair envelope |
|---|---|---|---|---|
| Polish Lotto, summer 1999 | 156 | **41.1** | 4.5% | no |
| Polish Lotto, summer 2026 | 234 | **41.4** | 4.3% | no |
| grok-4.5 | 1,200 | 18.0 | 9.6% | **yes** |
| claude-sonnet-5 | 1,176 | 13.5 | 14.4% | **yes** |
| mistral-large | 1,128 | 13.2 | 14.3% | **yes** |
| gpt-5.6-luna | 1,200 | 12.4 | 8.8% | **yes** |
| sonar (Perplexity) | 1,200 | 10.5 | 14.6% | **yes** |
| gemini-3.7-flash | 1,200 | 9.9 | 14.6% | **yes** |

Six engines out of six fall outside the envelope, and not marginally. The
worst uses a tenth of the wheel. Chi-square against uniform is p < 0.0001 for
every engine, against p = 0.98 and p = 0.68 for the two Lotto summers.

Read the comparison the right way. The machine is not avoiding anything and has
no preference to detect. That is what p = 0.98 means. The models produce a
strong preference. The contrast is *no favourite* against *a favourite*.

## 2. The finding that beats the headline

Asked 200 times for six numbers, a fair source returns 200 different tickets.
There are 13,983,816 of them.

| engine | distinct tickets in 200 asks | most frequent ticket | how often |
|---|---|---|---|
| gpt-5.6-luna | **8** | 7 14 22 31 38 46 | **50%** |
| mistral-large | 24 | 7 12 19 23 31 45 | 27% |
| sonar | 30 | 7 14 23 28 35 46 | **68%** |
| claude-sonnet-5 | 36 | 7 14 22 29 35 41 | 26% |
| gemini-3.7-flash | 36 | 7 14 23 31 42 48 | 38% |
| grok-4.5 | 93 | 7 14 23 31 42 48 | 22% |

Two things here.

**Every one of the six modal tickets opens on 7.** Six models, five companies,
one first number.

**Gemini and Grok return the identical ticket**, 7 14 23 31 42 48, as the most
common answer from each. Different vendors, different training runs, same six
numbers.

Perplexity gave the same six numbers in more than two thirds of all answers.
OpenAI's model produced eight distinct tickets in two hundred attempts.

## 3. The number 42

42 splits the field, which is the honest version of the story.

| engine | rank of 42 (of 49) | share |
|---|---|---|
| gemini-3.7-flash | 5th | 7.5% |
| grok-4.5 | 5th | 8.3% |
| mistral-large | 5th | 7.2% |
| claude-sonnet-5 | 8th | 4.8% |
| sonar | 30th | 0.2% |
| gpt-5.6-luna | **47th** | **0.0%, never once in 1,200 balls** |
| Polish Lotto 1999 | 48th | drawn once |
| Polish Lotto 2026 | 49th | drawn once |

Four engines over-pick 42 hard. Two do not touch it. Do not write "the models
love 42"; write that four of six do, and that one never picked it at all.

**42 landing last in both Lotto summers is chance.** With 49 numbers and a
small sample something must sit at the bottom, and twice it was 42. The machine
does not dislike 42. Saying otherwise would let a reader believe something false
in our favour.

**This study cannot say why.** 42 has an obvious cultural source, but nothing
here measures training-data frequency. Say "appears in 7.5% of answers", never
"because of Hitchhiker's".

## 4. Where the prediction was wrong

Registered in `PREDICTION.md` before the run.

| call | outcome |
|---|---|
| every engine below the fair floor | **right**, 6 of 6, N_eff 9.9 to 18.0 against a predicted 20 to 35 |
| 7 and 42 top-5 in at least three engines | **half right**. 7 is top-8 in all six. 42 is top-5 in three |
| 1–31 share above 63.3%, expected 68–78% | **wrong** |
| mean ball below 25.0 | **wrong** |
| ascending order over half the time | **right**, and further than expected |
| invalid rows under 5% | **right**, 0.0 to 2.0% |

**The birthday bias is not there.** Model shares of 1–31 run 63.8% to 68.0%
against the 63.3% a fair source gives, and the two Lotto summers sit at 67.3%
and 68.8%. The models are inside the same band as the machine. Mean ball is
24.4 to 27.0 against 25.0 expected. Whatever the models inherited from human
lottery text, it is not the human habit of marking birthdays.

This matters for the argument. The tell is not that models copy the specific
human bias. The tell is that they collapse onto a few remembered answers, which
is a different and stronger defect.

**Ascending order.** Five of six engines return the six numbers already sorted
almost every time: gemini 100%, gpt 100%, claude 99%, sonar 99%, grok 87%.
Mistral sorts 27% of the time and is the only engine that mostly does not. A
machine has no order. A model that always sorts is running a template.

## 5. Data quality

- 1,200 calls, 1,188 answered, 12 failed. All twelve are HTTP 429 rate limits on
  Mistral during the parallel run, a collection artifact, not model behaviour.
- Unparseable answers: claude 2.0%, mistral 6.0% (the 429s), every other engine
  0.0%. No answer contained a duplicate or an out-of-range number.
- Rows that returned two candidate sets ("wait, let me generate these more
  randomly") are flagged and excluded from the distribution, never repaired.
  `raw_answer` holds the verbatim text for every call, so any parse is checkable.

## 6. What this licenses saying, and what it does not

**Says:** a mechanical draw is indistinguishable from uniform in two separate
decades; six current models are not, by a wide margin; asked for a random
ticket they return a small set of remembered ones, and two rival engines return
the same one.

**Does not say:** why any model prefers a number; that any model is broken (none
was built as an RNG); that the lottery is a perfect RNG. What was tested is two
summers of one game, consistent with uniform at p = 0.98 and p = 0.68.

The Lotto figures are the operator's published draw statistics for
1 June – 31 August 1999 and 2026. They are not our collection.

## 7. The line for the post

An answer engine does not roll dice. Asked the same question, it reaches for the
answer it has reached for before. Six models, one first number.
