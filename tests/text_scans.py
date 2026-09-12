#!/usr/bin/env python3
"""Rendered-text scans — A1/D1 (provenance + banned patterns) and A12/D12 (numeric honesty).

Input: the per-page rendered-text dumps produced by tests/browser_checks.mjs (headless browser
text, not the HTML source). The mapped-content union is rebuilt from the generator's recorder, so
the provenance test compares the *page* against the *content model*, not against itself.

Usage:
  python3 tests/text_scans.py --text <evidence>/rendered-text --docs docs \
      [--ledger /root/company/BENCHMARK_01/FACTS_LEDGER.md]
Exit 0 = all checks passed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import build_site as B  # noqa: E402
import site_content as C  # noqa: E402

FAILURES: list[str] = []
CHECKS = 0

# Separators the renderer legitimately joins mapped blocks with.
SEPARATORS = [" · ", " — ", " – ", " | ", " → ", " ", "(", ")", ":", ",", "-", "/", "+"]

BANNED_VOCAB = ["expert", "world-class", "passionate", "cutting-edge", "state-of-the-art",
                "revolutionary", "best-in-class", "proven track record", "results-driven",
                "ninja", "guru", "rockstar", "i love", "i'm excited to"]

# Ledger section 9 banned content themes that have a word-level fingerprint.
BANNED_THEMES = ["followers", "connections count", "testimonial", "endorsement",
                 "years of experience", "per hour", "per job", "retainer", "notice period",
                 "open to opportunities", "available for hire", "$", "€", "£", "%"]


def norm(s: str) -> str:
    return " ".join(s.split())


def check(cond: bool, label: str, detail: str = "") -> bool:
    global CHECKS
    CHECKS += 1
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f" :: {detail}" if detail else ""))
    if not cond:
        FAILURES.append(label)
    return cond


def mapped_texts() -> list[str]:
    """Every string the content model authorises, as rendered (normalised)."""
    cfg = B.load_config(B.DEFAULT_CONFIG)
    rec = B.Recorder()
    B.render_all(cfg, None, rec)
    texts = {norm(b["text"]) for _page, b, _g in rec.entries}
    # Global strings the generator composes at render time from mapped blocks.
    texts.add(norm(C.NAME["text"]))
    texts.add(norm(C.LINKEDIN_URL))
    texts.add(norm(C.META_DESCRIPTION["text"]))
    texts.add(norm(C.S5_SUMMARY["text"]))
    texts.add(norm(C.HEADLINE["text"]))
    return sorted(texts, key=len, reverse=True)


def sourced(line: str, blocks: list[str]) -> bool:
    """A rendered line is sourced if it is a substring of an authorised string, or if it
    decomposes into authorised pieces joined by legitimate separators."""
    if not line:
        return True
    if any(line in b for b in blocks):
        return True
    # decompose on separators (longest first) and require every piece to be authorised
    pieces = [line]
    for sep in SEPARATORS:
        nxt = []
        for p in pieces:
            nxt.extend(p.split(sep) if sep in p else [p])
        pieces = nxt
    pieces = [p.strip() for p in pieces if len(p.strip()) > 1]
    if not pieces:
        return not line.strip(" ·—–|→()+:,-/")
    return all(any(p in b for b in blocks) for p in pieces)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", required=True, help="directory of rendered-text dumps")
    ap.add_argument("--ledger", default="/root/company/BENCHMARK_01/FACTS_LEDGER.md")
    ap.add_argument("--whitelist", default=str(Path(__file__).resolve().parent /
                                               "numeric_whitelist.txt"))
    args = ap.parse_args()

    text_dir = Path(args.text)
    files = sorted(text_dir.glob("*.txt"))
    ledger = Path(args.ledger).read_text(encoding="utf-8")
    whitelist = [l.strip() for l in Path(args.whitelist).read_text(encoding="utf-8").splitlines()
                 if l.strip() and not l.startswith("#")]

    print("=" * 78)
    print("RENDERED-TEXT SCANS (A1/D1 provenance + bans, A12/D12 numerics)")
    print(f"text dir  = {text_dir}  ({len(files)} pages)")
    print(f"whitelist = {args.whitelist} ({len(whitelist)} entries)")
    print("=" * 78)
    check(len(files) == 12, "12 rendered-text dumps present", f"found {len(files)}")

    blocks = mapped_texts()
    print(f"authorised content strings: {len(blocks)}")

    # ---------------------------------------------------------------- provenance (A1/R4)
    print("\n-- provenance: every rendered line traces to the content model (A1 / AC-12.1) --")
    total_lines = 0
    unsourced: list[str] = []
    for f in files:
        lines = [norm(l) for l in f.read_text(encoding="utf-8").splitlines()]
        lines = [l for l in lines if l]
        total_lines += len(lines)
        for l in lines:
            if not sourced(l, blocks):
                unsourced.append(f"{f.name}: {l[:100]}")
    check(not unsourced, "0 unsourced rendered lines across all 12 pages",
          f"checked {total_lines} lines; unsourced={len(unsourced)}")
    for u in unsourced[:25]:
        print(f"        UNSOURCED {u}")

    # ---------------------------------------------------------------- banned patterns (A1/D1)
    print("\n-- banned patterns in rendered text (A1 / D1 / ledger 9) --")
    emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", ledger)
    phones = re.findall(r"\+\d[\d ]{8,}\d", ledger)
    tier_b_block = re.search(r"\*\*Tier B[^\n]*\n(.*?)\n\n", ledger, re.S)
    tier_b: list[str] = []
    if tier_b_block:
        raw = tier_b_block.group(1).split("*Conflict note")[0].replace("\n", " ")
        for part in raw.split("·"):
            nm = re.sub(r"\s*\(.*?\)\s*", " ", part).strip(" .;,")
            if len(nm) > 3:
                tier_b.append(nm)
    patterns = [("ledger contact value", v) for v in emails + phones]
    patterns += [("Tier-B certification name", v) for v in tier_b]
    patterns += [("banned vocabulary", v) for v in BANNED_VOCAB]
    patterns += [("ledger section 9 theme", v) for v in BANNED_THEMES]
    hits: list[str] = []
    for f in files:
        low = f.read_text(encoding="utf-8").lower()
        for label, pat in patterns:
            if pat.lower() in low:
                hits.append(f"{f.name}: {label} {pat!r}")
    check(not hits, "0 banned-pattern hits in rendered text",
          f"{len(patterns)} patterns checked; hits={hits}" if hits else
          f"{len(patterns)} patterns, 0 hits")
    print(f"        patterns: {len(emails)} ledger emails, {len(phones)} ledger phones, "
          f"{len(tier_b)} Tier-B names, {len(BANNED_VOCAB)} banned words, "
          f"{len(BANNED_THEMES)} banned themes")

    # ---------------------------------------------------------------- numeric whitelist (A12/D12)
    print("\n-- numeric honesty (A12 / D12) --")
    tok_re = re.compile(r"[A-Za-z0-9][A-Za-z0-9._+,/\-]*")
    seen: dict[str, list[str]] = {}
    for f in files:
        for tok in tok_re.findall(f.read_text(encoding="utf-8")):
            if any(ch.isdigit() for ch in tok):
                seen.setdefault(tok, []).append(f.stem)
    unknown = {}
    for tok, where in seen.items():
        ok = tok in whitelist
        if not ok:
            # D12: a checker that tokenises differently must normalise to the whitelisted
            # tokens or to substrings of them - but a bare integer never stands in for a
            # whitelisted compound token.
            ok = (not tok.isdigit()) and any(tok in w for w in whitelist)
        if not ok:
            unknown[tok] = sorted(set(where))
    print(f"digit-bearing tokens found: {len(seen)}")
    for tok in sorted(seen):
        mark = "ok " if tok not in unknown else "!! "
        print(f"        {mark}{tok!r:16} pages={sorted(set(seen[tok]))}")
    check(not unknown, "every digit-bearing token in rendered text is whitelisted",
          f"unwhitelisted={json_dumps(unknown)}" if unknown else
          f"{len(seen)} tokens, all whitelisted")
    used = set(seen)
    unused = [w for w in whitelist if w not in used and w != "ten"]
    print(f"        whitelist entries not currently rendered (allowed but unused): {unused}")

    print("\n" + "=" * 78)
    print(f"checks run: {CHECKS}   failures: {len(FAILURES)}")
    for f in FAILURES:
        print("  FAILED: " + f)
    print("TEXT SCANS RESULT: " + ("PASS" if not FAILURES else "FAIL"))
    print("=" * 78)
    return 0 if not FAILURES else 1


def json_dumps(o) -> str:
    import json
    return json.dumps(o, indent=1)


if __name__ == "__main__":
    sys.exit(main())
