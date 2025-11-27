#!/usr/bin/env bash

# repo_snapshot.sh

set -euo pipefail

# Load the shared ignore pattern
# Adjust the path if the script lives in a subdir
. "$(dirname "$0")/tree_ignore_pattern.sh"

SNAPSHOT="planit-mini-snapshot-$(date +%Y%m%d-%H%M%S).txt"

{
  echo "===== TREE ====="
  echo
  tree -a -I "$TREE_IGNORE"

  echo
  echo "===== FILE CONTENTS (git-tracked) ====="
  echo

  # List ONLY git-tracked files, excluding noisy ones
  git ls-files \
    ':!db.sqlite3' \
    ':!.env' \
    ':!*.pyc' \
    ':!*.pyo' \
    ':!*.sqlite3' \
    ':!*.log' \
  | while IFS= read -r f; do
      printf '\n\n===== FILE: %s =====\n\n' "$f"
      cat "$f"
    done

} > "$SNAPSHOT"

echo "Wrote snapshot to: $SNAPSHOT"
