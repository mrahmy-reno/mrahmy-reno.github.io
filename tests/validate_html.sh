#!/usr/bin/env bash
# A8 / D8 — HTML validation with named validators.
#   1. html-validate (local, offline, pinned version)
#   2. W3C Nu HTML Checker (https://validator.w3.org/nu/) over all 12 pages
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
nu_fail=0
for f in docs/index.html docs/404.html docs/projects/*.html; do
  resp=$(curl -sS --max-time 60 -H "Content-Type: text/html; charset=utf-8" \
    --data-binary "@${f}" "https://validator.w3.org/nu/?out=json")
  if [ -z "${resp}" ]; then
    echo "${f}: NO RESPONSE (network or rate limit) — recorded as a substitution gap"
    nu_fail=1
    continue
  fi
  summary=$(printf '%s' "${resp}" | jq -c '{errors: [.messages[] | select(.type=="error") | {lastLine, message}],
                                            warnings: [.messages[] | select(.type=="info" and (.subType=="warning")) | {lastLine, message}],
                                            errorCount: ([.messages[] | select(.type=="error")] | length)}')
  echo "${f}: ${summary}"
  n=$(printf '%s' "${resp}" | jq '[.messages[] | select(.type=="error")] | length')
  if [ "${n}" != "0" ]; then nu_fail=1; fi
  sleep 1
done
echo "w3c_nu_errors_found=${nu_fail}"

echo
echo "=============================================================="
if [ "${hv_rc}" -eq 0 ] && [ "${nu_fail}" -eq 0 ]; then
  echo "HTML VALIDATION RESULT: PASS"
  exit 0
fi
echo "HTML VALIDATION RESULT: FAIL (html_validate_exit=${hv_rc}, w3c_errors=${nu_fail})"
exit 1
