# DEPLOY_RUNBOOK — publishing the portfolio site

**Status: FINAL — B1-07, 2026-09-12; repaired by B1-10, 2026-09-12** (rollback, pre-push guard and
publishing rules, after the post-delivery incident `INCIDENT_2026-09-12_publish_rollback.md`).
Publishing is **RED**: it requires the owner's explicit approval and is executed by **B1-08**, not by
the implementing or verifying roles. Nothing in this repository publishes itself and no credentials
are stored here.

- **Revision rule for a publish — there is no frozen SHA.** The gate is the **`docs/` manifest
  diff**. At publish time record `git rev-parse HEAD` — that recorded SHA *is* the published
  revision — and prove `docs/` is byte-identical to the recorded accepted manifest. Because only
  `docs/` is published, a commit that does not touch `docs/` (tests, tooling, this runbook) cannot
  invalidate an accepted publish. History: the B1-07 acceptance gate ran at `4c84b7b`; B1-09 then
  touched `tests/` only; the manifest diff was exit 0 and the publish deployed
  `7d22469e7541ab1d9dd683f631731bb7c8121a6f`.
- **Target:** GitHub Pages, repository `mrahmy-reno.github.io`, serving the `/docs` folder at
  `https://mrahmy-reno.github.io/` (owner decisions Q1–Q4, `FACTS_LEDGER.md` §10).
- **Accepted published tree:** 22 files under `docs/`, recorded in
  `tests/accepted_manifest_hashes.txt` (`sha256  <path relative to docs/>`, 22 lines) — the same 22
  hashes as `/root/company/BENCHMARK_01/evidence/B1-08/work/accepted_manifest_hashes.txt`, which
  labels them with a `docs/` prefix. Use it to prove the published tree is the verified tree.
