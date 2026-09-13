#!/usr/bin/env python3
"""Static source-level checks over the built site (stdlib only, no browser).

Covers: coverage counts, internal link + anchor integrity, external link/subresource
containment, sitemap/robots/metadata, JSON-LD, banned Tier-B content, ledger PII absence,
secret patterns, attribution guard (D17), and repo hygiene.

Usage: python3 tests/static_scans.py [--docs docs] [--ledger <path>] [--repo .]
Exit code 0 = all checks passed.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

FAILURES: list[str] = []
CHECKS = 0


def check(cond: bool, label: str, detail: str = "") -> bool:
    global CHECKS
    CHECKS += 1
    status = "PASS" if cond else "FAIL"
    line = f"[{status}] {label}"
    if detail:
        line += f" :: {detail}"
    print(line)
    if not cond:
        FAILURES.append(label)
    return cond


# --------------------------------------------------------------------------- parsing


class Page(HTMLParser):
    """Collects the structure a link/metadata/metadata audit needs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.links: list[tuple[str, str]] = []      # (href, text-so-far)
        self.resources: list[tuple[str, str]] = []  # (tag, url)
        self.meta: list[dict] = []
        self.title: str = ""
        self.jsonld: list[str] = []
        self.img_count = 0
        self.img_alts: list[str] = []
        self.headings: list[tuple[str, str]] = []
        self.exp_text: list[str] = []
        self._in_title = False
        self._in_script_ld = False
        self._script_buf = ""
        self._href_stack: list[str] = []
        self._text_buf: list[str] = []
        self._exp_depth = 0
        self._exp_buf: list[str] = []
        self._tag_stack: list[str] = []

    # -- helpers
    def _anchor_text(self) -> str:
        return " ".join(" ".join(self._text_buf).split())

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self._tag_stack.append(tag)
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "a":
            self.links.append((a.get("href", ""), ""))
            self._href_stack.append(a.get("href", ""))
            self._text_buf = []
        if tag in ("img", "script", "source", "iframe"):
            url = a.get("src") or a.get("href") or a.get("data-src") or ""
            if url:
                self.resources.append((tag, url))
        if tag == "link":
            rel = (a.get("rel") or "").lower()
            # metadata relations are not runtime subresources
            if rel not in ("canonical", "alternate", "author", "license", "next", "prev",
                           "help", "search", "tag"):
                url = a.get("href") or ""
                if url:
                    self.resources.append((tag, url))
        if tag == "meta":
            self.meta.append(a)
        if tag == "title":
            self._in_title = True
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_script_ld = True
            self._script_buf = ""
        if tag == "img":
            self.img_count += 1
            self.img_alts.append(a.get("alt", ""))
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append((tag, ""))
            self._text_buf = []
        if tag == "article" and re.search(r"\bexp\b", a.get("class", "")):
            self._exp_depth = 1
            self._exp_buf = []

    def handle_endtag(self, tag):
        if self._tag_stack and tag in self._tag_stack:
            while self._tag_stack and self._tag_stack.pop() != tag:
                pass
        if tag == "a" and self._href_stack:
            href = self._href_stack.pop()
            text = self._anchor_text()
            for i in range(len(self.links) - 1, -1, -1):
                if self.links[i][0] == href and self.links[i][1] == "":
                    self.links[i] = (href, text)
                    break
            self._text_buf = []
        if tag == "title":
            self._in_title = False
        if tag == "script" and self._in_script_ld:
            self._in_script_ld = False
            self.jsonld.append(self._script_buf)
        if tag in ("h1", "h2", "h3", "h4", "h5", "h6") and self.headings:
            self.headings[-1] = (tag, self._anchor_text())
            self._text_buf = []
        if tag == "article" and self._exp_depth == 1:
            self._exp_depth = 0
            self.exp_text.append(" ".join(self._exp_buf))
        if self._exp_depth:
            pass

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_script_ld:
            self._script_buf += data
        else:
            self._text_buf.append(data)
            if self._exp_depth:
                self._exp_buf.append(data)


