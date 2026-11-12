#!/usr/bin/env python3
"""Recompute every number this repo claims, from labels/labels.csv alone.

No dependencies. Run it:  python3 scripts/reproduce.py
"""
import csv
import pathlib
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent.parent
ROWS = list(csv.DictReader(open(ROOT / "labels/labels.csv", encoding="utf-8")))


def kappa(pairs):
    """Cohen's kappa for two raters over the same items."""
    n = len(pairs)
    agree = sum(1 for a, b in pairs if a == b)
    po = agree / n
    labels = {a for a, _ in pairs} | {b for _, b in pairs}
    pe = sum((sum(1 for a, _ in pairs if a == l) / n)
             * (sum(1 for _, b in pairs if b == l) / n) for l in labels)
    return n, agree, po, pe, (po - pe) / (1 - pe)


def line(title, pairs):
    n, agree, po, pe, k = kappa(pairs)
    a = sum(1 for x, _ in pairs if x == "bad")
    b = sum(1 for _, x in pairs if x == "bad")
    both = sum(1 for x, y in pairs if x == "bad" and y == "bad")
    print(f"  {title}")
    print(f"    n={n}  agreement={po:.3f}  Pe={pe:.3f}  kappa={k:.3f}"
          f"   A flagged {a}, B flagged {b}, both {both}")
    return k


print("=" * 74)
print("1. Inter-annotator agreement")
print("=" * 74)

# B is the model that was itself being judged; it marked 19 turns as not-a-human
# utterance. Those are out of the denominator, which is how the 166 arises.
scored = [r for r in ROWS if r["annotator_b"] != "skip"]

k_all = line("all turns, as originally reported",
             [(r["annotator_a"], r["annotator_b"]) for r in scored])

# Does the low kappa come from the two raters measuring different things?
# A flagged both same-turn corrections and after-the-fact rework; B could only
# ever see the former. Recode A's after-the-fact flags to 'ok' and re-measure.
k_axis1 = line("same-turn axis only (A's 'late' recoded to ok)",
               [("bad" if (r["annotator_a"] == "bad" and r["a_late"] == "0") else "ok",
                 r["annotator_b"]) for r in scored])

print(f"\n  >> aligning the task definition moved kappa {k_all:.3f} -> {k_axis1:.3f}"
      f"  ({k_axis1 - k_all:+.3f})")
print("     The axis mismatch does NOT explain the low agreement.")

late = [r for r in ROWS if r["a_late"] == "1"]
same = [r for r in scored if r["annotator_a"] == "bad" and r["a_late"] == "0"]
bflag = [r for r in ROWS if r["annotator_b"] == "bad"]
print(f"\n  A's {len(late)} after-the-fact flags -> B said {dict(Counter(r['annotator_b'] for r in late))}")
print(f"  A's {len(same)} same-turn flags       -> B said {dict(Counter(r['annotator_b'] for r in same))}")
print(f"  B's {len(bflag)} flags                 -> A said "
      f"{dict(Counter(('late' if r['a_late'] == '1' else r['annotator_a']) for r in bflag))}")

print()
print("=" * 74)
print("2. Category distribution")
print("=" * 74)
for axis in ("1", "2"):
    cats = Counter(r["category"] for r in ROWS if r["axis"] == axis)
    total = sum(cats.values())
    print(f"  axis {axis}  (n={total}): {dict(cats.most_common())}")

a2 = [r for r in ROWS if r["axis"] == "2"]
x = [r for r in a2 if r["category"].startswith("X")]
human = [r for r in a2 if r["category"] == "HUMAN"]
mapped = [r for r in a2 if r["category"].startswith("S")]
print(f"\n  axis 2: {len(mapped)} map onto the public taxonomy, "
      f"{len(x)} do not ({len(x) / len(a2):.0%}), {len(human)} are not the agent's fault")

print()
print("=" * 74)
print("3. How many of the X classes rest on a single observation")
print("=" * 74)
xc = Counter(r["category"] for r in ROWS if r["category"].startswith("X"))
singles = [c for c, n in xc.items() if n == 1]
print(f"  {dict(sorted(xc.items()))}")
print(f"  >> {len(singles)} of {len(xc)} X classes have n=1: {sorted(singles)}")
print("     A class resting on one observation is an anecdote, not a failure mode.")

vis = sum(n for c, n in xc.items() if c in ("X1", "X2", "X3"))
denom = len(scored)
p = vis / denom
print(f"\n  The one class with support is the visibility boundary (X1+X2+X3) = {vis}/{denom} = {p:.4f}")
print("  Sample size needed to see it again in fresh material:")
for n in (20, 45, 60, 80):
    print(f"    {n:3d} turns -> {1 - (1 - p) ** n:.0%} chance of at least one, "
          f"expected {n * p:.1f}")
print(f"  Singleton classes (p=1/{denom}): 20 turns -> "
      f"{1 - (1 - 1 / denom) ** 20:.0%}. Not testable at that size.")
print("=" * 74)
