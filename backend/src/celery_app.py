"""Celery application configuration for asynchronous task processing."""
from celery import Celery
from config.settings import settings

# Create Celery app
celery_app = Celery(
    'question_answer_generator',
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=['src.tasks']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour max per task
    task_soft_time_limit=3300,  # 55 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Optional: Configure task routes
celery_app.conf.task_routes = {
    'src.tasks.process_question_paper': {'queue': 'celery'},
}

if __name__ == '__main__':
    celery_app.start()
