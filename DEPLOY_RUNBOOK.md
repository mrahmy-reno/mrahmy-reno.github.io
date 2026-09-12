# DEPLOY_RUNBOOK — publishing the portfolio site

**Status: FINAL — B1-07, 2026-09-12.** Publishing is **RED**: it requires the owner's explicit
approval and is executed by **B1-08**, not by the implementing or verifying roles. Nothing in this
repository publishes itself and no credentials are stored here.

- **Frozen revision for the publish:** the commit B1-07 accepted — `4c84b7b` (record the exact
  `git rev-parse HEAD` at publish time; if it is not this revision, re-run the acceptance gate).
- **Target:** GitHub Pages, repository `mrahmy-reno.github.io`, serving the `/docs` folder at
  `https://mrahmy-reno.github.io/` (owner decisions Q1–Q4, `FACTS_LEDGER.md` §10).
- **Accepted-artefact hash:** 22 published files, manifest
  `10_manifest.txt` = `7c0ffc19eedaa1f4…` (byte-identical across B1-03/B1-04/B1-05/B1-06/B1-07).
  Use it to prove the published tree is the verified tree.

## What is published

The `docs/` directory of the git repository rooted at `/root/projects/portfolio-benchmark1/`,
served by GitHub Pages from the `mrahmy-reno.github.io` repository at
`https://mrahmy-reno.github.io/`. Everything outside `docs/` (tests, tooling, `content-map.md`,
this runbook) stays private.

Contents of the published surface (`docs/`): `index.html`, `404.html`, `robots.txt`, `sitemap.xml`,
`.nojekyll`, `assets/` (css, js, icons, `og-image.png`, `profile.jpg`), `projects/*.html` ×10 —
**22 files**. Paths are root-absolute and correct at a domain root.

## 1. Serve it locally (no tooling, the whole procedure)

```bash
cd /root/projects/portfolio-benchmark1
python3 -m http.server -d docs 8000      # then open http://127.0.0.1:8000/
```

There is no compile, bundle or install step; the files in `docs/` **are** the site. A clean-copy
reproduction of this command (plus the documented build) is recorded in
`/root/company/BENCHMARK_01/evidence/B1-07/REPRODUCIBILITY.md`.

**Verify locally before publishing** (expect HTTP 200 for each, 404 for the last):

```bash
for p in / /index.html /projects/sama-soc-triage.html /assets/styles.css /assets/profile.jpg \
         /robots.txt /sitemap.xml /.nojekyll; do
  printf '%s ' "$p"
  curl -sS -o /dev/null -w '%{http_code}\n' "http://127.0.0.1:8000$p"
done
curl -sS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:8000/no-such-page   # expect 404
```

Then spot-check in a browser at 1366×768 and 390×844: name, headline, current role, employer and
the LinkedIn link must be visible **without scrolling**, and the LinkedIn link must be in the header
of every page. These are the A2 checks; the automated evidence is in
`/root/company/BENCHMARK_01/evidence/B1-07/`.

## 2. Preconditions (all must hold before any publish)

1. `bash tests/run_all.sh` exits 0 on the exact commit to be published (step 08 Lighthouse included —
   see the A5 note in `OWNER_BRIEF.md`: on this shared host the median-of-3 is the accepted reading).
2. `/root/company/BENCHMARK_01/evidence/B1-06/REVERIFICATION.md` and
   `/root/company/BENCHMARK_01/evidence/B1-07/ACCEPTANCE_PASS.md` show every verifiable criterion
   PASS with independent raw evidence; no open BLOCKER/HIGH defect. **A13** (public reachability) is
   the only criterion that can be evaluated only *after* publishing (it is the point of B1-08).
3. `delivery-lead` has signed the acceptance record (A15) — `evidence/B1-07/ACCEPTANCE_PASS.md`.
4. The owner has approved publication (Q1–Q4) and the target route is unchanged. The route and the
   contact/photo/certification decisions are re-confirmed in
   `/root/company/BENCHMARK_01/reports/OWNER_BRIEF.md`.
5. `site.config.json` is in the state the owner approved — delivered state: **photo included,
   LinkedIn-only contact, no Tier-B certifications** — and `tests/switch_integrity.py` passes.
6. The v0.2 baseline seal is unchanged (`V0.2_BASELINE_SEAL.txt`) — nothing was written under
   `/root/company/COMPANY_OS_v0.2/`.
7. `git status --porcelain` is clean on the revision to be published.

## 3. Publish steps (B1-08, owner-gated)

