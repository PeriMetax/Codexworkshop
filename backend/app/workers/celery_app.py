from celery import Celery

from app.core.config import settings

celery = Celery("taxonomy_validator", broker=settings.redis_url, backend=settings.redis_url)


@celery.task(name="ping")
def ping() -> str:
    return "pong"
