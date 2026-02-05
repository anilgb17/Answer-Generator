"""Data models for the Question Answer Generator system."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class Question:
    """Represents a question to be answered."""
    id: str
    text: str
    context: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate question data after initialization."""
        if not self.text.strip():
            raise ValueError("Question text cannot be empty")


@dataclass
class VisualElementSpec:
    """Specification for a visual element (diagram, chart, etc.)."""
    type: str  # 'block_diagram', 'flowchart', 'hierarchy', 'sequence'
    description: str
    elements: List[Dict[str, Any]]
    language: str  # Target language for labels
    
    def __post_init__(self):
        """Validate visual element specification after initialization."""
        valid_types = ['block_diagram', 'flowchart', 'hierarchy', 'sequence']
        if self.type not in valid_types:
            raise ValueError(f"Invalid visual element type: {self.type}")
        if not self.language:
            raise ValueError("Language code cannot be empty")


@dataclass
class Answer:
    """Represents an answer to a question."""
    question_id: str
    content: str
    language: str  # ISO 639-1 language code
    visual_elements: List[VisualElementSpec] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    knowledge_sources: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Validate answer data after initialization."""
        if not self.content.strip():
            raise ValueError("Answer content cannot be empty")
        if not self.language:
            raise ValueError("Language code cannot be empty")


@dataclass
class Diagram:
    """Represents a generated diagram."""
    image_data: bytes
    format: str  # 'png', 'svg'
    caption: str
    language: str  # Language of labels and captions
    
    def __post_init__(self):
        """Validate diagram data after initialization."""
        if self.format not in ['png', 'svg']:
            raise ValueError(f"Unsupported image format: {self.format}")
        if not self.image_data:
            raise ValueError("Image data cannot be empty")
        if not self.language:
            raise ValueError("Language code cannot be empty")


@dataclass
class PDFDocument:
    """Represents a generated PDF document."""
    content: bytes
    filename: str
    page_count: int
    
    def __post_init__(self):
        """Validate PDF document data after initialization."""
        if not self.content:
            raise ValueError("PDF content cannot be empty")
        if self.page_count < 1:
            raise ValueError("Page count must be at least 1")


@dataclass
class LanguageConfig:
    """Configuration for a supported language."""
    code: str  # ISO 639-1 language code
    name: str  # English name
    native_name: str  # Native language name
    font_family: str  # Appropriate font for the language
    rtl: bool = False  # Right-to-left text direction
    
    def __post_init__(self):
        """Validate language configuration after initialization."""
        if not self.code or len(self.code) != 2:
            raise ValueError("Language code must be 2-character ISO 639-1 code")


@dataclass
class KnowledgeEntry:
    """Represents an entry in the educational knowledge base."""
    id: str
    subject: str  # e.g., 'mathematics', 'physics', 'history'
    topic: str
    content: str
    references: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate knowledge entry data after initialization."""
        if not self.content.strip():
            raise ValueError("Knowledge entry content cannot be empty")
        if not self.subject.strip() or not self.topic.strip():
            raise ValueError("Subject and topic are required")
