# config/settings/base.py

import os
from pathlib import Path

from dotenv import load_dotenv

from config.utils import get_database_config_variables

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME_IN_DEV_ONLY")

DEBUG = False  # default; env modules will override

ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()
]


def postgres_from_database_url(database_url: str):
    """
    Shared Postgres DATABASES builder using your custom DATABASE_URL parser.
    Env-specific policy belongs in dev.py/prod.py.
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


INSTALLED_APPS = [
    "accounts.apps.AccountsConfig",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admindocs",
    "rest_framework",
    "django_filters",
    "storages",
    "base",
    "django_celery_beat",
    "assets.apps.AssetsConfig",
    "core.apps.CoreConfig",
    "work.apps.WorkConfig",
    "api",
]

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

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
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
        "api.throttling.NonStaffUserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        # Non-staff users; staff are exempt via the custom class
        "non_staff_user": "1000/day",
    },
}

# Email (safe defaults; override per-env)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = os.getenv("EMAIL_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = True

TEST_EMAIL_ADDRESS = os.getenv("TEST_EMAIL_ADDRESS", "test@example.com")

# AWS S3 (optional; leave envs empty in dev)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
if AWS_STORAGE_BUCKET_NAME:
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    AWS_S3_OBJECT_PARAMETERS = {"ACL": "public-read", "CacheControl": "max-age=86400"}
    AWS_MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/"
    DEFAULT_FILE_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"

# Celery (shared defaults; envs may override)
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = os.getenv("REDIS_URL") or os.getenv(
    "REDISCLOUD_URL", "redis://localhost:6379/0"
)
CELERY_RESULT_BACKEND = os.getenv("REDIS_URL") or os.getenv(
    "REDISCLOUD_URL", "redis://localhost:6379/0"
)
CELERY_TASK_ALWAYS_EAGER = (
    os.getenv("CELERY_TASK_ALWAYS_EAGER", "False").lower() == "true"
)

# Logging (minimal; expand in prod.py)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "loggers": {
        "celery": {"handlers": ["console"], "level": "INFO", "propagate": True}
    },
}
