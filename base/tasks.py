# base/tasks.py

import logging
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def ping_redis_task(self):
    """
    Tiny task to prove Celery -> Redis -> worker works.
    """
    logger.info("ping_redis_task is running. Task id=%s", self.request.id)
    return "pong"
