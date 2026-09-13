#!/usr/bin/env python3
"""Dump the main-thread breakdown + long tasks of a Lighthouse run (B2-04 working tool)."""
import json
import sys
from pathlib import Path

for p in sys.argv[1:]:
    d = json.loads(Path(p).read_text())
    a = d["audits"]
    print(f"== {Path(p).name} perf={round(d['categories']['performance']['score'] * 100)}")
    if "mainthread-work-breakdown" in a:
        for item in a["mainthread-work-breakdown"].get("details", {}).get("items", []):
            print(f"   {item['groupLabel']:24} {item['duration']:9.1f} ms")
    lt = a.get("long-tasks", {}).get("details", {}).get("items", [])
    print(f"   long tasks: {len(lt)}")
    for item in lt[:6]:
        print(f"      {item['duration']:7.0f} ms  url={item.get('url', '')[:60]}")
    if "bootup-time" in a:
        for item in a["bootup-time"].get("details", {}).get("items", [])[:4]:
            print(f"   bootup {item['url'][:50]:50} total={item['total']:.0f} script={item['scripting']:.0f}")
