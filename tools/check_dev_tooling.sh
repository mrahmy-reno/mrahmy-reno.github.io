#!/usr/bin/env bash
# B1-05 / D-02 repair — tooling preflight for the check suite.
#
# The Node-dependent checks in tests/run_all.sh (browser_checks, text_scans, link_check,
# html validation, Lighthouse) need the pinned dev tooling in node_modules/, which is gitignored
# and therefore ABSENT in a fresh clone. Without this preflight a fresh-clone user sees five steps
# fail with an opaque `ERR_MODULE_NOT_FOUND`.
#
# This script only REPORTS. It never installs anything (no network, no side effects) and it never
# relaxes a check: a missing prerequisite exits non-zero so the suite still reports FAIL.
#
# Usage: bash tools/check_dev_tooling.sh
# Exit 0 = every prerequisite for the full suite is present.
set -uo pipefail
cd "$(dirname "$0")/.."
REPO="$(pwd)"

missing=0
ok()      { printf '  [OK]      %s\n' "$1"; }
absent()  { printf '  [MISSING] %s\n' "$1"; missing=1; }

echo "tooling preflight for the check suite (repo: ${REPO})"

# --- interpreters / generic tools -------------------------------------------------------------
for cmd in python3 node npm jq; do
  if command -v "$cmd" >/dev/null 2>&1; then
    ok "$cmd -> $(command -v "$cmd") ($("$cmd" --version 2>&1 | head -1))"
  else
    absent "$cmd (command not found on PATH)"
  fi
done

# --- headless browser (used by browser_checks, Lighthouse and the asset rasteriser) ------------
CHROME_BIN="${CHROME_PATH:-/usr/bin/google-chrome}"
if [ -x "${CHROME_BIN}" ]; then
  ok "chrome -> ${CHROME_BIN} ($("${CHROME_BIN}" --version 2>&1 | head -1))"
else
  absent "chrome at ${CHROME_BIN} (set CHROME_PATH if it lives elsewhere)"
fi

# --- the pinned test tooling (package.json devDependencies), installed by npm ------------------
if [ -d node_modules ]; then
  ok "node_modules/ present"
else
  absent "node_modules/ (gitignored: a fresh clone never has it)"
fi
for pkg in axe-core puppeteer-core html-validate lighthouse; do
  if [ -e "node_modules/${pkg}" ]; then
    ok "node_modules/${pkg}"
  else
    absent "node_modules/${pkg} (package.json devDependency)"
  fi
done

echo
if [ "${missing}" -eq 0 ]; then
  echo "TOOLING PREFLIGHT: OK — the full check suite can run."
  exit 0
fi
echo "TOOLING PREFLIGHT: PREREQUISITE MISSING — the Node-dependent steps cannot run in this checkout."
echo "  Install the test-only tooling (never shipped, no runtime dependency):"
echo "    bash tools/install_dev_tooling.sh      # npm install of the pinned devDependencies"
echo "  or: npm install --no-audit --no-fund"
echo "  Then re-run: bash tests/run_all.sh"
exit 1
