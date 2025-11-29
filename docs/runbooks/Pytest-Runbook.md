# Pytest Runbook

This guide shows developers how to run and work with tests in the `planit-mini` Django project using `pytest`.

---

## 1. What You’ll Do Most Often

### 1.1. Activate the environment

From the project root (where `Pipfile` lives):

```bash
pipenv shell
````

If you’re not using Pipenv, just make sure your virtualenv is active and all dev deps are installed.

### 1.2. Run the full test suite

From the project root:

```bash
pytest
```

* Uses the project’s `pytest.ini` configuration.
* By default this will:

  * Use the configured Django settings module (usually something like `config.settings.dev`).
  * Auto-discover tests in `tests/` and in each app’s `tests` module.

### 1.3. Run tests for a single app

```bash
pytest assets
pytest api
pytest work
```

Pytest will discover tests inside those app directories (e.g. `assets/tests/`).

### 1.4. Run tests in a single file

```bash
pytest assets/tests/test_models.py
pytest api/tests/test_permissions.py
```

### 1.5. Run a single test or test class

```bash
pytest assets/tests/test_models.py::TestAssetModel
pytest assets/tests/test_models.py::TestAssetModel::test_str
```

This is extremely useful while iterating on one failing test.

---

## 2. Things You’ll Need Sometimes

### 2.1. Using different Django settings

If you want to run tests with a different settings module:

**Option A – via `--ds` flag:**

```bash
pytest --ds=config.settings.test
pytest --ds=config.settings.dev
pytest --ds=config.settings.prod
```

**Option B – via environment variable:**

```bash
export DJANGO_SETTINGS_MODULE=config.settings.test
pytest
```

(Use the appropriate module names for your `dev.py`, `test.py`, and `prod.py`.)

---

### 2.2. Run only tests matching a keyword

```bash
pytest -k "workspace"
pytest -k "maintenance and not slow"
```

* `-k` filters tests by name or node id substring.
* Combine with `-vv` to see more detail:

```bash
pytest -k "workspace" -vv
```

---

### 2.3. Last-failed and fast feedback options

* **Only re-run failing tests from the previous run:**

  ```bash
  pytest --lf
  ```

* **Stop after the first failure:**

  ```bash
  pytest -x
  # or
  pytest --maxfail=1 -x
  ```

These are great when you’re in “fix this one thing” mode.

---

### 2.4. Running with coverage

Run the full suite with coverage:

```bash
coverage run -m pytest
```

Show a summary in the terminal:

```bash
coverage report
```

Generate an HTML report:

```bash
coverage html
# Then open htmlcov/index.html in a browser
```

If you prefer a one-liner:

```bash
coverage run -m pytest && coverage report
```

---

### 2.5. How pytest finds tests in this project

By default:

* Files named `test_*.py` or `*_test.py`.
* Inside:

  * `tests/` packages (e.g. `assets/tests/`).
  * App modules that follow pytest discovery rules.

Manual scripts (e.g. `tests/manual/maintenance_tasks.py`) should **not** start with `test_` if you don’t want pytest to run them automatically.

---

## 3. Troubleshooting & Handy Tips

### 3.1. “Invalid HTTP_HOST header: 'testserver'”

If you see something like:

> Invalid HTTP_HOST header: 'testserver'. You may need to add 'testserver' to ALLOWED_HOSTS.

Add `"testserver"` to `ALLOWED_HOSTS` in the appropriate settings (usually `config/settings/dev.py` or `test.py`) so tests that use the Django test client work correctly.

---

### 3.2. Database / migrations issues

* Pytest-django creates a **test database** automatically.

* If migrations are causing trouble, try:

  ```bash
  pytest --create-db
  ```

* If you change models and see weird failures, ensure you’ve run migrations locally (for sanity), then re-run tests. The test DB is built from migrations.

---

### 3.3. Debugging inside a test

Drop into a debugger in a test:

```python
import pdb; pdb.set_trace()
```

Or use pytest’s built-in `--pdb`:

```bash
pytest --pdb -k "failing_test_name"
```

Pytest will open a debugger when a test fails.

---

### 3.4. Markers (slow / e2e / etc.)

If there are custom markers defined in `pytest.ini` (for example: `slow`, `e2e`, `integration`), you can:

* Run only marked tests:

  ```bash
  pytest -m slow
  pytest -m "e2e"
  ```

* Exclude marked tests:

  ```bash
  pytest -m "not slow"
  ```

If pytest complains about “unknown marker”, add the marker to `pytest.ini` under `markers =` (or remove it from the test).

---

### 3.5. When tests aren’t being collected

If a test isn’t running:

1. Check the filename:

   * Must be `test_*.py` or `*_test.py`.
2. Check the function/class name:

   * Test functions: `def test_something(...)`.
   * Test classes: `class TestSomething:`.
3. Make sure the file is inside a package that pytest can import (usually a directory with `__init__.py` or a top-level `tests/` directory).

---

### 3.6. Quick “is pytest working?” sanity check

From the project root:

```bash
pytest -q
```

You should see tests being collected and run. If not:

* Confirm you’re in the right directory (where `pytest.ini` lives).
* Confirm your virtualenv is active and pytest is installed.
* Check that `pytest.ini` doesn’t point to a non-existent Django settings module.

---

Happy testing! 🧪
