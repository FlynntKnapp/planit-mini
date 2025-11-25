# base/tasks.py

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def ping_redis_task(self):
    """
    Tiny task to prove Celery -> Redis -> worker works.
    """
    logger.info("ping_redis_task is running. Task id=%s", self.request.id)
    return "pong"


@shared_task(bind=True)
def send_redis_test_email(self, to_email: str):
    subject = "Redis / Celery test from Plan-It Mini"
    message = "If you got this, Celery + Redis + Mailgun are all working in prod."
    send_mail(
        subject,
        message,
        settings.TEST_EMAIL_ADDRESS,  # or settings.DEFAULT_FROM_EMAIL if you set it
        [to_email],
        fail_silently=False,
    )
    return "sent"
