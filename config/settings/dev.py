# config/settings/dev.py
from .base import *  # noqa: F403, F401

DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

STATICFILES_DIRS = [BASE_DIR / "static"]  # noqa: F405

# Dev nicety: console email
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
