#!/usr/bin/env bash
# A5 / D5 — Lighthouse (mobile preset) against the local static server.
# Runs on the index and on one project detail page; records the JSON, the Lighthouse version,
# the Chrome version and the exact CLI flags. Fails if any category < 0.90.
# Usage: bash tests/run_lighthouse.sh <evidence dir> [port]
set -uo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-/root/company/BENCHMARK_01/evidence/B1-03}"
PORT="${2:-8123}"
mkdir -p "$OUT"

LH=node_modules/.bin/lighthouse
export CHROME_PATH=/usr/bin/google-chrome

echo "=============================================================="
echo "LIGHTHOUSE — $(date -Is)"
echo "lighthouse version : $("${LH}" --version)"
echo "chrome version     : $("${CHROME_PATH}" --version)"
echo "flags              : --output=json --only-categories=performance,accessibility,best-practices,seo --chrome-flags='--headless=new --no-sandbox --disable-dev-shm-usage --disable-gpu'"
echo "form factor        : mobile (Lighthouse CLI default preset)"
echo "server             : python3 -m http.server -d docs ${PORT} --bind 127.0.0.1"
echo "=============================================================="

python3 -m http.server -d docs "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill ${SERVER_PID} >/dev/null 2>&1 || true' EXIT

for i in $(seq 1 20); do
  if curl -sf -o /dev/null "http://127.0.0.1:${PORT}/index.html"; then break; fi
  sleep 0.5
done

rc=0
for spec in "index:index.html" "sama-soc-triage:projects/sama-soc-triage.html"; do
  name="${spec%%:*}"
  page="${spec#*:}"
  echo
  echo "----- ${page} -----"
  "${LH}" "http://127.0.0.1:${PORT}/${page}" \
    --output=json --output-path="${OUT}/lighthouse-${name}.json" \
    --only-categories=performance,accessibility,best-practices,seo \
    --chrome-flags="--headless=new --no-sandbox --disable-dev-shm-usage --disable-gpu" \
    --max-wait-for-load=45000 --quiet
  lh_rc=$?
  echo "lighthouse_exit_code=${lh_rc}"
  [ "${lh_rc}" -ne 0 ] && rc=1
done

echo
echo "===== scores ====="
for name in index sama-soc-triage; do
  f="${OUT}/lighthouse-${name}.json"
  if [ ! -f "${f}" ]; then echo "${name}: NO JSON"; rc=1; continue; fi
  echo "${name}: $(jq -c '.categories | map_values((.score*100)|round)' "${f}")"
  echo "${name}: lighthouseVersion=$(jq -r '.lighthouseVersion' "${f}") userAgent=$(jq -r '.userAgent' "${f}") formFactor=$(jq -r '.configSettings.formFactor' "${f}") throttlingMethod=$(jq -r '.configSettings.throttlingMethod' "${f}")"
  low=$(jq -r '[.categories | to_entries[] | select(.value.score < 0.9) | .key] | join(",")' "${f}")
  if [ -n "${low}" ]; then echo "${name}: BELOW 0.90 -> ${low}"; rc=1; fi
  jq -r '.categories | to_entries[] | "    \(.key): \((.value.score*100)|round)  (threshold 90)"' "${f}"
done

echo
echo "=============================================================="
if [ "${rc}" -eq 0 ]; then
  echo "LIGHTHOUSE RESULT: PASS (all four categories >= 90 on both pages)"
else
  echo "LIGHTHOUSE RESULT: FAIL"
fi
echo "=============================================================="
exit "${rc}"
