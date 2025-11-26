# config/settings/dev.py

import os

from .base import *  # noqa: F403, F401

DEBUG = True

if not ALLOWED_HOSTS:  # noqa: F405
    # Local + Heroku dev fallback
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Heroku DEV (persistent Postgres)
    DATABASES = postgres_from_database_url(database_url)  # noqa: F405
else:
    # Local dev only (SQLite)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

STATICFILES_DIRS = [BASE_DIR / "static"]  # noqa: F405

# Dev nicety: console email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "planit-mini-dev",
    }
}
