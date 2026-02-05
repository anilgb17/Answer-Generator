"""Input parser components for extracting questions from various formats."""
import re
import uuid
from abc import ABC, abstractmethod
from typing import List
from io import BytesIO

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    from PIL import Image
    import pytesseract
except ImportError:
    Image = None
    pytesseract = None

from .models import Question
from .exceptions import UnsupportedFormatError, ParseError


class InputParser(ABC):
    """Base class for input parsers."""
    
    @abstractmethod
    def parse(self, input_data: bytes, format: str) -> List[Question]:
        """
        Parse input and extract questions.
        
        Args:
            input_data: Raw input bytes
            format: Input format ('text', 'pdf', 'image')
            
        Returns:
            List of Question objects
            
        Raises:
            UnsupportedFormatError: If format is not supported
            ParseError: If parsing fails
        """
        pass
    
    def _detect_questions(self, text: str) -> List[str]:
        """
        Detect and separate individual questions from text.
        
        Uses heuristics to identify question boundaries:
        - Lines starting with numbers (1., 2., Q1, etc.)
        - Lines ending with question marks
        - Empty lines between questions
        
        Args:
            text: Text containing one or more questions
            
        Returns:
            List of question strings
        """
        if not text.strip():
            return []
        
        # Pattern to match question numbering: "1.", "Q1.", "Question 1:", etc.
        question_pattern = re.compile(
            r'^(?:\d+\.|Q\d+\.?|Question\s+\d+:?)\s*',
            re.IGNORECASE | re.MULTILINE
        )
        
        # Split by question numbering patterns
        parts = question_pattern.split(text)
        
        # If no numbering found, try splitting by double newlines
        if len(parts) <= 1:
            parts = re.split(r'\n\s*\n', text)
        
        # Clean and filter questions
        questions = []
        for part in parts:
            cleaned = part.strip()
            if cleaned and len(cleaned) > 3:  # Minimum question length
                questions.append(cleaned)
        
        # If still no questions found, treat entire text as one question
        if not questions and text.strip():
            questions = [text.strip()]
        
        return questions


class TextParser(InputParser):
    """Parser for plain text input."""
    
    def parse(self, input_data: bytes, format: str) -> List[Question]:
        """
        Parse plain text input and extract questions.
        
        Args:
            input_data: Raw text bytes
            format: Should be 'text'
            
        Returns:
            List of Question objects
            
        Raises:
            ParseError: If text cannot be decoded
        """
        try:
            text = input_data.decode('utf-8')
        except UnicodeDecodeError as e:
            raise ParseError(
                f"Failed to decode text input: {str(e)}",
                parse_issue="Invalid UTF-8 encoding"
            )
        
        question_texts = self._detect_questions(text)
        
        questions = []
        for idx, q_text in enumerate(question_texts, start=1):
            question = Question(
                id=str(uuid.uuid4()),
                text=q_text,
                metadata={'source': 'text', 'index': idx}
            )
            questions.append(question)
        
        return questions


class PDFParser(InputParser):
    """Parser for PDF documents."""
    
    def __init__(self):
        """Initialize PDF parser."""
        if PyPDF2 is None:
            raise ImportError("PyPDF2 is required for PDF parsing. Install with: pip install PyPDF2")
    
    def parse(self, input_data: bytes, format: str) -> List[Question]:
        """
        Parse PDF document and extract questions.
        
        Args:
            input_data: Raw PDF bytes
            format: Should be 'pdf'
            
        Returns:
            List of Question objects
            
        Raises:
            ParseError: If PDF cannot be parsed
        """
        try:
            pdf_file = BytesIO(input_data)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            # Extract text from all pages
            text_parts = []
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                except Exception as e:
                    # Continue with other pages if one fails
                    pass
            
            if not text_parts:
                raise ParseError("No text could be extracted from PDF")
            
            full_text = '\n\n'.join(text_parts)
            question_texts = self._detect_questions(full_text)
            
            questions = []
            for idx, q_text in enumerate(question_texts, start=1):
                question = Question(
                    id=str(uuid.uuid4()),
                    text=q_text,
                    metadata={'source': 'pdf', 'index': idx}
                )
                questions.append(question)
            
            return questions
            
        except PyPDF2.errors.PdfReadError as e:
            raise ParseError("Failed to parse PDF", f"Invalid PDF structure: {str(e)}")
        except Exception as e:
            if isinstance(e, ParseError):
                raise
            raise ParseError("Failed to parse PDF", str(e))


class ImageParser(InputParser):
    """Parser for image files using OCR."""
    
    def __init__(self):
        """Initialize image parser."""
        if Image is None or pytesseract is None:
            raise ImportError(
                "Pillow and pytesseract are required for image parsing. "
                "Install with: pip install Pillow pytesseract"
            )
    
    def parse(self, input_data: bytes, format: str) -> List[Question]:
        """
        Parse image file and extract questions using OCR.
        
        Args:
            input_data: Raw image bytes
            format: Should be 'image'
            
        Returns:
            List of Question objects
            
        Raises:
            ParseError: If image cannot be parsed or OCR fails
        """
        try:
            image_file = BytesIO(input_data)
            image = Image.open(image_file)
            
            # Perform OCR
            try:
                text = pytesseract.image_to_string(image)
            except pytesseract.TesseractNotFoundError:
                raise ParseError(
                    "Tesseract OCR engine not found. "
                    "Please install Tesseract: https://github.com/tesseract-ocr/tesseract"
                )
            
            if not text.strip():
                raise ParseError("No text could be extracted from image")
            
            question_texts = self._detect_questions(text)
            
            questions = []
            for idx, q_text in enumerate(question_texts, start=1):
                question = Question(
                    id=str(uuid.uuid4()),
                    text=q_text,
                    metadata={'source': 'image', 'index': idx}
                )
                questions.append(question)
            
            return questions
            
        except Exception as e:
            if isinstance(e, ParseError):
                raise
            raise ParseError(f"Failed to parse image: {str(e)}")


class InputParserFactory:
    """Factory for creating appropriate parser based on format."""
    
    @staticmethod
    def create_parser(format: str) -> InputParser:
        """
        Create appropriate parser for the given format.
        
        Args:
            format: Input format ('text', 'pdf', 'image')
            
        Returns:
            InputParser instance
            
        Raises:
            UnsupportedFormatError: If format is not supported
        """
        format_lower = format.lower()
        
        if format_lower == 'text':
            return TextParser()
        elif format_lower == 'pdf':
            return PDFParser()
        elif format_lower in ['image', 'png', 'jpg', 'jpeg']:
            return ImageParser()
        else:
            supported = ['text', 'pdf', 'image', 'png', 'jpg', 'jpeg']
            raise UnsupportedFormatError(
                format,
                supported
            )
    
    @staticmethod
    def parse(input_data: bytes, format: str) -> List[Question]:
        """
        Parse input data using appropriate parser.
        
        Args:
            input_data: Raw input bytes
            format: Input format
            
        Returns:
            List of Question objects
            
        Raises:
            UnsupportedFormatError: If format is not supported
            ParseError: If parsing fails
        """
        parser = InputParserFactory.create_parser(format)
        return parser.parse(input_data, format)
