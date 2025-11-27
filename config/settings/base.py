# config/settings/base.py
#
# Base settings shared by all environments (dev, test, prod).
# - dev.py, prod.py, and test.py import from here and then override as needed.

import os
from pathlib import Path

from dotenv import load_dotenv

from config.utils import get_database_config_variables

# Load environment variables from a .env file if present.
# In Heroku, config vars are already in the environment, so this is a no-op.
load_dotenv()

# Project root (one level above the "config" package)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Core security / environment knobs
# ---------------------------------------------------------------------------

# Default secret key for local development only.
# prod.py requires SECRET_KEY to be set via environment variable.
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_IN_DEV_ONLY")

# Default to DEBUG = False; per-env modules (dev/prod/test) override this.
DEBUG = False

# ALLOWED_HOSTS is read from the environment, e.g.:
# ALLOWED_HOSTS=localhost,127.0.0.1,planit-mini-prod-xxxx.herokuapp.com
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()
]

# ---------------------------------------------------------------------------
# Database helper
# ---------------------------------------------------------------------------


def postgres_from_database_url(database_url: str):
    """
    Return a Django DATABASES dict for Postgres using a parsed DATABASE_URL.

    This keeps all "how to talk to Postgres" logic in one place.
    Each environment (dev/prod) decides *when* to call this helper.
    """
    database_config_variables = get_database_config_variables(database_url)

    options = database_config_variables.get("OPTIONS") or {}
    sslmode_list = options.get("sslmode") or ["require"]
    sslmode = (
        sslmode_list[0] if isinstance(sslmode_list, (list, tuple)) else sslmode_list
    )

    return {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": database_config_variables["DATABASE_NAME"],
            "HOST": database_config_variables["DATABASE_HOST"],
            "PORT": database_config_variables.get("DATABASE_PORT") or "5432",
            "USER": database_config_variables["DATABASE_USER"],
            "PASSWORD": database_config_variables["DATABASE_PASSWORD"],
            "OPTIONS": {
                "sslmode": sslmode,
            },
        }
    }


# ---------------------------------------------------------------------------
# Installed apps / middleware / URL routing / templates
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    # Local apps
    "accounts.apps.AccountsConfig",
    "base",
    "assets.apps.AssetsConfig",
    "core.apps.CoreConfig",
    "work.apps.WorkConfig",
    "api",
    # Django contrib apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admindocs",
    # Third-party apps
    "rest_framework",
    "django_filters",
    "storages",
    "django_celery_beat",
]

# Whitenoise handles static files in all environments by default.
# prod.py relies on this for Heroku.
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Project-level templates directory; app templates still work via APP_DIRS.
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"

# ---------------------------------------------------------------------------
# Auth / internationalization / defaults
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"  # noqa: E501
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "America/New_York"
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "accounts.CustomUser"

LOGIN_REDIRECT_URL = "home"
LOGOUT_REDIRECT_URL = "home"

THE_SITE_NAME = "Plan-It Mini"

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"
# On Heroku, collectstatic will put everything here; Whitenoise serves from it.
STATIC_ROOT = BASE_DIR / "staticfiles"

# ---------------------------------------------------------------------------
# Django REST Framework
# ---------------------------------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        # Browsable API / session-based views.
        "rest_framework.authentication.SessionAuthentication",
        # For quick CLI/manual testing.
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        # Custom project-wide API permission.
        "api.permissions.IsAuthenticatedReadOnlyOrManager",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        # Non-staff users are throttled by this custom class.
        "api.throttling.NonStaffUserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        # Non-staff users; staff are exempt via the custom class.
        "non_staff_user": "1000/day",
    },
}

# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

# Safe defaults: real SMTP in prod, overridden in dev/test.
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

# Convenience address for smoke tests / demo flows.
TEST_EMAIL_ADDRESS = os.getenv("TEST_EMAIL_ADDRESS", "test@example.com")

# ---------------------------------------------------------------------------
# File storage (optional AWS S3 integration)
# ---------------------------------------------------------------------------

# If these are not set, Django falls back to local filesystem storage.
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")

if AWS_STORAGE_BUCKET_NAME:
    # These settings only apply if you configure S3.
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_S3_OBJECT_PARAMETERS = {"ACL": "public-read", "CacheControl": "max-age=86400"}
    AWS_MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
    # Default file storage (uploads). Static files are still served by Whitenoise
    # unless you explicitly change STATICFILES_STORAGE.
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# ---------------------------------------------------------------------------
# Celery
# ---------------------------------------------------------------------------

CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = TIME_ZONE

# Prefer REDIS_URL/REDISCLOUD_URL from Heroku; fall back to localhost for dev.
CELERY_BROKER_URL = os.getenv("REDIS_URL") or os.getenv(
    "REDISCLOUD_URL", "redis://localhost:6379/0"
)
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL") or os.getenv(
    "REDISCLOUD_URL", "redis://localhost:6379/0"
)

# For local experiments or tests you can enable synchronous task execution by
# setting CELERY_TASK_ALWAYS_EAGER=true in the environment.
CELERY_TASK_ALWAYS_EAGER = (
    os.getenv("CELERY_TASK_ALWAYS_EAGER", "False").lower() == "true"
)

# ---------------------------------------------------------------------------
# Caching / sessions
# ---------------------------------------------------------------------------

# Prefer a dedicated cache URL (DJANGO_CACHE_URL), otherwise fall back to typical
# Heroku Redis env vars. Local fallback is Redis on localhost DB 1.
DJANGO_CACHE_URL = (
    os.getenv("DJANGO_CACHE_URL")
    or os.getenv("REDISCLOUD_URL")
    or os.getenv("REDIS_URL")  # heroku-redis uses this
    or "redis://127.0.0.1:6379/1"  # local fallback
)

# Default cache: Redis via django-redis. dev.py overrides this to LocMem.
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": DJANGO_CACHE_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Optional safety net:
            # "IGNORE_EXCEPTIONS": True,  # behave like LocMem cache if Redis is down
        },
    }
}

# Use the cache for sessions by default; in dev this is LocMem, in prod Redis.
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

# Minimal console logging. prod.py can extend this with more handlers/formatters.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "celery": {"handlers": ["console"], "level": "INFO", "propagate": True}
    },
}
