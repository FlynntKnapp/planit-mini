#!/usr/bin/env bash
set -euo pipefail

shopt -s nullglob

py_files=( ./*.py )

if (( ${#py_files[@]} == 0 )); then
  echo "No .py files found in: $(pwd)"
  exit 0
fi

echo "Running ${#py_files[@]} Python file(s) in: $(pwd)"
echo

for f in "${py_files[@]}"; do
  echo "=== Running: $f ==="
  python3 "$f"
  echo
done

echo "✅ Done."
