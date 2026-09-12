#!/usr/bin/env bash
# pre-push guard for the portfolio repository.
#
# WHY THIS EXISTS: during Benchmark #1 the publish step "confirmed the rollback works" by
# committing and PUSHING a temporary commit that deleted docs/ to the live public repo. That
# removed the live site, failed the GitHub Pages build, and emailed the owner a deployment-failure
# notification. Rollback must be rehearsed locally or on a scratch branch/repo — never against the
# production repository.
#
# WHAT IT BLOCKS (exit 1):
#   1. any push that DELETES a file under docs/ (the published surface)
#   2. any push whose commit messages look like a destructive rehearsal
#        (e.g. "rollback rehearsal", "temporary: remove docs")
# WHAT IT WARNS (exit 0, but prints loudly):
#   3. docs/ content differing from the recorded accepted manifest
#
# Bypass for a legitimate change:  ALLOW_DOCS_CHANGE=1 git push
# Bypass for a legitimate deletion:  ALLOW_DOCS_DELETION=1 git push   (expect a loud reason in the
# commit message; this should be rare and deliberate)
set -uo pipefail

MANIFEST="tests/accepted_manifest_hashes.txt"
fail=0

while read -r local_ref local_sha remote_ref remote_sha; do
  [ "$local_sha" = "0000000000000000000000000000000000000000" ] && continue   # branch deletion
  if [ "$remote_sha" = "0000000000000000000000000000000000000000" ] || [ -z "$remote_sha" ]; then
    echo "[pre-push] initial push to $remote_ref — checking the tree only"
    range="$local_sha"
  else
    range="$remote_sha..$local_sha"
  fi

  # 1. deletions under docs/
  if [ -n "${range##*..*}" ]; then
    changed=$(git diff --name-status "$range" 2>/dev/null || true)
  else
    changed=$(git diff --name-status $range 2>/dev/null || true)
  fi
  deletions=$(printf '%s\n' "$changed" | awk '$1 ~ /^D/ && $2 ~ /^docs\// {print $2}')
  if [ -n "$deletions" ] && [ "${ALLOW_DOCS_DELETION:-0}" != "1" ]; then
    echo "[pre-push] BLOCKED: this push deletes files from the published surface (docs/):"
    printf '  %s\n' $deletions
    echo "  Rehearse rollback locally or on a scratch branch/repo. To override: ALLOW_DOCS_DELETION=1"
    fail=1
  fi

  # 2. destructive-rehearsal commit messages
  if [ -n "${range##*..*}" ]; then :; else
    msgs=$(git log --format=%s $range 2>/dev/null || true)
    bad=$(printf '%s\n' "$msgs" | grep -iE 'rollback rehearsal|rehearsal.*remove|temporary.*remove docs' || true)
    if [ -n "$bad" ]; then
      echo "[pre-push] BLOCKED: commit message looks like a destructive rehearsal:"
      printf '  %s\n' "$bad"
      fail=1
    fi
  fi

  # 3. docs/ vs the recorded accepted manifest (advisory)
  if [ -d docs ] && [ -f "$MANIFEST" ] && [ "${ALLOW_DOCS_CHANGE:-0}" != "1" ]; then
    now=$(cd docs && find . -type f -print0 | sort -z | xargs -0 sha256sum 2>/dev/null | sed 's| \./| |' | sort)
    if [ -n "$now" ] && ! diff -q <(printf '%s\n' "$now") <(sort "$MANIFEST") >/dev/null 2>&1; then
      echo "[pre-push] WARNING: docs/ differs from the recorded accepted manifest ($MANIFEST)."
      echo "           If this is an accepted change, update the manifest and re-verify."
    fi
  fi
done

[ "$fail" -eq 0 ] || { echo "[pre-push] push refused."; exit 1; }
echo "[pre-push] checks passed."
exit 0
