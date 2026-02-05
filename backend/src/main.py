"""Main FastAPI application for Question Answer Generator."""
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from config.logging_config import logger
from config.settings import settings
from src.session_manager import SessionManager, SessionStatus
from src.storage import PDFStorage
from src.language_service import LanguageService
from src.exceptions import ValidationError, FileSizeError, UnsupportedFormatError
from src.security import SecurityValidator

# Create rate limiter
limiter = Limiter(key_func=get_remote_address)

# Create FastAPI app
app = FastAPI(
    title="Question Answer Generator API",
    description="API for generating comprehensive answers with visual elements",
    version="1.0.0"
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Security Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add Content Security Policy
        if settings.csp_enabled:
            response.headers["Content-Security-Policy"] = settings.csp_directives
        
        # Add other security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce HTTPS in production."""
    
    async def dispatch(self, request: Request, call_next):
        if settings.enforce_https and request.url.scheme != "https":
            # Redirect to HTTPS
            url = request.url.replace(scheme="https")
            return Response(
                status_code=301,
                headers={"Location": str(url)}
            )
        return await call_next(request)


# Add security middlewares
if settings.enforce_https:
    app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://10.83.89.67:3000",
        "http://172.24.48.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
session_manager = SessionManager(
    redis_host=settings.redis_host,
    redis_port=settings.redis_port,
    redis_db=settings.redis_db
)
pdf_storage = PDFStorage(retention_days=settings.pdf_retention_days)
language_service = LanguageService()

# Include authentication routes
from src.auth_routes import router as auth_router
from src.admin_routes import router as admin_router

app.include_router(auth_router)
app.include_router(admin_router)

# Supported file formats
SUPPORTED_FORMATS = {'.txt', '.pdf', '.png', '.jpg', '.jpeg'}


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup."""
    from pathlib import Path
    from src.database import init_db
    
    # Create necessary directories
    directories = [
        settings.upload_dir,
        settings.output_dir,
        Path(settings.log_file).parent,
        settings.vector_db_path,
        settings.data_dir,  # For database
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
    
    logger.info("Starting Question Answer Generator API")
    logger.info(f"API running on {settings.api_host}:{settings.api_port}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down Question Answer Generator API")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Question Answer Generator API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.post("/api/upload")
@limiter.limit("10/minute")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    language: str = Form(default="en"),
    provider: str = Form(default="gemini"),
    user_id: Optional[int] = Form(default=None)
):
    """
    Upload a question paper file for processing.
    
    Args:
        file: The uploaded file (text, PDF, or image)
        language: Target language for answers (ISO 639-1 code)
        provider: AI provider to use ('gemini', 'perplexity', or 'openai')
        user_id: Optional user ID for authenticated users
        
    Returns:
        JSON response with session_id and status
        
    Raises:
        HTTPException: If validation fails
    """
    try:
        logger.info(f"Received upload request: filename={file.filename}, language={language}, provider={provider}")
        
        # Sanitize filename
        sanitized_filename = SecurityValidator.sanitize_filename(file.filename)
        
        # Validate language code format
        SecurityValidator.validate_language_code(language)
        
        # Validate provider
        valid_providers = ['gemini', 'perplexity', 'openai']
        if provider not in valid_providers:
            raise ValidationError(
                f"Invalid provider '{provider}'. Supported providers: {', '.join(valid_providers)}"
            )
        
        # Validate language
        if not language_service.is_supported(language):
            raise ValidationError(
                f"Language '{language}' is not supported. "
                f"Supported languages: {', '.join([lang.code for lang in language_service.get_supported_languages()])}"
            )
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        SecurityValidator.validate_file_size(content, int(settings.max_file_size_mb * 1024 * 1024))
        
        # Validate file type using magic numbers
        SecurityValidator.validate_file_type(content, sanitized_filename)
        
        # Get file extension
        file_ext = Path(sanitized_filename).suffix.lower()
        if file_ext not in SUPPORTED_FORMATS:
            raise UnsupportedFormatError(
                format=file_ext,
                supported_formats=list(SUPPORTED_FORMATS)
            )
        
        # Create session with secure token
        session_id = SecurityValidator.generate_secure_token(16)  # 32 character hex string
        session_manager.create_session(
            session_id=session_id,
            language=language,
            metadata={
                'filename': sanitized_filename,
                'file_size': len(content),
                'file_format': file_ext,
                'user_id': user_id,
                'provider': provider
            }
        )
        
        # Save uploaded file
        upload_path = Path(settings.upload_dir) / f"{session_id}{file_ext}"
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        with open(upload_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"File uploaded successfully: session_id={session_id}")
        
        # Trigger Celery task for asynchronous processing
        from src.tasks import process_question_paper
        
        # Determine format string for parser
        format_map = {
            '.txt': 'text',
            '.pdf': 'pdf',
            '.png': 'image',
            '.jpg': 'image',
            '.jpeg': 'image'
        }
        parser_format = format_map.get(file_ext, 'text')
        
        # Submit task to Celery
        task = process_question_paper.apply_async(
            args=[session_id, str(upload_path), parser_format, language, provider, user_id],
            task_id=session_id  # Use session_id as task_id for easy tracking
        )
        
        logger.info(f"Submitted processing task for session {session_id}")
        
        return JSONResponse(
            status_code=200,
            content={
                "session_id": session_id,
                "status": "pending",
                "message": "File uploaded successfully. Processing will begin shortly."
            }
        )
        
    except (ValidationError, UnsupportedFormatError, FileSizeError) as e:
        logger.warning(f"Validation error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error during file upload")


@app.get("/api/languages")
@limiter.limit("30/minute")
async def get_languages(request: Request):
    """
    Get list of supported languages.
    
    Returns:
        JSON response with list of supported languages
    """
    try:
        languages = language_service.get_supported_languages()
        
        return JSONResponse(
            status_code=200,
            content={
                "languages": [
                    {
                        "code": lang.code,
                        "name": lang.name,
                        "native_name": lang.native_name
                    }
                    for lang in languages
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error fetching languages: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/status/{session_id}")
@limiter.limit("60/minute")
async def get_status(request: Request, session_id: str):
    """
    Get processing status for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        JSON response with status, progress, message, and answers
        
    Raises:
        HTTPException: If session not found
    """
    try:
        logger.info(f"Status check for session: {session_id}")
        
        # Validate session ID format
        try:
            SecurityValidator.validate_session_id(session_id)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get session data
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get latest progress
        progress_info = session_manager.get_latest_progress(session_id)
        
        status = session.get('status', 'pending')
        progress = progress_info.get('progress', 0) if progress_info else 0
        stage = progress_info.get('stage', 'pending') if progress_info else 'pending'
        
        # Generate appropriate message
        if status == SessionStatus.COMPLETE.value:
            message = "Processing complete. PDF is ready for download."
        elif status == SessionStatus.ERROR.value:
            message = "An error occurred during processing. Please try again."
        elif status == SessionStatus.PROCESSING.value:
            message = f"Processing in progress: {stage}"
        else:
            message = "Waiting to start processing"
        
        # Get generated answers for real-time preview
        answers = session_manager.get_answers(session_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "status": status,
                "progress": progress,
                "message": message,
                "answers": answers
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/regenerate/{session_id}/{question_index}")
@limiter.limit("20/minute")
async def regenerate_answer(
    request: Request,
    session_id: str,
    question_index: int,
    change_request: str = Form(...)
):
    """
    Regenerate a specific answer with modifications.
    
    Args:
        session_id: Session identifier
        question_index: Index of the question to regenerate (0-based)
        change_request: User's request for changes (e.g., "make it simpler")
        
    Returns:
        JSON response with the new answer
        
    Raises:
        HTTPException: If session not found or regeneration fails
    """
    try:
        logger.info(f"Regenerate request for session {session_id}, question {question_index}")
        
        # Validate session ID format
        try:
            SecurityValidator.validate_session_id(session_id)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get session data
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get current answers
        answers = session_manager.get_answers(session_id)
        if question_index >= len(answers):
            raise HTTPException(status_code=400, detail="Invalid question index")
        
        current_answer = answers[question_index]
        
        # Initialize services
        from src.knowledge_base import EducationalKnowledgeBase
        from src.answer_generator import AnswerGenerator
        from src.models import Question
        
        knowledge_base = EducationalKnowledgeBase(persist_directory=settings.vector_db_path)
        
        # Use Gemini or Perplexity (both are free alternatives)
        # Priority: Gemini > Perplexity > OpenAI
        llm_provider = "gemini"
        if not settings.gemini_api_key and settings.perplexity_api_key:
            llm_provider = "perplexity"
        elif not settings.gemini_api_key and not settings.perplexity_api_key and settings.openai_api_key:
            llm_provider = "openai"
        
        answer_generator = AnswerGenerator(
            knowledge_base=knowledge_base,
            language_service=language_service,
            llm_provider=llm_provider
        )
        
        # Create question object
        question = Question(
            id=f"q_{question_index}",
            text=current_answer['question'],
            marks=0,
            difficulty="medium"
        )
        
        # Get language from session
        target_language = session.get('language', 'en')
        
        # Generate new answer with modification request
        logger.info(f"Regenerating answer with request: {change_request}")
        
        # Modify the question text to include the change request
        modified_question = Question(
            id=question.id,
            text=f"{question.text}\n\n[Modification request: {change_request}]",
            marks=question.marks,
            difficulty=question.difficulty
        )
        
        new_answer = answer_generator.generate_answer(modified_question, target_language)
        
        # Update stored answer
        session_manager.update_answer(
            session_id=session_id,
            question_index=question_index,
            new_answer_text=new_answer.content
        )
        
        logger.info(f"Successfully regenerated answer for question {question_index}")
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "question_index": question_index,
                "answer": new_answer.content,
                "message": "Answer regenerated successfully"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error regenerating answer: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to regenerate answer: {str(e)}")


@app.get("/api/download/{session_id}")
@limiter.limit("20/minute")
async def download_pdf(request: Request, session_id: str):
    """
    Download the generated PDF for a session.
    
    Args:
        session_id: Session identifier
        
    Returns:
        PDF file response
        
    Raises:
        HTTPException: If session not found or PDF not ready
    """
    try:
        logger.info(f"Download request for session: {session_id}")
        
        # Validate session ID format
        try:
            SecurityValidator.validate_session_id(session_id)
        except ValidationError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        # Get session data
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if processing is complete
        status = session.get('status')
        if status != SessionStatus.COMPLETE.value:
            raise HTTPException(
                status_code=400,
                detail=f"PDF not ready. Current status: {status}"
            )
        
        # Get result data
        result = session_manager.get_result(session_id)
        if not result or 'pdf_identifier' not in result:
            raise HTTPException(status_code=404, detail="PDF not found")
        
        # Retrieve PDF from storage
        pdf_identifier = result['pdf_identifier']
        pdf_document = pdf_storage.retrieve_pdf(pdf_identifier)
        
        if not pdf_document:
            raise HTTPException(status_code=404, detail="PDF file not found in storage")
        
        # Save to temporary file for download
        temp_path = Path(settings.output_dir) / f"{session_id}_temp.pdf"
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        with open(temp_path, 'wb') as f:
            f.write(pdf_document.content)
        
        logger.info(f"PDF download successful: session_id={session_id}")
        
        return FileResponse(
            path=temp_path,
            media_type="application/pdf",
            filename=pdf_document.filename,
            headers={
                "Content-Disposition": f"attachment; filename={pdf_document.filename}"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading PDF: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
