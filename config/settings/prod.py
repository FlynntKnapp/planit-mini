# config/settings/prod.py

import os

from .base import *  # noqa: F403, F401

DEBUG = False

# If someone forgot to set env var, fail safe with explicit fallback
if not ALLOWED_HOSTS:  # noqa: F405
    ALLOWED_HOSTS = [
        "planit-mini-prod-f2a603e4e8d0.herokuapp.com",
    ]

# Security
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
REFERRER_POLICY = "same-origin"

SECRET_KEY = os.environ["SECRET_KEY"]  # must be set

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    raise RuntimeError(
        "DATABASE_URL is required in prod; refusing to start without Postgres."
    )

# Database (shared helper using your parser)
DATABASES = postgres_from_database_url(database_url)  # noqa: F405
