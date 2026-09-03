# Prediction, written before the model arm ran

Date: 2026-09-01. Registered before any model call, per SPEC §7.1.

## Baseline to beat

Polish Lotto, N_eff 41.1 (1999, 156 balls) and 41.4 (2026, 234 balls), out of 49.

## What I expect

| engine | N_eff, predicted | outside the envelope? |
|---|---|---|
| claude-sonnet-5 | 20 to 30 | yes |
| gpt-5.6-luna | 25 to 35 | yes |
| gemini-3.6-flash | 25 to 35 | yes |
| grok-4.5 | 25 to 35 | yes |

Every engine lands below the fair-RNG 5th percentile at 1,200 balls. None of them
comes close to 41.

## Specific calls

1. **7 and 42 are top-5 in at least three engines.** 7 is the human lucky number,
   42 is the Adams number, and both are heavily written down in the training text.
2. **The 1 to 31 share exceeds 63.3%.** Models inherit the birthday bias from human
   lottery text. I expect 68% to 78%.
3. **Mean below 25.0.** Low-number bias, following from the same tell.
4. **Ascending order in over half of answers**, and plausibly over 90%. A machine
   has no order; a model that sorts is running a template.
5. **Invalid rows under 5%.** The prompt is tight and the task is easy.

## What would falsify the story

Any engine with N_eff above 38 and a 1 to 31 share inside the fair band. If that
happens, name the engine and lead with it.
