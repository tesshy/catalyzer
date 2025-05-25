"""Tests for vectorization service."""

import pytest
from unittest.mock import Mock, patch

from app.services.vectorization_service import VectorizationService


class TestVectorizationService:
    """Test class for VectorizationService."""
    
    def test_preprocess_text(self):
        """Test text preprocessing."""
        service = VectorizationService()
        
        # Test markdown removal
        markdown_text = """
        # Header
        
        This is **bold** and *italic* text.
        
        Here's some `code` and [a link](http://example.com).
        
        ![image](image.png)
        
        Multiple    spaces    should    be    normalized.
        """
        
        processed = service.preprocess_text(markdown_text)
        
        # Check that markdown formatting is removed
        assert "# Header" not in processed
        assert "**bold**" not in processed
        assert "*italic*" not in processed
        assert "`code`" not in processed
        assert "[a link](http://example.com)" not in processed
        assert "![image](image.png)" not in processed
        
        # Check that content is preserved
        assert "Header" in processed
        assert "bold" in processed
        assert "italic" in processed
        assert "code" in processed
        assert "a link" in processed
        
        # Check that whitespace is normalized
        assert "    " not in processed
    
    def test_preprocess_empty_text(self):
        """Test preprocessing empty text."""
        service = VectorizationService()
        assert service.preprocess_text("") == ""
        assert service.preprocess_text(None) == ""
    
    def test_tokenize_text_without_lindera(self):
        """Test tokenization without Lindera (fallback)."""
        with patch('app.services.vectorization_service.LINDERA_AVAILABLE', False):
            service = VectorizationService()
            
            text = "これは日本語のテストです"
            tokens = service.tokenize_text(text)
            
            # Should fall back to simple split
            assert tokens == text.split()
    
    @patch('app.services.vectorization_service.LINDERA_AVAILABLE', True)
    def test_tokenize_text_with_lindera(self):
        """Test tokenization with Lindera."""
        # Mock Lindera
        mock_token = Mock()
        mock_token.surface = "テスト"
        
        mock_lindera = Mock()
        mock_lindera.tokenize.return_value = [mock_token]
        
        with patch('app.services.vectorization_service.Lindera', return_value=mock_lindera):
            service = VectorizationService()
            
            text = "テスト"
            tokens = service.tokenize_text(text)
            
            assert tokens == ["テスト"]
            mock_lindera.tokenize.assert_called_once_with(text)
    
    def test_create_simple_vector(self):
        """Test simple vector creation."""
        service = VectorizationService()
        
        tokens = ["test", "word", "vector"]
        vector = service.create_simple_vector(tokens, dimension=100)
        
        # Check vector properties
        assert len(vector) == 100
        assert all(isinstance(x, float) for x in vector)
        
        # Check normalization (vector magnitude should be 1.0 or close)
        magnitude = sum(x ** 2 for x in vector) ** 0.5
        assert abs(magnitude - 1.0) < 0.0001 or magnitude == 0.0
    
    def test_create_simple_vector_empty_tokens(self):
        """Test vector creation with empty tokens."""
        service = VectorizationService()
        
        vector = service.create_simple_vector([], dimension=100)
        
        assert len(vector) == 100
        assert all(x == 0.0 for x in vector)
    
    def test_vectorize_text_full_pipeline(self):
        """Test full text vectorization pipeline."""
        service = VectorizationService()
        
        text = "# Test Document\n\nThis is a **test** document for vectorization."
        vector = service.vectorize_text(text)
        
        assert vector is not None
        assert len(vector) == 384  # Default dimension
        assert all(isinstance(x, float) for x in vector)
    
    def test_vectorize_empty_text(self):
        """Test vectorizing empty text."""
        service = VectorizationService()
        
        assert service.vectorize_text("") is None
        assert service.vectorize_text(None) is None
        assert service.vectorize_text("   ") is None
    
    def test_vectorize_japanese_text(self):
        """Test vectorizing Japanese text."""
        service = VectorizationService()
        
        text = "これは日本語のテスト文書です。データベースの説明が含まれています。"
        vector = service.vectorize_text(text)
        
        assert vector is not None
        assert len(vector) == 384
        assert any(x != 0.0 for x in vector)  # Should not be all zeros
    
    def test_is_available(self):
        """Test service availability check."""
        service = VectorizationService()
        
        # Should return True or False, not crash
        availability = service.is_available()
        assert isinstance(availability, bool)