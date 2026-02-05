# Session Management and Progress Tracking

This document describes the session management and progress tracking implementation for the Question Answer Generator system.

## Overview

The system uses Redis for session management and progress tracking, providing:

- **Session Management**: Track user sessions with language preferences and metadata
- **Progress Tracking**: Real-time progress updates during multi-stage processing
- **Language Persistence**: Store and retrieve language preferences per session
- **Result Storage**: Store processing results for later retrieval

## Components

### SessionManager

The `SessionManager` class provides the main interface for session management:

```python
from src.session_manager import SessionManager, SessionStatus, ProgressEvent

# Initialize session manager
session_manager = SessionManager(
    redis_host='localhost',
    redis_port=6379,
    redis_db=0,
    session_ttl=3600  # 1 hour
)

# Create a new session
session_id = session_manager.create_session(
    language='en',
    metadata={'user_id': '123', 'filename': 'questions.pdf'}
)

# Update session status
session_manager.update_session_status(session_id, SessionStatus.PROCESSING)

# Set language preference
session_manager.set_language_preference(session_id, 'es')

# Get language preference
language = session_manager.get_language_preference(session_id)
```

### ProgressEvent

The `ProgressEvent` class represents a progress update:

```python
from src.session_manager import ProgressEvent

# Create a progress event
event = ProgressEvent(
    session_id=session_id,
    stage='parsing',
    progress=25,
    message='Parsing input document'
)

# Add to session
session_manager.add_progress_event(event)

# Get all progress events
events = session_manager.get_progress_events(session_id)

# Get latest progress
latest = session_manager.get_latest_progress(session_id)
# Returns: {'progress': 25, 'stage': 'parsing', 'status': 'processing'}
```

### SessionStatus

The `SessionStatus` enum defines possible session states:

- `PENDING`: Session created, processing not started
- `PROCESSING`: Processing in progress
- `COMPLETE`: Processing completed successfully
- `ERROR`: Processing failed with error

## Integration with Answer Generator

The `AnswerGenerator` supports progress callbacks for real-time updates:

```python
from src.answer_generator import AnswerGenerator
from src.session_manager import SessionManager, ProgressEvent

# Create session
session_manager = SessionManager()
session_id = session_manager.create_session(language='en')

# Define progress callback
def progress_callback(stage: str, progress: int, message: str):
    event = ProgressEvent(
        session_id=session_id,
        stage=stage,
        progress=progress,
        message=message
    )
    session_manager.add_progress_event(event)

# Initialize answer generator with callback
answer_generator = AnswerGenerator(
    knowledge_base=knowledge_base,
    language_service=language_service,
    progress_callback=progress_callback
)

# Generate answer - progress events will be emitted automatically
answer = answer_generator.generate_answer(question, target_language='en')
```

## Progress Stages

The answer generator emits progress events at the following stages:

1. **knowledge_search** (10%): Searching knowledge base
2. **context_building** (20%): Building context from knowledge entries
3. **answer_generation** (40%): Generating answer with LLM
4. **visual_detection** (70%): Detecting visual elements
5. **citation_generation** (90%): Generating citations
6. **complete** (100%): Answer generation complete

## Multi-Question Processing

For processing multiple questions, emit progress events for each question:

```python
questions = [q1, q2, q3, q4, q5]
n = len(questions)

for i, question in enumerate(questions):
    # Process question
    answer = answer_generator.generate_answer(question)
    
    # Update overall progress
    overall_progress = int((i + 1) / n * 100)
    event = ProgressEvent(
        session_id=session_id,
        stage=f'question_{i+1}',
        progress=overall_progress,
        message=f'Completed question {i+1} of {n}'
    )
    session_manager.add_progress_event(event)
```

## Result Storage

Store processing results for later retrieval:

```python
# Store result
result_data = {
    'pdf_filename': 'answers_2024-12-11.pdf',
    'question_count': 5,
    'success': True,
    'language': 'en'
}
session_manager.store_result(session_id, result_data)

# Retrieve result
result = session_manager.get_result(session_id)
```

## Session Cleanup

Sessions automatically expire after the TTL period. Manual cleanup:

```python
# Delete session and all associated data
session_manager.delete_session(session_id)
```

## Redis Configuration

### Local Development

For local development, start Redis using Docker:

```bash
docker compose up -d redis
```

### Production

Configure Redis connection via environment variables:

```bash
REDIS_HOST=redis.example.com
REDIS_PORT=6379
REDIS_DB=0
SESSION_TTL=3600
```

## Testing

### Property-Based Tests

The system includes property-based tests for:

- **Property 26**: Progress indication for multi-question processing
- **Property 29**: Processing progress updates
- **Property 31**: Language preference persistence

Run property tests:

```bash
pytest backend/tests/test_session_manager_property.py -v
```

### Unit Tests

Unit tests cover:

- Session creation and retrieval
- Status updates
- Language preference management
- Progress event tracking
- Result storage

Run unit tests:

```bash
pytest backend/tests/test_session_manager.py -v
```

## Demo

Run the demo script to see session management in action:

```bash
python backend/src/demo_progress_tracking.py
```

This demonstrates:
- Session creation with language preference
- Multi-stage progress tracking
- Language preference updates
- Result storage and retrieval

## API Integration

The session management system integrates with the REST API:

### Create Session

```http
POST /api/upload
Content-Type: multipart/form-data

file: questions.pdf
language: es
```

Response:
```json
{
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending"
}
```

### Check Progress

```http
GET /api/status/{session_id}
```

Response:
```json
{
  "status": "processing",
  "progress": 60,
  "stage": "answer_generation",
  "message": "Generating answers"
}
```

### Download Result

```http
GET /api/download/{session_id}
```

Returns the generated PDF file.

## Best Practices

1. **Always create a session** before starting processing
2. **Emit progress events** at meaningful stages
3. **Update session status** to reflect current state
4. **Store language preference** early in the session
5. **Clean up sessions** after download or expiry
6. **Handle Redis connection errors** gracefully
7. **Use appropriate TTL** based on expected processing time

## Troubleshooting

### Redis Connection Errors

If Redis is not available, tests will be skipped. Ensure Redis is running:

```bash
docker compose up -d redis
```

### Session Not Found

Sessions expire after TTL. Check if session has expired and create a new one.

### Progress Not Updating

Ensure progress callback is properly configured in AnswerGenerator initialization.

## Requirements Validation

This implementation validates the following requirements:

- **Requirement 8.2**: Progress indication for multi-question processing
- **Requirement 8.3**: Estimated completion time (via progress percentage)
- **Requirement 9.4**: Progress indicator during processing
- **Requirement 10.3**: Language preference storage in session
