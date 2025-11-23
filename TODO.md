# `planit-mini` GitHub Repo
- [https://github.com/FlynntKnapp/planit-mini](https://github.com/FlynntKnapp/planit-mini)

> Template notes (what’s already there):  
> • Generated from **DjangoStarter-heroku** (CustomUser, DEV/PROD settings, Pipenv, Procfile)
> • Repo shows `accounts/`, `config/`, `templates/`, `Procfile`, `.flake8`, `README.md`, `LICENSE (GPL-3.0)`, and a `.circleci/` folder scaffold.
> • README explicitly lists **Custom user**, **separate DEV/PROD settings**, **Pipfile included**, **Heroku Procfile included**, and Heroku setup steps.

# Plan-It Mini (Django + DRF) — Tiny-Step Roadmap (Assets + Maintenance)

> **Domains**  
> - **Assets**: `Asset`, `FormFactor`, `OS`, `Application`, `Project`  
> - **Planning/Work**: `MaintenanceTask` (template), `WorkOrder` (generated task), `ActivityInstance` (completion/evidence)  
> **Core Features**: auth, role permissions, pagination/filtering, polished admin  
> **Infra**: Postgres, Redis cache, Celery (beat w/ 1 scheduled job), pytest + coverage  
> **CI/Deploy**: CircleCI badge → Heroku first → Docker later (Pi self-host optional)

## Sprint 0 — Bootstrap (1–2 sessions)

- [x] **Create repo** `planit-mini`.  
  * Generated from `DjangoStarter-heroku` for a clean base.
- [x] **Python env**: **Pipenv** (Pipfile) included by template.
- [x] **Django project** exists (`config/`, `manage.py`).
- [x] **Apps**: add `core`, `assets`, `work`  
  - `python manage.py startapp core && startapp assets && startapp work`
- [x] **Install base apps already present**: `accounts` custom user.
- [x] **Settings split**: DEV/PROD present in template; keep and extend.
- [ ] **Postgres** via `dj-database-url` (`DATABASE_URL`)
- [ ] **Redis cache** (`REDIS_URL`) + DRF settings stub
- [x] **Celery**: add `config/celery.py` + loader in `config/__init__.py`
- [x] **.env.example**: `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `DEBUG`, `ALLOWED_HOSTS`
- [x] **Makefile**: `run`, `test`, `lint`, `migrate`, `seed`, `superuser`
- [x] **README skeleton** present; will replace with Plan-It specifics & screenshots.
- [x] **Precommit/linting**: `.flake8` already in repo (add `ruff`, `black`, `isort` via pre-commit).
- [x] **Procfile** present for Heroku.
- [x] **License** present (GPL-3.0).
- [x] **CircleCI**: confirm `.circleci/config.yml`; add if missing (see Sprint 6).

**Files to add now**
```

Makefile  
.env.example  
config/settings/{base.py,local.py,prod.py} # extend existing split if needed  
config/celery.py  
config/**init**.py # celery loader

```

## Sprint 1 — Data Model & Admin (Assets + Work) (1–3 sessions)

**assets/models.py**
- [x] `FormFactor(name, slug)`  — e.g., “Raspberry Pi”, “Server”, “Laptop”
- [x] `OS(name, version, slug)` — e.g., “RaspiOS 64-bit”, “Ubuntu 24.04”
- [x] `Application(name, version, slug)`
- [x] `Project(name, description, slug)` — “Q1 Patch Wave”, “Lab Refresh”
- [x] `Asset(name, kind, form_factor=FK, os=FK, location, purchase_date?, warranty_expires?, notes)`
- [x] `Asset.applications` — M2M to `Application`

**work/models.py**
- [x] `MaintenanceTask(name, cadence, description?, threshold_json?)`
  - examples: “Monthly OS patches”, “Weekly backup verify”
- [x] `WorkOrder(asset=FK, task=FK, due=DateTime, status=choices[open,done,cancelled])`
- [x] `ActivityInstance(work_order=FK null, asset=FK, kind=choices[checked,patched,backup_verified], note, occurred_at=DateTime)`

**Admin polish**
- [x] `AssetAdmin`: `list_display` (warranty/due status chips), `search_fields`, `list_filter` (form_factor, os, apps)
- [x] Inlines: `WorkOrder` & recent `ActivityInstance` on `Asset`
- [x] `WorkOrderAdmin`: quick actions “Mark done”, filter by `due` window
- [x] `MaintenanceTaskAdmin`: show cadence, “Generate Preview” action

**Seed command**
- [x] `python manage.py seed_demo_data` → some form factors, OSes, apps, assets, tasks, work orders

**Migrations**
- [x] `make migrate`

## Sprint 2 — API (DRF) (1–3 sessions)

**Serializers**
- [x] `FormFactorSerializer`, `OSSerializer`, `ApplicationSerializer`, `ProjectSerializer`
- [x] `AssetSerializer` (include apps list)
- [x] `MaintenanceTaskSerializer`, `WorkOrderSerializer`, `ActivityInstanceSerializer`

**Viewsets + Router**
- [x] ModelViewSets for all models, registered on `/api/...`

**Permissions**
- [x] Read: authenticated users
- [x] Write: users in `maintenance_manager` group or `user.is_staff`
- [x] Object-level (optional): owners/managers for changes

**Pagination/Filters/Ordering**
- [x] Default `PageNumberPagination` (20)
- [x] Filters:
  - `Asset`: by `form_factor`, `os`, `applications`, `location`, `warranty_expires__lt`, `name__icontains`
  - `WorkOrder`: by `asset`, `task`, `status`, `due__date` range
  - `ActivityInstance`: by `asset`, `kind`, `occurred_at` range
- [x] Ordering: `?ordering=name` (Assets) / `?ordering=-due` (WorkOrders) / `?ordering=-occurred_at` (Activities)
- [x] Throttling: simple user throttle for non-staff

## Sprint 3 — Celery & Scheduled Job (1–2 sessions)

- [ ] Enable **django-celery-beat** in settings; DB schedules
- [ ] **Generator task**: `work.tasks.generate_workorders()`
  - Reads `MaintenanceTask.cadence` (monthly/weekly) and creates upcoming `WorkOrder`s per `Asset`
- [ ] **Healthcheck task** (optional): `core.tasks.daily_asset_healthcheck()` — flag overdue; auto-create `ActivityInstance(kind="checked")`
- [ ] **Manual staff endpoint**: DRF action to run generator/healthcheck

## Sprint 4 — Auth & Roles (1–2 sessions)

- [x] **Custom user** already present from template; set `AUTH_USER_MODEL` if not already.
- [ ] Create groups via data migration or `post_migrate`: `maintenance_viewer`, `maintenance_manager`
- [ ] Role tests: viewer read-only; manager full write

## Sprint 5 — Tests (full coverage; start in Sprint 1 and grow)

> Target: **95–100%** on `assets` + `work` + critical paths in `config` and `accounts` integration

- [ ] **Test stack**: `pytest`, `pytest-django`, `pytest-cov`, `model_bakery` or `factory_boy`, `freezegun`
- [ ] **Factories**: `AssetFactory`, `FormFactorFactory`, `OSFactory`, `ApplicationFactory`, `ProjectFactory`, `MaintenanceTaskFactory`, `WorkOrderFactory`, `ActivityInstanceFactory`, `UserFactory(with Group)`
- [ ] **Model tests**: str/repr; relationships; `WorkOrder.status` transitions; cadence parsing edge cases
- [ ] **Admin tests**: list loads; filters; actions; perms
- [ ] **API tests**: list/detail/create/update/delete; perms by role; pagination; filters; ordering; throttling
- [ ] **Celery tests**: unit test `generate_workorders` & healthcheck (freeze time)
- [ ] **Settings smoke**: prod env parsing
- [ ] **Coverage gate**: `--cov-fail-under=95`

## Sprint 6 — CI (CircleCI) (1 session)

- [x] Ensure `.circleci/config.yml` exists; if not, add job with **Python + Postgres + Redis** services → run `pytest --cov` → store `coverage.xml`
- [x] Add **badge** to README:
  `[![CircleCI](https://circleci.com/gh/<ORG>/planit-mini.svg?style=shield)](https://circleci.com/gh/<ORG>/planit-mini)`

## Sprint 7 — Heroku (vanilla) (1 session)

- [x] `Procfile` present; keep `web:` and add `worker:` & `beat:` entries for Celery.
  ```
  web: gunicorn config.wsgi --log-file -  
  worker: celery -A config worker -l info  
  beat: celery -A config beat -l info
  ```
- [x] `.python-version`
- [x] `Pipfile`: add `gunicorn`, `psycopg2-binary`, `config.utils.get_database_config_variables`, `whitenoise`, `django-celery-beat`
- [x] `settings/prod.py`: `DEBUG=False`, `ALLOWED_HOSTS`, `SECURE_*`, `whitenoise`
- [ ] **Addons**: Heroku Postgres + Heroku Redis
- [x] **Config Vars**: `SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`, `DJANGO_SETTINGS_MODULE=config.settings.prod`
- [ ] `collectstatic`, smoke test `/api/assets/`, `/api/workorders/`

## Sprint 8 — UX & Admin Polish (1–2 sessions)

- [ ] DRF: default pagination + `?search=` on Asset name/notes
- [ ] Admin: filters (form factor, OS, apps, status), autocomplete FKs
- [ ] README screenshots: Admin lists, API results, coverage report

## Sprint 9 — Dockerize (later) (1–2 sessions)

- [ ] Multi-stage `Dockerfile`, `docker-compose.yml` (web, worker, beat, postgres, redis)
- [ ] Healthchecks; `.env.docker` sample; Make targets: `up`, `down`, `logs`

---

## Optional Side Quest — Self-Host on a Pi (after Heroku)

**Host prep**
- [ ] OS updates, static IP; Postgres 16, Redis 7
- [ ] Python 3.12 venv; `/srv/planit-mini/{app,static,media}`
- [ ] System users; firewall; (TLS via Caddy/Traefik optional)

**Services**
- [ ] systemd units: `gunicorn`, `celery` worker, `celery beat` (bind 127.0.0.1:8000)
- [ ] Reverse proxy; monitoring via `node_exporter` + `blackbox_exporter` hitting `/healthz`

**Deploy flow**
- [ ] git pull → install deps → migrate → collectstatic → restart units

---

## Test Inventory (tick-off list)

**Models**
- [ ] `Asset` CRUD, apps M2M, warranty status helpers  
- [ ] `WorkOrder` state transitions, due date queries  
- [ ] `MaintenanceTask` cadence parse/validate  
- [ ] `ActivityInstance` attach to `WorkOrder` or just `Asset` (both paths)

**Admin**
- [ ] Asset/WorkOrder list pages load; filters/search work  
- [ ] Inline relations render; bulk actions perms enforced

**API**
- [ ] Auth required; anonymous 401  
- [ ] Viewer read-only; Manager write  
- [ ] Pagination default 20; filters & ordering correct  
- [ ] Throttling for non-staff

**Tasks**
- [ ] `generate_workorders` creates the correct future window  
- [ ] Healthcheck flags overdue; creates Activity evidence

**Config**
- [ ] Env parsing in `prod.py` smoke  
- [ ] `/admin/` + `/healthz` up locally & in prod

**Coverage**
- [ ] `pytest --cov=. --cov-report=term-missing --cov-fail-under=95`

---

## README blurb (use this in the repo)

> **Plan-It Mini** helps you plan maintenance, track assets, and prove completion.  
> Define maintenance templates (monthly patches, weekly backup verify), generate scheduled work orders for your devices, and capture evidence as activities. Built with Django + DRF, fully tested, Dockerized, CI’d, and deployable to Heroku or a Raspberry Pi.

---

## Next Actions (today)

1. **Add apps** `core`, `assets`, `work`; wire DRF + URLs.  
2. **Add Celery + django-celery-beat** and a first scheduled task.  
3. **Implement models + admin**, migrate, and seed demo data.  
4. **Add CircleCI config** (Postgres/Redis) and a coverage badge.
