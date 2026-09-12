#!/usr/bin/env bash
# B1-11 regression test for the pre-push guard (tools/prepush_guard.sh) — card t_2e0396ce.
#
# Reproduces the guard findings and asserts the FIXED verdicts (13 checks):
#    1. a removal expressed as a RENAME inside docs/ (`git mv docs/a docs/b`)  -> BLOCKED (exit 1)
#    2. a plain deletion of a published file                                   -> BLOCKED (exit 1)
#    3. a commit message that looks like a destructive rehearsal                -> BLOCKED (exit 1)
#    4. an ordinary non-docs/ commit                                            -> checks passed (0)
#    5. NEW remote ref whose push adds no content (B1-10 "H1"): the push must NOT be refused, and
#       the docs/ WARNING must not be produced by the checkout, only a note                  -> exit 0
#    6. NEW remote ref whose push removes a published file                     -> BLOCKED (exit 1)
#    7. that same removal pushed onto the EXISTING master ref                  -> BLOCKED (exit 1)
#    8. a docs/ change pushed with ALLOW_DOCS_CHANGE=1                          -> exit 0 (override)
#    9. a docs/ change pushed without the override                             -> exit 0 + WARNING
#   10. the guard and the recorded manifest are tracked in git (a fresh clone carries them)
#
# The new-ref probes run BEFORE the docs/-change probes so that the revision they publish is still
# byte-identical to the recorded manifest — that is what makes check 5 a faithful reproduction of
# B1-10's H1 (there, the pushed tree matched the manifest while the checkout did not).
#
# Safety: everything happens in a temporary clone of THIS repository whose `origin` is repointed at
# a throwaway bare repo under $TMPDIR. Nothing is pushed anywhere else, no credential is read, and
# the production repository / GitHub remote are never written to.
#
# Usage:
#   bash tests/test_prepush_guard.sh
#   KEEP_LOGS=/path bash tests/test_prepush_guard.sh   # also copy the raw per-probe logs there
set -uo pipefail

REPO_ROOT=$(cd "$(dirname "$0")/.." && pwd)
TMP=$(mktemp -d "${TMPDIR:-/tmp}/b1-11-prepush-guard.XXXXXX") || exit 1
RESULTS="$TMP/results"
BARE="$TMP/remote.git"
CLONE="$TMP/clone"
KEEP_LOGS="${KEEP_LOGS:-}"
ok=0
bad=0

cleanup() { rm -rf "$TMP"; }
trap cleanup EXIT

pass() { printf '  PASS  %-42s %s\n' "$1" "${2:-}"; ok=$((ok + 1)); }
fail() { printf '  FAIL  %-42s %s\n' "$1" "$2"; bad=$((bad + 1)); }

probe() { # probe <name> <expected-exit> <command> [required-substring | !forbidden-substring]...
  local name="$1" want="$2" cmd="$3" rc why="" pat
  shift 3
  mkdir -p "$RESULTS"
  (cd "$CLONE" && eval "$cmd") >"$RESULTS/$name.log" 2>&1
  rc=$?
  [ "$rc" = "$want" ] || why="exit $rc, expected $want"
  for pat in "$@"; do
    case "$pat" in
      '!'*)
        if [ -z "$why" ] && grep -qF -- "${pat#!}" "$RESULTS/$name.log"; then
          why="output unexpectedly contains: ${pat#!}"
        fi
        ;;
      *)
        if [ -z "$why" ] && ! grep -qF -- "$pat" "$RESULTS/$name.log"; then
          why="output lacks: $pat"
        fi
        ;;
    esac
  done
  if [ -z "$why" ]; then
    pass "$name" "(exit $rc)"
  else
    fail "$name" "$why"
    sed 's/^/        | /' "$RESULTS/$name.log"
  fi
}

remote_tip() { # remote_tip <ref> -> sha or "none"
  git --git-dir="$BARE" rev-parse --verify --quiet "refs/heads/$1" 2>/dev/null || echo none
}

echo "== B1-11 pre-push guard regression =="
echo "repository : $REPO_ROOT"
echo "scratch    : $TMP"
echo "guard      : sha256 $(sha256sum "$REPO_ROOT/tools/prepush_guard.sh" | cut -d' ' -f1)"
echo

echo "-- throwaway environment: clone + bare remote, origin repointed, guard installed --"
git init --quiet --bare "$BARE" || exit 1
git clone --quiet "$REPO_ROOT" "$CLONE" || exit 1
cd "$CLONE" || exit 1
git remote set-url origin "$BARE"
git config user.email "b1-11-guard-test@example.invalid"
git config user.name "B1-11 guard test"
if [ "$(git remote get-url origin)" != "$BARE" ]; then
  echo "FATAL: origin is not the throwaway bare repository — refusing to run"
  exit 1
fi
if [ ! -f tools/prepush_guard.sh ] || [ ! -f tests/accepted_manifest_hashes.txt ]; then
  echo "FATAL: this clone does not carry tools/prepush_guard.sh and tests/accepted_manifest_hashes.txt."
  echo "       They must be committed (they are versioned by B1-11); a clone only sees committed files."
  exit 1
fi
if ! git diff --quiet HEAD -- tools/prepush_guard.sh tests/accepted_manifest_hashes.txt 2>/dev/null; then
  echo "warning: tools/prepush_guard.sh / tests/accepted_manifest_hashes.txt differ from HEAD — this test"
  echo "         exercises the COMMITTED revision in the clone, not the working tree."
