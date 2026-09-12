#!/usr/bin/env bash
# Full check suite for the Benchmark #1 portfolio site.
#
#   bash tests/run_all.sh                 # evidence -> /root/company/BENCHMARK_01/evidence/B1-03
#   EVIDENCE_DIR=/tmp/x bash tests/run_all.sh
#
# PREREQUISITE (B1-05 / D-02): the browser, link, HTML-validation and Lighthouse steps need the
# pinned test-only tooling in node_modules/, which is gitignored and therefore absent in a fresh
# clone. Install it once with:  bash tools/install_dev_tooling.sh      (npm install)
# Serving or deploying the site needs none of it: `python3 -m http.server -d docs 8000`.
# If the tooling is absent the suite does NOT pretend to pass: those steps are recorded as SKIPPED,
# the reason is printed, and the run still exits non-zero.
#
# Every step writes its raw output into the evidence directory and the script exits non-zero if any
# step fails. Serve the site exactly as documented with: python3 -m http.server -d docs 8000
set -uo pipefail
cd "$(dirname "$0")/.."
REPO="$(pwd)"
OUT="${EVIDENCE_DIR:-/root/company/BENCHMARK_01/evidence/B1-03}"
mkdir -p "$OUT"

declare -a NAMES=()
declare -a CODES=()

step() { # step <logfile-name> <command...>
  local name="$1"; shift
  echo "=============================================================="
  echo "STEP ${name}: $*"
  echo "=============================================================="
  "$@" >"${OUT}/${name}" 2>&1
  local rc=$?
  NAMES+=("${name}")
  CODES+=("${rc}")
  echo "-> exit ${rc}  (log: ${OUT}/${name})"
  tail -n 6 "${OUT}/${name}" | sed 's/^/    /'
  echo
  return "${rc}"
}

skipped() { # skipped <logfile-name> <command...> — prerequisite tooling absent (D-02)
  local name="$1"; shift
  echo "=============================================================="
  echo "STEP ${name}: SKIPPED — node test tooling missing (run bash tools/install_dev_tooling.sh)"
  echo "=============================================================="
  {
    echo "STEP SKIPPED: ${name}"
    echo "command         : $*"
    echo "reason          : the Node test tooling is not installed in this checkout (node_modules/"
    echo "                  is gitignored, so a fresh clone never has it)."
    echo "remedy          : bash tools/install_dev_tooling.sh   # npm install (test-only tooling)"
    echo "status          : NOT RUN — this is not a pass and not a failure of the site."
  } >"${OUT}/${name}"
  NAMES+=("${name}")
  CODES+=("3")
  echo "-> SKIPPED (prerequisite missing; log: ${OUT}/${name})"
  echo
  return 3
}

run_step() { # run_step <logfile-name> <command...> — step, or honest SKIP when tooling is absent
  if [ "${TOOLING_RC:-1}" -eq 0 ]; then
    step "$@"
  else
    skipped "$@"
  fi
}

row() { # row <label> <exit-code> — 3 is rendered as SKIP, never as a pass
  if [ "$2" -eq 3 ]; then
    printf '%-28s %s\n' "$1" "SKIP (node tooling missing — not run)"
  else
    printf '%-28s %s\n' "$1" "$2"
  fi
}

echo "Benchmark #1 — full check suite"
echo "repo     : ${REPO}"
echo "evidence : ${OUT}"
echo "started  : $(date -Is)"
echo

# 0. tooling preflight (B1-05 / D-02): fail loudly and actionably instead of five opaque
#    ERR_MODULE_NOT_FOUND errors. Report only — this never installs anything.
echo "=============================================================="
echo "TOOLING PREFLIGHT"
echo "=============================================================="
bash "$REPO/tools/check_dev_tooling.sh" 2>&1 | tee "${OUT}/00b_tooling_preflight.txt"
TOOLING_RC=${PIPESTATUS[0]}
echo "-> preflight exit ${TOOLING_RC}  (log: ${OUT}/00b_tooling_preflight.txt)"
if [ "${TOOLING_RC}" -ne 0 ]; then
  echo
  echo "PREREQUISITE MISSING: the Node check tooling is not installed in this checkout."
  echo "  Install it once:  bash tools/install_dev_tooling.sh     # npm install (test-only)"
  echo "  The steps that need it are recorded as SKIPPED below and this run exits non-zero."
  echo "  The published site itself needs no tooling: python3 -m http.server -d docs 8000"
fi
echo

# 0. tool versions and environment (A11 / D9 / D13: reproducibility record)
{
  echo "== environment =="
  echo "date            : $(date -Is)"
  echo "host            : $(uname -a)"
  echo "python          : $(python3 -V 2>&1)"
  echo "node            : $(node -v 2>&1)"
  echo "npm             : $(npm -v 2>&1)"
  echo "chrome          : $(/usr/bin/google-chrome --version 2>&1)"
  echo "lighthouse      : $(node_modules/.bin/lighthouse --version 2>&1)"
  echo "html-validate   : $(node_modules/.bin/html-validate --version 2>&1)"
  echo
  echo "== pinned dev tooling (package.json devDependencies) =="
  cat package.json
  echo
  echo "== node-resolved versions =="
  node tools/versions.cjs
  echo
  echo "== runtime dependencies =="
  echo "0 (static HTML/CSS/JS; the npm packages above are test-only and are not shipped in docs/)"
  echo
  echo "== revision under test =="
  echo "git HEAD      : $(git rev-parse HEAD 2>/dev/null || echo 'no git')"
  echo "git worktree  : $(git status --porcelain 2>/dev/null | wc -l) uncommitted change(s)"
  echo "commits       : $(git log --oneline 2>/dev/null | head -5 | tr '\n' '|')"
  echo
  echo "== published asset hashes (sha256) =="
  find docs -type f | sort | xargs sha256sum
} >"${OUT}/00_environment.txt" 2>&1
echo "wrote ${OUT}/00_environment.txt"

