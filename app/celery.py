import asyncio
from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
from app.core.tasks import first_task

celery = Celery("tasks", broker=settings.CELERY_BROKER_URL)


@celery.task
def send_notifications():
    asyncio.run(first_task())


celery.conf.beat_schedule = {
    'run-task-every-5-minutes': {
        'task': 'app.celery.send_notifications',
        'schedule': timedelta(seconds=10),
    },
}

