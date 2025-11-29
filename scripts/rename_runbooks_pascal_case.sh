#!/usr/bin/env bash
# rename_runbooks_pascal_case.sh
#
# Rename docs/runbooks/*.md files so each segment is PascalCase,
# joined by dashes (e.g. ASSETS-ADMIN-RUNBOOK.md -> Assets-Admin-Runbook.md)

set -euo pipefail

# Adjust this if you want to run from a different directory
RUNBOOK_DIR="docs/runbooks"

cd "$RUNBOOK_DIR"

for f in *.md; do
  # Strip extension
  base="${f%.md}"

  # Split on dashes
  IFS='-' read -r -a parts <<< "$base"

  new_parts=()
  for p in "${parts[@]}"; do
    # lowercase entire part
    lower=$(echo "$p" | tr '[:upper:]' '[:lower:]')
    # capitalize first character
    first=${lower:0:1}
    rest=${lower:1}
    cap_part="$(printf "%s%s" "$(printf "%s" "$first" | tr '[:lower:]' '[:upper:]')" "$rest")"
    new_parts+=( "$cap_part" )
  done

  # Join back with dashes
  new_base=$(IFS='-'; printf "%s" "${new_parts[*]}")
  new_name="${new_base}.md"

  # Only rename if different
  if [[ "$f" != "$new_name" ]]; then
    echo "Renaming: $f -> $new_name"
    mv -- "$f" "$new_name"
  fi
done
