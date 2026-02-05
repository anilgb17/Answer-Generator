"""Answer Generator with knowledge base and multi-language support."""
import os
import re
import time
from typing import List, Optional, Dict, Any, Callable
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai

from src.models import Question, Answer, VisualElementSpec, KnowledgeEntry
from src.knowledge_base import EducationalKnowledgeBase
from src.language_service import LanguageService
from src.exceptions import AnswerGenerationError, LanguageNotSupportedError
from config.settings import settings


class AnswerGenerator:
    """
    Generates comprehensive answers for questions with multi-language support.
    
    Integrates with Educational Knowledge Base for accurate, educationally sound responses
    and uses LLM APIs (OpenAI/Anthropic) for answer generation.
    """
    
    def __init__(
        self,
        knowledge_base: EducationalKnowledgeBase,
        language_service: LanguageService,
        llm_provider: str = "gemini",
        max_retries: int = 3,
        progress_callback: Optional[Callable[[str, int, str], None]] = None,
        api_key_override: Optional[str] = None
    ):
        """
        Initialize the Answer Generator.
        
        Args:
            knowledge_base: Educational knowledge base for retrieving educational materials
            language_service: Language service for language configuration
            llm_provider: LLM provider to use ('openai', 'anthropic', 'gemini', or 'perplexity')
            max_retries: Maximum number of retry attempts for API calls
            progress_callback: Optional callback function for progress updates
                              Signature: callback(stage: str, progress: int, message: str)
            api_key_override: Optional API key to use instead of settings/env
        """
        self.knowledge_base = knowledge_base
        self.language_service = language_service
        self.llm_provider = llm_provider
        self.max_retries = max_retries
        self.progress_callback = progress_callback
        
        # Initialize LLM client based on provider
        if llm_provider == "openai":
            api_key = api_key_override or settings.openai_api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise AnswerGenerationError(
                    "OpenAI API key not found. Set OPENAI_API_KEY environment variable."
                )
            self.llm_client = OpenAI(api_key=api_key)
        elif llm_provider == "anthropic":
            api_key = api_key_override or settings.anthropic_api_key or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise AnswerGenerationError(
                    "Anthropic API key not found. Set ANTHROPIC_API_KEY environment variable."
                )
            self.llm_client = Anthropic(api_key=api_key)
        elif llm_provider == "gemini":
            api_key = api_key_override or settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise AnswerGenerationError(
                    "Gemini API key not found. Set GEMINI_API_KEY environment variable."
                )
            genai.configure(api_key=api_key)
            # Use gemini-2.5-flash model (latest and fastest)
            self.llm_client = genai.GenerativeModel('gemini-2.5-flash')
        elif llm_provider == "perplexity":
            api_key = api_key_override or settings.perplexity_api_key or os.getenv("PERPLEXITY_API_KEY")
            if not api_key:
                raise AnswerGenerationError(
                    "Perplexity API key not found. Set PERPLEXITY_API_KEY environment variable."
                )
            # Perplexity uses OpenAI-compatible API
            self.llm_client = OpenAI(
                api_key=api_key,
                base_url="https://api.perplexity.ai"
            )
        else:
            raise AnswerGenerationError(f"Unsupported LLM provider: {llm_provider}")
    
    def generate_answer(
        self,
        question: Question,
        target_language: str = 'en'
    ) -> Answer:
        """
        Generate answer for a question in the target language.
        
        Args:
            question: Question object to answer
            target_language: ISO 639-1 language code for answer (default: 'en')
            
        Returns:
            Answer object with content and visual element specifications
            
        Raises:
            LanguageNotSupportedError: If target language is not supported
            AnswerGenerationError: If answer generation fails
        """
        # Validate language support
        if not self.language_service.is_supported(target_language):
            raise LanguageNotSupportedError(
                f"Language '{target_language}' is not supported. "
                f"Use LanguageService.get_supported_languages() to see available languages."
            )
        
        try:
            # Step 1: Search knowledge base for relevant materials
            self._emit_progress('knowledge_search', 10, f'Searching knowledge base for question {question.id}')
            knowledge_entries = self._search_knowledge_base(question)
            
            # Step 2: Build context from knowledge entries
            self._emit_progress('context_building', 20, f'Building context for question {question.id}')
            context = self._build_context(knowledge_entries)
            
            # Step 3: Generate answer using LLM
            self._emit_progress('answer_generation', 40, f'Generating answer for question {question.id}')
            answer_content = self._generate_answer_with_llm(
                question, context, target_language, knowledge_entries
            )
            
            # Step 4: Detect and create visual element specifications
            self._emit_progress('visual_detection', 70, f'Detecting visual elements for question {question.id}')
            visual_elements = self._detect_visual_elements(question, answer_content, target_language)
            
            # Step 5: Generate citations for knowledge sources
            self._emit_progress('citation_generation', 90, f'Generating citations for question {question.id}')
            knowledge_source_ids = [entry.id for entry in knowledge_entries]
            references = self._generate_references(knowledge_entries)
            
            # Create and return Answer object
            self._emit_progress('complete', 100, f'Completed answer generation for question {question.id}')
            return Answer(
                question_id=question.id,
                content=answer_content,
                language=target_language,
                visual_elements=visual_elements,
                references=references,
                knowledge_sources=knowledge_source_ids
            )
            
        except LanguageNotSupportedError:
            raise
        except Exception as e:
            raise AnswerGenerationError(
                f"Failed to generate answer for question '{question.id}': {str(e)}"
            )
    
    def _emit_progress(self, stage: str, progress: int, message: str) -> None:
        """
        Emit progress update if callback is configured.
        
        Args:
            stage: Current processing stage
            progress: Progress percentage (0-100)
            message: Progress message
        """
        if self.progress_callback:
            self.progress_callback(stage, progress, message)
    
    def _search_knowledge_base(self, question: Question) -> List[KnowledgeEntry]:
        """
        Search knowledge base for relevant educational materials.
        
        Args:
            question: Question to search for
            
        Returns:
            List of relevant knowledge entries
        """
        try:
            # Search using question text
            entries = self.knowledge_base.search(
                query=question.text,
                limit=5
            )
            return entries
        except Exception as e:
            # Log error but don't fail - we can generate answers without knowledge base
            print(f"Warning: Knowledge base search failed: {str(e)}")
            return []
    
    def _build_context(self, knowledge_entries: List[KnowledgeEntry]) -> str:
        """
        Build context string from knowledge entries.
        
        Args:
            knowledge_entries: List of knowledge entries
            
        Returns:
            Formatted context string
        """
        if not knowledge_entries:
            return ""
        
        context_parts = ["Relevant educational materials:"]
        for i, entry in enumerate(knowledge_entries, 1):
            context_parts.append(
                f"\n{i}. {entry.topic} ({entry.subject}):\n{entry.content}"
            )
            if entry.references:
                context_parts.append(f"   References: {', '.join(entry.references)}")
        
        return "\n".join(context_parts)
    
    def _generate_answer_with_llm(
        self,
        question: Question,
        context: str,
        target_language: str,
        knowledge_entries: List[KnowledgeEntry]
    ) -> str:
        """
        Generate answer using LLM API with retry logic.
        
        Args:
            question: Question to answer
            context: Context from knowledge base
            target_language: Target language code
            knowledge_entries: Knowledge entries used
            
        Returns:
            Generated answer text
            
        Raises:
            AnswerGenerationError: If all retry attempts fail
        """
        # Get language configuration
        lang_config = self.language_service.get_language_config(target_language)
        
        # Build prompt
        prompt = self._build_prompt(question, context, lang_config, knowledge_entries)
        
        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(self.max_retries):
            try:
                if self.llm_provider == "openai":
                    response = self._call_openai(prompt)
                elif self.llm_provider == "anthropic":
                    response = self._call_anthropic(prompt)
                elif self.llm_provider == "gemini":
                    response = self._call_gemini(prompt)
                elif self.llm_provider == "perplexity":
                    response = self._call_perplexity(prompt)
                else:
                    raise AnswerGenerationError(f"Unsupported provider: {self.llm_provider}")
                
                return response
                
            except Exception as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    time.sleep(wait_time)
                    continue
                else:
                    break
        
        # All retries failed
        raise AnswerGenerationError(
            f"Failed to generate answer after {self.max_retries} attempts. "
            f"Last error: {str(last_error)}"
        )
    
    def _build_prompt(
        self,
        question: Question,
        context: str,
        lang_config,
        knowledge_entries: List[KnowledgeEntry]
    ) -> str:
        """
        Build prompt for LLM based on question, context, and language.
        
        Args:
            question: Question to answer
            context: Context from knowledge base
            lang_config: Language configuration
            knowledge_entries: Knowledge entries used
            
        Returns:
            Formatted prompt string
        """
        # Base prompt template
        prompt_parts = []
        
        # Language instruction
        if lang_config.code != 'en':
            prompt_parts.append(
                f"Please provide your answer in {lang_config.name} ({lang_config.native_name})."
            )
        
        # Context from knowledge base
        if context:
            prompt_parts.append(context)
            prompt_parts.append(
                "\nUse the above educational materials to inform your answer. "
                "Include citations where appropriate."
            )
        else:
            prompt_parts.append(
                "Note: No specialized educational materials were found for this topic. "
                "Please provide a comprehensive answer using general knowledge."
            )
        
        # Question
        prompt_parts.append(f"\nQuestion: {question.text}")
        
        # Additional context if provided
        if question.context:
            prompt_parts.append(f"Context: {question.context}")
        
        # Instructions for answer format
        prompt_parts.append(
            "\nProvide a comprehensive, detailed answer that:"
            "\n1. Directly addresses the question"
            "\n2. Includes relevant explanations and examples"
            "\n3. Is educationally sound and accurate"
            "\n4. Uses clear, understandable language"
        )
        
        if knowledge_entries:
            prompt_parts.append(
                "5. References the educational materials provided where relevant"
            )
        
        return "\n".join(prompt_parts)
    
    def _call_openai(self, prompt: str) -> str:
        """
        Call OpenAI API to generate answer.
        
        Args:
            prompt: Prompt to send to API
            
        Returns:
            Generated answer text
        """
        response = self.llm_client.chat.completions.create(
            model="gpt-4o-mini",  # Faster and cheaper model
            messages=[
                {
                    "role": "system",
                    "content": "You are an educational assistant that provides comprehensive, "
                               "accurate answers to questions. Your answers should be detailed, "
                               "well-structured, and educationally sound."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,  # Lower temperature for faster, more focused responses
            max_tokens=800,  # Reduced tokens for faster generation
            stream=False
        )
        
        return response.choices[0].message.content.strip()
    
    def _call_anthropic(self, prompt: str) -> str:
        """
        Call Anthropic API to generate answer.
        
        Args:
            prompt: Prompt to send to API
            
        Returns:
            Generated answer text
        """
        response = self.llm_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        return response.content[0].text.strip()
    
    def _call_gemini(self, prompt: str) -> str:
        """
        Call Google Gemini API to generate answer.
        
        Args:
            prompt: Prompt to send to API
            
        Returns:
            Generated answer text
        """
        try:
            response = self.llm_client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=800,
                )
            )
            return response.text.strip()
        except Exception as e:
            # If gemini-pro fails, try with models/gemini-pro
            error_msg = str(e)
            if "not found" in error_msg.lower():
                # Try listing available models
                raise AnswerGenerationError(
                    f"Gemini model not available. Error: {error_msg}. "
                    "Please check your API key at https://makersuite.google.com/app/apikey"
                )
            raise
    
    def _call_perplexity(self, prompt: str) -> str:
        """
        Call Perplexity API to generate answer.
        Perplexity uses OpenAI-compatible API.
        
        Args:
            prompt: Prompt to send to API
            
        Returns:
            Generated answer text
        """
        response = self.llm_client.chat.completions.create(
            model="llama-3.1-sonar-small-128k-online",  # Fast Perplexity model with online search
            messages=[
                {
                    "role": "system",
                    "content": "You are an educational assistant that provides comprehensive, "
                               "accurate answers to questions. Your answers should be detailed, "
                               "well-structured, and educationally sound."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=800,
            stream=False
        )
        
        return response.choices[0].message.content.strip()
    
    def _detect_visual_elements(
        self,
        question: Question,
        answer_content: str,
        target_language: str
    ) -> List[VisualElementSpec]:
        """
        Detect and create visual element specifications based on content analysis.
        
        Args:
            question: Original question
            answer_content: Generated answer content
            target_language: Target language code
            
        Returns:
            List of visual element specifications
        """
        visual_elements = []
        combined_text = (question.text + " " + answer_content).lower()
        
        # Detect architecture/component diagrams
        architecture_keywords = [
            'system', 'component', 'module', 'architecture', 'structure',
            'design', 'layer', 'tier', 'service', 'microservice'
        ]
        if any(keyword in combined_text for keyword in architecture_keywords):
            visual_elements.append(self._create_block_diagram_spec(
                question, answer_content, target_language
            ))
        
        # Detect process/workflow diagrams
        process_keywords = [
            'process', 'workflow', 'steps', 'procedure', 'algorithm',
            'flow', 'sequence', 'stage', 'phase', 'cycle'
        ]
        if any(keyword in combined_text for keyword in process_keywords):
            visual_elements.append(self._create_flowchart_spec(
                question, answer_content, target_language
            ))
        
        # Detect hierarchy diagrams
        hierarchy_keywords = [
            'hierarchy', 'tree', 'organization', 'classification',
            'taxonomy', 'inheritance', 'parent', 'child', 'level'
        ]
        if any(keyword in combined_text for keyword in hierarchy_keywords):
            visual_elements.append(self._create_hierarchy_spec(
                question, answer_content, target_language
            ))
        
        return visual_elements
    
    def _create_block_diagram_spec(
        self,
        question: Question,
        answer_content: str,
        target_language: str
    ) -> VisualElementSpec:
        """Create block diagram specification."""
        return VisualElementSpec(
            type='block_diagram',
            description=f"Block diagram for: {question.text[:50]}...",
            elements=[
                {
                    'id': 'diagram_1',
                    'label': 'Component Diagram',
                    'nodes': [],  # To be populated by diagram generator
                    'edges': []
                }
            ],
            language=target_language
        )
    
    def _create_flowchart_spec(
        self,
        question: Question,
        answer_content: str,
        target_language: str
    ) -> VisualElementSpec:
        """Create flowchart specification."""
        return VisualElementSpec(
            type='flowchart',
            description=f"Flowchart for: {question.text[:50]}...",
            elements=[
                {
                    'id': 'flowchart_1',
                    'label': 'Process Flow',
                    'steps': [],  # To be populated by diagram generator
                }
            ],
            language=target_language
        )
    
    def _create_hierarchy_spec(
        self,
        question: Question,
        answer_content: str,
        target_language: str
    ) -> VisualElementSpec:
        """Create hierarchy diagram specification."""
        return VisualElementSpec(
            type='hierarchy',
            description=f"Hierarchy diagram for: {question.text[:50]}...",
            elements=[
                {
                    'id': 'hierarchy_1',
                    'label': 'Hierarchical Structure',
                    'root': None,  # To be populated by diagram generator
                    'children': []
                }
            ],
            language=target_language
        )
    
    def _generate_references(self, knowledge_entries: List[KnowledgeEntry]) -> List[str]:
        """
        Generate reference list from knowledge entries.
        
        Args:
            knowledge_entries: List of knowledge entries used
            
        Returns:
            List of reference strings
        """
        references = []
        seen_refs = set()
        
        for entry in knowledge_entries:
            for ref in entry.references:
                if ref not in seen_refs:
                    references.append(ref)
                    seen_refs.add(ref)
        
        return references
