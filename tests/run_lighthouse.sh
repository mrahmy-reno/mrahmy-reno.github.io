#!/usr/bin/env bash
# A5 / D5 — Lighthouse (mobile preset) against the local static server.
#
# Measurement methodology: the page is measured RUNS times (default 9, always an ODD count) and the
# MEDIAN per category is the reported score, because this host runs other benchmark processes and a
# single lab run is noisy. Every individual run's JSON is kept (lighthouse-<page>-run<N>.json) and
# the spread is printed, so the raw data is auditable rather than reduced to one number. The 90
# threshold is applied to the median; any individual run is visible in the log and in the JSON
# files.
#
# B2-05b / N4 — the count is odd BY CONSTRUCTION and the median has ONE definition. An even count
# has two middle values, and the two halves of the suite used to disagree about which to report:
# this step took the lower-middle value (for the 8 index runs 69,72,84,88,97,98,98,99 it printed
# 88 and FAILED the step) while the summary (tools/lh_median.py) took the standard median (92) and
# PASSED the same criterion in the same run — the suite ended FAIL while its own A5 line said
# PASS, so no acceptance number could be written from it. Now: (a) `LIGHTHOUSE_RUNS` is forced odd
# (an even request is run one extra time, stated in the log, never by dropping a run), (b) both
# halves report `tools/lh_median.py`'s single definition, named in the log, and (c) the `>= 90`
# threshold is unchanged.
#
# Usage: bash tests/run_lighthouse.sh <evidence dir> [port]
#
# B2-04 / D13: the port is no longer assumed. When no port is given one is probed (tools/
# free_port.py), and a server that fails to bind is reported as an ENVIRONMENT ERROR (exit 3)
# instead of being scored — a reviewer's own probe can no longer silently corrupt this step.
set -uo pipefail
cd "$(dirname "$0")/.."
OUT="${1:-/root/company/BENCHMARK_01/evidence/B1-03}"
PORT="${2:-}"
if [ -z "${PORT}" ]; then
  PORT="$(python3 tools/free_port.py)" || { echo "could not probe a free port"; exit 3; }
  echo "port      : probed free port ${PORT} (tools/free_port.py)"
fi
RUNS="${LIGHTHOUSE_RUNS:-9}"
RUNS_NOTE=""
if [ $((RUNS % 2)) -eq 0 ]; then
  RUNS_NOTE=" (requested ${RUNS}, even: an even count has two middle values, so one extra run is "
  RUNS_NOTE="${RUNS_NOTE}taken to $((RUNS + 1)) rather than dropping a measured run)"
  RUNS=$((RUNS + 1))
fi
MEDIAN_CONVENTION="$(python3 tools/lh_median.py --convention)"
mkdir -p "$OUT"
# a stale run from an earlier, longer invocation must never enter this median
rm -f "${OUT}"/lighthouse-*-run*.json

LH=node_modules/.bin/lighthouse
export CHROME_PATH=/usr/bin/google-chrome

echo "=============================================================="
echo "LIGHTHOUSE — $(date -Is)"
echo "lighthouse version : $("${LH}" --version)"
echo "chrome version     : $("${CHROME_PATH}" --version)"
echo "form factor        : mobile (Lighthouse CLI default preset)"
echo "runs per page      : ${RUNS}${RUNS_NOTE} (median is reported; every run is kept)"
echo "median convention  : ${MEDIAN_CONVENTION}"
echo "flags              : --output=json --only-categories=performance,accessibility,best-practices,seo"
echo "                     --chrome-flags='--headless=new --no-sandbox --disable-dev-shm-usage --disable-gpu'"
echo "server             : python3 -m http.server -d docs ${PORT} --bind 127.0.0.1"
echo "load average       : $(cut -d' ' -f1-3 /proc/loadavg)"
echo "=============================================================="

python3 -m http.server -d docs "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SERVER_PID=$!
trap 'kill ${SERVER_PID} >/dev/null 2>&1 || true' EXIT

BOUND=0
for i in $(seq 1 20); do
  if curl -sf -o /dev/null "http://127.0.0.1:${PORT}/index.html"; then BOUND=1; break; fi
  sleep 0.5
done

# B2-04 / D13: a server that never came up is an environment error, never a score.
if [ "${BOUND}" -ne 1 ]; then
  echo "ENVIRONMENT ERROR: the static server never answered on port ${PORT}."
  echo "  A port collision or a missing docs/ tree is a problem with the RUN, not with the site:"
  echo "  Lighthouse was not executed and no score is reported for it."
  echo "  Re-run: bash tests/run_lighthouse.sh \"${OUT}\"        (a free port is probed automatically)"
  exit 3
fi

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
echo "      convention: ${MEDIAN_CONVENTION}"
for name in index sama-soc-triage; do
  files=$(ls "${OUT}"/lighthouse-${name}-run*.json 2>/dev/null | sort)
  if [ -z "${files}" ]; then echo "${name}: NO JSON"; rc=1; continue; fi
  # publish the median run as the canonical artefact as well
  jq -s '.' ${files} > "${OUT}/lighthouse-${name}-all-runs.json"
  for cat in performance accessibility best-practices seo; do
    values=$(for f in ${files}; do jq -r --arg c "${cat}" '(.categories[$c].score*100)|round' "${f}"; done | sort -n)
    n=$(printf '%s\n' ${values} | wc -l)
    # B2-05b / N4: the SAME median as the summary (tools/lh_median.py) — one definition, one code
    # path — and the count is odd, so it is always a single measured run.
    med=$(python3 tools/lh_median.py --median-of ${values})
    min=$(printf '%s\n' ${values} | head -1)
    max=$(printf '%s\n' ${values} | tail -1)
    csv=$(printf '%s\n' ${values} | paste -sd, -)
    mark=""
    if [ "${med}" -lt 90 ]; then mark="  <-- BELOW THRESHOLD"; rc=1; fi
    printf '  %-22s median=%s (n=%s, runs: %s)  min=%s max=%s%s\n' \
      "${name}/${cat}" "${med}" "${n}" "${csv}" "${min}" "${max}" "${mark}"
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
