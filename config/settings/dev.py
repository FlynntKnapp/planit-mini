# config/settings/dev.py
#
# Development settings.
# - Used for local development.
# - Can also be used for a Heroku "dev" app if you want.

import os

from .base import *  # noqa: F403, F401

# Explicitly enable debug in dev.
DEBUG = True

# If nobody set ALLOWED_HOSTS in the environment, be generous for local dev.
if not ALLOWED_HOSTS:  # noqa: F405
    # Local + simple dev Heroku fallback.
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Heroku DEV (persistent Postgres)
    DATABASES = postgres_from_database_url(database_url)  # noqa: F405
else:
    # Local dev only (SQLite). Simple, no extra services required.
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
        }
    }

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

# Where your uncollected static files live during development.
STATICFILES_DIRS = [BASE_DIR / "static"]  # noqa: F405

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

# In dev, print emails to the console instead of sending them.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# ---------------------------------------------------------------------------
# Caching
# ---------------------------------------------------------------------------

# In dev, stick with a simple in-memory cache. This overrides the Redis
# configuration defined in base.py.
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "planit-mini-dev",
    }
}
