#!/usr/bin/env bash
# A8 / D8 — HTML validation with named validators.
#   1. html-validate (local, offline, pinned version) — authoritative for this run
#   2. W3C Nu HTML Checker (https://validator.w3.org/nu/) over all 12 pages, paced + retried
#      (see tests/validate_nu.py for how a rate-limited page is reported)
# Usage: bash tests/validate_html.sh <evidence dir>
set -uo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-/root/company/BENCHMARK_01/evidence/B1-03}"
mkdir -p "$OUT"

echo "=============================================================="
echo "HTML VALIDATION — $(date -Is)"
echo "html-validate: $(node_modules/.bin/html-validate --version)"
echo "=============================================================="

echo
echo "===== 1. html-validate (local, offline) ====="
node_modules/.bin/html-validate --config tests/htmlvalidate.json "docs/**/*.html"
hv_rc=$?
echo "html_validate_exit_code=${hv_rc}"

echo
echo "===== 2. W3C Nu HTML Checker (validator.w3.org) ====="
python3 tests/validate_nu.py --docs docs --json "${OUT}/w3c-nu-results.json"
nu_rc=$?
echo "w3c_nu_exit_code=${nu_rc}"

echo
echo "=============================================================="
if [ "${hv_rc}" -eq 0 ] && [ "${nu_rc}" -eq 0 ]; then
  echo "HTML VALIDATION RESULT: PASS"
  exit 0
fi
echo "HTML VALIDATION RESULT: FAIL (html_validate_exit=${hv_rc}, w3c_nu_exit=${nu_rc})"
exit 1
