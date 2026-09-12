#!/usr/bin/env python3
"""B1-05 / D-06 repair — report Lighthouse scores as the MEDIAN of the kept runs.

`tests/run_all.sh` summarised Lighthouse by reading the *first* run's JSON file and printing it
under the label "median of 3 runs per page", which is not what the file contains (B1-04 defect
D-06 / E-1: the summary quoted a 99 while the raw log recorded 99/100/100 -> median 100). This
helper takes every per-run JSON file and prints, per category, the median, all individual values
and the min/max spread, so the reported number is the real median and the spread stays auditable.

It also applies the A5 bar (`median >= 90` on every category) and exits non-zero if any median is
below it — the threshold is never relaxed here.

Usage: python3 tools/lh_median.py <run1.json> [run2.json ...]
Exit 0 = every category's median >= 90 (or --no-threshold and no JSON at all is a caller error).
"""
import json
import statistics
import sys

CATEGORIES = ["performance", "accessibility", "best-practices", "seo"]
THRESHOLD = 90


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
    files = [a for a in argv if not a.startswith("--")]
    if not files:
        print("lh_median: no Lighthouse run JSON given", file=sys.stderr)
        return 2
    runs = [scores(f) for f in files]
    print(f"runs kept      : {len(files)}")
    rc = 0
    for cat in CATEGORIES:
        values = [r[cat] for r in runs if r[cat] is not None]
        if not values:
            print(f"  {cat:<22} UNAVAILABLE (no score in the run JSON)")
            rc = 1
            continue
        med = int(statistics.median(values))
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
