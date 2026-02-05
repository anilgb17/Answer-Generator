"""Custom exception classes for the Question Answer Generator system."""
from typing import Optional, Dict, Any


class QuestionAnswerError(Exception):
    """
    Base exception for all system errors.
    
    Provides structured error information including context and guidance.
    """
    
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        guidance: Optional[str] = None
    ):
        """
        Initialize error with message, context, and guidance.
        
        Args:
            message: Error message describing what went wrong
            context: Additional context (question_id, file_info, language, etc.)
            guidance: Actionable guidance for resolving the error
        """
        self.message = message
        self.context = context or {}
        self.guidance = guidance
        
        # Build full error message
        full_message = message
        if context:
            context_str = ", ".join(f"{k}={v}" for k, v in context.items())
            full_message += f" [Context: {context_str}]"
        if guidance:
            full_message += f" [Guidance: {guidance}]"
        
        super().__init__(full_message)


class ValidationError(QuestionAnswerError):
    """Raised when file validation fails."""
    
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        guidance: Optional[str] = None
    ):
        """Initialize validation error with specific guidance."""
        if guidance is None:
            guidance = "Please check the file format and size requirements."
        super().__init__(message, context, guidance)


class UnsupportedFormatError(ValidationError):
    """Raised when input format is not supported."""
    
    def __init__(
        self,
        format: str,
        supported_formats: list,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize unsupported format error."""
        message = f"Unsupported format: {format}"
        context = context or {}
        context['format'] = format
        guidance = f"Supported formats: {', '.join(supported_formats)}"
        super().__init__(message, context, guidance)


class FileSizeError(ValidationError):
    """Raised when file size exceeds limits."""
    
    def __init__(
        self,
        file_size: int,
        max_size: int,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize file size error."""
        message = f"File size ({file_size} bytes) exceeds maximum ({max_size} bytes)"
        context = context or {}
        context['file_size'] = file_size
        context['max_size'] = max_size
        guidance = f"Please reduce file size to under {max_size} bytes"
        super().__init__(message, context, guidance)


class ParseError(QuestionAnswerError):
    """Raised when parsing fails."""
    
    def __init__(
        self,
        message: str,
        parse_issue: str,
        context: Optional[Dict[str, Any]] = None,
        guidance: Optional[str] = None
    ):
        """
        Initialize parse error with specific parsing issue.
        
        Args:
            message: Error message
            parse_issue: Specific parsing issue (e.g., "Invalid PDF structure", "OCR failed")
            context: Additional context
            guidance: Actionable guidance
        """
        context = context or {}
        context['parse_issue'] = parse_issue
        
        if guidance is None:
            guidance = "Please ensure the file is not corrupted and is in the correct format."
        
        super().__init__(message, context, guidance)


class AnswerGenerationError(QuestionAnswerError):
    """Raised when answer generation fails."""
    
    def __init__(
        self,
        message: str,
        question_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        guidance: Optional[str] = None
    ):
        """
        Initialize answer generation error with question context.
        
        Args:
            message: Error message
            question_id: ID of the question that failed
            context: Additional context
            guidance: Actionable guidance
        """
        context = context or {}
        if question_id:
            context['question_id'] = question_id
        
        if guidance is None:
            guidance = "Please try again or contact support if the issue persists."
        
        super().__init__(message, context, guidance)


class KnowledgeBaseError(QuestionAnswerError):
    """Raised when knowledge base operations fail."""
    
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        guidance: Optional[str] = None
    ):
        """Initialize knowledge base error."""
        if guidance is None:
            guidance = "The system will continue with general knowledge. Check knowledge base connectivity."
        super().__init__(message, context, guidance)


class LanguageNotSupportedError(QuestionAnswerError):
    """Raised when requested language is not supported."""
    
    def __init__(
        self,
        language: str,
        supported_languages: Optional[list] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        """Initialize language not supported error."""
        message = f"Language '{language}' is not supported"
        context = context or {}
        context['language'] = language
        
        guidance = "Please select a supported language"
        if supported_languages:
            guidance += f": {', '.join(supported_languages)}"
        
        super().__init__(message, context, guidance)


class DiagramGenerationError(QuestionAnswerError):
    """Raised when diagram generation fails."""
    
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        guidance: Optional[str] = None
    ):
        """Initialize diagram generation error."""
        if guidance is None:
            guidance = "The answer will be generated without diagrams."
        super().__init__(message, context, guidance)


class PDFGenerationError(QuestionAnswerError):
    """Raised when PDF generation fails."""
    
    def __init__(
        self,
        message: str,
        context: Optional[Dict[str, Any]] = None,
        guidance: Optional[str] = None,
        partial_results: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize PDF generation error.
        
        Args:
            message: Error message
            context: Additional context
            guidance: Actionable guidance
            partial_results: Successfully generated content that can be preserved
        """
        self.partial_results = partial_results or {}
        
        if guidance is None:
            if partial_results:
                guidance = "Partial results are available. You can retry PDF generation."
            else:
                guidance = "Please check the input data and try again."
        
        super().__init__(message, context, guidance)
