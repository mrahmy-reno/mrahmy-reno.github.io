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
#   1. any push that REMOVES a file from the published surface (docs/): a plain deletion, and
#      equally a removal expressed as a RENAME. `git mv docs/a docs/b` is reported by git as
#      `R100  docs/a  docs/b` (status R, not D) while docs/a has left the published surface, so
#      rename detection is OFF (`--no-renames`) for this check and an R whose OLD path is under
#      docs/ is also treated as a removal. (B1-11 finding 1)
#   2. any push whose commit messages look like a destructive rehearsal
#        (e.g. "rollback rehearsal", "temporary: remove docs")
# WHAT IT WARNS (exit 0, but prints loudly):
#   3. the pushed docs/ differing from the recorded accepted manifest
#
# HOW A PUSH IS EVALUATED — always against a real base, never the working tree (B1-11 finding 2):
#   * existing remote ref :  git diff --name-status --no-renames <remote_sha>..<local_sha>
#   * brand-new remote ref:  the commits this push introduces (`git rev-list <local_sha> --not
#                            --remotes`) are compared with the base they branch from: the parent of
#                            the oldest introduced commit, or the empty tree for a root commit. A
#                            push that introduces no commit at all (an already-published revision
#                            copied to a new ref) adds no content and checks nothing.
#   The manifest warning (3) is evaluated against docs/ as it exists in the revision being pushed,
#   i.e. what would actually be published. A checkout that merely differs from what is being pushed
#   is reported as a note, not as a verdict — it is not part of the push.
#
# Bypass for a legitimate change:  ALLOW_DOCS_CHANGE=1 git push
# Bypass for a legitimate deletion:  ALLOW_DOCS_DELETION=1 git push   (expect a loud reason in the
# commit message; this should be rare and deliberate)
set -uo pipefail

MANIFEST="tests/accepted_manifest_hashes.txt"
ZERO_SHA="0000000000000000000000000000000000000000"
fail=0

worktree_docs_hashes() { # hashes of the LOCAL docs/ checkout, manifest format, sorted
  [ -d docs ] || return 1
  (cd docs && find . -type f -print0 | sort -z | xargs -0 sha256sum 2>/dev/null | sed 's| \./| |' | sort) || true
}

pushed_docs_hashes() { # <rev> -> hashes of docs/ as it exists in that revision (manifest format)
  local rev="$1" tmp
  tmp=$(mktemp -d) || return 1
  if git archive "$rev" docs 2>/dev/null | tar -x -C "$tmp" 2>/dev/null && [ -d "$tmp/docs" ]; then
    (cd "$tmp/docs" && find . -type f -print0 | sort -z | xargs -0 sha256sum 2>/dev/null | sed 's| \./| |' | sort) || true
  fi
  rm -rf "$tmp"
}

removed_from_docs() { # <name-status stream> -> every path that leaves the published surface
  printf '%s\n' "$1" | awk '
    $1 ~ /^D/ && $2 ~ /^docs\// { print $2; next }
    $1 ~ /^R/ && $2 ~ /^docs\// { print $2; next }
  '
}

while read -r local_ref local_sha remote_ref remote_sha; do
  [ -n "${local_sha:-}" ] || continue
  [ "$local_sha" = "$ZERO_SHA" ] && continue   # branch deletion: nothing is published

  changed=""
  msgs=""
  if [ "$remote_sha" = "$ZERO_SHA" ] || [ -z "${remote_sha:-}" ]; then
    # ---- brand-new remote ref: this ref has no previous state, so evaluate the content the push
    #      ADDS, against the base those commits branch from. Never the working tree.
    commits=$(git rev-list "$local_sha" --not --remotes 2>/dev/null || true)
    if [ -z "$commits" ]; then
      echo "[pre-push] new remote ref $remote_ref — $(git rev-parse --short "$local_sha" 2>/dev/null) is already published on an existing remote ref: this push adds no new content"
    else
      oldest=$(printf '%s\n' "$commits" | tail -n 1)
      base=$(git rev-parse --verify --quiet "${oldest}^" 2>/dev/null) || base=$(git hash-object -t tree /dev/null)
      echo "[pre-push] new remote ref $remote_ref — evaluating $(git rev-parse --short "$base" 2>/dev/null)..$(git rev-parse --short "$local_sha" 2>/dev/null) (the content this push adds), never the working tree"
      changed=$(git diff --name-status --no-renames "$base" "$local_sha" 2>/dev/null || true)
      msgs=$(git log --format=%s $commits 2>/dev/null || true)
    fi
  else
    # ---- existing remote ref: exactly what the remote gains
    range="$remote_sha..$local_sha"
    changed=$(git diff --name-status --no-renames "$range" 2>/dev/null || true)
    msgs=$(git log --format=%s "$range" 2>/dev/null || true)
  fi

  # 1. removals from the published surface: deletions, and renames whose old path is under docs/
  removals=$(removed_from_docs "$changed")
  if [ -n "$removals" ] && [ "${ALLOW_DOCS_DELETION:-0}" != "1" ]; then
    echo "[pre-push] BLOCKED: this push deletes files from the published surface (docs/):"
    printf '  %s\n' $removals
    echo "  Rehearse rollback locally or on a scratch branch/repo. To override: ALLOW_DOCS_DELETION=1"
    fail=1
  fi

  # 2. destructive-rehearsal commit messages
  if [ -n "$msgs" ]; then
    bad=$(printf '%s\n' "$msgs" | grep -iE 'rollback rehearsal|rehearsal.*remove|temporary.*remove docs' || true)
    if [ -n "$bad" ]; then
      echo "[pre-push] BLOCKED: commit message looks like a destructive rehearsal:"
      printf '  %s\n' "$bad"
      fail=1
    fi
  fi

  # 3. docs/ vs the recorded accepted manifest (advisory) — evaluated against the PUSHED revision
  if [ -f "$MANIFEST" ] && [ "${ALLOW_DOCS_CHANGE:-0}" != "1" ]; then
    published=$(pushed_docs_hashes "$local_sha")
    checkout=$(worktree_docs_hashes || true)
    if [ -n "$published" ] && ! diff -q <(printf '%s\n' "$published") <(sort "$MANIFEST") >/dev/null 2>&1; then
      echo "[pre-push] WARNING: docs/ differs from the recorded accepted manifest ($MANIFEST)."
      echo "           If this is an accepted change, update the manifest and re-verify."
    fi
    if [ -n "$published" ] && [ -n "$checkout" ] && [ "$checkout" != "$published" ]; then
      echo "[pre-push] note: this checkout's docs/ differs from docs/ in $(git rev-parse --short "$local_sha" 2>/dev/null) —"
      echo "           the check above is about the revision being pushed, not about the checkout."
    fi
  fi
done

[ "$fail" -eq 0 ] || { echo "[pre-push] push refused."; exit 1; }
echo "[pre-push] checks passed."
exit 0
