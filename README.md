# Corpus Forge: AI-Powered Document Intelligence Platform

**Corpus Forge** is a capstone project that enables users to upload documents in multiple formats, intelligently search them, and ask AI-powered questions about their content using Google Gemini API.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [How It Works](#how-it-works)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Implementation Details](#implementation-details)
6. [Getting Started](#getting-started)
7. [API Endpoints](#api-endpoints)
8. [Project Status](#project-status)

---

## 🎯 Project Overview

Corpus Forge solves the problem: **"How do users interact with documents intelligently without reading them cover-to-cover?"**

### Core Features (MVP)
1. **Multi-Format Document Ingestion** – Upload `.txt`, `.md`, `.pdf`, `.py`, `.js` files
2. **Smart Document Storage** – Extract and clean text, maintain metadata, store in MySQL
3. **Keyword-Based Search** – Find documents by content, file type, or date range
4. **AI-Powered Q&A** – Ask questions about documents using Google Gemini
5. **Cost Observability** – Track API usage and token consumption

### User Journey
```
User uploads file → System extracts text → Stored in database
                                          ↓
                                    User searches
                                          ↓
                                User picks document
                                          ↓
                                User asks AI questions
                                          ↓
                                Get intelligent answers
```

---

## 🚀 How It Works

### 1. **Document Upload & Processing**

When you upload a file:

```
File (file.pdf, script.py, notes.txt)
    ↓
ReaderFactory (routes to correct reader)
    ↓
Format-Specific Reader:
  • TextReader: Extracts .txt, .md content
  • CodeReader: Parses .py, .js (extracts functions, classes, comments)
  • PdfReader: Extracts text + images from PDFs
    ↓
Output: {
  file_type: "pdf",
  raw_text: "original content...",
  cleaned_text: "cleaned content...",
  word_count: 1250
}
    ↓
Database Storage:
  • Save metadata (filename, size, date)
  • Store cleaned text for searching & querying
```

**Example**: Upload `machine-learning.pdf` → Extract all text → Store in MySQL → Ready to search

---

### 2. **Search Documents**

The **SearchLayer** finds documents using keyword matching:

```
User enters: "machine learning"
    ↓
SearchQuery creates filter:
  • Keyword: "machine learning"
  • File type: [optional]
  • Date range: [optional]
    ↓
SearchLayer queries database:
  SELECT * FROM uploaded_files
  WHERE cleaned_text LIKE '%machine learning%'
  AND file_type = '.pdf'  [if filtered]
  AND upload_date BETWEEN start_date AND end_date  [if filtered]
    ↓
For each result:
  • Calculate match_score (0-1 based on keyword frequency)
  • Create text preview (first 200 chars)
    ↓
Return: [
  {
    file_id: 1,
    file_name: "research.pdf",
    file_type: ".pdf",
    word_count: 5000,
    match_score: 0.85,
    cleaned_text_preview: "Machine learning is a subset of..."
  },
  ...
]
```

---

### 3. **Ask AI Questions**

The **AIQueryLayer** uses Google Gemini to answer questions about documents:

```
User selects document and asks: "What are the main topics?"
    ↓
Retrieve document text from database
    ↓
AIQueryLayer processes:
  1. Truncate document if > 20,000 chars (prevents token overflow)
  2. Build prompt: "Given this document: [TEXT], answer: [QUESTION]"
  3. Call Google Gemini API
  4. Extract answer + token usage metadata
    ↓
Gemini Response Analysis:
  • Extract answer text
  • Count input_tokens (question + document)
  • Count output_tokens (response length)
    ↓
Log to database:
  INSERT INTO api_usage_logs
  (document_id, query_text, input_tokens, output_tokens, total_tokens, created_at)
    ↓
Return to user:
  {
    "success": true,
    "answer": "The main topics are...",
    "input_token_count": 500,
    "output_token_count": 150,
    "total_token_count": 650
  }
```

### 4. **Prompt Steering** (Customize Response Style)

Users can customize how AI responses are delivered using **Prompt Steering**. This feature lets users control the *presentation style* of answers without changing the factual content.

**What is Prompt Steering?**

Prompt steering injects instructions into the Gemini prompt to customize four dimensions of the response:

| Parameter | Options | Effect |
|-----------|---------|--------|
| **Audience Level** | beginner, intermediate, expert | Technical depth of explanation |
| **Tone** | professional, casual, academic | How formal or conversational the response is |
| **Output Format** | summary, detailed, code | Whether to provide summaries, deep explanations, or code examples |
| **Creativity** | literal, balanced, creative | How much to go beyond the document (cite document vs. add context) |

**Example: Same Question, Different Steerings**

Question: *"What is machine learning?"*

**Steering 1: Beginner + Casual + Summary + Literal**
```
Response: "Machine learning? It's like teaching a computer to learn from examples,
kind of like how you learn by practicing. No fancy technical jargon needed!"
```

**Steering 2: Expert + Academic + Detailed + Creative**
```
Response: "Machine learning encompasses supervised, unsupervised, and reinforcement
learning paradigms. The optimization of loss functions through gradient descent enables
neural networks to approximate arbitrary functions..."
```

**How It Works (Technical)**

When users select steering options in the UI:

```
User selects:
  • Audience: "beginner"
  • Tone: "casual"
  • Format: "summary"
  • Creativity: "literal"
    ↓
JavaScript captures dropdown values:
  {
    audience_level: "beginner",
    tone: "casual",
    output_format: "summary",
    creativity: "literal"
  }
    ↓
Frontend sends to /query endpoint with steering parameter
    ↓
Backend AIQueryLayer._build_steered_prompt() injects instructions:
  "You are answering a question for a beginner with no technical background.
   Your response should be conversational and casual in tone.
   Format your answer as a concise summary.
   Keep your response strictly based on the document content."
    ↓
Modified prompt sent to Gemini API
    ↓
Gemini generates response in requested style
    ↓
Response returned to user with token counts (steering doesn't add tokens)
```

**Important: What Steering Does & Doesn't Do**

✅ **Steering Controls:**
- How explanations are presented
- Technical depth of response
- Tone and formality
- Format (summary vs. detailed)
- Whether to use document content only or add context

❌ **Steering Does NOT Control:**
- Factual accuracy (answers are still based on document)
- Answer content (different steering, same answer from document)
- Harmful behavior (safety filters still apply)
- API costs (token usage unaffected by steering)

**Use Cases**

- **Student**: Explain using beginner language + casual tone + summary format = quick understanding
- **Expert Reviewer**: Use expert audience + academic tone + detailed format = deep technical analysis
- **Manager**: Intermediate audience + professional tone + summary + balanced = executive summary
- **Developer**: Expert + professional + code format = implementation-ready examples

---

## 🏗️ System Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────┐
│         Frontend (HTML/CSS/JavaScript)              │
│  • Upload UI, Search form, Document list            │
│  • Query chat interface, Prompt Steering controls   │
│  • Cost dashboard                                   │
└─────────────────┬───────────────────────────────────┘
                  │ HTTP Requests
┌─────────────────▼───────────────────────────────────┐
│         Flask Web Server (main.py)                  │
│  Endpoints: /upload, /search, /query, /stats        │
└─────────────────┬───────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬────────────────┐
    │             │             │                │
┌───▼──────┐  ┌──▼──────┐  ┌──▼──────┐   ┌─────▼─────┐
│ Reader   │  │ Search  │  │ AI      │   │  Database │
│ Factory  │  │ Layer   │  │ Query   │   │  Layer    │
│          │  │         │  │ Layer   │   │           │
│ Text     │  │Keyword  │  │Gemini   │   │ MySQL     │
│ Code     │  │matching │  │API      │   │uploaded   │
│ PDF      │  │Filter   │  │         │   │_files     │
└──────────┘  │Rank     │  │Token    │   │api_usage  │
              └─────────┘  │tracking │   │_logs      │
                           └────────┘    └───────────┘
```

### Component Breakdown

| Component | Responsibility | Technologies |
|---|---|---|
| **ReaderFactory** | Route files to correct reader based on extension | Python pattern matching |
| **TextReader** | Extract text from `.txt`, `.md` files | regex, string manipulation |
| **CodeReader** | Parse `.py`, `.js` files, extract structure | ast module (for Python) |
| **PdfReader** | Extract text and images from PDFs | pdfplumber library |
| **SearchLayer** | Keyword search with filtering & scoring | SQL, string matching |
| **AIQueryLayer** | Question-answering via Gemini API | google-generativeai SDK |
| **Database Layer** | Persist documents and usage logs | MySQL, mysql-connector-python |
| **Flask API** | Handle HTTP requests, route to business logic | Flask, Werkzeug |
| **Frontend** | User interface for all operations | HTML, CSS, JavaScript |

---

## 💻 Technology Stack

### Backend
- **Language**: Python 3.9.6
- **Framework**: Flask + Werkzeug
- **Database**: MySQL with mysql-connector-python
- **AI/LLM**: Google Generative AI SDK (Gemini API)
- **Libraries**:
  - `pdfplumber` – PDF text extraction
  - `reportlab` – PDF generation for tests
  - `python-dotenv` – Environment variable management
  - `regex` – Advanced text processing

### Frontend
- **HTML5** – Structure
- **CSS3** – Styling
- **JavaScript (Vanilla)** – Interactivity

### Deployment & Environment
- **Virtual Environment**: Python venv (.venv-1 active)
- **Version Control**: Git
- **API Key Management**: Environment variables (GOOGLE_GEMINI_API_KEY)

---

## 🔧 Implementation Details

### 1. **File Reading & Extraction** (`TextReader.py`, `CodeReader.py`, `PdfReader.py`)

Each reader follows a **unified interface**:

```python
class BaseReader:
    def process(self):
        return {
            'file_name': str,
            'file_type': str,
            'raw_text': str,
            'cleaned_text': str,
            'word_count': int,
            'error': str (if error)
        }
```

**TextReader Example**:
```python
# Input: notes.txt containing "## My Notes\nRead about AI"
# Output:
{
    'file_name': 'notes.txt',
    'file_type': '.txt',
    'raw_text': '## My Notes\nRead about AI',
    'cleaned_text': 'my notes read about ai',  # lowercased, punctuation removed
    'word_count': 5
}
```

**CodeReader Example**:
```python
# Input: script.py with functions and comments
# Output:
{
    'file_name': 'script.py',
    'file_type': '.py',
    'raw_text': '[full source code]',
    'cleaned_text': '[extracted functions, classes, comments]',
    'word_count': 250
}
```

### 2. **ReaderFactory** (`reader_factory.py`)

Routes files to the correct reader:

```python
class ReaderFactory:
    READER_MAP = {
        '.txt': TextReader,
        '.md': TextReader,
        '.pdf': PdfReader,
        '.py': CodeReader,
        '.js': CodeReader
    }
    
    @staticmethod
    def create_reader(filepath):
        ext = get_extension(filepath)
        if ext not in READER_MAP:
            raise ValueError(f"Unsupported format: {ext}")
        return READER_MAP[ext](filepath)
```

### 3. **Search Layer** (`search_layer.py`)

Three-layer search system:

```
User Input → SearchQuery (validation) → SearchLayer (SQL query) → Results
```

**SearchQuery** validates input:
```python
query = SearchQuery(
    keyword="AI",
    file_type=".pdf",
    start_date="2026-05-01",
    end_date="2026-05-31"
)
if query.is_valid():  # keyword OR date range required
    results = SearchLayer.search(query)
```

**SearchLayer** builds dynamic SQL:
```sql
SELECT file_id, filename, file_type, cleaned_text
FROM uploaded_files
WHERE cleaned_text LIKE '%ai%'
  AND file_type = '.pdf'
  AND upload_date BETWEEN '2026-05-01' AND '2026-05-31'
ORDER BY (match_score) DESC
LIMIT 100
```

### 4. **AI Query Layer** (`query_layer.py`)

Interfaces with Google Gemini:

```python
class AIQueryLayer:
    MAX_DOCUMENT_LENGTH = 20000  # ~5,000 tokens
    
    def query(self, user_question, document_text):
        # Truncate if needed
        truncated = document_text[:20000]
        
        # Build prompt
        prompt = f"""Given this document:
        {truncated}
        
        Answer this question: {user_question}"""
        
        # Call Gemini
        response = self.model.generate_content(prompt)
        
        # Extract tokens
        usage = response.usage_metadata
        return {
            'success': True,
            'answer': response.text,
            'input_token_count': usage.prompt_tokens,
            'output_token_count': usage.candidates_tokens
        }
```

### 5. **Database Layer** (`db.py`)

Manages persistence:

```python
def insert_uploaded_file(filename, file_type, file_size, raw_text, cleaned_text, word_count):
    # Store document metadata & content
    # Returns: file_id

def get_document_text(document_id):
    # Retrieve full document text for AI querying
    # Returns: cleaned_text string

def insert_api_usage_log(document_id, query_text, input_tokens, output_tokens, total_tokens):
    # Track every Gemini API call
    # Returns: log_id

def get_api_stats():
    # Aggregate statistics
    # Returns: { total_requests, total_input_tokens, total_output_tokens, total_tokens_overall }
```

**Database Schema**:

```sql
CREATE TABLE uploaded_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(100),
    file_size BIGINT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    raw_text LONGTEXT,
    cleaned_text LONGTEXT,
    word_count INT
);

CREATE TABLE api_usage_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    document_id INT NOT NULL,
    query_text LONGTEXT,
    input_tokens INT,
    output_tokens INT,
    total_tokens INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES uploaded_files(id)
);
```

### 6. **Flask API Endpoints** (`main.py`)

| Endpoint | Method | Purpose | Input | Output |
|---|---|---|---|---|
| `/` | GET | Serve frontend | N/A | HTML page |
| `/upload` | POST | Upload document | File + metadata | `{success, file_id, reader_type}` |
| `/search` | POST | Search documents | `{keyword, file_type?, start_date?, end_date?}` | `{success, results[], total_found}` |
| `/query` | POST | Ask AI question | `{document_id, query}` | `{success, answer, tokens}` |
| `/stats` | GET | View API usage | N/A | `{total_requests, total_tokens, ...}` |
| `/list-documents` | GET | List all documents | `?limit=50&file_type=` | `{success, documents[]}` |
| `/test-db` | GET | Verify DB connection | N/A | `{status}` |

---

## 🎬 Getting Started

### Prerequisites
- Python 3.9+
- MySQL 5.7+ (with `corpus_forge` database created)
- Google Gemini API key

### Installation

1. **Clone repository**:
```bash
git clone <repo_url>
cd capstone-corpus-forge
```

2. **Create virtual environment**:
```bash
python -m venv .venv-1
source .venv-1/bin/activate  # On Windows: .venv-1\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install flask werkzeug mysql-connector-python google-generativeai pdfplumber python-dotenv
```

4. **Set up database**:
```bash
mysql -u root < database.md  # Creates corpus_forge database & tables
```

5. **Configure API key**:
```bash
export GOOGLE_GEMINI_API_KEY="your-api-key-here"
```

6. **Run Flask server**:
```bash
python main.py
```

7. **Access frontend**:
Open browser: `http://127.0.0.1:5000`

---

## 📡 API Endpoints

### Upload Document
```bash
curl -X POST http://127.0.0.1:5000/upload \
  -F "file=@research-paper.pdf"
```

**Response**:
```json
{
  "success": true,
  "reader": "PdfReader",
  "file_name": "research-paper.pdf",
  "result": {
    "file_type": ".pdf",
    "word_count": 8500,
    "cleaned_text": "abstract introduction..."
  }
}
```

### Search Documents
```bash
curl -X POST http://127.0.0.1:5000/search \
  -H "Content-Type: application/json" \
  -d '{
    "keyword": "machine learning",
    "file_type": ".pdf",
    "start_date": "2026-05-01",
    "end_date": "2026-05-31"
  }'
```

**Response**:
```json
{
  "success": true,
  "total_found": 3,
  "results": [
    {
      "file_id": 1,
      "file_name": "research.pdf",
      "file_type": ".pdf",
      "word_count": 5000,
      "match_score": 0.95,
      "cleaned_text_preview": "Machine learning is..."
    }
  ]
}
```

### Ask AI Question
```bash
curl -X POST http://127.0.0.1:5000/query \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": 1,
    "query": "What are the main findings?"
  }'
```

**Response**:
```json
{
  "success": true,
  "answer": "The main findings show that...",
  "document_id": 1,
  "input_token_count": 500,
  "output_token_count": 150,
  "total_token_count": 650
}
```

### View API Usage Statistics
```bash
curl http://127.0.0.1:5000/stats
```

**Response**:
```json
{
  "success": true,
  "total_api_requests": 42,
  "total_input_tokens": 18500,
  "total_output_tokens": 6200,
  "total_tokens_overall": 24700
}
```

---

## ✅ Project Status

### Completed (MVP Core)
- ✅ TextReader, CodeReader, PdfReader (3 formats supported)
- ✅ ReaderFactory (centralized routing)
- ✅ SearchLayer (keyword search + filtering)
- ✅ AIQueryLayer (Gemini integration)
- ✅ Database persistence
- ✅ Flask API (6 endpoints)
- ✅ Cost observability (token tracking)
- ✅ Frontend integration
- ✅ Comprehensive testing (40+ tests passing)

### In Progress / Planned
- ⏳ Prompt Steering (user customization of AI output)
- ⏳ Engineering Challenges Layer 2 (choose 2 of 4)
- ⏳ Advanced workflows (flashcards, quizzes, code review)
- ⏳ Performance optimization
- ⏳ Production deployment

---

## 📝 Testing

Run all tests:
```bash
python test_text_reader.py
python test_code_reader.py
python test_pdf_reader.py
python test_reader_factory.py
python test_search_layer.py
python test_query_layer.py
```

Expected: **40+ tests passing** ✅

---

## 📚 Key Design Patterns Used

1. **Factory Pattern** – ReaderFactory routes to correct reader
2. **Layered Architecture** – Separation of concerns (readers → search → query → database)
3. **Unified Interface** – All readers return same data structure
4. **Template Method** – Base reader class with shared behavior
5. **Strategy Pattern** – Different search/ranking strategies
6. **Repository Pattern** – Database abstraction layer

---

## 🤝 Contributors

- **Backend & Core Logic**: Divine Byishimo
- **Frontend UI/UX**: Friend (HTML/CSS/JS)
- **Testing & Documentation**: Team

---

## 📄 License

This project is part of EPITA AI4SE Capstone Program (2026).

---

## 🎓 Learning Outcomes

This project demonstrates:
- Multi-format file parsing and data extraction
- Layered software architecture
- Relational database design
- REST API development
- Integration with third-party AI services (Gemini)
- Observability and cost tracking
- Test-driven development practices
- Agile methodology (MVP-first approach)

