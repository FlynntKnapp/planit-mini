# Plan-It Mini

[![CircleCI](https://dl.circleci.com/status-badge/img/gh/FlynntKnapp/planit-mini/tree/main.svg?style=svg)](https://dl.circleci.com/status-badge/redirect/gh/FlynntKnapp/planit-mini/tree/main)

Plan-It Mini is a small, focused maintenance planner for home labs and small fleets.

You’ll define assets (Pis, servers, laptops), attach maintenance templates (monthly OS patches, weekly backup verification), generate scheduled work orders, and capture completion evidence as activities.

This repo currently contains a solid **Django + Celery + DRF-ready scaffold** with a custom user model, CI, and environment wiring. The asset/work domain models and API are intentionally being built in small, testable steps (see `TODO.md`).

---

## Table of Contents

- [Project Status](#project-status)
- [Features](#features)
  - [What’s already implemented](#whats-already-implemented)
  - [Planned roadmap](#planned-roadmap)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Local setup](#local-setup)
  - [Running the app](#running-the-app)
  - [Running tests & linting](#running-tests--linting)
- [Configuration](#configuration)
  - [Environment variables](#environment-variables)
  - [Database & Celery](#database--celery)
- [CI / CD](#ci--cd)
- [Deployment](#deployment)
  - [Heroku](#heroku)
  - [Future: Docker & Raspberry Pi](#future-docker--raspberry-pi)
- [Roadmap](#roadmap)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Project Status

**Status:** early WIP.

Right now, Plan-It Mini is:

- A working Django project using a custom user model and auth flows.
- Wired for Celery + `django-celery-beat`, Redis, and DRF (settings-level).
- Running basic CI via CircleCI (flake8 + `accounts` coverage).
- Prepared for Heroku deployment with production settings and a Procfile.

The **asset/maintenance domain models**, **DRF API**, **Celery work-order generator**, and **full pytest test suite** are still to come and are tracked in detail in [`TODO.md`](./TODO.md).

---

## Features

### What’s already implemented

**Core framework**

- Django project scaffolded from `DjangoStarter-heroku`.
- Settings split:
  - `config/settings/base.py` – shared config, REST framework, Celery, S3, logging.
  - `config/settings/dev.py` – SQLite dev DB, `DEBUG=True`, console email, static files.
  - `config/settings/prod.py` – hardened for Heroku (secure headers, WhiteNoise, Postgres from `DATABASE_URL`, `SECRET_KEY` from env).

**Auth & accounts**

- Custom user model: `accounts.CustomUser` extending `AbstractUser` with:
  - `registration_accepted` boolean flag for moderation.
- Auth views & URLs:
  - Signup, login, update, and detail views using class-based views.
  - `accounts/urls.py` overriding login/signup and wiring to Django’s built-in auth URLs.
- Admin integration:
  - Custom `CustomUserAdmin` registering `CustomUser`.
  - Additional “Moderator Permissions” fieldset exposing `registration_accepted`.
  - `list_display` and `list_filter` tuned for moderation.

**Shared building blocks**

- `base/models.py`:
  - `CreatedUpdatedBase` – reusable abstract base model with `created`/`updated` timestamps.
  - Abstract `Note` model – `title`, `content`, `url`, `main_image`, and helper `display_content()` for admin previews.
- `THE_SITE_NAME` in settings (`"Plan-It Mini"`) used in templates and views.

**Celery & scheduling**

- `config/celery.py`:
  - Configured Celery app with timezone awareness.
  - Autodiscovery of `tasks.py` within installed apps.
  - `django_celery_beat` as beat scheduler (database-backed).
- Celery broker/result backend configured via:
  - `REDIS_URL` or `REDISCLOUD_URL`, with a local Redis default fallback.

**Environment & seeding**

- `.env.example` includes:
  - `SECRET_KEY`, `ENVIRONMENT`, `MAINTENANCE_MODE`.
  - `ALLOWED_HOSTS`, `DATABASE_URL` (Heroku-style Postgres URL).
  - Email/SMTP values.
  - AWS S3 configuration.
  - Redis/Celery configuration (`REDIS_URL`, `REDISCLOUD_URL`, `CELERY_TASK_ALWAYS_EAGER`).
  - Seed user env vars (`DJANGO_SU_*`, `DJANGO_USER_*`).
- Management command: `accounts/management/commands/create_user.py`
  - `python manage.py create_user`
  - Creates or updates a superuser and/or regular user from `.env`.
  - Perfect for local bootstrap and CI.

**Tooling & CI**

- **Pipenv**: `Pipfile` with:
  - Django, DRF, Celery, `django-storages`, `django-celery-beat`.
  - `gunicorn`, `whitenoise`, `psycopg2-binary`, `coverage`, `python-dotenv`, `isort`, `flake8`, `black`.
- **Makefile** with convenience targets:
  - `run`, `runserver`, `test`, `coverage`, `lint`, `clean`,
  - `makemigrations`, `migrate`, `makemigrate`,
  - `seed`, `createuser`, `superuser`, `delete_db`, `resetdb`, `shell`, `help`.
- **Linting**:
  - `.flake8` with `max-line-length=88`.
  - `make lint` runs `isort` in check-only mode as a starting point.
- **CircleCI**:
  - `.circleci/config.yml` using `cimg/python:3.12`.
  - Steps: install pipenv, `pipenv install --dev`, run `flake8`, then coverage for `accounts` tests (with `--fail-under=80`).

**Deployment prep**

- `Procfile`:
  - `web: gunicorn config.wsgi`
  - `release: python manage.py migrate accounts && python manage.py migrate`
- `config/utils.py`: helper to parse Heroku-style `DATABASE_URL` into Postgres config for `prod.py`.

### Planned roadmap

All of this is designed but not yet built — see `TODO.md` for the full checkbox view.

- Asset domain:
  - `FormFactor`, `OS`, `Application`, `Project`, `Asset` with M2M to `Application`.
- Work domain:
  - `MaintenanceTask` templates with cadence (weekly/monthly).
  - `WorkOrder` instances with due dates & status.
  - `ActivityInstance` records of what was done and when.
- DRF API:
  - ModelViewSets and serializers for assets, tasks, work orders, and activities.
  - Filters, search, ordering, and pagination.
  - Role-based permissions (`maintenance_viewer` vs `maintenance_manager`).
- Celery:
  - Recurring generator task to create `WorkOrder`s from `MaintenanceTask.cadence`.
  - Optional healthcheck task to flag overdue work and create “checked” activities.
- Testing:
  - `pytest` + `pytest-django` + `pytest-cov`.
  - Factories for all domain models + users.
  - Coverage gate at 95–100% on domain apps.
- Infra:
  - CircleCI with Postgres + Redis services and full-project test coverage.
  - Heroku deployment flow with `runtime.txt` and `requirements.txt`.
  - Docker + `docker-compose` for local development.
  - Optional self-hosting on a Raspberry Pi.

---

## Tech Stack

- **Language:** Python 3.12
- **Web framework:** Django
- **API layer:** Django REST Framework (configured, API still WIP)
- **Task queue:** Celery
- **Scheduling:** `django-celery-beat`
- **Cache/broker (planned):** Redis
- **Storage (optional):** AWS S3 via `django-storages`
- **Database:**
  - Dev: SQLite (via `dev.py`)
  - Prod: Postgres (Heroku-style `DATABASE_URL` parsed in `prod.py`)
- **Web server:** gunicorn (Heroku-style deployment)
- **CI:** CircleCI
- **Env management:** pipenv, `python-dotenv`

---

## Project Structure

High-level structure:

```text
planit-mini/
├─ accounts/            # Custom user model, forms, views, admin, create_user command
├─ assets/              # (Planned) asset domain models & admin
├─ work/                # (Planned) maintenance/work-order domain models & admin
├─ base/                # Shared abstract models (CreatedUpdatedBase, Note)
├─ core/                # (Reserved for healthchecks, core views, etc.)
├─ config/
│  ├─ settings/
│  │  ├─ base.py
│  │  ├─ dev.py
│  │  └─ prod.py
│  ├─ celery.py
│  ├─ urls.py
│  └─ utils.py
├─ templates/
│  └─ home.html         # Minimal home template using THE_SITE_NAME
├─ .circleci/
│  └─ config.yml
├─ .env.example
├─ Makefile
├─ Pipfile
├─ Procfile
├─ TODO.md
└─ manage.py
```

---

## Getting Started

### Prerequisites

* Python **3.12**
* `pip` and `pipenv`
* A running Redis instance (optional for local development; Celery falls back to `redis://localhost:6379/0`)

### Local setup

```bash
# Clone the repo
git clone https://github.com/FlynntKnapp/planit-mini.git
cd planit-mini

# Install dependencies
pipenv install --dev

# Create a local .env based on the example
cp .env.example .env
# Edit .env and set at least SECRET_KEY and DATABASE_URL for prod usage later
```

By default, `manage.py` and `config/celery.py` use:

```bash
DJANGO_SETTINGS_MODULE=config.settings.dev
```

which is backed by SQLite and `DEBUG=True`.

### Running the app

Using the Makefile helpers:

```bash
# Activate virtualenv
pipenv shell

# Apply migrations (dev)
make makemigrate
make migrate

# Create users from .env
make createuser

# Run the dev server
make run
# or
python manage.py runserver
```

Then visit: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

Admin is at: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

### Running tests & linting

Right now, coverage is focused on the Django test runner; pytest is planned.

```bash
# Lint imports (isort dry-run)
make lint

# Run Django tests
make test

# Run tests with coverage
make coverage
```

CircleCI currently runs a subset: flake8 + coverage for the `accounts` app.

---

## Configuration

### Environment variables

See `.env.example` for full documentation. Core ones:

**Core Django**

* `SECRET_KEY` – **required in production** (prod settings use `os.environ["SECRET_KEY"]`).
* `ENVIRONMENT` – e.g., `development`, `production`.
* `MAINTENANCE_MODE` – currently not used in settings; reserved for future maintenance banners.

**Hosts / deployment**

* `ALLOWED_HOSTS` – comma-separated; used in `prod.py`.

**Database**

* `DATABASE_URL` – Heroku-style Postgres URL, used by `get_database_config_variables` in `prod.py`.

**Email**

* `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`.

**AWS S3 (optional)**

* `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_STORAGE_BUCKET_NAME`.

**Redis / Celery**

* `REDIS_URL` – primary Redis URL for Celery.
* `REDISCLOUD_URL` – alternate provider (fallback).
* `CELERY_TASK_ALWAYS_EAGER` – parsed in `base.py` for test/dev behavior.

**Seed users (for `create_user` command)**

* `DJANGO_SU_NAME`, `DJANGO_SU_EMAIL`, `DJANGO_SU_PASSWORD`.
* `DJANGO_USER_NAME`, `DJANGO_USER_EMAIL`, `DJANGO_USER_PASSWORD`.
* `DJANGO_USER_ACCEPTED`, `DJANGO_USER_IS_STAFF`.

### Database & Celery

Dev DB is SQLite, defined in `config/settings/dev.py`.

Prod DB is Postgres, defined in `config/settings/prod.py` via:

```python
from config.utils import get_database_config_variables

database_config_variables = get_database_config_variables(os.environ.get("DATABASE_URL"))
```

Celery broker/result backend are configured in `base.py` using `REDIS_URL` / `REDISCLOUD_URL`.

---

## CI / CD

CI is handled by CircleCI via `.circleci/config.yml`:

* Uses `cimg/python:3.12`.
* Steps:

  * Upgrade pip, install `pipenv`.
  * `pipenv install --dev`.
  * `pipenv run flake8 .`
  * `pipenv run coverage run` for `accounts` tests, with `--fail-under=80`.
  * `pipenv run coverage report`.

The README includes the live status badge at the top.

Future work (see `TODO.md`):

* Add Postgres + Redis services for integration tests.
* Switch to `pytest` and full-project coverage.
* Upload `coverage.xml` as an artifact.

---

## Deployment

### Heroku

Prod settings are written with Heroku in mind:

* `DEBUG=False`
* `ALLOWED_HOSTS` from env.
* Security headers (`SECURE_*`, `X_FRAME_OPTIONS`, `REFERRER_POLICY`).
* WhiteNoise middleware and `STATIC_ROOT`.

Current steps you’ll eventually take:

1. Create a Heroku app.
2. Add **Heroku Postgres** and **Heroku Redis**.
3. Set config vars:
   `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`/`REDISCLOUD_URL`, `DJANGO_SETTINGS_MODULE=config.settings.prod`.
4. Add `runtime.txt` (`python-3.12.x`) and a `requirements.txt` exported from Pipenv.
5. Push to Heroku and run migrations.

Celery worker and beat entries will be added to `Procfile` once tasks exist:

```procfile
worker: celery -A config worker -l info
beat: celery -A config beat -l info
```

### Future: Docker & Raspberry Pi

The roadmap includes:

* Multi-stage `Dockerfile` + `docker-compose.yml` (web, worker, beat, postgres, redis).
* Healthchecks and `.env.docker`.
* Optional Pi self-host:

  * systemd units for gunicorn, Celery worker, and beat.
  * Reverse proxy + basic monitoring (`node_exporter` / `blackbox_exporter`).

---

## Roadmap

For a detailed, checkbox-level view of what’s done vs planned, see:

- [`TODO.md`](./TODO.md)

That file is kept in sync with the current implementation and serves as the sprint/feature tracker.

---

## License

This project is licensed under the **GNU GPL-3.0** license.
See the [`LICENSE`](./LICENSE) file for details.

---

## Acknowledgements

Plan-It Mini is built on top of the `DjangoStarter-heroku` template and owes a lot to:

* Django & Django REST Framework
* Celery & django-celery-beat
* The broader open-source ecosystem around Django, Celery, and Redis
