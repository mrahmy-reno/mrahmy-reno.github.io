# Mohammed Tawfiq Rahmy — portfolio site (Benchmark #1)

A production-quality, single-author portfolio site: **static HTML + CSS + minimal vanilla JS**.
No framework, no build step to serve, no runtime dependencies, no third-party requests, no
analytics, no trackers, no cookies, no storage.

- **Publish root:** `docs/` — this is the only directory that is public (GitHub Pages serves it).
  Nothing outside `docs/` is published: not the tests, not the provenance map, not the tooling.
- **Live URL:** `https://mrahmy-reno.github.io/` — **live since 2026-09-13** with the accepted B2
  redesign (published revision `bef2341`, 26 files, verified byte-identical from outside the host:
  `evidence/B2-06/08_outside_verify.txt`). The B1 build it replaced is in the history at `7d22469`.
- **Pages:** 11 content pages (`docs/index.html` + 10 project detail pages) + `docs/404.html`.

## 1. Serve it locally

```bash
python3 -m http.server -d docs 8000      # then open http://127.0.0.1:8000/
```

That is the whole procedure — the files in `docs/` are the site. There is no compile, bundle or
install step, and no Node/Python package is required to serve or deploy it. (Paths are
root-absolute, correct when `docs/` is the web root, as on GitHub Pages at a domain root.)

## 2. Repository layout

```
.
├── site.config.json        ← THE ONE PLACE the owner-decision switches live (§4)
├── docs/                   ← PUBLISH ROOT (what the public sees) · 26 files
│   ├── .nojekyll           ← required so GitHub Pages does not hide paths starting with "_"
│   ├── index.html          the whole pitch on one page + jump-off to depth
│   ├── 404.html            recovery page (excluded from sitemap.xml, marked noindex)
│   ├── robots.txt  sitemap.xml
│   ├── assets/
│   │   ├── styles.css      all presentation, incl. @media print and prefers-reduced-motion
│   │   ├── main.js         progressive enhancement only (mobile nav); site works with JS off
│   │   ├── fonts/          Spectral Subset (self-hosted, with its OFL licence text)
│   │   ├── grain.png       the redesign's surface texture
│   │   ├── favicon.svg  favicon-32.png  apple-touch-icon.png
│   │   ├── og-image.png    locally generated 1200×630 social card
│   │   └── profile.jpg     owner-approved likeness (see §4)
│   └── projects/<slug>.html ×10
├── content-map.md          provenance map: every rendered claim → FACTS_LEDGER row
├── README.md               this file
├── DEPLOY_RUNBOOK.md       publish / rollback steps + owner-decision switches + publish record
├── tools/                  generator + asset + scan helpers (not published)
└── tests/                  the runnable check suite (not published), incl.
                            accepted_manifest_hashes.txt — the recorded accepted state of docs/
```

## 3. Build / regenerate

The site is hand-authored *through a generator* so that every string carries its provenance and
the owner-decision switches have exactly one home. The generated output is committed, so you never
**need** to run the generator to serve or deploy; run it after editing content or config:

```bash
python3 tools/build_site.py            # renders docs/ from site.config.json + tools/site_content.py
python3 tools/gen_content_map.py       # rewrites content-map.md from the same content model
bash tests/run_all.sh                  # the full check suite (needs the test tooling — see §7)
```

`tools/build_site.py` is Python-stdlib only. `tools/make_assets.sh` regenerates the icon and OG
raster images with headless Chrome (only needed if you change the artwork) and re-copies the
approved portrait.

## 4. Owner-decision switches (the only values that change what is published)

`site.config.json` is the single place the three pending owner decisions live. All three are
one-line changes; a test asserts both states and that flipping a switch changes **only** the
contact/photo/certification surface (`tests/switch_integrity.py`).

| Switch | Delivered state | Alternatives |
|---|---|---|
| `contact.strategy` | `"linkedin"` — LinkedIn only, **no** personal email, **no** phone anywhere in the build | `"email"` / `"email_phone"` (set `contact.email` / `contact.phone` to the exact `FACTS_LEDGER.md` §8 values first) |
| `photo.enabled` | `true` — owner-approved self-hosted portrait at `docs/assets/profile.jpg` | `false` removes the portrait and the `<img>` entirely |
| `certifications.tier_b` | `[]` — zero Tier-B certifications | add an entry **only after** the owner confirms it and the ledger row is added |

**Decision log**

- Contact: owner decision **Q5 = LinkedIn only** (`FACTS_LEDGER.md` §10). Email/phone are not
  published and are asserted absent from every page, from JSON-LD and from the repository.
