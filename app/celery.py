import asyncio
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

from app.core.tasks import first_task

from app.core.config import settings


celery = Celery("tasks", broker=settings.CELERY_BROKER_URL)


@celery.task
def send_notifications():
    asyncio.run(first_task())


celery.conf.beat_schedule = {
    'run-task': {
        'task': 'app.celery.send_notifications',
        'schedule': crontab(hour="0", minute="0"),
    },
}

