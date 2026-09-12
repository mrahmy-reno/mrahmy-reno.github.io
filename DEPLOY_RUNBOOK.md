# DEPLOY_RUNBOOK — publishing the portfolio site

**Status: STUB (drafted by B1-03 for B1-07 to finalise).** Publishing is **RED**: it requires the
owner's approval and is executed by **B1-08**, not by the implementing or verifying roles. Nothing
in this repository publishes itself and no credentials are stored here.

## What is published

The `docs/` directory of the git repository rooted at `/root/projects/portfolio-benchmark1/`,
served by GitHub Pages from the `mrahmy-reno.github.io` repository at
`https://mrahmy-reno.github.io/`. Everything outside `docs/` (tests, tooling, `content-map.md`,
this runbook) stays private.

## Preconditions (must all hold before any publish)

1. `bash tests/run_all.sh` exits 0 on the exact commit to be published.
2. `evidence/B1-04/ACCEPTANCE_RESULTS.md` shows every criterion A1–A17 PASS with independent raw
   evidence, and `evidence/B1-04/DEFECTS.md` shows no open BLOCKER/HIGH defect.
3. `delivery-lead` has signed the acceptance record (A15).
4. The owner has approved publication (owner decision Q1–Q4) and the target route is unchanged.
5. `site.config.json` is in the state the owner approved (delivered state: photo included,
   LinkedIn-only contact, no Tier-B certifications) and `tests/switch_integrity.py` passes.
6. The v0.2 baseline seal is unchanged (`V0.2_BASELINE_SEAL.txt`) — nothing was written under
   `/root/company/COMPANY_OS_v0.2/`.

## Publish steps (B1-08, owner-gated)

```bash
# 0. pin the exact revision
cd /root/projects/portfolio-benchmark1
git rev-parse HEAD && git status --porcelain      # must be clean

# 1. create the public repository (owner-approved in Q3) and push the product tree.
#    The GitHub Pages source is: branch <default>, folder /docs
#    (equivalent to: Settings -> Pages -> Source: Deploy from a branch -> /docs)

# 2. verify the published surface (do not trust the push's exit code):
curl -sS -o /dev/null -w '%{http_code} %{url_effective}\n' https://mrahmy-reno.github.io/
curl -sS -o /dev/null -w '%{http_code}\n' https://mrahmy-reno.github.io/sitemap.xml
curl -sS -o /dev/null -w '%{http_code}\n' https://mrahmy-reno.github.io/projects/sama-soc-triage.html
curl -sS https://mrahmy-reno.github.io/robots.txt

# 3. confirm .nojekyll survived the deploy (otherwise paths starting with "_" would be hidden)
curl -sS -o /dev/null -w '%{http_code}\n' https://mrahmy-reno.github.io/.nojekyll
```

Post-publish evidence belongs in `evidence/B1-08/` (HTTP statuses, final URLs, a fetched copy of
`index.html`, and the owner's confirmation for A13).

## Rollback

1. **Fast path (content config only):** change the one value in `site.config.json` (e.g. set
   `photo.enabled: false`), run `python3 tools/build_site.py`, `bash tests/run_all.sh`, commit and
   push. One line, fully reversible.
2. **Full revert:** `git revert <publish-commit>` (or `git checkout <previous-sha> -- docs/`) and
   push; GitHub Pages redeploys from `docs/` on the next build. Record the action.
3. **Emergency unpublish:** set the repository's Pages source to *None* in Settings → Pages (or
   make the repository private) and confirm the URL returns 404 from outside. Record the action and
   the time in `METRICS.md`; a public page cannot be un-indexed retroactively, so the owner must be
   told within the same session.
4. After any rollback, re-run `bash tests/run_all.sh` and record the result, then notify the
   chief-of-staff (never the owner directly).

## Local re-verification of a deployed revision

```bash
git clone <repo> /tmp/verify && cd /tmp/verify
python3 -m http.server -d docs 8000     # spot-check in a browser
bash tests/run_all.sh                   # full suite against the same content
```
