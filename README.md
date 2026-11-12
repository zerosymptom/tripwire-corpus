# tripwire-corpus

The label data behind the numbers in
[legacy-tripwire](https://github.com/zerosymptom/legacy-tripwire), so that anyone
can recompute them instead of taking them on trust.

```bash
python3 scripts/reproduce.py
```

No dependencies. It reads `labels/labels.csv` and prints every figure the article
claims, including the ones that are unflattering.

## What is in here

`labels/labels.csv` — 185 rows, one per developer utterance across 30 sessions.

| column | meaning |
|---|---|
| `turn_id` | `T<session>-<turn>`; opaque, stable |
| `annotator_a` | the human's blind label: `ok` / `bad` |
| `a_late` | `1` if A judged the problem surfaced only after the fact |
| `annotator_b` | the model's independent blind label: `ok` / `bad` / `skip` |
| `axis` | `1` same-turn correction · `2` after-the-fact rework · blank if neither |
| `category` | public-taxonomy symptom (`S1`–`S7`), this project's residual classes (`X1`–`X8`), or `HUMAN` where the root cause was the person, not the agent |

`skip` marks utterances that were not a human speaking; they are out of the
denominator, which is where `n = 166` comes from.

## What is deliberately not in here

**The utterances themselves, the session identifiers, and the work-item names.**
They are internal records from a commercial codebase and include a colleague's
account name. They are not mine to publish, and no amount of interest in the
result changes that.

This is not much of a loss for reproduction: every number below is a function of
the labels alone. What you cannot do with this repo is *re-derive* the labels —
you would have to trust that they were applied honestly, or repeat the exercise
on material of your own. That is a real limitation and it is the main one.

## What the numbers say

| | |
|---|---|
| Raw agreement between the two annotators | **0.813** |
| Cohen's κ | **0.296** |
| Axis-2 failures the public taxonomy cannot hold | **10 of 24 (42%)** |

**On the κ.** 0.813 agreement sits close to the 0.78 reported by the public study
this work benchmarks against. The κ does not: at a ~15% positive rate, chance
agreement alone is 0.735, so two annotators can agree on four turns in five while
sharing almost no view of what counts as a failure.

That study reports percent agreement **rather than** Cohen's κ, and says so
explicitly, citing severe class imbalance. So the gap below is not an oversight
being exposed — it is what that stated caveat measures out to on comparable
material. Smaller claim, but one that survives contact with the paper.

The obvious explanation is that the two annotators were measuring different
things: A could see after-the-fact rework, B structurally could not. `reproduce.py`
tests it by recoding A's after-the-fact flags and re-measuring. κ moves **0.296 →
0.307**. So that is not the explanation. On the same axis, A flagged 24 and B
flagged 17, and they agreed on 8. They disagree about what a failure is.

**On the X classes.** Six of the eight rest on a single observation. One
observation is an anecdote. The one class with any support is the visibility
boundary — X1 rendering, X2 organisational knowledge, X3 the other team's
implementation — 6 of 166, sharing one root cause: *the information was never in
anything the agent could read*. Claims in the article should rest on that class
and on X8, which is a gap in the taxonomy's structure rather than a frequency
claim. They should not rest on "eight novel failure modes".

**On annotator B.** B is the same model being evaluated. For any category about
misreporting one's own work this is a conflict of interest with a predictable
direction, which is why `S7 = 0` here is treated as an artefact of the method and
never as a result.

## Licence

[CC BY 4.0](LICENSE). Cite it, correct it, argue with it.
