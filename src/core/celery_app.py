"""Celery application configuration.

Start worker::

    celery -A src.core.celery_app worker --loglevel=info --concurrency=4

Start beat (periodic tasks)::

    celery -A src.core.celery_app beat --loglevel=info

Tracing: ``worker_process_init`` re-initializes the OpenTelemetry SDK
inside each forked worker process. Span context propagates from the API
through RabbitMQ headers, so HTTP → task spans form one connected trace.
"""

from celery import Celery
from celery.signals import worker_process_init

from .config import settings
from .logging_config import configure_logging
from .tracing import init_tracing_for_worker

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

# Explicitly include all task modules so Celery registers them on worker startup.
# autodiscover_tasks(["src.tasks"]) expects src/tasks/tasks.py (missing).
celery_app.conf.include = [
    "src.tasks.cache_tasks",
    "src.tasks.image_analysis_tasks",
    "src.tasks.experiment_tasks",
]


@worker_process_init.connect
def _setup_worker_observability(**_kwargs) -> None:
    """Re-init structlog + OpenTelemetry inside each worker process.

    Celery forks; the parent's TracerProvider/logging configuration do
    NOT carry across the fork boundary cleanly. Re-initializing here
    gives each worker its own SDK with the correct
    ``service.role=worker`` resource attribute and proper JSON logging
    that includes ``trace_id`` automatically (the structlog processor
    looks up the current span on every log call).
    """
    configure_logging()
    init_tracing_for_worker()
