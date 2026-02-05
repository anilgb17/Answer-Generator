"""Celery tasks for asynchronous question paper processing."""
import os
import traceback
from pathlib import Path
from typing import Dict, Any, List

from src.celery_app import celery_app
from src.session_manager import SessionManager, SessionStatus, ProgressEvent
from src.input_parser import InputParserFactory
from src.answer_generator import AnswerGenerator
from src.diagram_generator import DiagramGenerator
from src.pdf_generator import PDFGenerator
from src.knowledge_base import EducationalKnowledgeBase
from src.language_service import LanguageService
from src.storage import PDFStorage
from src.models import Question, Answer, Diagram
from src.exceptions import (
    QuestionAnswerError, ParseError, AnswerGenerationError,
    DiagramGenerationError, PDFGenerationError
)
from config.settings import settings
from config.logging_config import logger


@celery_app.task(bind=True, name='src.tasks.process_question_paper')
def process_question_paper(
    self,
    session_id: str,
    file_path: str,
    file_format: str,
    target_language: str = 'en',
    provider: str = 'gemini',
    user_id: int = None
) -> Dict[str, Any]:
    """
    Process a question paper: parse → generate answers → generate diagrams → create PDF.
    
    This is the main orchestration task that coordinates all processing steps
    and provides progress updates throughout the pipeline.
    
    Args:
        session_id: Session identifier for tracking progress
        file_path: Path to the uploaded file
        file_format: Format of the file ('text', 'pdf', 'image')
        target_language: Target language for answers (ISO 639-1 code)
        provider: AI provider to use ('gemini', 'perplexity', 'openai', 'anthropic')
        user_id: Optional user ID for using user's API keys
        
    Returns:
        Dictionary with processing results including:
        - success: bool
        - pdf_identifier: str (if successful)
        - error: str (if failed)
        - questions_processed: int
        
    Raises:
        Exception: Any unhandled exceptions during processing
    """
    # Initialize services
    session_manager = SessionManager(
        redis_host=settings.redis_host,
        redis_port=settings.redis_port,
        redis_db=settings.redis_db
    )
    
    try:
        logger.info(f"Starting processing for session {session_id}")
        
        # Update session status to processing
        session_manager.update_session_status(session_id, SessionStatus.PROCESSING)
        
        # Emit initial progress
        _emit_progress(session_manager, session_id, 'initializing', 0, 'Initializing processing')
        
        # Step 1: Parse input file
        logger.info(f"Step 1: Parsing input file for session {session_id}")
        _emit_progress(session_manager, session_id, 'parsing', 5, 'Parsing input file')
        
        questions = _parse_input_file(file_path, file_format)
        
        if not questions:
            raise ParseError("No questions found in the input file")
        
        logger.info(f"Parsed {len(questions)} questions from input file")
        _emit_progress(
            session_manager, session_id, 'parsing_complete', 15,
            f'Successfully parsed {len(questions)} questions'
        )
        
        # Step 2: Initialize services for answer generation
        logger.info(f"Step 2: Initializing services for session {session_id}")
        _emit_progress(session_manager, session_id, 'initializing_services', 20, 'Initializing services')
        
        knowledge_base = EducationalKnowledgeBase(persist_directory=settings.vector_db_path)
        language_service = LanguageService()
        
        # Create progress callback for answer generator
        def answer_progress_callback(stage: str, progress: int, message: str):
            # Map answer generation progress to overall progress (20-60%)
            overall_progress = 20 + int((progress / 100) * 40)
            _emit_progress(session_manager, session_id, stage, overall_progress, message)
        
        # Get user API keys if user_id is provided
        user_api_keys = {}
        if user_id:
            from src.database import SessionLocal
            from src.auth import get_user_api_key
            db = SessionLocal()
            try:
                for prov in ['openai', 'gemini', 'anthropic', 'perplexity']:
                    key = get_user_api_key(db, user_id, prov)
                    if key:
                        user_api_keys[prov] = key
                logger.info(f"Loaded {len(user_api_keys)} API keys for user {user_id}")
            finally:
                db.close()
        
        # Determine LLM provider and API key
        llm_provider = provider
        api_key_override = None
        
        if user_api_keys:
            # Use user's API key if available
            if provider in user_api_keys:
                api_key_override = user_api_keys[provider]
                logger.info(f"Using user's {provider} API key")
            else:
                # Fallback to any available user key
                for prov in ['gemini', 'perplexity', 'openai', 'anthropic']:
                    if prov in user_api_keys:
                        llm_provider = prov
                        api_key_override = user_api_keys[prov]
                        logger.info(f"Falling back to user's {prov} API key")
                        break
        
        # If no user keys, use system keys
        if not api_key_override:
            if provider == 'gemini' and settings.gemini_api_key:
                api_key_override = settings.gemini_api_key
            elif provider == 'perplexity' and settings.perplexity_api_key:
                api_key_override = settings.perplexity_api_key
            elif provider == 'openai' and settings.openai_api_key:
                api_key_override = settings.openai_api_key
            elif provider == 'anthropic' and settings.anthropic_api_key:
                api_key_override = settings.anthropic_api_key
            else:
                # Fallback to any available system key
                if settings.gemini_api_key:
                    llm_provider = "gemini"
                    api_key_override = settings.gemini_api_key
                elif settings.perplexity_api_key:
                    llm_provider = "perplexity"
                    api_key_override = settings.perplexity_api_key
                elif settings.openai_api_key:
                    llm_provider = "openai"
                    api_key_override = settings.openai_api_key
        
        answer_generator = AnswerGenerator(
            knowledge_base=knowledge_base,
            language_service=language_service,
            llm_provider=llm_provider,
            progress_callback=answer_progress_callback,
            api_key_override=api_key_override
        )
        
        diagram_generator = DiagramGenerator(language_service=language_service)
        pdf_generator = PDFGenerator(language_service=language_service)
        pdf_storage = PDFStorage(retention_days=settings.pdf_retention_days)
        
        # Step 3: Generate answers for all questions
        logger.info(f"Step 3: Generating answers for {len(questions)} questions")
        _emit_progress(
            session_manager, session_id, 'generating_answers', 25,
            f'Generating answers for {len(questions)} questions'
        )
        
        answers = []
        for i, question in enumerate(questions, 1):
            try:
                logger.info(f"Generating answer for question {i}/{len(questions)}")
                
                # Calculate progress for this question (25-60% range)
                question_progress = 25 + int((i / len(questions)) * 35)
                _emit_progress(
                    session_manager, session_id, 'generating_answer',
                    question_progress,
                    f'Generating answer {i}/{len(questions)}'
                )
                
                answer = answer_generator.generate_answer(question, target_language)
                answers.append(answer)
                
                # Store answer for real-time preview
                session_manager.store_answer(
                    session_id=session_id,
                    question_index=i - 1,  # 0-based index
                    question_text=question.text,
                    answer_text=answer.content,
                    diagrams_count=len(answer.visual_elements)
                )
                
                logger.info(f"Successfully generated answer for question {i}/{len(questions)}")
                
            except Exception as e:
                logger.error(f"Error generating answer for question {i}: {str(e)}", exc_info=True)
                # Create a fallback answer with error information
                from src.models import Answer
                error_answer = Answer(
                    question_id=question.id,
                    content=f"Error generating answer: {str(e)}",
                    language=target_language,
                    visual_elements=[],
                    references=[],
                    knowledge_sources=[]
                )
                answers.append(error_answer)
                
                # Store error answer for preview
                session_manager.store_answer(
                    session_id=session_id,
                    question_index=i - 1,
                    question_text=question.text,
                    answer_text=error_answer.content,
                    diagrams_count=0
                )
        
        logger.info(f"Generated {len(answers)} answers")
        _emit_progress(
            session_manager, session_id, 'answers_complete', 60,
            f'Successfully generated {len(answers)} answers'
        )
        
        # Step 4: Generate diagrams for visual elements
        logger.info(f"Step 4: Generating diagrams for session {session_id}")
        _emit_progress(session_manager, session_id, 'generating_diagrams', 65, 'Generating diagrams')
        
        diagrams_by_answer = {}
        total_visual_elements = sum(len(answer.visual_elements) for answer in answers)
        
        if total_visual_elements > 0:
            processed_elements = 0
            for answer in answers:
                answer_diagrams = []
                for visual_spec in answer.visual_elements:
                    try:
                        diagram = diagram_generator.generate_diagram(visual_spec)
                        answer_diagrams.append(diagram)
                        processed_elements += 1
                        
                        # Update progress (65-75% range)
                        diagram_progress = 65 + int((processed_elements / total_visual_elements) * 10)
                        _emit_progress(
                            session_manager, session_id, 'generating_diagram',
                            diagram_progress,
                            f'Generated diagram {processed_elements}/{total_visual_elements}'
                        )
                        
                    except DiagramGenerationError as e:
                        logger.warning(f"Failed to generate diagram: {str(e)}")
                        # Continue without this diagram
                        continue
                
                if answer_diagrams:
                    diagrams_by_answer[answer.question_id] = answer_diagrams
            
            logger.info(f"Generated {processed_elements} diagrams")
        
        _emit_progress(
            session_manager, session_id, 'diagrams_complete', 75,
            'Diagram generation complete'
        )
        
        # Step 5: Generate PDF document
        logger.info(f"Step 5: Generating PDF for session {session_id}")
        _emit_progress(session_manager, session_id, 'generating_pdf', 80, 'Generating PDF document')
        
        pdf_document = pdf_generator.generate_pdf(
            questions=questions,
            answers=answers,
            diagrams=diagrams_by_answer,
            target_language=target_language
        )
        
        logger.info(f"Generated PDF with {pdf_document.page_count} pages")
        _emit_progress(session_manager, session_id, 'pdf_complete', 90, 'PDF generation complete')
        
        # Step 6: Store PDF
        logger.info(f"Step 6: Storing PDF for session {session_id}")
        _emit_progress(session_manager, session_id, 'storing_pdf', 95, 'Storing PDF')
        
        pdf_identifier = pdf_storage.save_pdf(pdf_document)
        
        logger.info(f"Stored PDF with identifier: {pdf_identifier}")
        
        # Step 7: Store result and update session
        result_data = {
            'success': True,
            'pdf_identifier': pdf_identifier,
            'filename': pdf_document.filename,
            'page_count': pdf_document.page_count,
            'questions_processed': len(questions),
            'answers_generated': len(answers),
            'diagrams_generated': sum(len(d) for d in diagrams_by_answer.values())
        }
        
        session_manager.store_result(session_id, result_data)
        session_manager.update_session_status(session_id, SessionStatus.COMPLETE)
        
        _emit_progress(session_manager, session_id, 'complete', 100, 'Processing complete')
        
        logger.info(f"Successfully completed processing for session {session_id}")
        
        return result_data
        
    except Exception as e:
        # Handle any errors
        logger.error(f"Error processing session {session_id}: {str(e)}", exc_info=True)
        
        error_message = str(e)
        error_type = type(e).__name__
        
        # Store error result
        error_data = {
            'success': False,
            'error': error_message,
            'error_type': error_type,
            'traceback': traceback.format_exc()
        }
        
        session_manager.store_result(session_id, error_data)
        session_manager.update_session_status(session_id, SessionStatus.ERROR)
        
        _emit_progress(
            session_manager, session_id, 'error', 0,
            f'Processing failed: {error_message}'
        )
        
        # Re-raise to mark task as failed
        raise
    
    finally:
        # Cleanup: Remove uploaded file
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up uploaded file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup uploaded file {file_path}: {str(e)}")


def _parse_input_file(file_path: str, file_format: str) -> List[Question]:
    """
    Parse input file and extract questions.
    
    Args:
        file_path: Path to the input file
        file_format: Format of the file
        
    Returns:
        List of Question objects
        
    Raises:
        ParseError: If parsing fails
    """
    try:
        # Read file content
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Parse using appropriate parser
        questions = InputParserFactory.parse(file_content, file_format)
        
        return questions
        
    except Exception as e:
        if isinstance(e, ParseError):
            raise
        raise ParseError(f"Failed to parse input file: {str(e)}")


def _emit_progress(
    session_manager: SessionManager,
    session_id: str,
    stage: str,
    progress: int,
    message: str
) -> None:
    """
    Emit progress event to session manager.
    
    Args:
        session_manager: Session manager instance
        session_id: Session identifier
        stage: Current processing stage
        progress: Progress percentage (0-100)
        message: Progress message
    """
    try:
        event = ProgressEvent(
            session_id=session_id,
            stage=stage,
            progress=progress,
            message=message
        )
        session_manager.add_progress_event(event)
    except Exception as e:
        logger.warning(f"Failed to emit progress event: {str(e)}")
