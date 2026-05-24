"""
AI Query Layer: Uses Google Gemini to answer questions about documents.

MVP Implementation:
- Takes user question + document text
- Calls Gemini API
- Returns answer or error

Configuration:
- API key: Read from GOOGLE_GEMINI_API_KEY environment variable
- Document truncation: 20,000 characters max (~5,000 tokens)
- Error handling: Return structured error responses
"""

import os

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover - optional runtime dependency
    genai = None

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - optional runtime dependency
    load_dotenv = None


if load_dotenv is not None:
    load_dotenv()


class AIQueryLayer:
    """
    Basic AI Query Layer using Google Gemini API.
    
    Accepts user questions and document text, returns answers from Gemini.
    """
    
    MAX_DOCUMENT_LENGTH = 20000  # characters, ~5,000 tokens
    
    def __init__(self, api_key=None):
        """
        Initialize Gemini API.
        
        Args:
            api_key (str, optional): Google Gemini API key. 
                                    If None, reads from GOOGLE_GEMINI_API_KEY env var.
        """
        if genai is None:
            raise ImportError(
                "google-generativeai is not installed. "
                "Install it or set up the Gemini runtime dependency."
            )

        if api_key is None:
            api_key = os.environ.get('GOOGLE_GEMINI_API_KEY')
        
        if not api_key or api_key.strip() in {"", "your_google_gemini_api_key_here"}:
            raise ValueError(
                "Google Gemini API key not found. "
                "Set GOOGLE_GEMINI_API_KEY in .env or your shell with a real Gemini API key."
            )
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.5-flash')
    
    def _truncate_document(self, text):
        """
        Truncate document if it exceeds MAX_DOCUMENT_LENGTH.
        
        Args:
            text (str): Document text
            
        Returns:
            str: Truncated text with indicator if truncated
        """
        if len(text) > self.MAX_DOCUMENT_LENGTH:
            truncated = text[:self.MAX_DOCUMENT_LENGTH]
            return truncated + "\n\n[Document truncated due to length...]"
        return text
    
    def query(self, user_question, document_text):
        """
        Answer a question about a document using Gemini.
        
        Args:
            user_question (str): The question to ask
            document_text (str): The document content to query
            
        Returns:
            dict: {
                'success': bool,
                'answer': str (if success=True),
                'error': str (if success=False)
            }
        """
        try:
            # Validate inputs
            if not user_question or not user_question.strip():
                return {
                    'success': False,
                    'error': 'Question cannot be empty'
                }
            
            if not document_text or not document_text.strip():
                return {
                    'success': False,
                    'error': 'Document text cannot be empty'
                }
            
            # Truncate document if needed
            truncated_doc = self._truncate_document(document_text)
            
            # Build prompt
            prompt = f"""Given the document below, answer this question concisely. 
If the document does not contain information to answer the question, say "Not found in document".

Question: {user_question}

Document:
{truncated_doc}

Answer:"""
            
            # Call Gemini
            response = self.model.generate_content(prompt)
            answer = response.text.strip() if response.text else ""
            
            if not answer:
                return {
                    'success': False,
                    'error': 'Gemini returned empty response'
                }
            
            return {
                'success': True,
                'answer': answer
            }
        
        except ValueError as e:
            # API configuration error
            return {
                'success': False,
                'error': f'Configuration error: {str(e)}'
            }
        except Exception as e:
            # API call error, timeout, rate limit, etc.
            return {
                'success': False,
                'error': f'Gemini API error: {str(e)}'
            }
