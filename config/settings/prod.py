# config/settings/prod.py

import os

from config.utils import get_database_config_variables

from .base import *  # noqa: F403, F401

DEBUG = False

ALLOWED_HOSTS = (
    os.getenv("ALLOWED_HOSTS", "").split(",")
    if os.getenv("ALLOWED_HOSTS")
    else [
        "your-heroku-app.herokuapp.com",
    ]
)

# WhiteNoise & security
MIDDLEWARE = MIDDLEWARE + ["whitenoise.middleware.WhiteNoiseMiddleware"]  # noqa: F405
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

# Database (your helper or dj-database-url). Keeping your helper for continuity:
database_config_variables = get_database_config_variables(
    os.environ.get("DATABASE_URL")
)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": database_config_variables["DATABASE_NAME"],
        "HOST": database_config_variables["DATABASE_HOST"],
        "PORT": database_config_variables["DATABASE_PORT"] or "5432",
        "USER": database_config_variables["DATABASE_USER"],
        "PASSWORD": database_config_variables["DATABASE_PASSWORD"],
        # Optional: map sslmode into OPTIONS
        "OPTIONS": {
            "sslmode": database_config_variables["OPTIONS"].get("sslmode", ["prefer"])[
                0
            ],
        },
    }
}

STATIC_ROOT = BASE_DIR / "staticfiles"  # noqa: F405
