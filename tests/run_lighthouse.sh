#!/usr/bin/env bash
# A5 / D5 — Lighthouse (mobile preset) against the local static server.
#
# Measurement methodology: the page is measured three times and the MEDIAN per category is the
# reported score, because this host runs other benchmark processes and a single lab run is noisy.
# Every individual run's JSON is kept (lighthouse-<page>-run<N>.json) and the spread is printed, so
# the raw data is auditable rather than reduced to one number. The 90 threshold is applied to the
# median; any individual run is visible in the log and in the JSON files.
#
# Usage: bash tests/run_lighthouse.sh <evidence dir> [port]
set -uo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-/root/company/BENCHMARK_01/evidence/B1-03}"
PORT="${2:-8123}"
RUNS="${LIGHTHOUSE_RUNS:-3}"
mkdir -p "$OUT"

LH=node_modules/.bin/lighthouse
export CHROME_PATH=/usr/bin/google-chrome

echo "=============================================================="
echo "LIGHTHOUSE — $(date -Is)"
echo "lighthouse version : $("${LH}" --version)"
echo "chrome version     : $("${CHROME_PATH}" --version)"
echo "form factor        : mobile (Lighthouse CLI default preset)"
echo "runs per page      : ${RUNS} (median is reported; every run is kept)"
echo "flags              : --output=json --only-categories=performance,accessibility,best-practices,seo"
echo "                     --chrome-flags='--headless=new --no-sandbox --disable-dev-shm-usage --disable-gpu'"
echo "server             : python3 -m http.server -d docs ${PORT} --bind 127.0.0.1"
echo "load average       : $(cut -d' ' -f1-3 /proc/loadavg)"
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
  for run in $(seq 1 "${RUNS}"); do
    echo
    echo "----- ${page} — run ${run}/${RUNS} -----"
    "${LH}" "http://127.0.0.1:${PORT}/${page}" \
      --output=json --output-path="${OUT}/lighthouse-${name}-run${run}.json" \
      --only-categories=performance,accessibility,best-practices,seo \
      --chrome-flags="--headless=new --no-sandbox --disable-dev-shm-usage --disable-gpu" \
      --max-wait-for-load=45000 --quiet
    lh_rc=$?
    echo "lighthouse_exit_code=${lh_rc}"
    [ "${lh_rc}" -ne 0 ] && rc=1
    echo "  scores: $(jq -c '.categories | map_values((.score*100)|round)' "${OUT}/lighthouse-${name}-run${run}.json" 2>/dev/null)"
  done
done

echo
echo "===== median of ${RUNS} runs per page ====="
for name in index sama-soc-triage; do
  files=$(ls "${OUT}"/lighthouse-${name}-run*.json 2>/dev/null | sort)
  if [ -z "${files}" ]; then echo "${name}: NO JSON"; rc=1; continue; fi
  # publish the median run as the canonical artefact as well
  jq -s '.' ${files} > "${OUT}/lighthouse-${name}-all-runs.json"
  for cat in performance accessibility best-practices seo; do
    values=$(for f in ${files}; do jq -r --arg c "${cat}" '(.categories[$c].score*100)|round' "${f}"; done | sort -n)
    n=$(printf '%s\n' ${values} | wc -l)
    med=$(printf '%s\n' ${values} | awk -v n="${n}" 'NR==int((n+1)/2){print; exit}')
    min=$(printf '%s\n' ${values} | head -1)
    max=$(printf '%s\n' ${values} | tail -1)
    csv=$(printf '%s\n' ${values} | paste -sd, -)
    mark=""
    if [ "${med}" -lt 90 ]; then mark="  <-- BELOW THRESHOLD"; rc=1; fi
    printf '  %-22s median=%s (runs: %s)  min=%s max=%s%s\n' \
      "${name}/${cat}" "${med}" "${csv}" "${min}" "${max}" "${mark}"
  done
  echo "  ${name}: lighthouseVersion=$(jq -r '.lighthouseVersion' $(echo ${files} | awk '{print $1}')) formFactor=$(jq -r '.configSettings.formFactor' $(echo ${files} | awk '{print $1}')) throttling=$(jq -r '.configSettings.throttlingMethod' $(echo ${files} | awk '{print $1}'))"
done

echo
echo "=============================================================="
if [ "${rc}" -eq 0 ]; then
  echo "LIGHTHOUSE RESULT: PASS (median >= 90 on all four categories, both pages)"
else
  echo "LIGHTHOUSE RESULT: FAIL"
fi
echo "=============================================================="
exit "${rc}"
