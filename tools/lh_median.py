#!/usr/bin/env python3
"""B1-05 / D-06 repair — report Lighthouse scores as the MEDIAN of the kept runs.

`tests/run_all.sh` summarised Lighthouse by reading the *first* run's JSON file and printing it
under the label "median of 3 runs per page", which is not what the file contains (B1-04 defect
D-06 / E-1: the summary quoted a 99 while the raw log recorded 99/100/100 -> median 100). This
helper takes every per-run JSON file and prints, per category, the median, all individual values
and the min/max spread, so the reported number is the real median and the spread stays auditable.

It also applies the A5 bar (`median >= 90` on every category) and exits non-zero if any median is
below it — the threshold is never relaxed here.

B2-05b / N4 — ONE DEFINITION OF "THE MEDIAN", IN BOTH PLACES. `tests/run_lighthouse.sh` used to
take the lower-middle value for an even n (`awk 'NR==int((n+1)/2)'`): for the 8 index runs
69,72,84,88,97,98,98,99 it printed 88 and FAILED the step, while this file printed 92
(`statistics.median`) and PASSED the same criterion in the same run — so the suite ended FAIL
while its own A5 line said PASS and no acceptance number could be written. Both places now call
`median_of()` below, and the convention is printed with every report. run_lighthouse.sh also makes
the run count ODD by construction (an even count has two middle values and is the whole reason the
two readings could disagree); the 90 threshold does not move.

Usage: python3 tools/lh_median.py <run1.json> [run2.json ...]
       python3 tools/lh_median.py --median-of 88 92 97     # the same median, for shell callers
       python3 tools/lh_median.py --convention             # the convention, named, for logs
Exit 0 = every category's median >= 90 (or --no-threshold and no JSON at all is a caller error).
"""
import json
import re
import statistics
import sys

CATEGORIES = ["performance", "accessibility", "best-practices", "seo"]
THRESHOLD = 90

# The single definition both halves of the suite report under. Named here once so the step log and
# the summary cannot drift apart again.
MEDIAN_CONVENTION = ("median = the standard median of the sorted runs (for an odd count, the middle "
                     "measured run; for an even count, the mean of the two middle values). "
                     "run_lighthouse.sh keeps the count odd, so the reported median is always a "
                     "single measured run.")


def median_of(values: list[int]) -> int:
    """The one median. `tools/lh_median.py` and `tests/run_lighthouse.sh` both resolve here."""
    return int(statistics.median(values))


def scores(path):
    with open(path) as fh:
        data = json.load(fh)
    out = {}
    for cat in CATEGORIES:
        node = data.get("categories", {}).get(cat)
        if node is None or node.get("score") is None:
            out[cat] = None
        else:
            out[cat] = round(node["score"] * 100)
    return out


def main(argv):
    if argv[:1] == ["--convention"]:
        print(MEDIAN_CONVENTION)
        return 0
    if argv[:1] == ["--median-of"]:
        values = [int(v) for v in argv[1:] if re.fullmatch(r"-?\d+", v)]
        if not values:
            print("lh_median: --median-of needs at least one integer", file=sys.stderr)
            return 2
        print(median_of(values))
        return 0
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        print("lh_median: no Lighthouse run JSON given", file=sys.stderr)
        return 2
    runs = [scores(f) for f in files]
    print(f"runs kept      : {len(files)}")
    print(f"median         : {MEDIAN_CONVENTION}")
    rc = 0
    for cat in CATEGORIES:
        values = [r[cat] for r in runs if r[cat] is not None]
        if not values:
            print(f"  {cat:<22} UNAVAILABLE (no score in the run JSON)")
            rc = 1
            continue
        med = median_of(values)
        spread = ",".join(str(v) for v in values)
        mark = "  <-- BELOW THRESHOLD" if med < THRESHOLD else ""
        if med < THRESHOLD:
            rc = 1
        print(f"  {cat:<22} median={med} (runs: {spread})  min={min(values)} max={max(values)}{mark}")
    print(f"  A5 bar: median >= {THRESHOLD} on all four categories -> "
          f"{'PASS' if rc == 0 else 'FAIL'}")
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
