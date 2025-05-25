"""Vectorization service using Lindera for Japanese text processing."""

from typing import List, Optional
import re
import logging

try:
    from lindera import Lindera
    LINDERA_AVAILABLE = True
except ImportError:
    LINDERA_AVAILABLE = False
    logging.warning("Lindera library not available. Vector functionality will be disabled.")

logger = logging.getLogger(__name__)


class VectorizationService:
    """Service for vectorizing text using Lindera."""
    
    def __init__(self):
        """Initialize the vectorization service."""
        self.lindera = None
        if LINDERA_AVAILABLE:
            try:
                self.lindera = Lindera()
                logger.info("Lindera initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Lindera: {e}")
                self.lindera = None
    
    def is_available(self) -> bool:
        """Check if vectorization is available."""
        return self.lindera is not None
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess text for vectorization."""
        if not text:
            return ""
        
        # Remove markdown formatting
        text = re.sub(r'#+ ', '', text)  # Remove headers
        text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove bold
        text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove italics
        text = re.sub(r'`([^`]+)`', r'\1', text)  # Remove code blocks
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)  # Remove links, keep text
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', text)  # Remove images
        text = re.sub(r'\n+', ' ', text)  # Replace newlines with spaces
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        
        return text.strip()
    
    def tokenize_text(self, text: str) -> List[str]:
        """Tokenize text using Lindera."""
        if not self.is_available():
            # Fallback to simple tokenization
            return text.split()
        
        try:
            # Use Lindera to tokenize Japanese text
            tokens = self.lindera.tokenize(text)
            # Extract surface forms (actual words)
            return [token.surface for token in tokens]
        except Exception as e:
            logger.error(f"Error tokenizing text with Lindera: {e}")
            # Fallback to simple tokenization
            return text.split()
    
    def create_simple_vector(self, tokens: List[str], dimension: int = 384) -> List[float]:
        """Create a simple vector representation from tokens."""
        # This is a simple implementation for demonstration
        # In a real application, you would use a proper embedding model
        
        if not tokens:
            return [0.0] * dimension
        
        # Create a simple hash-based vector
        vector = [0.0] * dimension
        
        for token in tokens:
            # Simple hash-based approach
            hash_val = hash(token) % dimension
            vector[hash_val] += 1.0
        
        # Normalize the vector
        magnitude = sum(x ** 2 for x in vector) ** 0.5
        if magnitude > 0:
            vector = [x / magnitude for x in vector]
        
        return vector
    
    def vectorize_text(self, text: str) -> Optional[List[float]]:
        """Vectorize text and return the vector representation."""
        if not text:
            return None
        
        try:
            # Preprocess the text
            processed_text = self.preprocess_text(text)
            
            if not processed_text:
                return None
            
            # Tokenize the text
            tokens = self.tokenize_text(processed_text)
            
            if not tokens:
                return None
            
            # Create vector representation
            vector = self.create_simple_vector(tokens)
            
            logger.debug(f"Vectorized text with {len(tokens)} tokens into {len(vector)} dimensions")
            return vector
            
        except Exception as e:
            logger.error(f"Error vectorizing text: {e}")
            return None


# Global instance
vectorization_service = VectorizationService()


def get_vectorization_service() -> VectorizationService:
    """Get the global vectorization service instance."""
    return vectorization_service