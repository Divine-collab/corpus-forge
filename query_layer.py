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
    DEFAULT_PROMPT_VERSION = 'v2'
    SUPPORTED_PROMPT_VERSIONS = {'v1', 'v2'}
    
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
    
    def _build_steered_prompt(self, base_prompt, steering):
        """
        Inject steering parameters into the prompt to customize response style.
        
        Args:
            base_prompt (str): The original prompt template
            steering (dict): Steering parameters:
                - audience_level: 'beginner', 'intermediate', or 'expert'
                - tone: 'professional', 'casual', or 'academic'
                - output_format: 'summary', 'detailed', or 'code'
                - creativity: 'literal', 'balanced', or 'creative'
        
        Returns:
            str: Modified prompt with steering instructions injected
        """
        # Extract steering parameters with defaults
        audience = steering.get('audience_level', 'intermediate')
        tone = steering.get('tone', 'professional')
        output_format = steering.get('output_format', 'detailed')
        creativity = steering.get('creativity', 'balanced')
        
        # Build audience description
        audience_desc = {
            'beginner': 'a beginner with no technical background',
            'intermediate': 'someone with intermediate knowledge',
            'expert': 'an expert in the field'
        }.get(audience, 'someone with intermediate knowledge')
        
        # Build tone description
        tone_desc = {
            'professional': 'professional and formal',
            'casual': 'conversational and casual',
            'academic': 'academic and scholarly'
        }.get(tone, 'professional and formal')
        
        # Build format description
        format_desc = {
            'summary': 'a concise summary',
            'detailed': 'a detailed explanation',
            'code': 'with code examples where applicable'
        }.get(output_format, 'a detailed explanation')
        
        # Build creativity description
        creativity_desc = {
            'literal': 'strictly based on the document content',
            'balanced': 'grounded in the document with some helpful context',
            'creative': 'drawing on broader knowledge and creative interpretations'
        }.get(creativity, 'grounded in the document with some helpful context')
        
        # Inject steering instructions at the beginning of the prompt
        steered_prompt = f"""You are answering a question for {audience_desc}. 
Your response should be {tone_desc} in tone.
Format your answer as {format_desc}.
Keep your response {creativity_desc}.

{base_prompt}"""
        
        return steered_prompt

    def _normalize_prompt_version(self, prompt_version):
        """
        Normalize prompt version values and fall back to the default version.
        """
        if not isinstance(prompt_version, str):
            return self.DEFAULT_PROMPT_VERSION

        version = prompt_version.strip().lower()
        if version not in self.SUPPORTED_PROMPT_VERSIONS:
            return self.DEFAULT_PROMPT_VERSION
        return version

    def _build_quiz_prompt(self, truncated_doc, num_questions, prompt_version=None):
        """
        Build a quiz generation prompt using a named version.
        """
        version = self._normalize_prompt_version(prompt_version)

        if version == 'v1':
            return f"""Based on the document below, generate exactly {num_questions} multiple-choice quiz questions.

For each question, provide:
1. Question text
2. Four options (A, B, C, D)
3. Correct answer (A, B, C, or D)

Format each question like this:
Q1: [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Answer: [A/B/C/D]

Document:
{truncated_doc}

Generate the quiz:"""

        return f"""You are generating a quiz from the document below.

Hard rules:
- Use only facts that are explicitly stated or clearly supported by the document.
- Do not invent names, dates, numbers, examples, or concepts that are not present.
- Each question must be answerable from the document alone.
- Create exactly {num_questions} distinct multiple-choice questions that cover different parts of the document.
- Every question must have exactly one best answer and three plausible distractors.
- Distractors must sound reasonable but must be false according to the document.
- Prefer high-confidence concepts over obscure details.
- If the document is short, reuse different supported concepts rather than adding unsupported facts.
- Do not include markdown fences, bullets outside the required format, or explanations.

Quality check before answering:
1. Verify each correct answer is supported by the document.
2. Verify all four options are distinct.
3. Verify the question wording is unambiguous.

Required format for every question:
Q1: [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Answer: [A/B/C/D]

Document:
{truncated_doc}

Generate the quiz now:"""

    def _build_flashcard_prompt(self, truncated_doc, num_cards, prompt_version=None):
        """
        Build a flashcard generation prompt using a named version.
        """
        version = self._normalize_prompt_version(prompt_version)

        if version == 'v1':
            return f"""Based on the document below, generate exactly {num_cards} flashcard question-answer pairs.

For each flashcard, provide:
1. Front (question/concept to study)
2. Back (answer/explanation)

Format each card like this:
Card 1 Front: [Question or concept]
Card 1 Back: [Comprehensive answer or explanation]

Card 2 Front: [Question or concept]
Card 2 Back: [Comprehensive answer or explanation]

... and so on

Document:
{truncated_doc}

Generate the flashcards:"""

        return f"""You are generating flashcards from the document below.

Hard rules:
- Use only information that is explicitly stated or clearly supported by the document.
- Do not invent terminology, facts, examples, or explanations that are not in the document.
- Create exactly {num_cards} flashcards that cover different important ideas from the document.
- Fronts should be short study prompts: a term, concept, function, process, or question grounded in the document.
- Backs should be concise but complete answers, using the document language where possible.
- Prefer one idea per card instead of combining multiple concepts.
- If the document is short, vary the card style (definition, purpose, step, comparison) without adding unsupported facts.
- Do not include markdown fences, bullets outside the required format, or extra commentary.

Quality check before answering:
1. Verify each front maps to a real topic in the document.
2. Verify each back can be justified from the source.
3. Verify the cards are not duplicates.

Required format for every card:
Card 1 Front: [Question or concept]
Card 1 Back: [Concise answer or explanation]

Card 2 Front: [Question or concept]
Card 2 Back: [Concise answer or explanation]

Document:
{truncated_doc}

Generate the flashcards now:"""
    
    def query(self, user_question, document_text, steering=None):
        """
        Answer a question about a document using Gemini with optional prompt steering.
        
        Args:
            user_question (str): The question to ask
            document_text (str): The document content to query
            steering (dict, optional): Prompt steering parameters:
                {
                    "audience_level": "beginner|intermediate|expert",
                    "tone": "professional|casual|academic",
                    "output_format": "summary|detailed|code",
                    "creativity": "literal|balanced|creative"
                }
            
        Returns:
            dict: {
                'success': bool,
                'answer': str (if success=True),
                'error': str (if success=False),
                'input_token_count': int,
                'output_token_count': int
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
            
            # Build base prompt
            base_prompt = f"""Given the document below, answer this question concisely. 