- **Published revision today:** `7d22469e…`. The accepted B2 redesign is on local `master` and is
  **not published**; it becomes the published revision only through the B2-06 acceptance + republish
  (§6, "Updating the accepted manifest").

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
8. The `docs/` tree is byte-identical to the recorded accepted manifest
   `tests/accepted_manifest_hashes.txt` (see §3 step 0). If it is not, the manifest is out of date —
   update it only after an independent acceptance of the change (§6, "Updating the accepted
   manifest"), never to make a push go quiet.

## 3. Publish steps (B1-08, owner-gated)

```bash
# 0. pin the exact revision and prove the tree is the verified one
cd /root/projects/portfolio-benchmark1
git rev-parse HEAD                                    # RECORD this — it is the published revision
git status --porcelain                                # must print nothing
(cd docs && find . -type f -print0 | sort -z | xargs -0 sha256sum | sed 's| \./| |' | sort) \
  > /tmp/publish-manifest.txt
wc -l < /tmp/publish-manifest.txt                     # must be 22 for the accepted tree
diff /tmp/publish-manifest.txt tests/accepted_manifest_hashes.txt   # must be EMPTY — this is the gate

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

# 4. confirm the published bytes are the verified bytes — the whole manifest, not a sample (§4.5)
#    status codes alone are not proof; byte-identity against tests/accepted_manifest_hashes.txt is.

# 5. confirm no new network surface was introduced by the host
curl -sS -o /dev/null -w '%{http_code}\n' https://mrahmy-reno.github.io/projects/halalbot.html
```

Step 0's `diff` **is** the publish gate. It is a manifest comparison, not a commit pin: because only
`docs/` is published, a commit that does not change `docs/` cannot invalidate an accepted publish
(§2.8, §6). Record both the revision and the manifest of what was deployed, and keep the raw output.

Post-publish evidence belongs in `evidence/B1-08/` (HTTP statuses, final URLs, a fetched copy of
`index.html`, the CSS hash comparison, and the owner's confirmation for **A13**). A13 closes only
when the owner confirms the site loads in a normal browser from outside this server.

## 4. Rollback

**The rule (learned the hard way, 2026-09-12).** A rollback rehearsal is **never** performed against
the production repository. Rehearsals run **locally, or on a scratch branch or a throwaway
repository**, and the control being proven is the **pre-push guard** (§6) plus a post-push live-byte
check (§4.5) — not a destructive push. During the B1-08 publish the rehearsal *was* executed against
the live public repository: a temporary commit that deleted `docs/` was pushed, which removed the
site, failed the Pages build (Actions run #2, head commit `076ac8adf2`) and emailed the owner a
deployment-failure notification
(`/root/company/BENCHMARK_01/INCIDENT_2026-09-12_publish_rollback.md`). Production rollback is a
**documented procedure carried out only when a real rollback is intended**, with the reason and the
time recorded — it is not a test. Every rollback or rehearsal record states what was done, against
which repository (production or scratch), the raw command output, and the time.

### 4.1 Fast path (content config only)

Change the one value in `site.config.json` (e.g. set `photo.enabled: false`), run
`python3 tools/build_site.py`, `bash tests/run_all.sh`, commit and push. One line, fully reversible.

**A legitimate switch flip also requires the A16 assertion update in the same commit.**
`tests/switch_integrity.py` asserts the *delivered* state (photo ON, LinkedIn-only contact, no Tier-B
certifications). Flipping a switch without updating its A16 expectation makes that step fail **by
design** — that failure is the test doing its job, not a regression. Update the assertion for the
switch you flipped in the same commit and re-run the suite. Do not delete or weaken the assertion.

### 4.2 Full revert of the published content

```bash
git revert <publish-commit>        # or: git checkout <previous-sha> -- docs/
git push origin master             # Pages redeploys from docs/ on the next build
```

Verified for real in B1-08: `git reset --hard 7d22469 && git push --force origin master` → exit 0,
remote tip = the accepted revision, live `index.html` sha256 back to `ae436c6c…598`. Then re-run the
suite and re-verify the live bytes against the accepted manifest (§4.5).

### 4.3 Emergency takedown — what GitHub actually accepts for this repository

This repository is a **`<user>.github.io` user site**, and for that repository type most of the
"make it dark" routes either do not exist or do not work. All four rows below were **executed
against the live repository** on 2026-09-12; raw output is in
`/root/company/BENCHMARK_01/evidence/B1-08/logs/`.

| Route attempted | Actual result | Evidence |
|---|---|---|
| Set the Pages source to **`None`** (Settings → Pages → branch dropdown; the route GitHub documents for deleting a Pages site) | **Refused for this repo type.** `DELETE /repos/mrahmy-reno/mrahmy-reno.github.io/pages` → **HTTP 422** `{"message":"Deactivating GitHub pages for this repository is not allowed."}`. There is no *None* source to select for a user site. | `logs/rb_delete_response.json` |
| Delete the Pages source branch | Refused by the remote: `git push origin --delete master` → `! [remote rejected] master (refusing to delete the current branch: refs/heads/master)` | `logs/takedown_rehearsal.txt` |
| Push a commit that removes `docs/` | **Not a takedown.** The Pages build **errors** and the previous deployment keeps serving the accepted bytes (site stayed 200 for 95 s+). | `logs/takedown_rehearsal_docs_removal.txt` |
| **Make the repository private** | **Works.** Public URL returned **404 after 89 s** (edge-cache bound — not instant); the build itself stayed healthy. This is the only verified takedown route, and it is **RED/owner-gated**. | `logs/takedown_private_rehearsal.txt` |

**The private→public flip is not self-contained — the second step is mandatory.** Returning the
repository to public made GitHub **reset the Pages source to the repository root and auto-start a
build**. For **49 s** the site then served the repository root: `README` as the index, and
`/tests/run_all.sh`, `/tools/build_site.py`, `/content-map.md`, `/DEPLOY_RUNBOOK.md`,
`/site.config.json`, `/package.json` all reachable — risk R8 realised, the project tree published.
Full record: `evidence/B1-08/INCIDENT_001_pages_source_reset.md`.

So a takedown is **two steps plus a verification**, and the re-pin uses the right verb:

```bash
R=mrahmy-reno/mrahmy-reno.github.io
# credential: $TOKEN comes from the owner-approved stored credential (`git credential fill`, as in
# evidence/B1-08/work/fix_pages_put.sh) and is fed to curl on stdin (curl -K -) — never printed,
# never in argv, never in .git/config.
api() { curl -sS -K - -H 'Accept: application/vnd.github+json' "$@"; }

# 1. re-pin the Pages source — PUT, not PATCH (PATCH returns HTTP 404)
printf 'header = "Authorization: Bearer %s"\n' "$TOKEN" | api \
  -o /dev/null -w 'PUT /pages -> HTTP %{http_code}\n' \
  -X PUT "https://api.github.com/repos/$R/pages" \
  -d '{"source":{"branch":"master","path":"/docs"}}'
#   -> PUT /pages -> HTTP 204                    (logs/source_repin_fix.txt)

# 2. force the rebuild
printf 'header = "Authorization: Bearer %s"\n' "$TOKEN" | api \
  -o /dev/null -w 'POST /pages/builds -> HTTP %{http_code}\n' \
  -X POST "https://api.github.com/repos/$R/pages/builds"
#   -> POST /pages/builds -> HTTP 201            (logs/source_repin_rebuild.txt)

# 3. verify BOTH sides — the site is back AND the project tree is not served
for p in / /index.html /sitemap.xml /assets/styles.css; do
  printf '%s ' "$p"; curl -sS -o /dev/null -w '%{http_code} ' "https://mrahmy-reno.github.io$p"
done
curl -sS -o /dev/null -w '%{http_code}\n' https://mrahmy-reno.github.io/tests/run_all.sh   # must be 404
```

A takedown is **not** complete until `/tests/run_all.sh` (and the rest of the project tree) returns
**404** *and* the 22 published files are byte-identical to the accepted manifest again. Record the
action, the reason and the time in `METRICS.md`; a public page cannot be un-indexed retroactively, so
the chief-of-staff must be told within the same session (never the owner directly).

### 4.4 After any rollback

Re-run `bash tests/run_all.sh` and record the result, re-verify the live bytes against the accepted
manifest (§4.5), then notify the chief-of-staff (never the owner directly).

### 4.5 Post-rollback / post-push live verification

```bash
# every path in the accepted manifest, fetched from outside this host, compared byte-for-byte
while read -r want path; do
  got=$(curl -sS --retry 4 --retry-all-errors "https://mrahmy-reno.github.io/${path}" | sha256sum | cut -d' ' -f1)
  [ "$want" = "$got" ] && echo "ok   $path" || echo "FAIL $path"
done < tests/accepted_manifest_hashes.txt
curl -sS -o /dev/null -w 'project tree -> %{http_code} (must be 404)\n' \
  https://mrahmy-reno.github.io/tests/run_all.sh
```

Status codes alone are not proof: byte-identity against the manifest is the accepted evidence.

## 5. Publishing rules (non-negotiables)

1. **Never rehearse destruction against the production repository.** Rollback rehearsals are local, or
   on a scratch branch / throwaway repository. A rehearsal is proven by the guard (§6) and by a local
   or scratch push — never by pushing destruction. (2026-09-12: a rehearsal pushed a `docs/`-deleting
   commit to the live repository → public outage, failed Pages build, deployment-failure email to the
   owner.)
2. **Only `docs/` is published.** Everything else (`tests/`, `tools/`, `content-map.md`, `README.md`,
   `site.config.json`, this runbook) is private and must return **404** on the live site. Verify that
   after every push, not once.
3. **After every push, verify the live bytes against the accepted manifest** (§4.5) — status codes are
   not proof. And note the asymmetry that caused the incident: *a check made before a push cannot stop
   a push made after it*; the guard is the push-time protection, the manifest check is the
   result-time one. Both are required.
4. **The publish route is owner-approved and frozen:** repository `mrahmy-reno/mrahmy-reno.github.io`,
   GitHub Pages from branch `master`, folder `/docs`, HTTPS enforced, site
   `https://mrahmy-reno.github.io/`. **Any change to the route, the repository, or the credential is
   RED** — owner approval *before* execution, relayed by the chief-of-staff.
5. **No secret is ever stored or printed.** No token in a commit, a file, `.git/config`, a URL or a
   command line (`curl -K -` fed from the stored credential, as B1-08 did). Publishing is RED; a
   credential change is RED and owner-gated.
6. **Record what was published:** the revision (`git rev-parse HEAD`), the `docs/` manifest, the HTTP
   or API responses, and the time — raw output in `evidence/`, not a summary of it.

## 6. The pre-push guard (`tools/prepush_guard.sh`)

Added after the 2026-09-12 incident, because nothing at push time prevented a destructive commit from
reaching the live public repository. It is installed as `.git/hooks/pre-push`; git does not version
hooks, so install it in any fresh clone:

```bash
cd /root/projects/portfolio-benchmark1
cp tools/prepush_guard.sh .git/hooks/pre-push && chmod +x .git/hooks/pre-push
```

**What it blocks** (prints the reason and exits 1 — the push is refused):

- any push that deletes a file under `docs/`:
  ```
  [pre-push] BLOCKED: this push deletes files from the published surface (docs/):
    docs/robots.txt
    Rehearse rollback locally or on a scratch branch/repo. To override: ALLOW_DOCS_DELETION=1
  [pre-push] push refused.
  ```
- any commit message that looks like a destructive rehearsal:
  ```
  [pre-push] BLOCKED: commit message looks like a destructive rehearsal:
    B1-08 rollback rehearsal (temporary): remove docs/ to confirm the site can be taken down
  [pre-push] push refused.
  ```

**What it warns about** (exit 0 — the push proceeds, loudly):

- `docs/` differing from the recorded accepted manifest:
  ```
  [pre-push] WARNING: docs/ differs from the recorded accepted manifest (tests/accepted_manifest_hashes.txt).
             If this is an accepted change, update the manifest and re-verify.
  [pre-push] checks passed.
  ```

Both block demos were executed in a **throwaway clone pushing to a throwaway bare remote** — never
against the production repository — and the warning demo likewise; raw output in
`/root/company/BENCHMARK_01/evidence/B1-10/logs/guard_demo.txt` (scenarios A, B, D), with the clean
push passing (C) and the documented override working (E).

**The recorded accepted manifest: `tests/accepted_manifest_hashes.txt`.** 22 lines of
`sha256  <path relative to docs/>` — the accepted state of the published surface. Regenerate it with:
```bash
(cd docs && find . -type f -print0 | sort -z | xargs -0 sha256sum | sed 's| \./| |' | sort)
```
It is the *reference*, not a convenience: it is regenerated **only after an independent acceptance** of
a change to `docs/` (full suite green on the new tree, acceptance recorded), in the same commit as
that change, and **never** just to silence the warning. It is currently **untracked in git** (see the
repair card below), so a fresh clone does not carry it — copy it in with the guard.

**The overrides are deliberate and loud.** `ALLOW_DOCS_CHANGE=1` and `ALLOW_DOCS_DELETION=1` exist so
that a *legitimately accepted* change can be published — every push that changes `docs/` needs one, or
the guard's target state and the tree will disagree. Using one asserts that the change was
independently accepted: **put the reason in the commit message**, and for a deletion name the file
that is superseded and why. A silent override is the same defect as no guard at all.

**Known limitations (verified in B1-10; do not treat the guard as complete).** Raw output in
`/root/company/BENCHMARK_01/evidence/B1-10/logs/`; repair card **B1-11 (`t_2e0396ce`)**.

- A removal expressed as a **rename inside `docs/`** (`git mv docs/a.html docs/b.html`) is reported by
  git as `R100 …`, whose status is `R`, not `D` — the deletion check does not fire and only the
  manifest warning is printed, while the file does leave the published surface. Control and repro:
  `logs/guard_probe_rename.txt`.
- On the **first push of a brand-new remote ref** the guard evaluates the push against the **working
  tree**, so it can refuse a push for a deletion the push does not contain: `logs/guard_probe_initialpush.txt`.
  Every push to `master` has an existing ref, so the publish route itself is unaffected.
- The guard is a **local** hook. It protects pushes made from a clone that has it installed; it is not
  a server-side rule and must not be relied on as the only control.

### Updating the accepted manifest — the B2 redesign and later

The accepted redesign (phase B2) legitimately changes `docs/` and may delete a superseded asset. That
is an **accepted change, not a rehearsal**, and it follows the same rules as any other change:

1. the new `docs/` tree passes the full suite (`bash tests/run_all.sh`) and is **independently
   accepted first**;
2. then regenerate `tests/accepted_manifest_hashes.txt` from the accepted tree and commit it **in the
   same commit as the change**;
3. push with `ALLOW_DOCS_CHANGE=1` — plus `ALLOW_DOCS_DELETION=1` if a published file is genuinely
   removed — with the reason in the commit message;
4. then re-verify the live bytes against the **new** manifest (§4.5) and confirm the project-tree
   paths are still 404.

## 7. Owner-decision switches (`FACTS_LEDGER.md` §10) — the only values that change what is published

All three live in `site.config.json`; each is a one-line change followed by
`python3 tools/build_site.py` and `bash tests/run_all.sh` — **plus the A16 assertion update for the
switch you flipped, in the same commit (§4.1)**. `tests/switch_integrity.py` asserts the
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

## 8. Local re-verification of a deployed revision

```bash
git clone <repo> /tmp/verify && cd /tmp/verify
bash tools/install_dev_tooling.sh       # test-only Node tooling; node_modules/ is gitignored
                                        # (without it the Node steps are recorded as SKIPPED)
python3 -m http.server -d docs 8000     # spot-check in a browser
bash tests/run_all.sh                   # full suite against the same content
```

## 9. Known residual risks carried into the publish decision

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
