"""Celery application configuration.

Start worker::

    celery -A src.core.celery_app worker --loglevel=info --concurrency=4

Start beat (periodic tasks)::

    celery -A src.core.celery_app beat --loglevel=info
"""

from celery import Celery

from .config import settings

celery_app = Celery(
    "scratch",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    # Timezone
    timezone="UTC",
    enable_utc=True,
    # Task defaults
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    # Result expiry (24 hours)
    result_expires=86400,
    # Task routes
    task_routes={
        "src.tasks.image_analysis_tasks.*": {"queue": "image_analysis"},
        "src.tasks.experiment_tasks.*": {"queue": "experiments"},
        "src.tasks.cache_tasks.*": {"queue": "cache"},
    },
    # Default queue
    task_default_queue="default",
    # Beat schedule (periodic tasks)
    beat_schedule={
        "warm-cache-every-hour": {
            "task": "src.tasks.cache_tasks.warm_cache",
            "schedule": 3600.0,
        },
    },
)

# Auto-discover tasks in src.tasks package.
celery_app.autodiscover_tasks(["src.tasks"])
