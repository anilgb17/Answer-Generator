# Celery Task Queue Setup

This document describes how to set up and run the Celery task queue for asynchronous question paper processing.

## Overview

The Question Answer Generator uses Celery with Redis as a message broker to handle asynchronous processing of question papers. This allows the API to respond immediately to upload requests while processing happens in the background.

## Architecture

```
User Upload → FastAPI → Celery Task Queue → Worker Processes
                ↓                              ↓
            Redis Broker ←──────────────────────┘
                ↓
         Session Manager (Progress Tracking)
```

## Prerequisites

1. **Redis Server**: Celery requires Redis as a message broker
   - Windows: Download from https://github.com/microsoftarchive/redis/releases
   - Linux/Mac: `sudo apt-get install redis-server` or `brew install redis`

2. **Python Dependencies**: Already included in `requirements.txt`
   - celery==5.3.4
   - redis==5.0.1

## Configuration

Celery configuration is managed through environment variables in `.env`:

```env
# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Running the System

### 1. Start Redis Server

**Windows:**
```bash
redis-server
```

**Linux/Mac:**
```bash
sudo service redis-server start
# or
redis-server
```

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

### 2. Start Celery Worker

From the `backend` directory:

**Windows:**
```bash
python run_celery_worker.py
```

**Linux/Mac:**
```bash
celery -A src.celery_app worker --loglevel=info --concurrency=2
```

The worker will start and display:
```
-------------- celery@hostname v5.3.4 (emerald-rush)
--- ***** -----
-- ******* ---- Windows-10-10.0.19045-SP0 2024-12-11 10:00:00
- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         question_answer_generator:0x...
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 2 (solo)
-- ******* ---- .> task events: OFF
--- ***** -----
 -------------- [queues]
                .> default          exchange=default(direct) key=default

[tasks]
  . src.tasks.process_question_paper
```

### 3. Start FastAPI Server

In a separate terminal, from the `backend` directory:

```bash
python src/main.py
```

Or using uvicorn directly:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

## Task Processing Flow

1. **Upload**: User uploads a question paper via `/api/upload`
2. **Session Creation**: System creates a session and stores file
3. **Task Submission**: Celery task is submitted to the queue
4. **Worker Processing**: Worker picks up task and processes:
   - Parse input file
   - Generate answers (with knowledge base)
   - Generate diagrams
   - Create PDF
   - Store PDF
5. **Progress Updates**: Worker emits progress events to Redis
6. **Completion**: Session status updated to COMPLETE
7. **Download**: User downloads PDF via `/api/download/{session_id}`

## Monitoring

### Check Task Status

```python
from celery.result import AsyncResult
from src.celery_app import celery_app

# Check task status by session_id (which is used as task_id)
result = AsyncResult(session_id, app=celery_app)
print(f"Status: {result.state}")
print(f"Result: {result.result}")
```

### Monitor with Flower

Install Flower for web-based monitoring:

```bash
pip install flower
```

Run Flower:

```bash
celery -A src.celery_app flower
```

Access at: http://localhost:5555

### Redis CLI Monitoring

Monitor Redis activity:

```bash
redis-cli monitor
```

Check queue length:

```bash
redis-cli llen celery
```

## Troubleshooting

### Worker Not Picking Up Tasks

1. **Check Redis Connection:**
   ```bash
   redis-cli ping
   ```

2. **Verify Celery Configuration:**
   - Ensure `CELERY_BROKER_URL` matches Redis server
   - Check Redis is accessible from worker machine

3. **Check Worker Logs:**
   - Look for connection errors
   - Verify task is registered

### Tasks Failing

1. **Check Worker Logs:**
   - Worker terminal shows detailed error messages
   - Look for import errors or missing dependencies

2. **Verify File Paths:**
   - Ensure upload directory exists
   - Check file permissions

3. **Test Components Individually:**
   ```python
   from src.tasks import _parse_input_file
   questions = _parse_input_file('path/to/file.txt', 'text')
   ```

### Redis Connection Errors

1. **Check Redis is Running:**
   ```bash
   redis-cli ping
   ```

2. **Verify Port:**
   - Default is 6379
   - Check firewall settings

3. **Check Configuration:**
   - Verify `REDIS_HOST` and `REDIS_PORT` in `.env`

## Production Deployment

### Using Supervisor (Linux)

Create `/etc/supervisor/conf.d/celery.conf`:

```ini
[program:celery-worker]
command=/path/to/venv/bin/celery -A src.celery_app worker --loglevel=info --concurrency=4
directory=/path/to/backend
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/celery/worker.log
```

Start with:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery-worker
```

### Using Docker

See `docker-compose.yml` for containerized deployment with Redis and Celery worker.

### Scaling Workers

Increase concurrency for more parallel processing:

```bash
celery -A src.celery_app worker --loglevel=info --concurrency=4
```

Or run multiple worker instances:

```bash
# Terminal 1
celery -A src.celery_app worker --loglevel=info --hostname=worker1@%h

# Terminal 2
celery -A src.celery_app worker --loglevel=info --hostname=worker2@%h
```

## Performance Tuning

### Worker Configuration

- **Concurrency**: Number of parallel tasks (default: 2)
  - CPU-bound: Set to number of CPU cores
  - I/O-bound: Can be higher (2-4x CPU cores)

- **Prefetch Multiplier**: Tasks to prefetch per worker (default: 1)
  - Lower for long-running tasks
  - Higher for short tasks

- **Max Tasks Per Child**: Restart worker after N tasks (default: 50)
  - Prevents memory leaks
  - Set to 0 to disable

### Redis Configuration

For production, tune Redis:

```conf
# /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

## Testing

Run integration tests:

```bash
pytest tests/test_celery_tasks.py -v
```

Note: Tests use mocked Redis, so they don't require Redis to be running.

## Additional Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Redis Documentation](https://redis.io/documentation)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
