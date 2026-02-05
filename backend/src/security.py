"""Security utilities for the Question Answer Generator."""
import secrets
import hashlib
import re
from typing import Optional, Set
from pathlib import Path

from src.exceptions import ValidationError


class SecurityValidator:
    """Security validation utilities."""
    
    # Magic numbers for file type validation
    MAGIC_NUMBERS = {
        'pdf': b'%PDF',
        'png': b'\x89PNG\r\n\x1a\n',
        'jpeg': b'\xff\xd8\xff',
        'jpg': b'\xff\xd8\xff',
    }
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS: Set[str] = {'.txt', '.pdf', '.png', '.jpg', '.jpeg'}
    
    # Maximum file size in bytes (50 MB)
    MAX_FILE_SIZE: int = 50 * 1024 * 1024
    
    @staticmethod
    def validate_file_type(content: bytes, filename: str) -> bool:
        """
        Validate file type using magic numbers.
        
        Args:
            content: File content bytes
            filename: Original filename
            
        Returns:
            True if file type is valid
            
        Raises:
            ValidationError: If file type is invalid
        """
        if not content:
            raise ValidationError("File content is empty")
        
        # Get file extension
        file_ext = Path(filename).suffix.lower()
        
        # Check if extension is allowed
        if file_ext not in SecurityValidator.ALLOWED_EXTENSIONS:
            raise ValidationError(
                f"File extension '{file_ext}' is not allowed. "
                f"Allowed extensions: {', '.join(SecurityValidator.ALLOWED_EXTENSIONS)}"
            )
        
        # For text files, just check extension
        if file_ext == '.txt':
            # Validate that content is text-like
            try:
                content.decode('utf-8')
                return True
            except UnicodeDecodeError:
                raise ValidationError("Text file contains invalid UTF-8 content")
        
        # For binary files, check magic numbers
        file_type = file_ext.lstrip('.')
        if file_type in SecurityValidator.MAGIC_NUMBERS:
            magic = SecurityValidator.MAGIC_NUMBERS[file_type]
            if not content.startswith(magic):
                raise ValidationError(
                    f"File content does not match expected format for {file_ext} file. "
                    f"The file may be corrupted or have an incorrect extension."
                )
        
        return True
    
    @staticmethod
    def validate_file_size(content: bytes, max_size: Optional[int] = None) -> bool:
        """
        Validate file size.
        
        Args:
            content: File content bytes
            max_size: Maximum allowed size in bytes (optional)
            
        Returns:
            True if file size is valid
            
        Raises:
            ValidationError: If file size exceeds limit
        """
        if max_size is None:
            max_size = SecurityValidator.MAX_FILE_SIZE
        
        file_size = len(content)
        if file_size > max_size:
            max_size_mb = max_size / (1024 * 1024)
            file_size_mb = file_size / (1024 * 1024)
            raise ValidationError(
                f"File size ({file_size_mb:.2f} MB) exceeds maximum allowed size ({max_size_mb:.2f} MB)"
            )
        
        return True
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename to prevent path traversal and other attacks.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove any path components
        filename = Path(filename).name
        
        # Remove or replace dangerous characters
        # Allow only alphanumeric, dots, hyphens, and underscores
        sanitized = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Prevent hidden files
        if sanitized.startswith('.'):
            sanitized = '_' + sanitized[1:]
        
        # Prevent empty filename
        if not sanitized or sanitized == '_':
            sanitized = 'unnamed_file'
        
        # Limit length
        if len(sanitized) > 255:
            # Keep extension
            name, ext = Path(sanitized).stem, Path(sanitized).suffix
            max_name_length = 255 - len(ext)
            sanitized = name[:max_name_length] + ext
        
        return sanitized
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 10000) -> str:
        """
        Sanitize text input to prevent injection attacks.
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
            
        Raises:
            ValidationError: If input is invalid
        """
        if not text:
            return ""
        
        # Limit length
        if len(text) > max_length:
            raise ValidationError(f"Input text exceeds maximum length of {max_length} characters")
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newlines, tabs, and carriage returns
        text = ''.join(char for char in text if char in '\n\r\t' or not char.isprintable() or ord(char) >= 32)
        
        return text.strip()
    
    @staticmethod
    def generate_secure_token(length: int = 32) -> str:
        """
        Generate a cryptographically secure random token.
        
        Args:
            length: Token length in bytes
            
        Returns:
            Hex-encoded secure token
        """
        return secrets.token_hex(length)
    
    @staticmethod
    def hash_session_id(session_id: str) -> str:
        """
        Hash session ID for secure storage.
        
        Args:
            session_id: Session identifier
            
        Returns:
            SHA-256 hash of session ID
        """
        return hashlib.sha256(session_id.encode()).hexdigest()
    
    @staticmethod
    def validate_language_code(language_code: str) -> bool:
        """
        Validate language code format.
        
        Args:
            language_code: ISO 639-1 language code
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If language code is invalid
        """
        if not language_code:
            raise ValidationError("Language code cannot be empty")
        
        # ISO 639-1 codes are exactly 2 lowercase letters
        if not re.match(r'^[a-z]{2}$', language_code):
            raise ValidationError(
                f"Invalid language code format: '{language_code}'. "
                f"Language codes must be 2 lowercase letters (ISO 639-1 format)"
            )
        
        return True
    
    @staticmethod
    def validate_session_id(session_id: str) -> bool:
        """
        Validate session ID format.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if valid
            
        Raises:
            ValidationError: If session ID is invalid
        """
        if not session_id:
            raise ValidationError("Session ID cannot be empty")
        
        # Session IDs should be UUIDs or secure tokens (alphanumeric and hyphens)
        if not re.match(r'^[a-zA-Z0-9-]{8,64}$', session_id):
            raise ValidationError(
                f"Invalid session ID format. Session IDs must be 8-64 alphanumeric characters or hyphens."
            )
        
        return True
