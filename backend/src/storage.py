"""Storage module for saving and retrieving generated PDFs."""
import os
import time
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from .models import PDFDocument


class StorageBackend(ABC):
    """Abstract base class for storage backends."""
    
    @abstractmethod
    def save(self, pdf_document: PDFDocument, identifier: str) -> str:
        """
        Save a PDF document to storage.
        
        Args:
            pdf_document: The PDF document to save
            identifier: Unique identifier for the document
            
        Returns:
            The storage path or URL of the saved document
        """
        pass
    
    @abstractmethod
    def retrieve(self, identifier: str) -> Optional[PDFDocument]:
        """
        Retrieve a PDF document from storage.
        
        Args:
            identifier: Unique identifier for the document
            
        Returns:
            The PDF document if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete(self, identifier: str) -> bool:
        """
        Delete a PDF document from storage.
        
        Args:
            identifier: Unique identifier for the document
            
        Returns:
            True if deleted successfully, False otherwise
        """
        pass
    
    @abstractmethod
    def cleanup_expired(self, retention_days: int) -> int:
        """
        Clean up expired PDF documents.
        
        Args:
            retention_days: Number of days to retain documents
            
        Returns:
            Number of documents deleted
        """
        pass


class LocalFileStorage(StorageBackend):
    """Local filesystem storage backend."""
    
    def __init__(self, base_path: str = "storage/pdfs"):
        """
        Initialize local file storage.
        
        Args:
            base_path: Base directory for storing PDFs
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
    
    def save(self, pdf_document: PDFDocument, identifier: str) -> str:
        """Save PDF document to local filesystem."""
        file_path = self.base_path / f"{identifier}.pdf"
        
        # Write PDF content
        with open(file_path, 'wb') as f:
            f.write(pdf_document.content)
        
        # Store metadata
        metadata_path = self.base_path / f"{identifier}.meta"
        with open(metadata_path, 'w') as f:
            f.write(f"filename={pdf_document.filename}\n")
            f.write(f"page_count={pdf_document.page_count}\n")
            f.write(f"created_at={datetime.now().isoformat()}\n")
        
        return str(file_path)
    
    def retrieve(self, identifier: str) -> Optional[PDFDocument]:
        """Retrieve PDF document from local filesystem."""
        file_path = self.base_path / f"{identifier}.pdf"
        metadata_path = self.base_path / f"{identifier}.meta"
        
        if not file_path.exists():
            return None
        
        # Read PDF content
        with open(file_path, 'rb') as f:
            content = f.read()
        
        # Read metadata
        filename = f"{identifier}.pdf"
        page_count = 1
        
        if metadata_path.exists():
            with open(metadata_path, 'r') as f:
                for line in f:
                    if line.startswith('filename='):
                        filename = line.split('=', 1)[1].strip()
                    elif line.startswith('page_count='):
                        page_count = int(line.split('=', 1)[1].strip())
        
        return PDFDocument(
            content=content,
            filename=filename,
            page_count=page_count
        )
    
    def delete(self, identifier: str) -> bool:
        """Delete PDF document from local filesystem."""
        file_path = self.base_path / f"{identifier}.pdf"
        metadata_path = self.base_path / f"{identifier}.meta"
        
        deleted = False
        
        if file_path.exists():
            file_path.unlink()
            deleted = True
        
        if metadata_path.exists():
            metadata_path.unlink()
        
        return deleted
    
    def cleanup_expired(self, retention_days: int) -> int:
        """Clean up expired PDF documents from local filesystem."""
        cutoff_time = time.time() - (retention_days * 24 * 60 * 60)
        deleted_count = 0
        
        for file_path in self.base_path.glob("*.pdf"):
            if file_path.stat().st_mtime < cutoff_time:
                identifier = file_path.stem
                if self.delete(identifier):
                    deleted_count += 1
        
        return deleted_count


class PDFStorage:
    """Main storage interface for PDF documents."""
    
    def __init__(self, backend: Optional[StorageBackend] = None, retention_days: int = 7):
        """
        Initialize PDF storage.
        
        Args:
            backend: Storage backend to use (defaults to LocalFileStorage)
            retention_days: Number of days to retain PDFs
        """
        self.backend = backend or LocalFileStorage()
        self.retention_days = retention_days
    
    def generate_filename(self, prefix: str = "answers") -> str:
        """
        Generate a descriptive filename with timestamp.
        
        Args:
            prefix: Prefix for the filename
            
        Returns:
            Filename in format: prefix_YYYY-MM-DD_HHMMSS.pdf
        """
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        return f"{prefix}_{timestamp}.pdf"
    
    def generate_identifier(self) -> str:
        """
        Generate a unique identifier for a PDF document.
        
        Returns:
            Unique identifier string
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Add microseconds for uniqueness
        microseconds = datetime.now().microsecond
        return f"pdf_{timestamp}_{microseconds}"
    
    def save_pdf(self, pdf_document: PDFDocument, identifier: Optional[str] = None) -> str:
        """
        Save a PDF document to storage.
        
        Args:
            pdf_document: The PDF document to save
            identifier: Optional identifier (generated if not provided)
            
        Returns:
            The identifier for the saved document
        """
        if identifier is None:
            identifier = self.generate_identifier()
        
        self.backend.save(pdf_document, identifier)
        return identifier
    
    def retrieve_pdf(self, identifier: str) -> Optional[PDFDocument]:
        """
        Retrieve a PDF document from storage.
        
        Args:
            identifier: Unique identifier for the document
            
        Returns:
            The PDF document if found, None otherwise
        """
        return self.backend.retrieve(identifier)
    
    def delete_pdf(self, identifier: str) -> bool:
        """
        Delete a PDF document from storage.
        
        Args:
            identifier: Unique identifier for the document
            
        Returns:
            True if deleted successfully, False otherwise
        """
        return self.backend.delete(identifier)
    
    def cleanup_expired_pdfs(self) -> int:
        """
        Clean up expired PDF documents based on retention period.
        
        Returns:
            Number of documents deleted
        """
        return self.backend.cleanup_expired(self.retention_days)
