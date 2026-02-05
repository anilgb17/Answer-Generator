"""Session management module for tracking user sessions and progress."""
import json
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
import redis

from src.exceptions import QuestionAnswerError


class SessionStatus(Enum):
    """Status of a processing session."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"


class ProgressEvent:
    """Represents a progress event during processing."""
    
    def __init__(
        self,
        session_id: str,
        stage: str,
        progress: int,
        message: str,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize a progress event.
        
        Args:
            session_id: Session identifier
            stage: Current processing stage
            progress: Progress percentage (0-100)
            message: Progress message
            timestamp: Event timestamp (defaults to now)
        """
        self.session_id = session_id
        self.stage = stage
        self.progress = progress
        self.message = message
        self.timestamp = timestamp or datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert progress event to dictionary."""
        return {
            'session_id': self.session_id,
            'stage': self.stage,
            'progress': self.progress,
            'message': self.message,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProgressEvent':
        """Create progress event from dictionary."""
        return cls(
            session_id=data['session_id'],
            stage=data['stage'],
            progress=data['progress'],
            message=data['message'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


class SessionManager:
    """
    Manages user sessions and progress tracking using Redis.
    
    Stores session data including:
    - Session status
    - Language preference
    - Progress events
    - Processing results
    """
    
    def __init__(
        self,
        redis_host: str = 'localhost',
        redis_port: int = 6379,
        redis_db: int = 0,
        session_ttl: int = 3600  # 1 hour default
    ):
        """
        Initialize the session manager.
        
        Args:
            redis_host: Redis server host
            redis_port: Redis server port
            redis_db: Redis database number
            session_ttl: Session time-to-live in seconds
        """
        self.redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=redis_db,
            decode_responses=True
        )
        self.session_ttl = session_ttl
    
    def create_session(
        self,
        session_id: Optional[str] = None,
        language: str = 'en',
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new session.
        
        Args:
            session_id: Optional session ID (generates UUID if not provided)
            language: Preferred language for the session
            metadata: Optional metadata to store with session
            
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        session_data = {
            'session_id': session_id,
            'status': SessionStatus.PENDING.value,
            'language': language,
            'created_at': datetime.utcnow().isoformat(),
            'metadata': json.dumps(metadata or {})
        }
        
        # Store session data
        session_key = self._get_session_key(session_id)
        self.redis_client.hset(session_key, mapping=session_data)
        self.redis_client.expire(session_key, self.session_ttl)
        
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session data.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session data dictionary or None if not found
        """
        session_key = self._get_session_key(session_id)
        session_data = self.redis_client.hgetall(session_key)
        
        if not session_data:
            return None
        
        # Parse metadata
        if 'metadata' in session_data:
            session_data['metadata'] = json.loads(session_data['metadata'])
        
        return session_data
    
    def update_session_status(
        self,
        session_id: str,
        status: SessionStatus
    ) -> None:
        """
        Update session status.
        
        Args:
            session_id: Session identifier
            status: New status
        """
        session_key = self._get_session_key(session_id)
        self.redis_client.hset(session_key, 'status', status.value)
        self.redis_client.expire(session_key, self.session_ttl)
    
    def set_language_preference(
        self,
        session_id: str,
        language: str
    ) -> None:
        """
        Set language preference for a session.
        
        Args:
            session_id: Session identifier
            language: Language code (ISO 639-1)
        """
        session_key = self._get_session_key(session_id)
        self.redis_client.hset(session_key, 'language', language)
        self.redis_client.expire(session_key, self.session_ttl)
    
    def get_language_preference(self, session_id: str) -> Optional[str]:
        """
        Get language preference for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Language code or None if session not found
        """
        session_key = self._get_session_key(session_id)
        return self.redis_client.hget(session_key, 'language')
    
    def add_progress_event(self, event: ProgressEvent) -> None:
        """
        Add a progress event to the session.
        
        Args:
            event: Progress event to add
        """
        progress_key = self._get_progress_key(event.session_id)
        event_data = json.dumps(event.to_dict())
        
        # Add to list of progress events
        self.redis_client.rpush(progress_key, event_data)
        self.redis_client.expire(progress_key, self.session_ttl)
        
        # Update session with latest progress
        session_key = self._get_session_key(event.session_id)
        self.redis_client.hset(session_key, 'progress', event.progress)
        self.redis_client.hset(session_key, 'current_stage', event.stage)
        self.redis_client.expire(session_key, self.session_ttl)
    
    def get_progress_events(self, session_id: str) -> List[ProgressEvent]:
        """
        Get all progress events for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of progress events
        """
        progress_key = self._get_progress_key(session_id)
        events_data = self.redis_client.lrange(progress_key, 0, -1)
        
        events = []
        for event_data in events_data:
            event_dict = json.loads(event_data)
            events.append(ProgressEvent.from_dict(event_dict))
        
        return events
    
    def get_latest_progress(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the latest progress information for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Dictionary with progress info or None if not found
        """
        session_key = self._get_session_key(session_id)
        progress = self.redis_client.hget(session_key, 'progress')
        stage = self.redis_client.hget(session_key, 'current_stage')
        status = self.redis_client.hget(session_key, 'status')
        
        if progress is None:
            return None
        
        return {
            'progress': int(progress) if progress else 0,
            'stage': stage or 'pending',
            'status': status or SessionStatus.PENDING.value
        }
    
    def store_result(
        self,
        session_id: str,
        result_data: Dict[str, Any]
    ) -> None:
        """
        Store processing result for a session.
        
        Args:
            session_id: Session identifier
            result_data: Result data to store
        """
        result_key = self._get_result_key(session_id)
        self.redis_client.set(
            result_key,
            json.dumps(result_data),
            ex=self.session_ttl
        )
    
    def get_result(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get processing result for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Result data or None if not found
        """
        result_key = self._get_result_key(session_id)
        result_data = self.redis_client.get(result_key)
        
        if result_data:
            return json.loads(result_data)
        return None
    
    def delete_session(self, session_id: str) -> None:
        """
        Delete a session and all associated data.
        
        Args:
            session_id: Session identifier
        """
        session_key = self._get_session_key(session_id)
        progress_key = self._get_progress_key(session_id)
        result_key = self._get_result_key(session_id)
        
        self.redis_client.delete(session_key, progress_key, result_key)
    
    def _get_session_key(self, session_id: str) -> str:
        """Get Redis key for session data."""
        return f"session:{session_id}"
    
    def _get_progress_key(self, session_id: str) -> str:
        """Get Redis key for progress events."""
        return f"progress:{session_id}"
    
    def _get_result_key(self, session_id: str) -> str:
        """Get Redis key for result data."""
        return f"result:{session_id}"
    
    def _get_answers_key(self, session_id: str) -> str:
        """Get Redis key for answers list."""
        return f"answers:{session_id}"
    
    def store_answer(
        self,
        session_id: str,
        question_index: int,
        question_text: str,
        answer_text: str,
        diagrams_count: int = 0
    ) -> None:
        """
        Store an individual answer for real-time preview.
        
        Args:
            session_id: Session identifier
            question_index: Index of the question (0-based)
            question_text: The question text
            answer_text: The generated answer text
            diagrams_count: Number of diagrams for this answer
        """
        answers_key = self._get_answers_key(session_id)
        answer_data = {
            'index': question_index,
            'question': question_text,
            'answer': answer_text,
            'diagrams_count': diagrams_count,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Store as list item
        self.redis_client.rpush(answers_key, json.dumps(answer_data))
        self.redis_client.expire(answers_key, self.session_ttl)
    
    def get_answers(self, session_id: str) -> List[Dict[str, Any]]:
        """
        Get all stored answers for a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            List of answer dictionaries
        """
        answers_key = self._get_answers_key(session_id)
        answers_data = self.redis_client.lrange(answers_key, 0, -1)
        
        answers = []
        for answer_data in answers_data:
            answers.append(json.loads(answer_data))
        
        return answers
    
    def update_answer(
        self,
        session_id: str,
        question_index: int,
        new_answer_text: str
    ) -> None:
        """
        Update a specific answer.
        
        Args:
            session_id: Session identifier
            question_index: Index of the question to update
            new_answer_text: New answer text
        """
        answers_key = self._get_answers_key(session_id)
        answers_data = self.redis_client.lrange(answers_key, 0, -1)
        
        # Find and update the answer
        for i, answer_data in enumerate(answers_data):
            answer = json.loads(answer_data)
            if answer['index'] == question_index:
                answer['answer'] = new_answer_text
                answer['timestamp'] = datetime.utcnow().isoformat()
                # Replace in Redis list
                self.redis_client.lset(answers_key, i, json.dumps(answer))
                break