def parse(path: Path) -> Page:
    p = Page()
    p.feed(path.read_text(encoding="utf-8"))
    return p


# --------------------------------------------------------------------------- main


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", default="docs")
    ap.add_argument("--ledger", default="/root/company/BENCHMARK_01/FACTS_LEDGER.md")
    ap.add_argument("--repo", default=".")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    docs = (repo / args.docs).resolve()
    ledger_path = Path(args.ledger)
    ledger = ledger_path.read_text(encoding="utf-8")

    html_files = sorted(p for p in docs.rglob("*.html"))
    pages = {p.relative_to(docs).as_posix(): parse(p) for p in html_files}

    print("=" * 78)
    print("STATIC SCANS — docs/ source-level audit")
    print(f"docs      = {docs}")
    print(f"ledger    = {ledger_path}")
    print(f"html files= {len(html_files)}")
    print("=" * 78)

    # ---------------------------------------------------------------- A3/D3 coverage
    print("\n-- coverage (A3 / D3) --")
    detail = sorted(pages.keys())
    check(len(html_files) == 12, "12 HTML files exist (index + 10 detail + 404)",
          f"found {len(html_files)}: {detail}")

    slugs = ["sama-soc-triage", "smartops-soc-app", "milo-ai-employee", "pulsesec",
             "tonsy-gpt", "smart-care", "halalbot", "forwheelz", "email-mcp",
             "voice-agent-core"]
    present = [s for s in slugs if f"projects/{s}.html" in pages]
    check(present == slugs, "10 project detail pages at the mandated slugs",
          f"{len(present)}/10")

    index = pages["index.html"]
    idx_src = (docs / "index.html").read_text(encoding="utf-8")
    n_roles = len(re.findall(r'class="exp" id="exp-\d+"', idx_src))
    check(n_roles == 3, "index renders exactly 3 experience entries", f"found {n_roles}")
    n_cards = len(re.findall(r'class="card(?: card-[a-z]+)?"', idx_src))
    check(n_cards == 10, "index renders exactly 10 project cards", f"found {n_cards}")
    n_skills = len(re.findall(r'class="skill-group"', idx_src))
    check(n_skills == 8, "index renders exactly 8 skill groups", f"found {n_skills}")
    n_edu = len(re.findall(r'class="edu"', idx_src))
    check(n_edu == 2, "index renders exactly 2 education entries", f"found {n_edu}")
    n_certs = len(re.findall(r'class="cert-name"', idx_src))
    check(n_certs == 5, "index renders exactly 5 Tier-A certifications", f"found {n_certs}")

    # ---------------------------------------------------------------- ledger PII (A9)
    print("\n-- ledger-derived privacy scan (A9 / A16) --")
    emails = sorted(set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", ledger)))
    phones = sorted(set(re.findall(r"\+\d[\d ]{8,}\d", ledger)))
    print(f"ledger contact values to exclude: email={emails} phone={phones}")
    text_exts = {".html", ".css", ".js", ".mjs", ".cjs", ".json", ".md", ".txt", ".py",
                 ".sh", ".svg", ".xml", ".yml", ".yaml"}
    scan_files = [p for p in repo.rglob("*")
                  if p.is_file() and p.suffix.lower() in text_exts
                  and ".git" not in p.parts and "node_modules" not in p.parts]
    hits = []
    for f in scan_files:
        try:
            body = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for value in emails + phones:
            if value and value in body:
                hits.append(f"{f.relative_to(repo)}:{value}")
    check(not hits, "no ledger email/phone value anywhere in the repository",
          f"hits={hits}" if hits else "0 occurrences")
    check("mailto:" not in "\n".join(
        f.read_text(encoding="utf-8", errors="ignore") for f in scan_files
        if f.suffix == ".html"), "no mailto: link anywhere in the built site")

    # ---------------------------------------------------------------- Tier-B (A16)
    print("\n-- Tier-B certification scan (A16 / AC-11.2) --")
    tier_b_block = re.search(r"\*\*Tier B[^\n]*\n(.*?)\n\n", ledger, re.S)
    tier_b_names: list[str] = []
    if tier_b_block:
        raw = tier_b_block.group(1).split("*Conflict note")[0]
        for part in raw.replace("\n", " ").split("·"):
            name = re.sub(r"\s*\(.*?\)\s*", " ", part).strip(" .;,")
            if len(name) > 3:
                tier_b_names.append(name)
    print(f"Tier-B names taken from the ledger ({len(tier_b_names)}): {tier_b_names}")
    tb_hits = []
    for f in scan_files:
        try:
            body = f.read_text(encoding="utf-8", errors="ignore").lower()
        except OSError:
            continue
        for name in tier_b_names:
            if name.lower() in body:
                tb_hits.append(f"{f.relative_to(repo)} <- {name}")
    check(bool(tier_b_names), "Tier-B name list was extracted from the ledger",
          f"{len(tier_b_names)} names")
    check(not tb_hits, "no Tier-B certification name appears anywhere in the repository",
          f"hits={tb_hits}" if tb_hits else "0 occurrences")

    # ---------------------------------------------------------------- secrets (A9)
    print("\n-- secret pattern scan (A9) --")
    secret_pats = [
        re.compile(r"(api[_-]?key|secret|password|passwd|access[_-]?token|auth[_-]?token)"
                   r"\s*[:=]\s*['\"][^'\"]{8,}['\"]", re.I),
        re.compile(r"sk-[A-Za-z0-9]{20,}"),
        re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
        re.compile(r"ghp_[A-Za-z0-9]{20,}"),
        re.compile(r"AKIA[0-9A-Z]{16}"),
    ]
    sec_hits = []
    for f in scan_files:
        if f.name == "package-lock.json":
            continue
        try:
            body = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in secret_pats:
            m = pat.search(body)
            if m:
                sec_hits.append(f"{f.relative_to(repo)} :: {m.group(0)[:40]!r}")
    check(not sec_hits, "no credential-shaped string in the repository",
          f"hits={sec_hits}" if sec_hits else "0 occurrences")

    # ---------------------------------------------------------------- external containment
    print("\n-- external reference containment (A7 / D7 / A9) --")
    ext_links: dict[str, list[str]] = {}
    ext_resources: list[str] = []
    for rel, page in pages.items():
        for href, text in page.links:
            if href.startswith(("http://", "https://", "//")):
                ext_links.setdefault(href, []).append(rel)
        for tag, url in page.resources:
            if url.startswith(("http://", "https://", "//")):
                ext_resources.append(f"{rel}: <{tag} {url}>")
    print(f"external hyperlink destinations: {json.dumps(ext_links, indent=1)}")
    check(list(ext_links.keys()) == ["https://www.linkedin.com/in/mohammed-rahmy"],
          "exactly one external hyperlink destination (the L8.3 LinkedIn profile)",
          f"destinations={list(ext_links.keys())}")
    check(not ext_resources, "zero external subresources at runtime",
          f"found={ext_resources}" if ext_resources else "0")
    # every external anchor must be rel-protected and have discernible text
    bad_rel, empty_text = [], []
    for rel, page in pages.items():
        for href, text in page.links:
            if href.startswith("http"):
                src = (docs / rel).read_text(encoding="utf-8")
                for m in re.finditer(r'<a[^>]*href="https?://[^"]*"[^>]*>', src):
                    if 'rel="noopener noreferrer"' not in m.group(0):
                        bad_rel.append(f"{rel}: {m.group(0)[:70]}")
                if not text.strip():
                    empty_text.append(rel)
    check(not bad_rel, "every external link carries rel=\"noopener noreferrer\"",
          f"bad={bad_rel[:5]}" if bad_rel else "0")
    check(not empty_text, "every external link has discernible link text",
          f"pages with empty anchor text={set(empty_text)}")

    # ---------------------------------------------------------------- internal links
    print("\n-- internal link + anchor integrity (A7 / D7) --")
    broken, bad_anchor = [], []
    for rel, page in pages.items():
        for href, text in page.links:
            if href.startswith(("http", "mailto:", "tel:", "//")):
                continue
            if href.startswith("#"):
                if href != "#" and href[1:] not in page.ids:
                    bad_anchor.append(f"{rel}: {href}")
                continue
            path_part, _, frag = href.partition("#")
            if not path_part:
                continue
            p = urlparse(path_part)
            if p.scheme:
                continue
            target = (docs / path_part.lstrip("/")).resolve()
            if not target.exists():
                broken.append(f"{rel}: {href}")
            elif frag:
                tp = pages.get(target.relative_to(docs).as_posix())
                if tp is None:
                    tp = parse(target)
                if frag not in tp.ids:
                    bad_anchor.append(f"{rel}: {href}")
    check(not broken, "0 broken internal links", f"broken={broken[:10]}")
    check(not bad_anchor, "0 broken in-page anchors", f"broken={bad_anchor[:10]}")

    # ---------------------------------------------------------------- metadata / A10
    print("\n-- metadata, sitemap, robots, JSON-LD (A10) --")
    titles = [p.title.strip() for p in pages.values()]
    check(all(titles), "every page has a non-empty <title>")
    check(len(set(titles)) == len(titles), "every page <title> is unique",
          f"{len(set(titles))} unique of {len(titles)}")
    descs = []
    for rel, page in pages.items():
        d = [m.get("content", "") for m in page.meta if m.get("name") == "description"]
        descs.append((rel, d[0] if d else ""))
    check(all(d for _, d in descs), "every page has a meta description")
    check(len(set(d for _, d in descs)) == len(descs), "every meta description is unique",
          f"{len(set(d for _, d in descs))} unique of {len(descs)}")

    sm = (docs / "sitemap.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>([^<]+)</loc>", sm)
    check(len(locs) == 11, "sitemap.xml lists exactly 11 pages", f"found {len(locs)}")
    check(not any(l.endswith("404.html") for l in locs), "sitemap excludes 404.html")
    expected_urls = {"https://mrahmy-reno.github.io/index.html"} | {
        f"https://mrahmy-reno.github.io/projects/{s}.html" for s in slugs}
    check(set(locs) == expected_urls, "sitemap URLs match the built pages",
          f"missing={sorted(expected_urls - set(locs))} extra={sorted(set(locs) - expected_urls)}")

    robots = (docs / "robots.txt").read_text(encoding="utf-8")
    check("Sitemap: https://mrahmy-reno.github.io/sitemap.xml" in robots,
          "robots.txt points crawlers at the sitemap", robots.replace("\n", " | "))
    check((docs / ".nojekyll").exists(), ".nojekyll exists in the publish root")

    ld = index.jsonld
    check(len(ld) >= 1, "index carries JSON-LD")
    parsed = None
    if ld:
        try:
            parsed = json.loads(ld[0])
            ok = True
        except json.JSONDecodeError as exc:
            ok = False
            print(f"        JSON-LD parse error: {exc}")
        check(ok, "JSON-LD parses as valid JSON")
    if parsed:
        need = ["name", "jobTitle", "url", "sameAs", "address", "alumniOf", "knowsLanguage",
                "hasCredential"]
        missing = [k for k in need if k not in parsed]
        check(not missing, "JSON-LD Person carries the required properties (D10)",
              f"missing={missing}")
        check(parsed.get("@type") == "Person", "JSON-LD @type is Person")
        check(len(parsed.get("hasCredential", [])) == 5,
              "JSON-LD lists exactly 5 Tier-A credentials",
              f"found {len(parsed.get('hasCredential', []))}")

    # og / twitter
    og = [m for m in index.meta if (m.get("property") or "").startswith("og:")]
    tw = [m for m in index.meta if (m.get("name") or "").startswith("twitter:")]
    check(len(og) >= 6, "OpenGraph tags present", f"{len(og)} tags")
    check(len(tw) >= 4, "Twitter card tags present", f"{len(tw)} tags")
    check(any(m.get("property") == "og:image"
              and str(m.get("content", "")).endswith("/assets/og-image.png") for m in og),
          "og:image points at the locally generated card")

    # ---------------------------------------------------------------- photo / assets
    print("\n-- owner-decision switch surface (A16) --")
    img_srcs = []
    for rel, page in pages.items():
        for tag, url in page.resources:
            if tag == "img":
                img_srcs.append((rel, url))
    check(img_srcs == [("index.html", "/assets/profile.jpg")],
          "exactly one <img> in the build, the owner-approved self-hosted portrait",
          f"found={img_srcs}")
    check((docs / "assets/profile.jpg").exists(), "docs/assets/profile.jpg exists")
    for asset in ["assets/styles.css", "assets/main.js", "assets/favicon.svg",
                  "assets/favicon-32.png", "assets/apple-touch-icon.png",
                  "assets/og-image.png", "assets/profile.jpg"]:
        check((docs / asset).exists(), f"asset present: {asset}")

    # ---------------------------------------------------------------- attribution guard
    print("\n-- attribution guard (D17 / PRD 4.0.4) --")
    project_tokens = ["SAMA", "SmartOps", "Milo", "PulseSec", "Tonsy", "Smart Care",
                      "HalalBot", "ForWheelz", "email-MCP", "Voice agent core"]
    employers = ["Renosystems", "Sumitomo", "MNR Lab"]
    violations = []
    for i, text in enumerate(index.exp_text, start=1):
        for tok in project_tokens:
            if tok.lower() in text.lower():
                violations.append(f"experience entry {i} mentions project token {tok!r}")
    check(len(index.exp_text) == 3, "3 experience entries parsed for the guard",
          f"found {len(index.exp_text)}")
    for rel, page in pages.items():
        if not rel.startswith("projects/"):
            continue
        src = (docs / rel).read_text(encoding="utf-8")
        for emp in employers:
            if emp.lower() in src.lower():
                violations.append(f"{rel} asserts employer name {emp!r}")
    check(not violations, "no project name inside an experience entry and no employer name "
                          "on a project page (no employer<->project link)",
          f"violations={violations}" if violations else "0 violations")

    # ---------------------------------------------------------------- static ban list
    print("\n-- banned vocabulary / character scan (source level) --")
    banned_words = ["expert", "world-class", "passionate", "cutting-edge", "state-of-the-art",
                    "revolutionary", "best-in-class", "proven track record", "results-driven",
                    "ninja", "guru", "rockstar", "I love", "I'm excited to"]
    src_hits = []
    for rel in pages:
        body = (docs / rel).read_text(encoding="utf-8").lower()
        for w in banned_words:
            if w.lower() in body:
                src_hits.append(f"{rel}: {w!r}")
    check(not src_hits, "banned vocabulary absent from the built HTML",
          f"hits={src_hits}" if src_hits else "0")
    currency = []
    for rel in pages:
        body = (docs / rel).read_text(encoding="utf-8")
        for sym in ["$", "€", "£", "%"]:
            if sym in body:
                currency.append(f"{rel}: {sym!r}")
    check(not currency, "no currency symbol or percent sign in the built HTML",
          f"hits={currency}" if currency else "0")

    # ---------------------------------------------------------------- baseline isolation
    print("\n-- baseline isolation (D16) --")
    baseline = Path("/root/company/COMPANY_OS_v0.2")
    disjoint = not str(repo).startswith(str(baseline))
    check(disjoint, "product tree is disjoint from the v0.2 baseline tree",
          f"repo={repo} baseline={baseline}")

    print("\n" + "=" * 78)
    print(f"checks run: {CHECKS}   failures: {len(FAILURES)}")
    for f in FAILURES:
        print(f"  FAILED: {f}")
    print("STATIC SCANS RESULT: " + ("PASS" if not FAILURES else "FAIL"))
    print("=" * 78)
    return 0 if not FAILURES else 1


if __name__ == "__main__":
    sys.exit(main())
