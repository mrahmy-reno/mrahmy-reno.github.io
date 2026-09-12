#!/usr/bin/env python3
"""Show main-thread / long-task detail from a Lighthouse JSON."""
import json
import sys

d = json.load(open(sys.argv[1]))
for key in ["mainthread-work-breakdown", "bootup-time", "long-tasks", "dom-size",
            "network-requests", "third-party-summary"]:
    a = d["audits"].get(key)
    if not a:
        continue
    print(f"== {key}: {a.get('displayValue','')} score={a.get('score')}")
    det = a.get("details") or {}
    for item in (det.get("items") or [])[:8]:
        keep = {k: v for k, v in item.items() if k in
                ("groupLabel", "duration", "total", "startTime", "url", "transferSize",
                 "resourceSize", "value", "wastedMs", "scripting", "render", "styleLayout",
                 "parseHTML", "other", "garbageCollection", "urlLength")}
        print("   ", json.dumps(keep)[:200])
    print()
