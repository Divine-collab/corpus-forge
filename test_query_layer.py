"""
Tests for AI Query Layer.

Tests cover:
1. Initialization with API key
2. Document truncation
3. Error handling (empty inputs, API failures)
4. Response format validation
"""

import unittest
import os
from unittest.mock import patch, MagicMock
from query_layer import AIQueryLayer


class TestAIQueryLayerInit(unittest.TestCase):
    """Test initialization and configuration."""
    
    def test_init_with_provided_api_key(self):
        """Should initialize with provided API key."""
        with patch('query_layer.genai.configure') as mock_config:
            layer = AIQueryLayer(api_key='test-key-123')
            mock_config.assert_called_once_with(api_key='test-key-123')
    
    def test_init_with_env_variable(self):
        """Should read API key from environment variable."""
        with patch.dict(os.environ, {'GOOGLE_GEMINI_API_KEY': 'env-key-456'}):
            with patch('query_layer.genai.configure') as mock_config:
                layer = AIQueryLayer()
                mock_config.assert_called_once_with(api_key='env-key-456')
    
    def test_init_missing_api_key(self):
        """Should raise ValueError if API key not provided or in env."""
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError) as context:
                AIQueryLayer()
            
            self.assertIn('GOOGLE_GEMINI_API_KEY', str(context.exception))


class TestDocumentTruncation(unittest.TestCase):
    """Test document truncation logic."""
    
    def setUp(self):
        """Set up layer with mocked API."""
        with patch('query_layer.genai.configure'):
            self.layer = AIQueryLayer(api_key='test-key')
    
    def test_truncate_long_document(self):
        """Should truncate documents exceeding MAX_DOCUMENT_LENGTH."""
        long_doc = "a" * 25000  # Longer than 20,000 limit
        truncated = self.layer._truncate_document(long_doc)
        
        # Should be truncated and marked
        self.assertLess(len(truncated), len(long_doc))
        self.assertIn("[Document truncated", truncated)
    
    def test_short_document_unchanged(self):
        """Should not truncate documents under limit."""
        short_doc = "This is a short document."
        truncated = self.layer._truncate_document(short_doc)
        
        self.assertEqual(truncated, short_doc)
        self.assertNotIn("[Document truncated", truncated)


class TestQueryMethod(unittest.TestCase):
    """Test the main query() method."""
    
    def setUp(self):
        """Set up layer with mocked API."""
        with patch('query_layer.genai.configure'):
            self.layer = AIQueryLayer(api_key='test-key')
    
    def test_query_empty_question(self):
        """Should return error for empty question."""
        result = self.layer.query('', 'Some document text')
        
        self.assertFalse(result['success'])
        self.assertIn('empty', result['error'].lower())
        self.assertNotIn('answer', result)
    
    def test_query_empty_document(self):
        """Should return error for empty document."""
        result = self.layer.query('What is this?', '')
        
        self.assertFalse(result['success'])
        self.assertIn('empty', result['error'].lower())
        self.assertNotIn('answer', result)
    
    def test_query_success(self):
        """Should return answer on successful query."""
        with patch.object(self.layer.model, 'generate_content') as mock_gen:
            # Mock Gemini response
            mock_response = MagicMock()
            mock_response.text = "The answer is 42."
            mock_gen.return_value = mock_response
            
            result = self.layer.query('What is the answer?', 'Some document.')
            
            self.assertTrue(result['success'])
            self.assertEqual(result['answer'], 'The answer is 42.')
            self.assertNotIn('error', result)
    
    def test_query_api_error(self):
        """Should handle API errors gracefully."""
        with patch.object(self.layer.model, 'generate_content') as mock_gen:
            # Mock API error
            mock_gen.side_effect = Exception('API connection failed')
            
            result = self.layer.query('What is this?', 'Some document.')
            
            self.assertFalse(result['success'])
            self.assertIn('API error', result['error'])
    
    def test_query_response_format(self):
        """Should always return dict with correct structure."""
        # Test error case
        result_error = self.layer.query('', 'doc')
        self.assertIsInstance(result_error, dict)
        self.assertIn('success', result_error)
        self.assertIn('error', result_error)
        
        # Test success case (mocked)
        with patch.object(self.layer.model, 'generate_content') as mock_gen:
            mock_response = MagicMock()
            mock_response.text = "Answer"
            mock_gen.return_value = mock_response
            
            result_success = self.layer.query('Q?', 'doc')
            self.assertIsInstance(result_success, dict)
            self.assertIn('success', result_success)
            self.assertIn('answer', result_success)


if __name__ == '__main__':
    unittest.main()
