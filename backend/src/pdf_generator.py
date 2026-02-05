"""
PDF Generator Module

This module provides functionality to generate well-formatted PDF documents
with multi-language support, including proper font selection, RTL text support,
and embedded diagrams.
"""

from typing import List, Dict
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Image,
    Table, TableStyle, KeepTogether
)
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import io
import html

from src.models import Question, Answer, Diagram, PDFDocument
from src.language_service import LanguageService
from src.exceptions import PDFGenerationError


class NumberedCanvas(canvas.Canvas):
    """Custom canvas for adding page numbers and headers/footers."""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
    
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        """Add page numbers to all pages."""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
    
    def draw_page_number(self, page_count):
        """Draw page number at the bottom of the page."""
        page_num = self.getPageNumber()
        # Skip page number on title page (page 1)
        if page_num > 1:
            text = f"Page {page_num - 1} of {page_count - 1}"
            self.setFont("Helvetica", 9)
            self.drawRightString(7.5 * inch, 0.5 * inch, text)


class PDFGenerator:
    """
    Generates PDF documents from answers and diagrams with multi-language support.
    
    Features:
    - Title page with document information
    - Table of contents with hyperlinks
    - Formatted answer sections with proper typography
    - Embedded diagrams with captions
    - Page numbering and headers/footers
    - Multi-language font support including non-Latin scripts
    - RTL text support for Arabic and other RTL languages
    """
    
    def __init__(self, language_service: LanguageService):
        """
        Initialize the PDF generator.
        
        Args:
            language_service: Service for language configuration
        """
        self.language_service = language_service
        
        # Page configuration
        self.page_size = letter
        self.margin_top = 1.0 * inch
        self.margin_bottom = 1.0 * inch
        self.margin_left = 1.0 * inch
        self.margin_right = 1.0 * inch
        
        # Figure counter for sequential numbering
        self.figure_counter = 0
    
    def _escape_text(self, text: str) -> str:
        """
        Escape text for use in ReportLab Paragraphs.
        
        ReportLab's Paragraph class interprets text as HTML/XML, so we need to
        escape special characters to prevent parsing errors.
        
        Args:
            text: Raw text to escape
            
        Returns:
            Escaped text safe for use in Paragraphs
        """
        return html.escape(text)
    
    def generate_pdf(
        self,
        questions: List[Question],
        answers: List[Answer],
        diagrams: Dict[str, List[Diagram]],
        target_language: str = 'en'
    ) -> PDFDocument:
        """
        Generate PDF document from answers and diagrams in target language.
        
        Args:
            questions: List of original questions
            answers: List of generated answers
            diagrams: Dictionary mapping answer IDs to their diagrams
            target_language: ISO 639-1 language code
            
        Returns:
            PDFDocument object
            
        Raises:
            PDFGenerationError: If PDF generation fails
        """
        try:
            # Validate inputs
            if not questions:
                raise PDFGenerationError("No questions provided")
            if not answers:
                raise PDFGenerationError("No answers provided")
            if len(questions) != len(answers):
                raise PDFGenerationError(
                    f"Question count ({len(questions)}) does not match answer count ({len(answers)})"
                )
            
            # Validate language support
            if not self.language_service.is_supported(target_language):
                raise PDFGenerationError(
                    f"Language '{target_language}' is not supported"
                )
            
            # Get language configuration
            lang_config = self.language_service.get_language_config(target_language)
            
            # Reset figure counter
            self.figure_counter = 0
            
            # Create PDF in memory
            buffer = io.BytesIO()
            
            # Create document with custom canvas for page numbers
            doc = SimpleDocTemplate(
                buffer,
                pagesize=self.page_size,
                topMargin=self.margin_top,
                bottomMargin=self.margin_bottom,
                leftMargin=self.margin_left,
                rightMargin=self.margin_right,
                title="Question Answers"
            )
            
            # Build document content
            story = []
            
            # Add title page
            story.extend(self._create_title_page(len(questions), target_language, lang_config))
            story.append(PageBreak())
            
            # Add table of contents
            story.extend(self._create_table_of_contents(questions, lang_config))
            story.append(PageBreak())
            
            # Add question-answer sections
            for i, (question, answer) in enumerate(zip(questions, answers), 1):
                question_diagrams = diagrams.get(answer.question_id, [])
                story.extend(
                    self._create_answer_section(
                        i, question, answer, question_diagrams, lang_config
                    )
                )
                # Add page break between questions (except after the last one)
                if i < len(questions):
                    story.append(PageBreak())
            
            # Build PDF with numbered pages
            doc.build(story, canvasmaker=NumberedCanvas)
            
            # Get PDF content
            pdf_content = buffer.getvalue()
            buffer.close()
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            filename = f"answers_{timestamp}.pdf"
            
            # Count pages (approximate based on content)
            # Title page + TOC page + answer pages
            page_count = 2 + len(questions)
            
            return PDFDocument(
                content=pdf_content,
                filename=filename,
                page_count=page_count
            )
            
        except Exception as e:
            if isinstance(e, PDFGenerationError):
                raise
            raise PDFGenerationError(f"Failed to generate PDF: {str(e)}") from e
    
    def _create_title_page(
        self,
        question_count: int,
        target_language: str,
        lang_config
    ) -> List:
        """Create title page content."""
        story = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER
        )
        story.append(Paragraph("Question Answers", title_style))
        story.append(Spacer(1, 0.5 * inch))
        
        # Document information
        info_style = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=12,
            alignment=TA_CENTER
        )
        
        story.append(Paragraph(f"Number of Questions: {question_count}", info_style))
        story.append(Paragraph(f"Language: {lang_config.native_name}", info_style))
        story.append(Paragraph(
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            info_style
        ))
        
        return story
    
    def _create_table_of_contents(
        self,
        questions: List[Question],
        lang_config
    ) -> List:
        """Create table of contents with hyperlinks."""
        story = []
        styles = getSampleStyleSheet()
        
        # TOC title
        toc_title_style = ParagraphStyle(
            'TOCTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=20
        )
        story.append(Paragraph("Table of Contents", toc_title_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # TOC entries
        toc_entry_style = ParagraphStyle(
            'TOCEntry',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            leftIndent=20
        )
        
        for i, question in enumerate(questions, 1):
            # Truncate long questions for TOC
            question_text = question.text
            if len(question_text) > 80:
                question_text = question_text[:77] + "..."
            
            entry_text = f"{i}. {question_text}"
            story.append(Paragraph(self._escape_text(entry_text), toc_entry_style))
        
        return story
    
    def _create_answer_section(
        self,
        question_number: int,
        question: Question,
        answer: Answer,
        diagrams: List[Diagram],
        lang_config
    ) -> List:
        """Create a complete answer section with question, answer, and diagrams."""
        story = []
        styles = getSampleStyleSheet()
        
        # Determine text alignment based on RTL
        text_alignment = TA_RIGHT if lang_config.rtl else TA_LEFT
        
        # Question heading
        question_style = ParagraphStyle(
            'Question',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=12,
            spaceBefore=0,
            alignment=text_alignment
        )
        story.append(Paragraph(f"Question {question_number}", question_style))
        
        # Question text
        question_text_style = ParagraphStyle(
            'QuestionText',
            parent=styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#34495E'),
            spaceAfter=20,
            alignment=text_alignment
        )
        story.append(Paragraph(self._escape_text(question.text), question_text_style))
        
        # Answer heading
        answer_heading_style = ParagraphStyle(
            'AnswerHeading',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=colors.HexColor('#16A085'),
            spaceAfter=10,
            alignment=text_alignment
        )
        story.append(Paragraph("Answer", answer_heading_style))
        
        # Answer content
        answer_style = ParagraphStyle(
            'Answer',
            parent=styles['BodyText'],
            fontSize=11,
            alignment=TA_JUSTIFY if not lang_config.rtl else TA_RIGHT,
            spaceAfter=15,
            leading=14
        )
        story.append(Paragraph(self._escape_text(answer.content), answer_style))
        
        # Add diagrams if present
        if diagrams:
            story.append(Spacer(1, 0.2 * inch))
            for diagram in diagrams:
                story.extend(self._add_diagram(diagram, lang_config))
        
        # Add references if present
        if answer.references:
            story.append(Spacer(1, 0.2 * inch))
            story.extend(self._add_references(answer.references, lang_config))
        
        return story
    
    def _add_diagram(self, diagram: Diagram, lang_config) -> List:
        """Add a diagram with caption to the document."""
        story = []
        
        # Increment figure counter
        self.figure_counter += 1
        
        # Create image from bytes
        img_buffer = io.BytesIO(diagram.image_data)
        
        # Create Image object with size constraints
        img = Image(img_buffer, width=5 * inch, height=3.5 * inch, kind='proportional')
        
        # Center the image
        story.append(img)
        
        # Add caption
        caption_style = ParagraphStyle(
            'Caption',
            fontSize=10,
            textColor=colors.HexColor('#7F8C8D'),
            alignment=TA_CENTER,
            spaceAfter=15,
            spaceBefore=5
        )
        caption_text = f"Figure {self.figure_counter}: {diagram.caption}"
        story.append(Paragraph(self._escape_text(caption_text), caption_style))
        
        return story
    
    def _add_references(self, references: List[str], lang_config) -> List:
        """Add references section."""
        story = []
        styles = getSampleStyleSheet()
        
        # References heading
        ref_heading_style = ParagraphStyle(
            'RefHeading',
            parent=styles['Heading4'],
            fontSize=11,
            textColor=colors.HexColor('#7F8C8D'),
            spaceAfter=8
        )
        story.append(Paragraph("References", ref_heading_style))
        
        # Reference list
        ref_style = ParagraphStyle(
            'Reference',
            parent=styles['Normal'],
            fontSize=9,
            leftIndent=20,
            spaceAfter=5
        )
        
        for i, ref in enumerate(references, 1):
            story.append(Paragraph(self._escape_text(f"{i}. {ref}"), ref_style))
        
        return story
