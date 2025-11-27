# config/settings/prod.py
#
# Production settings for the Heroku app.
# - Assumes config vars are set in the Heroku dashboard / CLI.

import os

from .base import *  # noqa: F403, F401

# Never run with DEBUG=True in production.
DEBUG = False

# If someone forgot to set ALLOWED_HOSTS, fall back to the known Heroku host.
# You should prefer setting ALLOWED_HOSTS via environment.
if not ALLOWED_HOSTS:  # noqa: F405
    ALLOWED_HOSTS = [
        "planit-mini-prod-f2a603e4e8d0.herokuapp.com",
    ]

# ---------------------------------------------------------------------------
# Security / HTTPS
# ---------------------------------------------------------------------------

# Honor X-Forwarded-Proto from Heroku so Django knows the request is secure.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Basic HSTS configuration (can bump this to a larger value once confident).
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Extra browser hardening.
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
REFERRER_POLICY = "same-origin"

# ---------------------------------------------------------------------------
# Secret key / database
# ---------------------------------------------------------------------------

# In prod, SECRET_KEY MUST be set via environment variable.
SECRET_KEY = os.environ["SECRET_KEY"]

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    # Fail fast instead of silently falling back to SQLite.
    raise RuntimeError(
        "DATABASE_URL is required in prod; refusing to start without Postgres."
    )

# Use the shared Postgres helper from base.py
DATABASES = postgres_from_database_url(database_url)  # noqa: F405