- Photo: owner decision **Q6 = include the LinkedIn photo**. The asset is a self-hosted copy of
  `/root/company/BENCHMARK_01/sources/linkedin_profile_photo_400.jpg` (400×400 JPEG, 60 311 bytes,
  sha256 `be1dc0c6…89be`), rendered with explicit `width`/`height` (no layout shift) and the
  factual alt text `Mohammed Tawfiq Rahmy`. The expiring signed LinkedIn CDN URL is never
  hot-linked.
- Tier-B certifications: owner decision **Q8 = none**. Tier-B names appear nowhere in this
  repository (checked mechanically against the ledger list).

## 5. External requests

| Kind | Count | Detail |
|---|---|---|
| Runtime subresources (scripts, styles, fonts, images, frames, preload) | **0** | everything is self-hosted; system font stack; no CDN |
| External hyperlink destinations | **1** | `https://www.linkedin.com/in/mohammed-rahmy` (`FACTS_LEDGER.md` §8 `L8.3`) |
| Analytics / trackers / cookies / storage | **0** | none |
| Runtime dependencies | **0** | static files only |

A second external hyperlink is a change that must be justified here and in `content-map.md`.
The `package.json` `devDependencies` are **test tooling only** — they are never shipped and are
pinned to exact versions for reproducibility (see `evidence/B1-03/00_environment.txt`).

## 6. Accessibility, performance and print

- WCAG 2.1 AA target: semantic landmarks, skip-to-content, one `h1` per page, logical heading
  order, visible focus ring on every keyboard stop, AA contrast, meaningful alt text,
  `prefers-reduced-motion: reduce` removes all transitions/animation, fully keyboard operable.
- Responsive at 360 / 768 / 1024 / 1440 px with no horizontal overflow (measured).
- Cumulative layout shift measured at 0.000 on a mobile viewport (an in-page layout-shift observer
  is part of the suite, because a JS-revealed control must not move the page).
- Lighthouse mobile against the local server — **≥ 90 on all four categories** for the index and
  for a project detail page, measured as the **median of at least 5 kept runs on an idle host**
  (`ACCEPTANCE.md` A5.1; the suite runs 9, forced odd, and one median implementation is shared by
  every part of the suite). This host also runs other benchmark processes, so a single lab run is
  noisy; **every** individual run's JSON is kept and the spread is printed, including runs below the
  bar. The B2-06 acceptance run recorded index performance median 97 (runs 98,96,97,99,95,97,98,98,97)
  and SAMA 99, with accessibility/best-practices/SEO 100 on both — raw output in
  `/root/company/BENCHMARK_01/evidence/B2-06/suite/08_lighthouse.log`.
- Typefaces are **self-hosted**: the display voice is a subset of Spectral (`docs/assets/fonts/`,
  shipped with its OFL licence text), so there is still no third-party request at runtime.
- Print stylesheet for recruiters (A17): the first printed page shows the name, the current role
  and employer, and the LinkedIn URL as readable text; navigation and other interactive-only
  affordances are not printed.

## 7. Test suite

**Precondition:** the check suite is split into Python-only steps and Node steps. The Node steps
(browser/axe, rendered-text scans, link check, HTML validation, Lighthouse) need the pinned
test-only tooling, which is gitignored and therefore **absent in a fresh clone**. Install it once:

```bash
bash tools/install_dev_tooling.sh     # npm install of the pinned devDependencies
python3 -m http.server -d docs 8000   # (serving the site needs none of this)
```

If the tooling is missing, the suite does **not** report a false pass: `tools/check_dev_tooling.sh`
runs first, names what is missing, the affected steps are recorded as `SKIPPED` in the summary, and
the run still exits non-zero. A step is never silently downgraded to a pass.

```bash
bash tests/run_all.sh                      # everything, raw output into the evidence directory
EVIDENCE_DIR=/tmp/x bash tests/run_all.sh  # ...or somewhere else
```

