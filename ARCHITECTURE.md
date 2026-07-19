# AI Study Assistant - Architecture Documentation

## System Overview

The AI Study Assistant is a full-stack RAG (Retrieval-Augmented Generation) based platform designed to help students prepare for exams by intelligently processing their study materials and generating personalized learning resources.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (Planned)                   │
│              Next.js + Tailwind + Shadcn UI                  │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              API Layer (REST)                        │   │
│  │  - Authentication  - Subjects  - Upload             │   │
│  │  - Chat  - Notes  - Quiz  - Flashcards             │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                         │
│  ┌──────────────────▼───────────────────────────────────┐   │
│  │              Service Layer                           │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │          RAG Pipeline                       │    │   │
│  │  │  - PDF Processor  - Chunker                │    │   │
│  │  │  - Embeddings    - Retriever               │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  │  ┌─────────────────────────────────────────────┐    │   │
│  │  │          LLM Service                        │    │   │
│  │  │  - Gemini/OpenAI Integration               │    │   │
│  │  │  - Prompt Engineering                       │    │   │
│  │  └─────────────────────────────────────────────┘    │   │
│  └──────────────────┬───────────────────────────────────┘   │
└────────────────────┬┴───────────────────────────────────────┘
                     │
     ┌───────────────┼───────────────┐
     │               │               │
┌────▼─────┐  ┌─────▼──────┐  ┌────▼─────┐
│PostgreSQL│  │  Pinecone  │  │ File     │
│ Database │  │  (Vectors) │  │ Storage  │
└──────────┘  └────────────┘  └──────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.109.0
- **Language**: Python 3.10+
- **Database**: PostgreSQL 14+ with SQLAlchemy 2.0
- **Vector DB**: Pinecone (cloud-hosted)
- **LLM**: Google Gemini 2.0 Flash / OpenAI GPT-4
- **Embedding Model**: BAAI/bge-small-en-v1.5 (384 dimensions)

### Core Libraries
- **RAG Framework**: LangChain
- **PDF Processing**: PyMuPDF, PDFPlumber
- **Embeddings**: Sentence Transformers
- **Authentication**: python-jose, passlib
- **Background Tasks**: FastAPI BackgroundTasks
- **Logging**: Loguru

## System Components

### 1. API Layer

#### Authentication Module
```python
Components:
- JWT token generation (access + refresh)
- Password hashing with bcrypt
- OAuth integration (Google placeholder)
- Password reset flow

Endpoints:
- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- POST /auth/forgot-password
- POST /auth/reset-password
```

#### Subject Management
```python
Components:
- CRUD operations for subjects
- Subject statistics aggregation
- Session tracking

Endpoints:
- POST /subjects
- GET /subjects
- GET /subjects/{id}
- PUT /subjects/{id}
- DELETE /subjects/{id}
```

#### File Upload & Processing
```python
Components:
- Multipart file upload
- File validation (type, size)
- Background PDF processing
- Progress tracking

Endpoints:
- POST /upload/{subject_id}
- GET /upload/{subject_id}/files
- DELETE /upload/files/{file_id}
```

### 2. RAG Pipeline

#### PDF Processing Service
```python
Class: PDFProcessor

Methods:
- extract_text_pymupdf() - Primary extraction
- extract_text_pdfplumber() - Fallback/table extraction
- extract_tables() - Table-specific extraction
- get_pdf_metadata() - Extract metadata
- clean_text() - Text preprocessing

Flow:
1. Upload PDF → Validate size/type
2. Extract text (dual method for accuracy)
3. Extract tables separately
4. Clean and preprocess text
5. Store metadata
```

#### Text Chunking Service
```python
Class: TextChunker

Configuration:
- Chunk size: 1000 characters
- Overlap: 200 characters
- Separator hierarchy: \n\n → \n → . → space

Methods:
- chunk_text() - Basic chunking
- chunk_pages() - With page metadata
- chunk_with_context() - Include surrounding chunks
- extract_formulas() - Formula extraction
- extract_definitions() - Definition extraction

Features:
- Semantic chunking (respects sentence boundaries)
- Page number preservation
- Context window support
```

#### Embedding Service
```python
Class: EmbeddingService

Model: BAAI/bge-small-en-v1.5
Dimension: 384

Methods:
- generate_embedding() - Single text
- generate_embeddings_batch() - Batch processing
- compute_similarity() - Cosine similarity

Optimization:
- Batch processing for efficiency
- Progress tracking for large sets
- GPU support (if available)
```

