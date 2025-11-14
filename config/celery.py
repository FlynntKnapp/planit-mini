# config/celery.py

import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")
# In production, set env var: DJANGO_SETTINGS_MODULE=config.settings.prod

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.enable_utc = True
app.conf.timezone = settings.TIME_ZONE

app.autodiscover_tasks()
app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"