If the document does not contain information to answer the question, say "Not found in document".

Question: {user_question}

Document:
{truncated_doc}

Answer:"""
            
            # Inject steering instructions if provided
            if steering and isinstance(steering, dict):
                prompt = self._build_steered_prompt(base_prompt, steering)
            else:
                prompt = base_prompt
            
            # Call Gemini
            response = self.model.generate_content(prompt)
            answer = response.text.strip() if response.text else ""
            usage_metadata = getattr(response, 'usage_metadata', None)
            input_token_count = getattr(usage_metadata, 'prompt_token_count', None)
            output_token_count = getattr(usage_metadata, 'candidates_token_count', None)
            
            if not answer:
                return {
                    'success': False,
                    'error': 'Gemini returned empty response'
                }
            
            return {
                'success': True,
                'answer': answer,
                'input_token_count': input_token_count,
                'output_token_count': output_token_count
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
    
    def generate_quiz(self, document_text, num_questions=5, prompt_version=None):
        """
        Generate quiz questions from a document using Gemini.
        
        Args:
            document_text (str): The document to generate quiz from
            num_questions (int): Number of questions to generate (default 5)
            
        Returns:
            dict: {
                'success': bool,
                'questions': list of dicts with 'question' and 'correct_answer',
                'error': str (if success=False)
            }
        """
        try:
            if not document_text or not document_text.strip():
                return {
                    'success': False,
                    'error': 'Document text cannot be empty'
                }
            
            # Truncate document if needed
            truncated_doc = self._truncate_document(document_text)
            
            # Build prompt for quiz generation
            prompt = self._build_quiz_prompt(truncated_doc, num_questions, prompt_version=prompt_version)
            
            # Call Gemini
            response = self.model.generate_content(prompt)
            response_text = response.text.strip() if response.text else ""
            
            if not response_text:
                return {
                    'success': False,
                    'error': 'Gemini returned empty response'
                }
            
            # Parse questions from response
            questions = self._parse_quiz_questions(response_text)
            
            if not questions:
                return {
                    'success': False,
                    'error': 'Could not parse quiz questions from response'
                }
            
            return {
                'success': True,
                'questions': questions,
                'prompt_version': self._normalize_prompt_version(prompt_version)
            }
        
        except ValueError as e:
            return {
                'success': False,
                'error': f'Configuration error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Gemini API error: {str(e)}'
            }
    
    def _parse_quiz_questions(self, text):
        """
        Parse quiz questions from Gemini response text.
        Expects format: Q1: Question\nA) ...\nB) ...\nC) ...\nD) ...\nAnswer: X
        
        Returns list of question dicts with 'question' and 'correct_answer' keys.
        """
        questions = []
        lines = text.split('\n')
        
        current_question = None
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for question line (Q1:, Q2:, etc.)
            if line and (line.startswith('Q') and ':' in line):
                current_question = {
                    'question': line.split(':', 1)[1].strip(),
                    'options': {},
                    'correct_answer': None
                }
                
                # Next lines should be options A, B, C, D
                i += 1
                option_count = 0
                while i < len(lines) and option_count < 4:
                    opt_line = lines[i].strip()
                    if opt_line and opt_line[0] in 'ABCD' and ')' in opt_line:
                        option_key = opt_line[0]
                        option_text = opt_line.split(')', 1)[1].strip() if ')' in opt_line else ''
                        current_question['options'][option_key] = option_text
                        option_count += 1
                    i += 1
                
                # Look for answer line
                if i < len(lines):
                    answer_line = lines[i].strip()
                    if answer_line and 'answer:' in answer_line.lower():
                        answer = answer_line.split(':')[1].strip().upper()
                        if answer in 'ABCD':
                            current_question['correct_answer'] = answer
                
                # Only add if we have all required fields
                if current_question.get('correct_answer') and len(current_question.get('options', {})) >= 4:
                    questions.append(current_question)
            
            i += 1
        
        return questions
    
    def generate_flashcards(self, document_text, num_cards=10, prompt_version=None):
        """
        Generate flashcard Q&A pairs from document text using Gemini.
        
        Args:
            document_text (str): The source document text
            num_cards (int): Number of flashcards to generate (default 10)
        
        Returns:
            dict: {'success': bool, 'flashcards': [{'front': str, 'back': str}], 'error': str}
        """
        try:
            if not document_text or not document_text.strip():
                return {
                    'success': False,
                    'error': 'Document text cannot be empty'
                }
            
            # Truncate document if needed
            truncated_doc = self._truncate_document(document_text)
            
            # Build prompt for flashcard generation
            prompt = self._build_flashcard_prompt(truncated_doc, num_cards, prompt_version=prompt_version)
            
            # Call Gemini
            response = self.model.generate_content(prompt)
            response_text = response.text.strip() if response.text else ""
            
            if not response_text:
                return {
                    'success': False,
                    'error': 'Gemini returned empty response'
                }
            
            # Parse flashcards from response
            flashcards = self._parse_flashcards(response_text)
            
            if not flashcards:
                return {
                    'success': False,
                    'error': 'Could not parse flashcards from response'
                }
            
            return {
                'success': True,
                'flashcards': flashcards,
                'prompt_version': self._normalize_prompt_version(prompt_version)
            }
        
        except ValueError as e:
            return {
                'success': False,
                'error': f'Configuration error: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Gemini API error: {str(e)}'
            }
    
    def _parse_flashcards(self, text):
        """
        Parse flashcards from Gemini response text.
        Expects format: Card N Front: ...\nCard N Back: ...
        
        Returns list of flashcard dicts with 'front' and 'back' keys.
        """
        flashcards = []
        lines = text.split('\n')
        
        current_front = None
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for "Card N Front:" pattern
            if line and 'front:' in line.lower() and any(c.isdigit() for c in line):
                # Extract front text
                parts = line.split('Front:', 1)
                if len(parts) > 1:
                    current_front = parts[1].strip()
                    
                    # Look for corresponding "Card N Back:" on following lines
                    i += 1
                    while i < len(lines):
                        back_line = lines[i].strip()
                        if back_line and 'back:' in back_line.lower():
                            # Extract back text (could be multi-line)
                            back_parts = back_line.split('Back:', 1)
                            if len(back_parts) > 1:
                                current_back = back_parts[1].strip()
                                
                                # Continue reading back text until we hit the next card or end
                                i += 1
                                while i < len(lines):
                                    next_line = lines[i].strip()
                                    # Stop if we see the next card
                                    if next_line and 'Front:' in next_line.lower() and any(c.isdigit() for c in next_line):
                                        i -= 1  # Back up so outer loop processes this line
                                        break
                                    elif next_line:  # Append continuation lines to back
                                        current_back += '\n' + next_line
                                    i += 1
                                
                                # Add flashcard if we have both front and back
                                if current_front and current_back:
                                    flashcards.append({
                                        'front': current_front,
                                        'back': current_back
                                    })
                                current_front = None
                                break
                        i += 1
            
            i += 1
        
        return flashcards

