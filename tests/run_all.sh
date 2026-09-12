#!/usr/bin/env bash
# Full check suite for the Benchmark #1 portfolio site.
#
#   bash tests/run_all.sh                 # evidence -> /root/company/BENCHMARK_01/evidence/B1-03
#   EVIDENCE_DIR=/tmp/x bash tests/run_all.sh
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

echo "Benchmark #1 — full check suite"
echo "repo     : ${REPO}"
echo "evidence : ${OUT}"
echo "started  : $(date -Is)"
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

# 3. browser audit: rendered text, axe on all 12 pages, console, overflow, first screen,
#    keyboard walk, reduced motion, progressive enhancement, print/PDF, screenshots
step 03_browser_checks.log node tests/browser_checks.mjs --out "${OUT}" --port 8099
BROWSER_RC=$?

# 4. rendered-text scans: provenance (A1), banned patterns (D1), numeric whitelist (A12/D12)
step 04_text_scans.txt python3 tests/text_scans.py --text "${OUT}/rendered-text"
TEXT_RC=$?

# 5. owner-decision switch integrity (A16 / D14)
step 05_switch_integrity.txt python3 tests/switch_integrity.py
SWITCH_RC=$?

# 6. external link destination (A7) — network
step 06_link_check.log node tests/link_check.mjs --out "${OUT}"
LINK_RC=$?

# 7. HTML validation: html-validate + W3C Nu (A8 / D8)
step 07_html_validation.txt bash tests/validate_html.sh "${OUT}"
VALIDATE_RC=$?

# 8. Lighthouse mobile (A5 / D5)
step 08_lighthouse.log bash tests/run_lighthouse.sh "${OUT}"
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
  printf '%-28s %s\n' "STEP" "EXIT"
  printf '%-28s %s\n' "01_build" "${BUILD_RC}"
  printf '%-28s %s\n' "02_static_scans" "${STATIC_RC}"
  printf '%-28s %s\n' "03_browser_checks" "${BROWSER_RC}"
  printf '%-28s %s\n' "04_text_scans" "${TEXT_RC}"
  printf '%-28s %s\n' "05_switch_integrity" "${SWITCH_RC}"
  printf '%-28s %s\n' "06_link_check" "${LINK_RC}"
  printf '%-28s %s\n' "07_html_validation" "${VALIDATE_RC}"
  printf '%-28s %s\n' "08_lighthouse" "${LH_RC}"
  printf '%-28s %s\n' "09_reproduce" "${REPRO_RC}"
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
  fi
  echo
  echo "lighthouse scores (mobile, median of 3 runs per page):"
  for n in index sama-soc-triage; do
    f="${OUT}/lighthouse-${n}-run1.json"
    [ -f "${f}" ] || f=$(ls "${OUT}"/lighthouse-${n}-run*.json 2>/dev/null | head -1)
    [ -n "${f}" ] && echo "  ${n}: $(jq -c '.categories | map_values((.score*100)|round)' "${f}")  (see 08_lighthouse.log for every run)"
  done
} >"${OUT}/11_summary.txt" 2>&1
cat "${OUT}/11_summary.txt"

RC=0
for c in "${CODES[@]}"; do [ "${c}" -ne 0 ] && RC=1; done
echo
echo "=============================================================="
echo "CHECK SUITE RESULT: $([ ${RC} -eq 0 ] && echo PASS || echo FAIL)   (evidence: ${OUT})"
echo "=============================================================="
exit "${RC}"