# 1. build the publish root from site.config.json (must not change the committed output)
step 01_build.txt python3 tools/build_site.py
BUILD_RC=$?

# 2. static source-level audit (coverage, links, bans, PII, metadata, attribution guard)
step 02_static_scans.txt python3 tests/static_scans.py
STATIC_RC=$?

# 2b. regression tests for the defects repaired in B1-05 (tooling scripts, honest skip mode,
#     evidence-extraction guard, byte-reproducibility, Lighthouse median). Python-stdlib only and
#     independent of node_modules, so it is wired through `step` and NOT through `run_step`: it
#     runs in every checkout, including a fresh clone with no installed tooling, where only the
#     Node-dependent steps are the ones recorded as SKIPPED (R2-01: this line must stay in sync
#     with the comment above it).
step 02b_regression_repairs.txt python3 tests/regression_repairs.py
REGRESSION_RC=$?

# 3. browser audit: rendered text, axe on all 12 pages, console, overflow, first screen,
#    keyboard walk, reduced motion, progressive enhancement, print/PDF, screenshots
run_step 03_browser_checks.log node tests/browser_checks.mjs --out "${OUT}" --port 8099
BROWSER_RC=$?

# 4. rendered-text scans: provenance (A1), banned patterns (D1), numeric whitelist (A12/D12)
run_step 04_text_scans.txt python3 tests/text_scans.py --text "${OUT}/rendered-text"
TEXT_RC=$?

# 5. owner-decision switch integrity (A16 / D14)
step 05_switch_integrity.txt python3 tests/switch_integrity.py
SWITCH_RC=$?

# 6. external link destination (A7) — network
run_step 06_link_check.log node tests/link_check.mjs --out "${OUT}"
LINK_RC=$?

# 7. HTML validation: html-validate + W3C Nu (A8 / D8)
run_step 07_html_validation.txt bash tests/validate_html.sh "${OUT}"
VALIDATE_RC=$?

# 8. Lighthouse mobile (A5 / D5)
run_step 08_lighthouse.log bash tests/run_lighthouse.sh "${OUT}"
LH_RC=$?

# 9. fresh-clone reproduction (A11 / D11 — the builder's own rehearsal; B1-04 repeats it
#    independently)
step 09_reproduce.txt bash tests/reproduce.sh
REPRO_RC=$?

# 10. manifest of the published tree
find docs -type f | sort | xargs sha256sum >"${OUT}/10_manifest.txt"
echo "published files: $(find docs -type f | wc -l)" >>"${OUT}/10_manifest.txt"

# 11. summary
{
  echo "Benchmark #1 — check suite summary"
  echo "finished: $(date -Is)"
  echo
  if [ "${TOOLING_RC}" -eq 0 ]; then
    echo "tooling preflight: OK (node_modules present)"
  else
    echo "PREREQUISITE MODE: node tooling missing — steps 03/04/06/07/08 were SKIPPED, not run."
    echo "  remedy: bash tools/install_dev_tooling.sh   (see 00b_tooling_preflight.txt)"
  fi
  echo
  printf '%-28s %s\n' "STEP" "EXIT"
  row 01_build "${BUILD_RC}"
  row 02_static_scans "${STATIC_RC}"
  row 02b_regression_repairs "${REGRESSION_RC}"
  row 03_browser_checks "${BROWSER_RC}"
  row 04_text_scans "${TEXT_RC}"
  row 05_switch_integrity "${SWITCH_RC}"
  row 06_link_check "${LINK_RC}"
  row 07_html_validation "${VALIDATE_RC}"
  row 08_lighthouse "${LH_RC}"
  row 09_reproduce "${REPRO_RC}"
  echo
  echo "axe per page:"
  if [ -f "${OUT}/browser-summary.json" ]; then
    python3 - "${OUT}/browser-summary.json" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
for page, s in d["axe"].items():
    print(f"  {page:34} violations={s['violations']} critical={s['critical']} "
          f"serious={s['serious']} moderate={s['moderate']} minor={s['minor']} "
          f"passes={s['passes']}")
print(f"  browser checks: {d['checks']}  failures: {len(d['failures'])}")
PY
  else
    echo "  UNAVAILABLE (step 03 did not run — see 03_browser_checks.log)"
  fi
  echo
  echo "lighthouse scores (mobile, MEDIAN of every kept run per page; A5 bar = >= 90 everywhere):"
  for n in index sama-soc-triage; do
    files=$(ls "${OUT}"/lighthouse-${n}-run*.json 2>/dev/null | sort)
    if [ -z "${files}" ]; then
      echo "  ${n}: UNAVAILABLE (no run JSON — see 08_lighthouse.log)"
    else
      echo "  ${n}:"
      python3 tools/lh_median.py ${files} | sed 's/^/    /'
    fi
  done
} >"${OUT}/11_summary.txt" 2>&1
cat "${OUT}/11_summary.txt"

RC=0
for c in "${CODES[@]}"; do [ "${c}" -ne 0 ] && RC=1; done
echo
echo "=============================================================="
echo "CHECK SUITE RESULT: $([ ${RC} -eq 0 ] && echo PASS || echo FAIL)   (evidence: ${OUT})"
if [ "${RC}" -ne 0 ] && [ "${TOOLING_RC}" -ne 0 ]; then
  echo "CAUSE: prerequisite missing — at least one step could not run (not a site failure)."
  echo "  Install the test tooling and re-run: bash tools/install_dev_tooling.sh && bash tests/run_all.sh"
fi
echo "=============================================================="
exit "${RC}"
