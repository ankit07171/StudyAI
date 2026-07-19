# AI Study Assistant - MongoDB + Pinecone RAG Architecture

## 🏗️ System Architecture

### Database Layer

#### **MongoDB** (Primary Data Store)
- **Purpose**: Store all application data and metadata
- **Collections**:
  - `users` - User accounts and authentication
  - `subjects` - Subject information
  - `uploaded_files` - PDF file metadata
  - `vector_metadata` - Chunk metadata mapping to Pinecone vectors
  - `chat_history` - Conversation history with citations
  - `generated_notes` - AI-generated study notes
  - `quizzes`, `quiz_questions`, `quiz_attempts` - Quiz system
  - `flashcards` - Flashcard content and spaced repetition data
  - `revision_sheets` - One-page revision guides
  - `important_questions` - Generated exam questions
  - `study_plans` - Personalized study schedules
  - `bookmarks` - User bookmarks
  - `notifications` - System notifications
  - `study_sessions` - Study session tracking

#### **Pinecone** (Vector Database)
- **Purpose**: Store and search document embeddings
- **Index Structure**:
  ```
  Vector ID: unique identifier (UUID)
  Embedding: 384-dimensional vector (BAAI/bge-small-en-v1.5)
  Metadata:
    - user_id: User identifier
    - subject_id: Subject identifier  
    - file_id: Source file identifier
    - filename: Original filename
    - page_number: Page number in PDF
    - chunk_index: Chunk sequence number
    - chunk_type: text/table/formula/definition
    - text: Truncated chunk text (first 1000 chars)
  ```

---

## 🔄 RAG Pipeline Flow

### 1. **PDF Upload & Processing**

```
User uploads PDF
    ↓
Store file metadata in MongoDB (UploadedFile)
    ↓
Extract text using PyMuPDF + PDFPlumber
    ↓
Clean and preprocess text
    ↓
Split into semantic chunks (LangChain RecursiveTextSplitter)
    ↓
Generate embeddings (Sentence Transformers)
    ↓
Store vectors in Pinecone with metadata
    ↓
Store chunk metadata in MongoDB (VectorMetadata)
    ↓
Link vector IDs back to UploadedFile document
```

### 2. **Query & Retrieval**

```
User asks question in chat
    ↓
Generate query embedding
    ↓
Search Pinecone for similar vectors
  - Filter by subject_id
  - Top-k results (default: 5)
  - Cosine similarity
    ↓
Retrieve vector IDs from Pinecone
    ↓
Fetch full chunk text from MongoDB (VectorMetadata)
    ↓
Retrieve additional context (context_before, context_after)
    ↓
Format context for LLM
    ↓
Send to LLM (Google Gemini / OpenAI)
    ↓
Generate response with citations
    ↓
Store in MongoDB (ChatHistory)
```

### 3. **Why MongoDB + Pinecone?**

#### **MongoDB Advantages**:
- ✅ Stores full chunk text (no size limits)
- ✅ Flexible schema for diverse content types
- ✅ Fast document lookups by ID
- ✅ Rich metadata storage
- ✅ Context window preservation
- ✅ Easy to query and aggregate
- ✅ Supports complex relationships

#### **Pinecone Advantages**:
- ✅ Optimized vector similarity search
- ✅ Fast approximate nearest neighbor (ANN)
- ✅ Scales to millions of vectors
- ✅ Metadata filtering
- ✅ Real-time updates
- ✅ Managed service (no infrastructure)

