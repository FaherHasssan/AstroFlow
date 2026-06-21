from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "astroflow",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Make sure task definitions are registered with this app when the worker boots.
import app.workers.tasks  # noqa: E402,F401
