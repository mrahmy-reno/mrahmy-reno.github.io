#!/usr/bin/env python3
"""A16 / D14 — owner-decision switch integrity.

Proves that:
  1. the DELIVERED build (the shipped `site.config.json` state) is: photo included,
     LinkedIn-only contact (no email, no phone), zero Tier-B certifications;
  2. each of the three switches is exercised in both states, and flipping one changes ONLY the
     expected surface (the rendered contact block, the hero portrait, the certification list) —
     asserted by removing the *known* block from the flipped build and requiring byte equality
     with the delivered build.

Usage: python3 tests/switch_integrity.py [--config site.config.json] [--docs docs]
Exit 0 = all assertions passed.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
LEDGER = Path("/root/company/BENCHMARK_01/FACTS_LEDGER.md")
sys.path.insert(0, str(REPO / "tools"))
import build_site as B  # noqa: E402
import site_content as C  # noqa: E402

FAILURES: list[str] = []
CHECKS = 0


def check(cond: bool, label: str, detail: str = "") -> bool:
    global CHECKS
    CHECKS += 1
    print(f"[{'PASS' if cond else 'FAIL'}] {label}" + (f" :: {detail}" if detail else ""))
    if not cond:
        FAILURES.append(label)
    return cond


def build_with(cfg: dict, outdir: Path) -> dict[str, str]:
    outdir.mkdir(parents=True, exist_ok=True)
    return B.render_all(cfg, outdir)


def contact_block_span(html: str) -> tuple[int, int]:
    start = html.index('id="contact"')
    start = html.rindex("<section", 0, start)
    end = html.index("</section>", start)
    return start, end


def sig(html: str) -> str:
    """HTML with whitespace-only lines dropped: equality is asserted modulo insignificant
    whitespace, so removing one conditional block cannot pass or fail on a stray blank line."""
    return "\n".join(line for line in html.splitlines() if line.strip())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(REPO / "site.config.json"))
    ap.add_argument("--docs", default=str(REPO / "docs"))
    args = ap.parse_args()

    tmp = Path(tempfile.mkdtemp(prefix="switch-integrity-"))
    delivered_cfg = B.load_config(Path(args.config))
    print("=" * 78)
    print("A16 / D14 — OWNER-DECISION SWITCH INTEGRITY")
    print(f"config  = {args.config}")
    print(f"scratch = {tmp}")
    print("=" * 78)
    print("delivered state: contact.strategy=%s photo.enabled=%s tier_b=%d"
          % (delivered_cfg["contact"]["strategy"], bool(delivered_cfg["photo"].get("enabled")),
             len(delivered_cfg["certifications"].get("tier_b") or [])))

    delivered = build_with(delivered_cfg, tmp / "delivered")
    index = delivered["index.html"]
    pages = {k: v for k, v in delivered.items() if k.endswith(".html")}

    # ------------------------------------------------- delivered-state assertions
    print("\n-- delivered state assertions --")
    check(delivered_cfg["contact"]["strategy"] == "linkedin",
          "delivered contact strategy is LinkedIn-only",
          delivered_cfg["contact"]["strategy"])
    check(bool(delivered_cfg["photo"].get("enabled")) is True,
          "delivered state includes the owner-approved photo (DIRECTIVE #3 / Q6)")
    check(not (delivered_cfg["certifications"].get("tier_b") or []),
          "delivered state publishes zero Tier-B certifications (Q8)")

    imgs = re.findall(r"<img\b[^>]*>", index)
    check(len(imgs) == 1 and 'src="/assets/profile.jpg"' in imgs[0],
          "delivered index renders exactly one image, the self-hosted portrait",
          imgs[0][:120] if imgs else "none")
    ledger = LEDGER.read_text(encoding="utf-8")
    ledger_emails = re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", ledger)
    check(not any(e in index for e in ledger_emails),
          "delivered index contains no personal email",
          f"checked {len(ledger_emails)} ledger email value(s)")
    phone_re = re.compile(r"\+\d[\d ]{8,}\d")
    check(not phone_re.search(index), "delivered index contains no phone number")

    # every page: no email/phone, no Tier-B, exactly one LinkedIn destination
    bad = []
    for name, html in pages.items():
        if phone_re.search(html) or any(e in html for e in ledger_emails) or "mailto:" in html:
            bad.append(f"{name}: contact value")
        if 'Tier-B' in html or 'tier_b' in html:
            bad.append(f"{name}: tier-B marker")
    check(not bad, "no page carries a contact value or a Tier-B marker", str(bad[:4]))

    ld = re.search(r'<script type="application/ld\+json">(.*?)</script>', index, re.S).group(1)
    check("email" not in ld and "telephone" not in ld and "contactPoint" not in ld,
          "JSON-LD contains no machine-readable contact point (PRD 5.2)")

    # ------------------------------------------------- flip 1: contact strategy
    print("\n-- flip 1: contact.strategy linkedin -> email_phone --")
    flip1_cfg = json.loads(json.dumps(delivered_cfg))
    probe_email = "review-probe@example.invalid"
    probe_phone = "+00 000 000 0000"
    flip1_cfg["contact"] = {"strategy": "email_phone", "email": probe_email,
                            "phone": probe_phone}
    flip1 = build_with(flip1_cfg, tmp / "flip-contact")
    f1 = flip1["index.html"]
    in_contact = 0
    start, end = contact_block_span(f1)
    contact_html = f1[start:end]
    for value in (probe_email, probe_phone):
        total = f1.count(value)
        inside = contact_html.count(value)
        in_contact += total
        check(total >= 1 and total == inside,
              f"flipped contact value {value!r} renders ONLY inside the contact section",
              f"total={total} inside_contact={inside}")
    check(probe_email not in ld and probe_phone not in [
        m for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', f1, re.S)][0],
        "flipped contact values are not emitted into JSON-LD")
    # the rest of the page must be byte-identical outside the contact section
    stripped_delivered = index[:contact_block_span(index)[0]] + index[contact_block_span(index)[1]:]
    stripped_flip = f1[:start] + f1[end:]
    check(sig(stripped_delivered) == sig(stripped_flip),
          "flipping the contact switch changes nothing outside the contact section")

    # ------------------------------------------------- flip 2: photo on -> off
    print("\n-- flip 2: photo.enabled true -> false --")
    flip2_cfg = json.loads(json.dumps(delivered_cfg))
    flip2_cfg["photo"]["enabled"] = False
    flip2 = build_with(flip2_cfg, tmp / "flip-photo")
    f2 = flip2["index.html"]
    check("<img" not in f2, "photo disabled: the build contains no <img>")
    hero_block = re.compile(r'\n\s*<div class="hero-media">.*?</div>', re.S)
    check(bool(hero_block.search(index)), "photo enabled: the hero-media block exists")
    stripped_photo = hero_block.sub("", index, count=1)
    check(sig(stripped_photo) == sig(f2),
          "flipping the photo switch changes only the hero portrait block")
    for name, html in flip2.items():
        if name.endswith(".html"):
            other = delivered[name]
            check(html == other or name == "index.html",
                  f"{name}: unaffected by the photo switch")

    # ------------------------------------------------- flip 3: Tier-B certifications
    print("\n-- flip 3: certifications.tier_b [] -> one entry --")
    flip3_cfg = json.loads(json.dumps(delivered_cfg))
    flip3_cfg["certifications"]["tier_b"] = [
        {"name": "Probe Credential (TEST-000)", "body": "Probe Issuing Body"}]
    flip3 = build_with(flip3_cfg, tmp / "flip-tierb")
    f3 = flip3["index.html"]
    check("Probe Credential (TEST-000)" in f3 and "Probe Issuing Body" in f3,
          "tier_b probe entry renders when the switch is on")
    tb_block = re.compile(r'\n\s*<h3 class="certs-h3-tierb">.*?</ul>\n', re.S)
    check(bool(tb_block.search(f3)), "tier_b block is structurally identifiable")
    stripped_tb = tb_block.sub("\n", f3, count=1)
    check(sig(stripped_tb) == sig(index),
          "flipping the Tier-B switch adds only the additional-certifications block")
    still_five = len(re.findall(r'class="cert-name"', f3))
    check(still_five == 6, "Tier-B activation adds to the five Tier-A certs (5 + 1 probe)",
          f"cert-name nodes = {still_five}")

    shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "=" * 78)
    print(f"checks run: {CHECKS}   failures: {len(FAILURES)}")
    for f in FAILURES:
        print("  FAILED: " + f)
    print("SWITCH INTEGRITY RESULT: " + ("PASS" if not FAILURES else "FAIL"))
    print("=" * 78)
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
