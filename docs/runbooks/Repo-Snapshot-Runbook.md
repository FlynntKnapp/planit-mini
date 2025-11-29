# Repo Snapshot Runbook

This runbook describes how to:

- Use a **shared ignore pattern** for `tree` output.
- Generate a **snapshot text file** containing:
  - The current repository directory tree.
  - The contents of all git-tracked files (with some exclusions).

Scripts live in:

- `scripts/tree_ignore_pattern.sh`
- `scripts/repo_snapshot.sh`


---

## 1. Files & Purpose

### 1.1 `scripts/tree_ignore_pattern.sh`

**Purpose:**  
Define a single shared ignore pattern for `tree` so it can be reused across scripts and manual commands.

```bash
# scripts/tree_ignore_pattern.sh

# Shared ignore pattern for tree commands in this repo

TREE_IGNORE='.git|__pycache__|venv|.venv|node_modules|staticfiles|e2e|notes|add_noqa_f401.sh|cat_modules.txt|commits_and_changes.txt|ls_al_modules.txt|local_things|drf_requirements_check.txt|diff_without_pipfile_lock.patch'

export TREE_IGNORE
```

This file is **sourced**, not executed directly.

---

### 1.2 `scripts/repo_snapshot.sh`

**Purpose:**
Create a timestamped snapshot file of:

1. The current repo tree (respecting the ignore pattern).
2. The contents of all git-tracked files (with some noisy files excluded).

```bash
#!/usr/bin/env bash

# scripts/repo_snapshot.sh

set -euo pipefail

# Load the shared ignore pattern
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
```

---

## 2. Setup

From the repo root:

1. Ensure the directory structure:

   ```bash
   mkdir -p scripts
   # (place both .sh files into ./scripts)
   ```

2. Make the snapshot script executable:

   ```bash
   chmod +x scripts/repo_snapshot.sh
   ```

3. Verify `tree` is installed (Ubuntu/Debian example):

   ```bash
   sudo apt-get update
   sudo apt-get install tree
   ```

4. Verify you're in a git repo and have files tracked:

   ```bash
   git status
   ```

---

## 3. Usage

### 3.1 Print current repo structure with shared ignore pattern

**One-off, manual usage:**

From the repo root:

```bash
source scripts/tree_ignore_pattern.sh
tree -a -I "$TREE_IGNORE"
```

This will:

* Show a full directory tree.
* Hide `.git`, virtualenvs, `node_modules`, and other noisy items defined in `TREE_IGNORE`.

---

### 3.2 Generate a snapshot file

From the repo root:

```bash
./scripts/repo_snapshot.sh
```

What happens:

* `tree_ignore_pattern.sh` is sourced.

* A snapshot file named like:

  ```text
  planit-mini-snapshot-20251127-043015.txt
  ```

  is created in the current directory (usually the repo root).

* The file contains:

  1. **TREE section**
     Output of:

     ```bash
     tree -a -I "$TREE_IGNORE"
     ```

  2. **FILE CONTENTS section**
     For each git-tracked file (excluding dbs, envs, logs, etc.), it prints:

     ```text
     ===== FILE: path/to/file.py =====

     <file contents here>
     ```

Use this snapshot for:

* Archiving repo state before refactors.
* Attaching to bug reports or “here’s what it looked like” notes.
* Comparing structure/content changes over time.

---

## 4. Common Variations

### 4.1 Save snapshots into a dedicated directory

If you prefer to keep snapshots in `snapshots/`:

1. Create the directory:

   ```bash
   mkdir -p snapshots
   ```

2. Modify `SNAPSHOT` in `scripts/repo_snapshot.sh`:

   ```bash
   SNAPSHOT="snapshots/planit-mini-snapshot-$(date +%Y%m%d-%H%M%S).txt"
   ```

Now snapshots won’t clutter the repo root.

---

### 4.2 Use with a `just` recipe (optional)

If you use `just`, you can add:

```just
snapshot:
    ./scripts/repo_snapshot.sh
```

Then run:

```bash
just snapshot
```

Same effect, fewer keystrokes.

---

## 5. Maintenance

### 5.1 Updating the ignore pattern

To add or remove ignored paths/files:

1. Edit `scripts/tree_ignore_pattern.sh`.
2. Update the `TREE_IGNORE` string (pipe-separated list).
3. Save the file.

All places that use:

```bash
tree -a -I "$TREE_IGNORE"
```

will automatically pick up the new pattern (both manual commands and the snapshot script).

---

### 5.2 Safety notes

* The snapshot script **reads** git-tracked files and writes a single text file. It does **not** modify the repo.
* It can include sensitive config if those files are tracked by git.

  * If something shouldn’t be in snapshots, don’t track it with git, or add more `git ls-files ':!pattern'` exclusions.

---

## 6. Quick Reference

* **Print tree (manual):**

  ```bash
  source scripts/tree_ignore_pattern.sh
  tree -a -I "$TREE_IGNORE"
  ```

* **Create snapshot:**

  ```bash
  ./scripts/repo_snapshot.sh
  ```

* **Where scripts live:**

  ```text
  scripts/tree_ignore_pattern.sh
  scripts/repo_snapshot.sh
  ```

