#!/usr/bin/env bash
# Commit the Benchmark #1 implementation on the working branch.
set -uo pipefail
cd /root/projects/portfolio-benchmark1
git config user.email "eng-specialist@company.local"
git config user.name "eng-specialist (B1-03)"
git add -A
git status --short | head -40
echo "--- staged file count: $(git diff --cached --name-only | wc -l) ---"
echo "--- node_modules excluded: $(git diff --cached --name-only | grep -c node_modules || true) ---"
git commit -q -m "B1-03: build the Benchmark #1 portfolio site

Static site (HTML/CSS/vanilla JS) generated into the docs/ publish root from
site.config.json + tools/site_content.py, with every rendered string carrying its
FACTS_LEDGER row id.

- 11 content pages (index + 10 project detail pages) + 404, robots, sitemap, .nojekyll
- owner-decision switches: photo included (owner Q6), LinkedIn-only contact (Q5),
  no Tier-B certifications (Q8); tests assert both states of each switch
- test suite: static scans, axe on all 12 pages, rendered-text provenance + numeric
  whitelist, switch integrity, link check, html-validate + W3C Nu, Lighthouse mobile
- content-map.md: 451 rendered blocks mapped to ledger rows; 0 unsourced lines"
echo "commit_exit=$?"
git log --oneline | cat
echo "HEAD=$(git rev-parse HEAD)"
