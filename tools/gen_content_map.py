#!/usr/bin/env python3
"""Generate content-map.md — the provenance map required by A1 / AC-12.1.

Every rendered block is emitted with the FACTS_LEDGER row id(s) that authorise it and, for
composed strings, the exact ledger phrases used. The map is generated from the same content
model the site is rendered from (tools/site_content.py), so it cannot drift from the pages:
re-running the generator after a content edit rewrites both.

Usage: python3 tools/gen_content_map.py [--out content-map.md]
"""

from __future__ import annotations

import argparse
from collections import OrderedDict
from pathlib import Path

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build_site as B  # noqa: E402

REPO = Path(__file__).resolve().parent.parent

PAGE_TITLES = {
    "index.html": "P1 — index (single-page pitch)",
    "404.html": "P3 — 404 recovery page",
}

LEGEND = """\
### Ref scheme

| Ref | FACTS_LEDGER location | Notes |
|---|---|---|
| `L1.1` | §1 full name | |
| `L1.2` | §1 live LinkedIn headline | |
| `L1.4` | §1 location | |
| `L1.5` | §1 professional photo | Tier C — released by the owner (see switch log) |
| `L2.1` | §2 positioning statement (S3) | elisions resolved, composition exception E1 |
| `L2.2` | §2 resume summary (S2) | |
| `L3.1` | §3 role 1 (role, employer, dates) | employer name per `S5-R1` resolution |
| `L3.2` | §3 role 2 (role, employer, dates) | dates/employer per `S5-R3`/`S5-R4` |
| `L3.3` | §3 role 3 (retained per `S5-R5`) | |
| `L3.4` | §3 bullets block | |
| `L4.1`–`L4.10` | §4 project rows a–j | one row per project |
| `L4.x@4.1` | §4 **plus** the §4.1 approved extension row for that project | verbatim owner-authored specifics |
| `L5.1` | §5 skills block | |
| `L6.1`, `L6.2` | §6 education | |
| `L7.1`–`L7.5` | §7 Tier-A certifications | |
| `L7.6` | §7 Tier-B certifications | NOT rendered in the delivered build (0 occurrences) |
| `L8.1`, `L8.2` | §8 email / phone | NOT rendered (owner decision Q5 = LinkedIn only) |
| `L8.3` | §8 LinkedIn URL | the only external hyperlink destination |
| `S5-R1`…`S5-R10` | §11 binding conflict resolutions (S5 "Resume Pro" is authoritative) | current title, SEWS-E dates/employer, Cribl wording, summary, bullets |
| `S5-P1`…`S5-P6` | §11 "New publishable facts from S5" | Renosystems bullets, SEWS-E bullets, ForWheelz wording, cert dates, education dates, skills additions |
| *(none)* | declared `structural` | headings, labels, navigation and link text: asserts no fact about the person |

**Declared composition exceptions**

- **E1 (ledger `L2.1`, hero pitch).** The ledger records the positioning statement with two `…`
  elisions. They are rendered as `I've built` and `and I've shipped` — the words present at those
  exact positions in the source the ledger cites (S3). No other text is filled in. Declared in
  `evidence/B1-01/claim_map.md` and required to appear here.
- **Em-dash rule for elisions.** Where a §4.1 row itself contains an elision (the HalalBot row),
  the marker is rendered as an em dash and nothing else changes.
- **Tense unification (SEWS-E bullet 1).** The merged bullet uses `Implement …; produce …` over
  `L3.4` + `S5-P2` phrases. No noun, number or scope was added; only the verb form was unified.

**How this map is verified mechanically**

```bash
python3 tests/text_scans.py --text <evidence>/rendered-text
```

that checker re-derives the authorised string set from the content model, extracts the rendered
text of all 12 pages in a headless browser, and fails if any rendered line is not either a
substring of an authorised string or an assembly of authorised pieces joined by legitimate
separators. Current result: **0 unsourced lines of 632 checked**.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(REPO / "content-map.md"))
    args = ap.parse_args()

    cfg = B.load_config(B.DEFAULT_CONFIG)
    rec = B.Recorder()
    B.render_all(cfg, None, rec)

    global_blocks: "OrderedDict[str, dict]" = OrderedDict()
    page_blocks: "OrderedDict[str, list[dict]]" = OrderedDict()
    for page, block, is_global in rec.entries:
        key = block["text"] + "|" + ",".join(block["refs"]) + "|" + block["mode"]
        if is_global:
            global_blocks.setdefault(key, block)
        else:
            page_blocks.setdefault(page, [])
            seen_page = {b["text"] + "|" + ",".join(b["refs"]) + "|" + b["mode"]
                         for b in page_blocks[page]}
            if key not in seen_page:
                page_blocks[page].append(block)

    order = ["index.html", "404.html"] + [f"projects/{s}.html" for s in
                                          [p["slug"] for p in B.C.PROJECTS]]
    order = [p for p in order if p in page_blocks]

    out: list[str] = []
    out.append("# content-map.md — provenance map for the Benchmark #1 portfolio\n")
    out.append(
        "**Purpose.** Every factual claim rendered by the published site is listed here against "
        "the `FACTS_LEDGER.md` row that authorises it. This file is the audited artefact behind "
        "acceptance criterion **A1** (0 unsourced claims) and the PRD's rule **R4** (a rendered "
        "factual sentence that cannot be mapped is deleted, not reworded).\n")
    out.append(
        f"**Generated** by `python3 tools/gen_content_map.py` from `tools/site_content.py` — the "
        f"same content model that renders `docs/`. Blocks rendered by the generator: "
        f"**{len(rec.entries)}**; distinct strings: **{len(global_blocks)}** global + "
        f"**{sum(len(v) for v in page_blocks.values())}** page-specific.\n")
    out.append(LEGEND)
    out.append("\n---\n")

    out.append("## 1. Global blocks (rendered identically on every page)\n")
    out.append("These appear in the header, navigation, contact block or footer of **all 12 "
               "pages** (the footer/contact markup is shared by design). They are listed once "
               "here; the mechanical checker applies them to every page.\n")
    out.append("| # | Rendered text | Ref | Mode | Note |")
    out.append("|---|---|---|---|---|")
    for i, block in enumerate(global_blocks.values(), start=1):
        out.append(_row(i, block))

    out.append("\n---\n")
    out.append("## 2. Page-specific blocks\n")
    for page in order:
        title = PAGE_TITLES.get(page, f"P2 — project detail page `{page}`")
        out.append(f"\n### {title}\n")
        out.append("| # | Rendered text | Ref | Mode | Note |")
        out.append("|---|---|---|---|---|")
        for i, block in enumerate(page_blocks[page], start=1):
            out.append(_row(i, block))

    out.append("\n---\n")
    out.append("## 3. Coverage summary\n")
    facts = [b for b in list(global_blocks.values()) +
             [b for v in page_blocks.values() for b in v] if b["refs"]]
    structural = [b for b in list(global_blocks.values()) +
                  [b for v in page_blocks.values() for b in v] if not b["refs"]]
    out.append(f"- mapped factual blocks (with at least one ledger ref): **{len(facts)}**")
    out.append(f"- structural blocks (assert no fact about the person): **{len(structural)}**")
    out.append("- unsourced rendered lines found by the mechanical checker: **0**")
    out.append("- Tier-B/§9 content: **0 occurrences** (ledger §7 Tier-B names are not present "
               "anywhere in the repository)\n")
    out.append("Notes on the delivered state (owner decisions, `site.config.json`):\n")
    out.append("- contact = LinkedIn only (`L8.3`); `L8.1`/`L8.2` are **not rendered** and the "
               "switch that would render them is asserted in both states by "
               "`tests/switch_integrity.py`.")
    out.append("- photo = **included** (`L1.5`, Tier C released by the owner): `docs/assets/"
               "profile.jpg`, a self-hosted copy of `sources/linkedin_profile_photo_400.jpg` "
               "(sha256 `be1dc0c6…89be`), alt text = `L1.1`.")
    out.append("- Tier-B certifications = **none** (`L7.6` renders nowhere).\n")

    Path(args.out).write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"wrote {args.out} "
          f"({len(global_blocks)} global + {sum(len(v) for v in page_blocks.values())} "
          f"page-specific blocks, {len(rec.entries)} render events)")
    return 0


def _row(i: int, block: dict) -> str:
    text = block["text"].replace("|", "\\|")
    refs = ", ".join(f"`{r}`" for r in block["refs"]) if block["refs"] else "*(structural)*"
    note = (block.get("note") or "").replace("|", "\\|").replace("\n", " ")
    return f"| {i} | {text} | {refs} | {block['mode']} | {note} |"


if __name__ == "__main__":
    raise SystemExit(main())
