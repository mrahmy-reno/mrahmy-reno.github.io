#!/usr/bin/env python3
"""Compare the metric audits of two Lighthouse runs (B2-04 working tool, read-only)."""
import json
import sys
from pathlib import Path

KEYS = ["first-contentful-paint", "largest-contentful-paint", "total-blocking-time",
        "cumulative-layout-shift", "speed-index", "interactive"]


def row(path):
    d = json.loads(Path(path).read_text())
    out = {k: d["audits"][k]["displayValue"] for k in KEYS if k in d["audits"]}
    out["performance"] = round(d["categories"]["performance"]["score"] * 100)
    return out


for p in sys.argv[1:]:
    r = row(p)
    print(f"{Path(p).name:38} perf={r.pop('performance'):>3}  "
          + "  ".join(f"{k.split('-')[0]}={v}" for k, v in r.items()))
