#!/usr/bin/env bash
# A11 / D11 — fresh-clone reproduction.
#
# Clones the working repository into a temporary directory (the clone contains only committed
# files), re-runs the documented build command there, and compares the sha256 of every published
# file with the working tree. Any difference is a failure: it means the documented build does not
# reproduce the published site.
#
# NOTE (honesty): D11 requires this reproduction to be performed by a role that did NOT author the
# code. This script is the builder's own rehearsal so the documented commands are known to work;
# B1-04 (qa-specialist) repeats it independently and its run is the acceptance evidence.
#
# Usage: bash tests/reproduce.sh
set -uo pipefail
cd "$(dirname "$0")/.."
REPO="$(pwd)"
TMP="$(mktemp -d /tmp/b1-03-reproduce.XXXXXX)"
echo "repo      : ${REPO}"
echo "scratch   : ${TMP}"

cleanup() { rm -rf "${TMP}"; }
trap cleanup EXIT

echo
echo "== git status (the reproduction uses committed state only) =="
git status --porcelain | head -20
echo "HEAD commit: $(git rev-parse HEAD 2>/dev/null || echo 'no commits yet')"

echo
echo "== clone =="
git clone --quiet "${REPO}" "${TMP}/clone" || { echo "git clone FAILED"; exit 1; }
cd "${TMP}/clone"
echo "clone size: $(du -sh . | cut -f1)"
echo "tracked files: $(git ls-files | wc -l)"
echo "docs/ present in clone: $(find docs -type f 2>/dev/null | wc -l) files"

echo
echo "== documented build command =="
echo "\$ python3 tools/build_site.py"
python3 tools/build_site.py
build_rc=$?
echo "build exit: ${build_rc}"

echo
echo "== documented serve command (smoke test) =="
echo "\$ python3 -m http.server -d docs 8321"
python3 -m http.server -d docs 8321 --bind 127.0.0.1 >/dev/null 2>&1 &
SRV=$!
trap 'kill ${SRV} >/dev/null 2>&1 || true; cleanup' EXIT
for i in $(seq 1 20); do curl -sf -o /dev/null http://127.0.0.1:8321/index.html && break; sleep 0.5; done
code=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8321/index.html)
echo "GET /index.html -> ${code}"
code404=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8321/projects/sama-soc-triage.html)
echo "GET /projects/sama-soc-triage.html -> ${code404}"
css=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8321/assets/styles.css)
echo "GET /assets/styles.css -> ${css}"
kill "${SRV}" >/dev/null 2>&1 || true

echo
echo "== static scans in the clone =="
python3 tests/static_scans.py >/tmp/repro-static.txt 2>&1
scan_rc=$?
echo "static scans exit: ${scan_rc}"
tail -n 3 /tmp/repro-static.txt

echo
echo "== published-file hash comparison (working tree vs fresh clone) =="
cd "${REPO}"
find docs -type f | sort | xargs sha256sum > /tmp/repro-original.sha
cd "${TMP}/clone"
find docs -type f | sort | xargs sha256sum > /tmp/repro-clone.sha
if diff -u /tmp/repro-original.sha /tmp/repro-clone.sha; then
  echo "hashes identical: $(wc -l < /tmp/repro-clone.sha) files"
  hash_rc=0
else
  echo "HASH MISMATCH between the working tree and the fresh clone"
  hash_rc=1
fi

echo
echo "=============================================================="
RC=0
[ "${build_rc}" -ne 0 ] && { echo "build failed"; RC=1; }
[ "${scan_rc}" -ne 0 ] && { echo "static scans failed in the clone"; RC=1; }
[ "${code}" != "200" ] && { echo "serve smoke test failed (${code})"; RC=1; }
[ "${hash_rc}" -ne 0 ] && RC=1
if [ "${RC}" -eq 0 ]; then
  echo "FRESH-CLONE REPRODUCTION RESULT: PASS"
else
  echo "FRESH-CLONE REPRODUCTION RESULT: FAIL"
fi
echo "=============================================================="
exit "${RC}"