#### Vector Store Service
```python
Class: VectorStoreService

Provider: Pinecone
Index: studyai-embeddings

Methods:
- add_documents() - Store embeddings
- query() - Similarity search
- delete_by_file() - Cleanup
- delete_by_subject() - Bulk delete
- get_stats() - Index statistics

Metadata stored:
- user_id, subject_id, file_id
- filename, page_number
- chunk_index, chunk_type
- truncated text (for quick reference)
```

#### Retrieval Service
```python
Class: RAGRetriever

Methods:
- retrieve() - Basic retrieval
- retrieve_with_reranking() - Enhanced retrieval

Process:
1. Query → Generate embedding
2. Search vector store (top_k=10)
3. Filter by subject_id
4. Rerank results
5. Return top_k=5 with citations

Output:
- context: Combined text chunks
- citations: File names, page numbers
- confidence_score: Average similarity
```

### 3. LLM Service

#### LLM Integration
```python
Class: LLMService

Supported Providers:
- Google Gemini (primary)
- OpenAI GPT-4 (alternative)

Methods:
- generate() - Simple generation
- generate_with_context() - RAG-enhanced
- stream_generate() - Streaming responses

Configuration:
- Temperature: 0.7 (default)
- Max tokens: 4096
- System prompts: Customizable
```

#### Prompt Templates

**Chat Prompt**:
```
System: You are an AI study assistant...

Context: {retrieved_context}
Question: {user_query}

Provide detailed answer based on context.
```

**Notes Generation**:
```
Generate comprehensive notes from:
{content}

Include:
- Headings and subheadings
- Bullet points
- Examples
- Definitions
- Tables and formulas
```

**Quiz Generation**:
```
Generate {n} questions from:
{content}

Format as JSON with:
- question_text
- question_type
- options
- correct_answer
- explanation
```

### 4. Database Schema

#### Entity Relationship

```
User (1) ──────< (N) Subject
                       │
                       ├──< UploadedFile
                       ├──< ChatHistory
                       ├──< GeneratedNote
                       ├──< Quiz ──< QuizQuestion
                       ├──< Flashcard
                       ├──< RevisionSheet
                       └──< ImportantQuestion

UploadedFile (1) ──< (N) VectorMetadata

Quiz (1) ──< (N) QuizAttempt
```

#### Key Models

**User**
```python
- id (PK)
- email (unique)
- username (unique)
- hashed_password
- is_active, is_verified
- google_id (for OAuth)
- created_at, last_login
```

**Subject**
```python
- id (PK)
- user_id (FK)
- name, code, semester
- total_pdfs, total_pages
- created_at, last_accessed
```

**UploadedFile**
```python
- id (PK)
- subject_id (FK)
- filename, file_path
- file_size, total_pages
- is_processed
- vector_ids
- uploaded_at, processed_at
```

**ChatHistory**
```python
- id (PK)
- subject_id (FK)
- role (user/assistant)
- message
- context_used (JSON)
- citations (JSON)
- confidence_score
- created_at
```

**Quiz**
```python
- id (PK)
- subject_id (FK)
- title, quiz_mode
- total_marks, passing_marks
- time_limit_minutes
```

**QuizQuestion**
```python
- id (PK)
- quiz_id (FK)
- question_text
- question_type (enum)
- options (JSON)
- correct_answer (JSON)
- explanation
- marks, topic
```

### 5. Security Architecture

#### Authentication Flow
```
1. User registers → Password hashed (bcrypt)
2. User logs in → Credentials verified
3. Generate JWT tokens:
   - Access token (30 min)
   - Refresh token (7 days)
4. Client stores tokens
5. API requests include: Authorization: Bearer {token}
6. Middleware validates token
7. Request proceeds with user context
```

#### Authorization
```python
Decorator: @Depends(get_current_active_user)

Checks:
1. Token present?
2. Token valid?
3. Token expired?
4. User exists?
5. User active?

Access Control:
- Users can only access their own data
- Filter by user_id in all queries
- Cascade delete for data cleanup
```

#### Data Isolation
```python
Every query includes user_id filter:

subjects = db.query(Subject).filter(
    Subject.user_id == current_user.id
).all()

Prevents:
- Cross-user data access
- Information leakage
- Unauthorized modifications
```

## Data Flow