| Step | What it proves |
|---|---|
| `01_build` (`tools/build_site.py`) | the committed `docs/` is what the generator renders from `site.config.json` + `tools/site_content_b2.py` |
| `tests/static_scans.py` | coverage counts (3 roles, 10 detail pages, 8 skill groups, 2 education, 5 Tier-A certs, 0 Tier-B), internal link + anchor integrity, single external destination, zero external subresources, unique titles/descriptions, sitemap = 11 URLs, robots, JSON-LD `Person`, ledger PII absence, secret patterns, attribution guard (no project name in an experience entry; no employer name on a project page) |
| `tests/regression_repairs.py` | the B1-05 regression tests: the tooling scripts act on the checkout they are run from, the suite degrades honestly (SKIPPED + non-zero) without `node_modules`, the rendered-text extractor proves it reached the last section, regeneration leaves the tree clean, and the Lighthouse summary reports the median |
| `tests/design_checks.py` | the redesign's own mechanics: design-token conformance, the banned-defaults audit, motion-spec conformance, the palette contrast table, and the artefact label audits |
| `tests/test_prepush_guard.sh` | the pre-push guard blocks deletions/rehearsal messages and warns on a stale accepted manifest (run against a throwaway remote, never production) |
| `tests/browser_checks.mjs` | rendered-text extraction **+ last-section coverage assertion**, axe-core on all 12 pages (0 critical / 0 serious), console capture (0 errors / 0 warnings), first-screen assertions at 1366×768 and 390×844 with zero scroll, overflow at 4 widths, 8 screenshots, keyboard walk, reduced-motion check, JS-disabled check, print emulation + PDF |
| `tests/text_scans.py` | provenance (every rendered line maps to the content model / `content-map.md`), banned-pattern scan (ledger §9, contact values, Tier-B names, banned vocabulary), numeric-token whitelist (`tests/numeric_whitelist.txt`) |
| `tests/switch_integrity.py` | A16: delivered state + all three switches flipped, each changing only its own surface |
| `tests/link_check.mjs` | the external destination resolves (HTTP + real browser navigation) |
| `tests/validate_html.sh` | HTML validity: `html-validate` (0 errors, authoritative) **and** the W3C Nu checker over all 12 pages (advisory; the service may rate-limit) |
| `tests/run_lighthouse.sh` | Lighthouse mobile ≥ 90 on all four categories, on the index and one detail page; every run is kept and the summary (`tools/lh_median.py`) reports the **median** with the full spread |
| `tests/reproduce.sh` | A11: fresh `git clone` → documented build command → identical published-file hashes |

Test tooling is pinned in `package.json` and installed with:

```bash
bash tools/install_dev_tooling.sh     # npm install (test-only; skip if node_modules exists)
```

## 8. Deployment

GitHub Pages publishes the `docs/` folder of the `mrahmy-reno.github.io` repository at
`https://mrahmy-reno.github.io/`. Publishing is **B1-08** and is owner-gated (RED); see
`DEPLOY_RUNBOOK.md` for the publish and rollback steps. Nothing in this repository publishes
itself, and no credentials live here.

## 9. Content rules (why the copy reads the way it does)

Every factual string is traceable to a row of `/root/company/BENCHMARK_01/FACTS_LEDGER.md`; the
mapping is `content-map.md`, and the mechanical check is `tests/text_scans.py`. There are no
invented projects, employers, dates, numbers or metrics, no pricing or availability claims, and no
employer↔project attributions (the ledger does not assign a project to an employer, so neither does
the site). If you want to add a claim, add it to the ledger first, then to
`tools/site_content_b2.py`, then re-run the generator and the suite.

## 10. Acceptance status and declared limitations

**Accepted and live.** The independent round-4 verdict was *merits owner acceptance: **YES*** (0
BLOCKER, 0 HIGH, 0 FAIL; Q1–Q14 8 PASS / 6 PARTIAL / 0 FAIL) and the delivery acceptance pass is
recorded in `/root/company/BENCHMARK_01/evidence/B2-06/ACCEPTANCE_PASS.md` (one suite invocation,
all 12 steps exit 0, `CHECK SUITE RESULT: PASS`). The live site is
`https://mrahmy-reno.github.io/`, verified from outside this host: 26/26 files byte-identical to
`tests/accepted_manifest_hashes.txt` over HTTPS.

These limitations travel with the acceptance and are stated so the record is not read as flawless
(the full text is `/root/company/BENCHMARK_01/ACCEPTANCE.md` §L1/L2):

- **L1 — Q4 (demonstration) is PARTIAL by owner decision.** The site demonstrates the work through
  typed contracts, run traces and diagrams only; it carries **no real screenshot, log, eval table,
  terminal capture or live surface** anywhere (`img = 1` site-wide: the portrait). This is an
  owner-accepted scope limitation **and remains open** — it is to be closed later with owner-supplied
  assets. Nothing was fabricated to close it, and nothing may be.
- **L2 — Q3 (depth/atmosphere) and Q7 (editorial pacing)** are recorded reservations, not conditions
  of acceptance.
- **L3 — the hero's first object** and its (below-the-fold) proof affordance are a stated programme
  decision, recorded with measurements in `/root/company/BENCHMARK_01/cards/B2-11.md`.
- **P4 — apparatus only:** the suite's axe step samples the page during the shipped reveal transition
  and can produce a *false FAIL*; the measured contrast is 5.07–5.82:1 and 6/6 repeat runs are clean.
  To fix in the follow-up pass (settle the reveal before injecting axe); it never produces a false
  pass.
- **P6 — LOW, ships:** one label on `projects/smart-care.html` (`streaming React UI`) is clipped by
  its own SVG box (32.39 px at 1366 wide); one number to fix, listed first for the follow-up pass.
- **Follow-up asset constraint:** client work (SAMA / Splunk / SOC) is presumed **not publishable**
  without the owner's explicit written go-ahead; invented dashboards or metrics remain forbidden
  regardless of source.
