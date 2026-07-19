# AI Study Assistant - Complete Setup Guide

## 📋 Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB (local or Atlas account)
- Pinecone account
- Google Gemini API key or OpenAI API key

---

## 🚀 Backend Setup

### 1. Install MongoDB

#### **Option A: Local MongoDB**
```bash
# Windows (using Chocolatey)
choco install mongodb

# Or download from https://www.mongodb.com/try/download/community
```

#### **Option B: MongoDB Atlas (Recommended)**
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get connection string
4. Whitelist your IP address

### 2. Setup Pinecone

1. Create account at https://www.pinecone.io/
2. Create a new index:
   - **Name**: `studyai-embeddings`
   - **Dimensions**: `384`
   - **Metric**: `cosine`
   - **Environment**: Choose your region
3. Copy API key and environment

### 3. Get LLM API Keys

#### **Google Gemini (Recommended)**
1. Go to https://makersuite.google.com/app/apikey
2. Create API key
3. Copy the key

#### **OpenAI (Alternative)**
1. Go to https://platform.openai.com/api-keys
2. Create API key
3. Copy the key

### 4. Install Backend Dependencies

```powershell
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Configure Environment

```powershell
# Copy example env file
Copy-Item .env.example .env

# Edit .env file with your actual credentials
notepad .env
```

**Update the following in `.env`**:
```env
# MongoDB
MONGODB_URL=mongodb://localhost:27017/studyai
# Or for Atlas: mongodb+srv://username:password@cluster.mongodb.net/studyai

# Pinecone
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=studyai-embeddings

# Google Gemini
GOOGLE_API_KEY=your-google-api-key

# JWT Secret (generate a secure random string)
SECRET_KEY=your-secret-key-min-32-characters-long

# CORS (update for production)
CORS_ORIGINS=http://localhost:3000
```

### 6. Create Required Directories

```powershell
# Create directories
New-Item -ItemType Directory -Force -Path uploads
New-Item -ItemType Directory -Force -Path logs
```

### 7. Run Backend Server

```powershell
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/api/docs
- **Health**: http://localhost:8000/health

---

## 🎨 Frontend Setup (Next Steps)

### 1. Create Next.js App

```powershell
cd ..
npx create-next-app@latest frontend --typescript --tailwind --app

cd frontend
```

### 2. Install Dependencies

```powershell
npm install @tanstack/react-query axios
npm install @radix-ui/react-dialog @radix-ui/react-dropdown-menu
npm install framer-motion
npm install react-hook-form @hookform/resolvers zod
npm install lucide-react
npm install recharts
npm install date-fns

# Install Shadcn UI
npx shadcn-ui@latest init
npx shadcn-ui@latest add button card input label textarea dialog dropdown-menu
```

---

## 🧪 Testing the Setup

### 1. Test MongoDB Connection

```powershell
# In Python
python
```

```python
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

async def test_mongo():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.studyai
    await db.command("ping")
    print("MongoDB connected!")
    
asyncio.run(test_mongo())
```

### 2. Test Pinecone Connection

```python
import pinecone

pinecone.init(
    api_key="your-key",
    environment="your-env"
)

indexes = pinecone.list_indexes()
print("Pinecone indexes:", indexes)
```

### 3. Test API Endpoints

```powershell
# Test health endpoint
curl http://localhost:8000/health

# Test registration
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "TestPass123",
    "full_name": "Test User"
  }'
```

---

## 📁 Project Structure

```
StudyAI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── api.py
│   │   │       └── endpoints/
│   │   │           ├── auth.py
│   │   │           ├── subjects.py
│   │   │           ├── upload.py
│   │   │           ├── chat.py
│   │   │           └── ...
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── database.py
│   │   │   └── security.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── subject.py
│   │   │   └── ...
│   │   ├── schemas/
│   │   │   ├── user.py
│   │   │   └── ...
│   │   └── services/
│   │       ├── llm/
│   │       │   └── llm_service.py
│   │       └── rag/
│   │           ├── pdf_processor.py
│   │           ├── embeddings.py
│   │           ├── chunking.py
│   │           ├── vector_store.py
│   │           └── retriever.py
│   ├── main.py
│   ├── requirements.txt
│   └── .env
├── frontend/ (to be created)
├── uploads/
├── logs/
└── README.md
```

---

## 🔧 Troubleshooting

### MongoDB Connection Issues

**Error**: `ServerSelectionTimeoutError`

**Solutions**:
1. Check if MongoDB is running: `mongosh`
2. Verify connection string in `.env`
3. For Atlas: Check IP whitelist

### Pinecone Issues

**Error**: `IndexNotFoundError`

**Solutions**:
1. Create index in Pinecone dashboard
2. Verify index name matches `.env`
3. Check API key is correct

### Import Errors

**Error**: `ModuleNotFoundError`

**Solutions**:
```powershell
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or update pip
python -m pip install --upgrade pip
```

### Port Already in Use

**Error**: `Address already in use`

**Solutions**:
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <process_id> /F

# Or use different port
uvicorn main:app --port 8001
```

---

## 🌐 API Documentation

Once the server is running, visit:

**Swagger UI**: http://localhost:8000/api/docs

This provides interactive API documentation where you can:
- View all endpoints
- Test API calls
- See request/response schemas
- Download OpenAPI spec

---

## 📊 Database Schema

### MongoDB Collections

#### **users**
- email, username, hashed_password
- is_active, is_verified
- Authentication tokens

#### **subjects**
- user_id, name, code, semester
- total_pdfs, total_pages
- Timestamps

#### **uploaded_files**
- subject_id, filename, file_path
- total_pages, total_words
- vector_ids (array of Pinecone IDs)
- Processing status

#### **vector_metadata**
- vector_id (Pinecone reference)
- file_id, subject_id
- chunk_text, page_number
- context_before, context_after

#### **chat_history**
- subject_id, role, message
- citations, confidence_score
- vector_ids_used

### Pinecone Index

**Vectors**: 384-dimensional embeddings

**Metadata**:
- user_id, subject_id, file_id
- filename, page_number, chunk_index
- chunk_type, text (truncated)

---

## 🚦 Next Steps

1. ✅ Backend setup complete
2. 🔄 Create frontend application
3. 🔄 Implement PDF upload UI
4. 🔄 Build chat interface
5. 🔄 Create dashboard
6. 🔄 Deploy to production

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check MongoDB and Pinecone dashboards
4. Verify environment variables

---

## 🎉 Success!

If you can:
- ✅ Visit http://localhost:8000/health and see `"status": "healthy"`
- ✅ Create a user via `/api/v1/auth/register`
- ✅ Login and receive JWT tokens

**Your backend is ready!** 🚀

Now you can proceed with frontend development and PDF upload implementation.
