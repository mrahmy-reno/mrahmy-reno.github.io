#!/usr/bin/env python3
"""Show the CLS layout-shift elements from a Lighthouse JSON."""
import json
import sys

d = json.load(open(sys.argv[1]))
for key in ["layout-shift-elements", "layout-shifts", "cumulative-layout-shift"]:
    a = d["audits"].get(key)
    if not a:
        continue
    print(f"== {key}: score={a.get('score')} {a.get('displayValue','')}")
    det = a.get("details") or {}
    for item in (det.get("items") or [])[:12]:
        node = item.get("node") or {}
        print("    score=%s  selector=%s  snippet=%s" % (
            item.get("score"), node.get("selector"), (node.get("snippet") or "")[:80]))
        for phase in item.get("phase", []) if isinstance(item.get("phase"), list) else []:
            pass
        if item.get("phase"):
            print("        phase:", str(item["phase"])[:200])
    print()
