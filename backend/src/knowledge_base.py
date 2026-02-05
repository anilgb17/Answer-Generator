"""Educational Knowledge Base implementation."""
import uuid
from typing import List, Optional, Dict

from src.models import KnowledgeEntry
from src.exceptions import KnowledgeBaseError


class EducationalKnowledgeBase:
    """
    Educational Knowledge Base for storing and retrieving educational materials.
    
    Uses simple in-memory storage with keyword-based search.
    For production, this should be replaced with a vector database like ChromaDB, Pinecone, or Weaviate.
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the Educational Knowledge Base.
        
        Args:
            persist_directory: Directory to persist data (not used in simple implementation)
        """
        try:
            # Simple in-memory storage
            self.entries: Dict[str, KnowledgeEntry] = {}
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to initialize knowledge base: {str(e)}")
    
    def search(
        self, 
        query: str, 
        subject: Optional[str] = None, 
        limit: int = 5
    ) -> List[KnowledgeEntry]:
        """
        Search knowledge base for relevant educational materials.
        
        Args:
            query: Search query (question or topic)
            subject: Optional subject filter
            limit: Maximum number of results
            
        Returns:
            List of relevant knowledge entries
            
        Raises:
            KnowledgeBaseError: If search fails
        """
        try:
            # Simple keyword-based search
            query_lower = query.lower()
            results = []
            
            for entry in self.entries.values():
                # Check if subject filter matches
                if subject and entry.subject != subject:
                    continue
                
                # Simple keyword matching in content, topic, and subject
                if (query_lower in entry.content.lower() or 
                    query_lower in entry.topic.lower() or 
                    query_lower in entry.subject.lower()):
                    results.append(entry)
                    
                    if len(results) >= limit:
                        break
            
            return results
            
        except Exception as e:
            raise KnowledgeBaseError(f"Search failed: {str(e)}")
    
    def add_entry(self, entry: KnowledgeEntry) -> str:
        """
        Add new educational material to knowledge base.
        
        Args:
            entry: Knowledge entry to add
            
        Returns:
            ID of the added entry
            
        Raises:
            KnowledgeBaseError: If adding entry fails
        """
        try:
            # Generate ID if not provided or empty
            entry_id = entry.id if entry.id else str(uuid.uuid4())
            
            # Store the entry
            self.entries[entry_id] = entry
            
            return entry_id
            
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to add entry: {str(e)}")
    
    def get_subjects(self) -> List[str]:
        """
        Get list of all available subjects in the knowledge base.
        
        Returns:
            List of unique subject names
            
        Raises:
            KnowledgeBaseError: If retrieval fails
        """
        try:
            # Extract unique subjects
            subjects = set()
            for entry in self.entries.values():
                subjects.add(entry.subject)
            
            return sorted(list(subjects))
            
        except Exception as e:
            raise KnowledgeBaseError(f"Failed to get subjects: {str(e)}")
    
    def _populate_sample_data(self):
        """Populate the knowledge base with sample educational materials."""
        sample_entries = [
            # Mathematics
            KnowledgeEntry(
                id="math_001",
                subject="mathematics",
                topic="Pythagorean Theorem",
                content="The Pythagorean theorem states that in a right-angled triangle, "
                        "the square of the length of the hypotenuse (the side opposite the right angle) "
                        "is equal to the sum of squares of the lengths of the other two sides. "
                        "This can be written as: a² + b² = c², where c represents the length of the hypotenuse "
                        "and a and b represent the lengths of the other two sides.",
                references=["Euclid's Elements", "Basic Geometry Textbook"]
            ),
            KnowledgeEntry(
                id="math_002",
                subject="mathematics",
                topic="Quadratic Formula",
                content="The quadratic formula is used to solve quadratic equations of the form ax² + bx + c = 0. "
                        "The solutions are given by: x = (-b ± √(b² - 4ac)) / (2a). "
                        "The discriminant (b² - 4ac) determines the nature of the roots: "
                        "if positive, there are two real roots; if zero, one real root; if negative, two complex roots.",
                references=["Algebra Fundamentals", "College Algebra"]
            ),
            
            # Science - Physics
            KnowledgeEntry(
                id="physics_001",
                subject="science",
                topic="Newton's Laws of Motion",
                content="Newton's three laws of motion are fundamental principles in classical mechanics. "
                        "First Law (Inertia): An object at rest stays at rest and an object in motion stays in motion "
                        "with the same speed and direction unless acted upon by an unbalanced force. "
                        "Second Law: Force equals mass times acceleration (F = ma). "
                        "Third Law: For every action, there is an equal and opposite reaction.",
                references=["Principia Mathematica", "Physics Textbook"]
            ),
            KnowledgeEntry(
                id="physics_002",
                subject="science",
                topic="Photosynthesis",
                content="Photosynthesis is the process by which green plants and some other organisms use sunlight "
                        "to synthesize foods with the help of chlorophyll. The general equation is: "
                        "6CO₂ + 6H₂O + light energy → C₆H₁₂O₆ + 6O₂. "
                        "This process occurs in two stages: light-dependent reactions (in thylakoids) "
                        "and light-independent reactions or Calvin cycle (in stroma).",
                references=["Biology: The Science of Life", "Plant Physiology"]
            ),
            
            # History
            KnowledgeEntry(
                id="history_001",
                subject="history",
                topic="World War II",
                content="World War II (1939-1945) was a global war involving most of the world's nations. "
                        "It was the most widespread war in history, with more than 100 million people serving in military units. "
                        "Major participants included the Axis powers (Germany, Italy, Japan) and the Allied powers "
                        "(United States, Soviet Union, United Kingdom, China, and others). "
                        "The war ended with the unconditional surrender of the Axis powers.",
                references=["The Second World War by Winston Churchill", "World History Encyclopedia"]
            ),
            
            # Literature
            KnowledgeEntry(
                id="literature_001",
                subject="literature",
                topic="Shakespeare's Tragedies",
                content="William Shakespeare wrote several famous tragedies including Hamlet, Macbeth, Othello, "
                        "King Lear, and Romeo and Juliet. These plays typically feature a protagonist with a tragic flaw "
                        "that leads to their downfall. Common themes include ambition, jealousy, revenge, and fate. "
                        "Shakespeare's tragedies are known for their complex characters, poetic language, "
                        "and exploration of human nature.",
                references=["The Complete Works of Shakespeare", "Shakespearean Tragedy by A.C. Bradley"]
            ),
            
            # Technology
            KnowledgeEntry(
                id="tech_001",
                subject="technology",
                topic="Object-Oriented Programming",
                content="Object-Oriented Programming (OOP) is a programming paradigm based on the concept of 'objects', "
                        "which contain data in the form of fields (attributes) and code in the form of procedures (methods). "
                        "The four main principles of OOP are: Encapsulation (bundling data and methods), "
                        "Abstraction (hiding complex implementation details), Inheritance (creating new classes from existing ones), "
                        "and Polymorphism (objects of different types can be accessed through the same interface).",
                references=["Design Patterns: Elements of Reusable Object-Oriented Software", "Clean Code"]
            ),
            KnowledgeEntry(
                id="tech_002",
                subject="technology",
                topic="HTTP Protocol",
                content="HTTP (Hypertext Transfer Protocol) is an application-layer protocol for transmitting hypermedia documents. "
                        "It follows a client-server model where the client opens a connection to make a request, "
                        "then waits until it receives a response. Common HTTP methods include GET (retrieve data), "
                        "POST (submit data), PUT (update data), DELETE (remove data), and PATCH (partial update). "
                        "HTTP status codes indicate the result of the request: 2xx (success), 3xx (redirection), "
                        "4xx (client error), 5xx (server error).",
                references=["HTTP: The Definitive Guide", "RFC 2616"]
            ),
        ]
        
        for entry in sample_entries:
            try:
                self.add_entry(entry)
            except KnowledgeBaseError:
                # Entry might already exist, skip
                pass