### 1. PDF Upload Flow
```
User uploads PDF
    ↓
Validate file (type, size)
    ↓
Save to disk
    ↓
Create UploadedFile record
    ↓
Background task started
    ↓
Extract text (PyMuPDF + PDFPlumber)
    ↓
Clean and preprocess
    ↓
Chunk text (LangChain)
    ↓
Generate embeddings (batch)
    ↓
Store in Pinecone with metadata
    ↓
Update file status (processed)
    ↓
Notify user (optional)
```

### 2. Chat Flow
```
User sends message
    ↓
Save user message to ChatHistory
    ↓
Generate query embedding
    ↓
Search Pinecone (similarity search)
    ↓
Retrieve top 10 results
    ↓
Rerank to top 5
    ↓
Combine context
    ↓
Get recent chat history (6 messages)
    ↓
Build prompt with context + history
    ↓
Generate response (LLM)
    ↓
Save assistant message with citations
    ↓
Return response to user
```

### 3. Notes Generation Flow
```
User requests notes
    ↓
Background task started
    ↓
Retrieve all chunks for subject (top 50)
    ↓
Combine content
    ↓
Build generation prompt based on type:
  - Complete notes
  - Summary
  - Formula sheet
  - Keywords
    ↓
Generate with LLM (4096 tokens)
    ↓
Save to GeneratedNote
    ↓
Return note ID
```

### 4. Quiz Generation Flow
```
User requests quiz
    ↓
Background task started
    ↓
Retrieve content (top 30 chunks)
    ↓
Build quiz generation prompt
    ↓
Generate with LLM → JSON output
    ↓
Parse JSON response
    ↓
Create Quiz record
    ↓
Create QuizQuestion records
    ↓
Calculate total marks
    ↓
Return quiz ID
```

## Performance Considerations

### Optimization Strategies

1. **Database**
   - Indexes on foreign keys
   - Indexes on frequently queried fields (email, user_id)
   - Connection pooling (10 connections)
   - Lazy loading for relationships

2. **Vector Search**
   - Batch embedding generation
   - Metadata filtering before search
   - Top-k limited to necessary results
   - Reranking for precision

3. **Background Processing**
   - Async PDF processing
   - Non-blocking file uploads
   - Progress tracking
   - Error recovery

4. **Caching** (To be implemented)
   - Redis for frequent queries
   - Cache embeddings for repeated content
   - Cache LLM responses (optional)

### Scalability

**Current Capacity**:
- Single server deployment
- ~100 concurrent users
- ~10,000 PDFs total
- ~1M vector embeddings

**Scaling Strategy**:
1. Horizontal scaling with load balancer
2. Database read replicas
3. Separate workers for background tasks
4. CDN for file storage
5. Pinecone auto-scales

## Monitoring & Logging

### Logging Levels
```python
DEBUG: Development debugging
INFO: Normal operations
WARNING: Recoverable issues
ERROR: Errors requiring attention
```

### Log Locations
- Application logs: `backend/logs/app.log`
- Console output: Real-time during development
- Rotation: 500MB per file, 10 day retention

### Metrics (To be implemented)
- Request/response times
- Error rates
- Background task completion
- Vector store query performance
- LLM token usage

## Deployment Architecture

### Development
```
Local machine
- PostgreSQL: localhost:5432
- FastAPI: localhost:8000
- Pinecone: cloud
```

### Production (Recommended)
```
Frontend: Vercel
    ↓
Backend: Railway/Render
- FastAPI application
- Gunicorn WSGI server
- Environment variables
    ↓
Database: Managed PostgreSQL
- Railway/Render/AWS RDS
- Automated backups
    ↓
Vector DB: Pinecone Cloud
- Managed service
- Auto-scaling
    ↓
Storage: AWS S3 or similar
- PDF file storage
- Export file storage
```

## Security Best Practices

1. **Never commit .env files**
2. **Use environment variables for secrets**
3. **Rotate JWT secrets regularly**
4. **Implement rate limiting (production)**
5. **Validate all user inputs**
6. **Sanitize file uploads**
7. **Use HTTPS in production**
8. **Regular dependency updates**

## Future Enhancements

1. **Caching Layer**: Redis for performance
2. **Message Queue**: Celery for background tasks
3. **WebSockets**: Real-time notifications
4. **Microservices**: Separate PDF processing service
5. **CDN**: For file delivery
6. **Multi-region**: Deploy in multiple regions

---

**This architecture is designed for:**
- Scalability
- Maintainability
- Security
- Performance
- Extensibility

**Last Updated**: December 2024
