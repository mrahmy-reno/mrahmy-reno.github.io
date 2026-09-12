#!/usr/bin/env python3
"""Summarise the top Lighthouse opportunities/diagnostics for the index page."""
import json
import sys

f = sys.argv[1]
d = json.load(open(f))
print("score:", round(d["categories"]["performance"]["score"] * 100))
print("\n-- metrics --")
for k in ["first-contentful-paint", "largest-contentful-paint", "total-blocking-time",
          "cumulative-layout-shift", "speed-index"]:
    a = d["audits"].get(k)
    if a:
        print(f"  {k}: {a.get('displayValue')}  score={a.get('score')}")
print("\n-- LCP element --")
lcp = d["audits"].get("largest-contentful-paint-element")
if lcp:
    print(json.dumps(lcp.get("details", {}), indent=1)[:1200])
print("\n-- opportunities (<1) --")
for k, a in d["audits"].items():
    if a.get("score") is not None and a.get("score") < 1 and a.get("details", {}).get("type") in (
            "opportunity",) and a.get("scoreDisplayMode") in ("numeric", "binary"):
        print(f"  {k}: score={a['score']} {a.get('displayValue','')}")
print("\n-- failing diagnostics --")
for k, a in d["audits"].items():
    if a.get("scoreDisplayMode") == "binary" and a.get("score") == 0:
        print(f"  {k}: {a.get('title')} :: {a.get('displayValue','')}")
