"""Script to run Celery worker for processing tasks."""
import sys
from pathlib import Path

# Add backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from src.celery_app import celery_app

if __name__ == '__main__':
    # Run Celery worker
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=2',
        '--pool=solo' if sys.platform == 'win32' else '--pool=prefork'
    ])