fi
# the documented install line, verbatim from DEPLOY_RUNBOOK.md §6
cp tools/prepush_guard.sh .git/hooks/pre-push && chmod +x .git/hooks/pre-push
echo "   origin  : $(git remote get-url origin)"
if [ -x .git/hooks/pre-push ]; then
  echo "   hook    : installed, byte-identical to tools/prepush_guard.sh: $(cmp -s .git/hooks/pre-push tools/prepush_guard.sh && echo yes || echo NO)"
else
  echo "   hook    : MISSING"
  fail "install the guard as .git/hooks/pre-push" "the hook is not executable"
fi
echo

echo "-- 10. guard + recorded manifest are tracked (a fresh clone carries them) --"
for f in tools/prepush_guard.sh tests/accepted_manifest_hashes.txt; do
  if git ls-files --error-unmatch "$f" >/dev/null 2>&1; then
    pass "tracked: $f" ""
  else
    fail "tracked: $f" "not tracked — a fresh clone will not have it"
  fi
done
echo

echo "-- 0. seed the throwaway bare remote (clean push must pass) --"
SEED=$(git rev-parse HEAD)
probe 0_seed_clean_push 0 "git push --quiet origin master:refs/heads/master" "checks passed."
echo "   seed revision: $(git rev-parse --short "$SEED")  remote tip: $(remote_tip master | cut -c1-7)"
echo

echo "-- 1. removal expressed as a RENAME inside docs/ must be BLOCKED --"
probe 1_rename_inside_docs 1 \
  "git mv docs/robots.txt docs/robots-renamed.txt && git commit --quiet -m 'probe 1: rename robots.txt inside the published folder' && git push origin master" \
  "BLOCKED" "this push deletes files from the published surface" "docs/robots.txt"
if [ "$(remote_tip master)" = "$SEED" ]; then
  pass "1b remote tip unchanged after the refused push" ""
else
  fail "1b remote tip unchanged after the refused push" "tip moved to $(remote_tip master)"
fi
git reset --quiet --hard origin/master
echo

echo "-- 2. plain deletion of a published file must still be BLOCKED --"
probe 2_plain_deletion 1 \
  "git rm --quiet docs/robots.txt && git commit --quiet -m 'probe 2: plain deletion of a published file' && git push origin master" \
  "BLOCKED" "docs/robots.txt"
git reset --quiet --hard origin/master
echo

echo "-- 3. destructive-rehearsal commit message must still be BLOCKED --"
probe 3_rehearsal_message 1 \
  "echo probe >> README.md && git add README.md && git commit --quiet -m 'B1-08 rollback rehearsal (temporary): remove docs/ to confirm the site can be taken down' && git push origin master" \
  "BLOCKED" "looks like a destructive rehearsal"
git reset --quiet --hard origin/master
echo

echo "-- 4. an ordinary non-docs/ commit must pass --"
probe 4_clean_non_docs_commit 0 \
  "echo probe4 >> README.md && git add README.md && git commit --quiet -m 'probe 4: documentation-only change outside the published surface' && git push origin master" \
  "checks passed."
echo

echo "-- 5-7. new remote ref: computed against a real base, not the working tree --"
echo "    (the pushed revision still matches the recorded manifest, so any WARNING here could only"
echo "     come from the checkout — which is exactly what B1-10's H1 probe exposed)"
git checkout --quiet -B withdocs origin/master
git checkout --quiet -B nodocs origin/master
git rm --quiet docs/robots.txt
git commit --quiet -m "probe 5-7: a branch that does not contain the file"
echo "   checked out: $(git rev-parse --abbrev-ref HEAD)  docs/robots.txt in the worktree: $(test -f docs/robots.txt && echo yes || echo no)"
echo "   pushed branch withdocs contains docs/robots.txt: $(git cat-file -e withdocs:docs/robots.txt 2>/dev/null && echo yes || echo no)"
probe 5_new_ref_no_new_content 0 \
  "git push --quiet origin withdocs:refs/heads/newref-h1" \
  "checks passed." "this push adds no new content" "note: this checkout's docs/ differs" "!BLOCKED" "!WARNING"
probe 6_new_ref_genuine_removal 1 \
  "git push origin nodocs:refs/heads/newref-h2" \
  "BLOCKED" "docs/robots.txt"
probe 7_removal_to_existing_ref 1 \
  "git push origin nodocs:refs/heads/master" \
  "BLOCKED" "docs/robots.txt"
git checkout --quiet master
git reset --quiet --hard origin/master
echo

echo "-- 8. a docs/ change with the documented override must pass --"
probe 8_docs_change_with_override 0 \
  "printf '\n# probe 8\n' >> docs/robots.txt && git add docs/robots.txt && git commit --quiet -m 'probe 8: accepted docs change (override)' && ALLOW_DOCS_CHANGE=1 git push origin master" \
  "checks passed." "!push refused."
echo

echo "-- 9. a docs/ change without the override must warn (advisory, exit 0) --"
probe 9_manifest_warning_advisory 0 \
  "printf '\n# probe 9\n' >> docs/robots.txt && git add docs/robots.txt && git commit --quiet -m 'probe 9: docs change with a stale manifest' && git push origin master" \
  "WARNING: docs/ differs from the recorded accepted manifest" "checks passed."
echo

if [ -n "$KEEP_LOGS" ]; then
  mkdir -p "$KEEP_LOGS"
  cp "$RESULTS"/*.log "$KEEP_LOGS"/ 2>/dev/null || true
  echo "raw probe logs copied to $KEEP_LOGS"
fi

echo "=============================================================="
echo "checks: ${ok} passed, ${bad} failed"
if [ "$bad" -eq 0 ]; then
  echo "B1-11 PRE-PUSH GUARD REGRESSION: PASS"
  exit 0
fi
echo "B1-11 PRE-PUSH GUARD REGRESSION: FAIL"
exit 1
