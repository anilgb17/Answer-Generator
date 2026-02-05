# Celery Quick Start Guide

## Quick Setup (3 Steps)

### 1. Start Redis
```bash
redis-server
```

### 2. Start Celery Worker
```bash
cd backend
python run_celery_worker.py
```

### 3. Start API Server
```bash
cd backend
python src/main.py
```

## Test the System

### Upload a Question Paper
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@questions.txt" \
  -F "language=en"
```

Response:
```json
{
  "session_id": "abc-123-def",
  "status": "pending",
  "message": "File uploaded successfully. Processing will begin shortly."
}
```

### Check Processing Status
```bash
curl http://localhost:8000/api/status/abc-123-def
```

Response:
```json
{
  "status": "processing",
  "progress": 45,
  "message": "Processing in progress: generating_answers"
}
```

### Download PDF
```bash
curl -O http://localhost:8000/api/download/abc-123-def
```

## Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ Upload File
       ▼
┌─────────────┐      ┌──────────────┐
│  FastAPI    │─────▶│    Redis     │
│   Server    │      │   (Broker)   │
└─────────────┘      └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │    Celery    │
                     │    Worker    │
                     └──────┬───────┘
                            │
                            ▼
                     ┌──────────────┐
                     │  Processing  │
                     │   Pipeline   │
                     └──────────────┘
```

## What Happens Behind the Scenes

1. **Upload** → File saved, session created
2. **Task Queued** → Celery task submitted to Redis
3. **Worker Picks Up** → Background processing starts
4. **Progress Updates** → Real-time status in Redis
5. **PDF Generated** → Stored and ready for download

## Key Files

- `src/celery_app.py` - Celery configuration
- `src/tasks.py` - Main processing task
- `src/main.py` - FastAPI endpoints (updated)
- `run_celery_worker.py` - Worker startup script
- `tests/test_celery_tasks.py` - Integration tests

## Common Issues

**Worker not starting?**
- Check Redis is running: `redis-cli ping`
- Verify Python path includes backend directory

**Tasks not processing?**
- Check worker logs for errors
- Verify file upload directory exists
- Ensure all dependencies installed

**Need more details?**
See `docs/CELERY_SETUP.md` for comprehensive documentation.
