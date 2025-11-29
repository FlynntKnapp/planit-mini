# Runbook — Using `dev.py`, `test.py`, and `prod.py` Locally

Project: **planit-mini**
Settings package: `config.settings`

---

## 1. Overview

You have three settings modules:

* **DEV**: `config.settings.dev`

  * Local development, debug on, SQLite, console email, etc.
* **TEST**: `config.settings.test`

  * Isolated test config (used for `pytest`/`manage.py test`).
* **PROD**: `config.settings.prod`

  * Mirrors Heroku/production behavior as closely as possible.

You can select a settings module in two ways:

1. One-off: `python manage.py <command> --settings=config.settings.<name>`
2. Per-shell: `export DJANGO_SETTINGS_MODULE=config.settings.<name>` and then run commands normally.

---

## 2. Common Commands by Environment

### 2.1 DEV settings (`config.settings.dev`)

**One-off commands**

```bash
# Run dev server
python manage.py runserver --settings=config.settings.dev

# Apply migrations
python manage.py migrate --settings=config.settings.dev

# Create a superuser
python manage.py createsuperuser --settings=config.settings.dev

# Run tests under dev settings (usually you’ll use test settings instead)
python manage.py test --settings=config.settings.dev
```

**Use DEV for the whole shell**

```bash
# Linux/macOS
export DJANGO_SETTINGS_MODULE=config.settings.dev

python manage.py runserver
python manage.py migrate
python manage.py createsuperuser
# etc...
```

```powershell
# Windows PowerShell
$env:DJANGO_SETTINGS_MODULE = "config.settings.dev"

python manage.py runserver
```

---

### 2.2 TEST settings (`config.settings.test`)

Use this when you explicitly want to run tests against the `test.py` config.

**One-off tests**

```bash
# Django test runner
python manage.py test --settings=config.settings.test

# With pytest (if you want to override what pytest-django picks up)
DJANGO_SETTINGS_MODULE=config.settings.test pytest
```

**Per-shell for tests**

```bash
# Linux/macOS
export DJANGO_SETTINGS_MODULE=config.settings.test
pytest
# or
python manage.py test
```

---

### 2.3 PROD settings (`config.settings.prod`)

Use sparingly on your local machine—mostly for debugging production-like issues.

**One-off commands**

```bash
# Run server with prod settings
python manage.py runserver --settings=config.settings.prod

# Apply migrations as prod would see them
python manage.py migrate --settings=config.settings.prod

# Create a prod-style superuser (e.g., when pointing at a prod-like DB)
python manage.py createsuperuser --settings=config.settings.prod
```

**Per-shell**

```bash
# Linux/macOS
export DJANGO_SETTINGS_MODULE=config.settings.prod
python manage.py runserver
python manage.py migrate
```

---

## 3. Troubleshooting & Tips

* **“ImproperlyConfigured: Requested setting …, but settings are not configured”**
  → You forgot to choose settings.
  Fix: Either:

  ```bash
  export DJANGO_SETTINGS_MODULE=config.settings.dev
  ```

  or add `--settings=config.settings.dev` to your command.

* **ALLOWED_HOSTS / `Invalid HTTP_HOST header` in tests or local runs**

  * Make sure the right settings file is being used (dev vs test vs prod).
  * In dev/test, confirm `ALLOWED_HOSTS` includes what you need (`localhost`, `127.0.0.1`, maybe `testserver`).

* **Accidentally using PROD locally**

  * If commands feel “off” (wrong DB, missing debug), run:

    ```bash
    echo $DJANGO_SETTINGS_MODULE
    ```

    and switch back:

    ```bash
    export DJANGO_SETTINGS_MODULE=config.settings.dev
    ```

* **Optional: default via `.env`**
  You *can* set a default in `.env`:

  ```env
  DJANGO_SETTINGS_MODULE=config.settings.dev
  ```

  Then your usual `python manage.py ...` will use `dev` unless you override it with `--settings=...`.
