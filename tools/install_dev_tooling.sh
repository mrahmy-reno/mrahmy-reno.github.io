#!/usr/bin/env bash
# Dev-only toolchain install for the test suite. No runtime dependencies exist.
# Network is flaky in this environment; retry with explicit fetch tuning.
set -uo pipefail
# B1-05 / D-01 repair: install into the checkout this script lives in, never into a hardcoded
# authoring path. Works from any cwd and from a fresh clone.
cd "$(dirname "$0")/.."
export PUPPETEER_SKIP_DOWNLOAD=1
export PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=1
for attempt in 1 2 3 4 5; do
  echo "=== npm install attempt ${attempt} ==="
  npm install --no-audit --no-fund --fetch-retries=6 --fetch-retry-mintimeout=5000 \
    --fetch-retry-maxtimeout=120000 --fetch-timeout=600000
  rc=$?
  echo "npm_install_rc=${rc}"
  if [ "${rc}" -eq 0 ]; then
    echo "INSTALL_OK"
    exit 0
  fi
  sleep 5
done
echo "INSTALL_FAILED_AFTER_RETRIES"
exit 1