#### **Combined Benefits**:
1. **Pinecone** handles vector search (what it's best at)
2. **MongoDB** stores full text and rich metadata (what it's best at)
3. Vector ID serves as the bridge between systems
4. Best of both worlds: Fast retrieval + Rich context

---

## 📊 Data Flow Example

### Example: User asks "Explain deadlock in OS"

1. **Query Processing**:
   ```python
   query = "Explain deadlock in OS"
   query_embedding = embedding_service.generate_embedding(query)
   ```

2. **Pinecone Search**:
   ```python
   results = pinecone_index.query(
       vector=query_embedding,
       top_k=5,
       filter={"subject_id": "507f1f77bcf86cd799439011"}
   )
   # Returns: [
   #   {"id": "vec_001", "score": 0.92, "metadata": {...}},
   #   {"id": "vec_002", "score": 0.88, "metadata": {...}},
   # ]
   ```

3. **MongoDB Retrieval**:
   ```python
   vector_ids = [r["id"] for r in results]
   chunks = await VectorMetadata.find(
       {"vector_id": {"$in": vector_ids}}
   ).to_list()
   # Returns full chunk text + context
   ```

4. **Context Assembly**:
   ```python
   context = "\n\n".join([
       f"{chunk.context_before}\n{chunk.chunk_text}\n{chunk.context_after}"
       for chunk in chunks
   ])
   ```

5. **LLM Generation**:
   ```python
   response = llm_service.generate_with_context(
       query=query,
       context=context,
       chat_history=previous_messages
   )
   ```

6. **Response Storage**:
   ```python
   chat_message = ChatHistory(
       subject_id=subject_id,
       role="assistant",
       message=response,
       context_used=chunks,
       citations=[...],
       confidence_score=0.90,
       vector_ids_used=vector_ids
   )
   await chat_message.save()
   ```

---

## 🎯 Key Features Implementation

### **1. Subject-Wise Isolation**
- Each subject gets its own namespace in Pinecone (via `subject_id` filter)
- MongoDB queries filter by `subject_id`
- No cross-contamination between subjects

### **2. Incremental Updates**
- New PDFs are processed independently
- Vectors added to existing Pinecone index
- MongoDB documents created for new chunks
- No need to rebuild entire index

### **3. Efficient Deletion**
- Delete subject: Remove Pinecone vectors + MongoDB documents
- Delete file: Remove specific vectors + metadata
- Cascade deletes handled by MongoDB

### **4. Context Preservation**
- MongoDB stores `context_before` and `context_after`
- Provides surrounding text for better LLM understanding
- Pinecone metadata stores truncated text for quick reference

### **5. Citation Tracking**
- Vector IDs link responses to source chunks
- MongoDB provides filename, page number
- Full chain of custody for all generated content

---

## 🔧 Configuration

### MongoDB Connection
```env
MONGODB_URL=mongodb://localhost:27017/studyai
# Or MongoDB Atlas
MONGODB_URL=mongodb+srv://user:pass@cluster.mongodb.net/studyai
```

### Pinecone Configuration
```env
PINECONE_API_KEY=your-api-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=studyai-embeddings
EMBEDDING_DIMENSION=384
```

### Embedding Model
```env
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

---

## 📈 Performance Characteristics

| Operation | Latency | Scaling |
|-----------|---------|---------|
| Vector search (Pinecone) | ~50-100ms | Millions of vectors |
| Metadata fetch (MongoDB) | ~10-20ms | Unlimited documents |
| End-to-end query | ~200-500ms | Handles concurrent users |
| PDF processing | ~1-5s per page | Async/background jobs |

---

## 🔐 Security

- MongoDB: Document-level access control via `user_id`
- Pinecone: Namespace isolation via `subject_id` filter
- All queries filtered by authenticated user
- No cross-user data leakage

---

## 🚀 Deployment

### MongoDB
- Local: Docker container
- Production: MongoDB Atlas (recommended)

### Pinecone
- Managed service (Pinecone Cloud)
- No infrastructure management needed

### Application
- FastAPI backend: Render / Railway / AWS
- Automatic scaling based on load

---

## 📝 Summary

This architecture leverages the strengths of both systems:
- **Pinecone**: Lightning-fast vector similarity search
- **MongoDB**: Flexible document storage with rich metadata

The result is a scalable, maintainable RAG system that can handle:
- ✅ Millions of document chunks
- ✅ Thousands of concurrent users
- ✅ Complex metadata queries
- ✅ Real-time updates
- ✅ Subject-wise isolation
- ✅ Full citation tracking