```bash
# 0. pin the exact revision and prove the tree is the verified one
cd /root/projects/portfolio-benchmark1
git rev-parse HEAD && git status --porcelain          # HEAD must be the accepted revision; output empty
find docs -type f | sort | xargs sha256sum > /tmp/b1-08-manifest.txt
grep -c . /tmp/b1-08-manifest.txt                     # must be 22
diff /tmp/b1-08-manifest.txt "$(ls /root/company/BENCHMARK_01/evidence/B1-07/suite/10_manifest.txt \
     /root/company/BENCHMARK_01/evidence/B1-06/10_manifest.txt | head -1)"   # expect: only the trailing count line differs

# 1. create the public repository (owner-approved in Q3) and push the product tree.
#    The GitHub Pages source is: branch <default>, folder /docs
#    (equivalent to: Settings -> Pages -> Source: Deploy from a branch -> /docs)
#    Use the owner-approved stored credential (Q4). Do NOT commit any secret.

# 2. wait for the Pages build, then verify the published surface (do not trust the push's exit code)
curl -sS -o /dev/null -w '%{http_code} %{url_effective}\n' https://mrahmy-reno.github.io/
curl -sS -o /dev/null -w '%{http_code}\n' https://mrahmy-reno.github.io/sitemap.xml
curl -sS -o /dev/null -w '%{http_code}\n' https://mrahmy-reno.github.io/projects/sama-soc-triage.html
curl -sS -o /dev/null -w '%{http_code}\n' https://mrahmy-reno.github.io/assets/profile.jpg
curl -sS https://mrahmy-reno.github.io/robots.txt

# 3. confirm .nojekyll survived the deploy (otherwise paths starting with "_" would be hidden)
curl -sS -o /dev/null -w '%{http_code}\n' https://mrahmy-reno.github.io/.nojekyll

# 4. confirm the published bytes are the verified bytes
curl -sS https://mrahmy-reno.github.io/assets/styles.css | sha256sum
# compare with the same line in evidence/B1-07/suite/10_manifest.txt

# 5. confirm no new network surface was introduced by the host
curl -sS -o /dev/null -w '%{http_code}\n' https://mrahmy-reno.github.io/projects/halalbot.html
```

Post-publish evidence belongs in `evidence/B1-08/` (HTTP statuses, final URLs, a fetched copy of
`index.html`, the CSS hash comparison, and the owner's confirmation for **A13**). A13 closes only
when the owner confirms the site loads in a normal browser from outside this server.

## 4. Rollback

1. **Fast path (content config only):** change the one value in `site.config.json` (e.g. set
   `photo.enabled: false`), run `python3 tools/build_site.py`, `bash tests/run_all.sh`, commit and
   push. One line, fully reversible.
2. **Full revert:** `git revert <publish-commit>` (or `git checkout <previous-sha> -- docs/`) and
   push; GitHub Pages redeploys from `docs/` on the next build. Record the action.
3. **Emergency unpublish:** set the repository's Pages source to *None* in Settings → Pages (or make
   the repository private) and confirm the URL returns 404 from outside. Record the action and the
   time in `METRICS.md`; a public page cannot be un-indexed retroactively, so the owner must be told
   within the same session.
4. After any rollback, re-run `bash tests/run_all.sh` and record the result, then notify the
   chief-of-staff (never the owner directly).

## 5. Owner-decision switches (`FACTS_LEDGER.md` §10) — the only values that change what is published

All three live in `site.config.json`; each is a one-line change followed by
`python3 tools/build_site.py` and `bash tests/run_all.sh`. `tests/switch_integrity.py` asserts the
delivered state and that flipping a switch changes **only** its own surface.

| Switch | Delivered state (owner decision) | Change it by | Consequence |
|---|---|---|---|
| `contact.strategy` | `"linkedin"` — Q5 = LinkedIn only; **no** personal email, **no** phone anywhere in the build (§8 values are absent from every page, from JSON-LD and from the repo) | `"email"` / `"email_phone"` **after** filling `contact.email` / `contact.phone` with the exact §8 values | Reverses a privacy decision. Email/phone on a public page are scraped within days and cannot be un-published. **Owner decision required.** |
| `photo.enabled` | `true` — Q6 = include the LinkedIn photo; self-hosted `docs/assets/profile.jpg` (400×400 JPEG, 60 311 B, sha256 `be1dc0c6…89be`), explicit width/height, alt `Mohammed Tawfiq Rahmy` | `false` removes the portrait and its `<img>` | `false` is the privacy-preserving state. The signed LinkedIn CDN URL is never hot-linked. **Owner decision required.** |
| `certifications.tier_b` | `[]` — Q8 = none; zero Tier-B names anywhere in the repository | add an entry **only after** the owner confirms it **and** the `FACTS_LEDGER.md` row is added first | Tier-B names are currently absent from every page by construction; adding one makes an unverified claim publishable. **Owner decision required + ledger row first.** |

**Was any owner answer used as a switch default?** Yes, two of the three are *changes from the
privacy-preserving default* towards the owner's recorded answer (photo ON per Q6; LinkedIn-only per
Q5 means email/phone stay OFF). The Chief-of-Staff directive for this program fixed that; the
decisions themselves are the owner's and are re-confirmed in `OWNER_BRIEF.md` before publish.

## 6. Local re-verification of a deployed revision

```bash
git clone <repo> /tmp/verify && cd /tmp/verify
bash tools/install_dev_tooling.sh       # test-only Node tooling; node_modules/ is gitignored
                                        # (without it the Node steps are recorded as SKIPPED)
python3 -m http.server -d docs 8000     # spot-check in a browser
bash tests/run_all.sh                   # full suite against the same content
```

## 7. Known residual risks carried into the publish decision

- **A5 (Lighthouse ≥ 90) is host-sensitive.** On this shared 4-vCPU host the accepted reading is the
  **median of three runs per page**; the detail page has scored median 88 in one run under CPU steal
  while scoring 100 in another run of the byte-identical tree. CLS is 0 in every one of the 24
  recorded single-run reports, so this is not an artefact defect. The criterion text's aggregation
  rule is with the chief-of-staff (R2-04); the owner is asked to accept publish under this reading in
  `OWNER_BRIEF.md`.
- **A7 (external link):** LinkedIn answers an unauthenticated automated client with HTTP 999 /
  authwall. The authwall redirect carries the exact requested profile path (a login wall, not a
  404), and the URL is also printed as text on the page. Anonymous human visitors may hit the same
  wall.
- **A13 is not yet tested** — it can only be evaluated after publishing, from outside the host.
