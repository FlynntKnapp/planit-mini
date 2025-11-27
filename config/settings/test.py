# config/settings/test.py
#
# Test settings.
# - Starts from dev.py (SQLite or Postgres depending on env).
# - Then overrides a few things to make tests fast and deterministic.

from .dev import *  # noqa: F403, F401

# Use a very fast (but insecure) password hasher for tests.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]

# Keep test emails in memory; tests can inspect outbox without hitting a real SMTP server.  # noqa: E501
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Run Celery tasks synchronously during tests so you don't need a worker.
CELERY_TASK_ALWAYS_EAGER = True  # run tasks inline during tests
