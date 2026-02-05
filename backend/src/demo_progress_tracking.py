"""Demo script showing progress tracking and session management integration."""
import time
from src.session_manager import SessionManager, ProgressEvent, SessionStatus
from src.models import Question
from src.answer_generator import AnswerGenerator
from src.knowledge_base import EducationalKnowledgeBase
from src.language_service import LanguageService


def demo_progress_tracking():
    """
    Demonstrate progress tracking and session management.
    
    This example shows how to:
    1. Create a session with language preference
    2. Track progress through multiple stages
    3. Use progress callbacks in answer generation
    4. Store and retrieve session data
    """
    print("=== Progress Tracking and Session Management Demo ===\n")
    
    # Initialize session manager
    try:
        session_manager = SessionManager(
            redis_host='localhost',
            redis_port=6379,
            redis_db=0,
            session_ttl=3600
        )
        session_manager.redis_client.ping()
        print("✓ Connected to Redis")
    except Exception as e:
        print(f"✗ Redis not available: {e}")
        print("  Please start Redis with: docker compose up -d redis")
        return
    
    # Create a new session with language preference
    print("\n1. Creating session...")
    session_id = session_manager.create_session(
        language='es',  # Spanish
        metadata={'user': 'demo_user', 'source': 'demo'}
    )
    print(f"   Session ID: {session_id}")
    print(f"   Language: es (Spanish)")
    
    # Update session status
    session_manager.update_session_status(session_id, SessionStatus.PROCESSING)
    print(f"   Status: {SessionStatus.PROCESSING.value}")
    
    # Simulate processing with progress updates
    print("\n2. Simulating multi-stage processing...")
    stages = [
        ('parsing', 20, 'Parsing input document'),
        ('knowledge_search', 40, 'Searching knowledge base'),
        ('answer_generation', 60, 'Generating answers'),
        ('diagram_creation', 80, 'Creating diagrams'),
        ('pdf_generation', 100, 'Generating PDF')
    ]
    
    for stage, progress, message in stages:
        event = ProgressEvent(
            session_id=session_id,
            stage=stage,
            progress=progress,
            message=message
        )
        session_manager.add_progress_event(event)
        print(f"   [{progress:3d}%] {stage}: {message}")
        time.sleep(0.5)  # Simulate processing time
    
    # Get latest progress
    print("\n3. Retrieving progress information...")
    latest = session_manager.get_latest_progress(session_id)
    print(f"   Latest progress: {latest['progress']}%")
    print(f"   Current stage: {latest['stage']}")
    print(f"   Status: {latest['status']}")
    
    # Get all progress events
    all_events = session_manager.get_progress_events(session_id)
    print(f"   Total events: {len(all_events)}")
    
    # Test language preference persistence
    print("\n4. Testing language preference...")
    current_lang = session_manager.get_language_preference(session_id)
    print(f"   Current language: {current_lang}")
    
    # Change language preference
    session_manager.set_language_preference(session_id, 'fr')
    new_lang = session_manager.get_language_preference(session_id)
    print(f"   Updated language: {new_lang}")
    
    # Store result
    print("\n5. Storing processing result...")
    result_data = {
        'pdf_filename': 'answers_demo.pdf',
        'question_count': 5,
        'success': True,
        'language': new_lang
    }
    session_manager.store_result(session_id, result_data)
    print(f"   Result stored: {result_data}")
    
    # Retrieve result
    retrieved_result = session_manager.get_result(session_id)
    print(f"   Retrieved result: {retrieved_result}")
    
    # Update final status
    session_manager.update_session_status(session_id, SessionStatus.COMPLETE)
    print(f"\n6. Session complete!")
    
    # Get final session data
    session_data = session_manager.get_session(session_id)
    print(f"   Final session status: {session_data['status']}")
    print(f"   Final language: {session_data['language']}")
    
    print("\n=== Demo Complete ===")


def demo_answer_generator_with_progress():
    """
    Demonstrate answer generator with progress callbacks.
    
    This example shows how progress callbacks integrate with the answer generator.
    """
    print("\n=== Answer Generator Progress Tracking Demo ===\n")
    
    try:
        session_manager = SessionManager()
        session_manager.redis_client.ping()
    except Exception as e:
        print(f"✗ Redis not available: {e}")
        return
    
    # Create session
    session_id = session_manager.create_session(language='en')
    print(f"Session ID: {session_id}\n")
    
    # Define progress callback
    def progress_callback(stage: str, progress: int, message: str):
        """Callback to track answer generation progress."""
        event = ProgressEvent(
            session_id=session_id,
            stage=stage,
            progress=progress,
            message=message
        )
        session_manager.add_progress_event(event)
        print(f"[{progress:3d}%] {stage}: {message}")
    
    # Initialize components (would normally use real implementations)
    print("Note: This demo requires full system setup with LLM API keys.")
    print("Progress callback integration is demonstrated above.\n")
    
    # Show how to initialize answer generator with progress callback
    print("Example initialization:")
    print("  answer_generator = AnswerGenerator(")
    print("      knowledge_base=knowledge_base,")
    print("      language_service=language_service,")
    print("      progress_callback=progress_callback")
    print("  )")
    print("\nWhen generate_answer() is called, progress events will be emitted automatically.")


if __name__ == '__main__':
    demo_progress_tracking()
    print("\n" + "="*60 + "\n")
    demo_answer_generator_with_progress()
