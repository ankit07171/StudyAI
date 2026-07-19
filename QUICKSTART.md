# 🚀 AI Study Assistant - Quick Start Guide

Get the application running in 10 minutes!

## ⚡ Prerequisites

```powershell
# Check Python version (need 3.10+)
python --version

# Check if MongoDB is installed
mongosh --version

# If not installed, install MongoDB Community Server
# Download from: https://www.mongodb.com/try/download/community
```

## 📦 1. Quick Setup (5 minutes)

### Install Backend Dependencies

```powershell
cd backend

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install all dependencies
pip install -r requirements.txt
```

### Setup Environment

```powershell
# Copy environment template
Copy-Item .env.example .env
```

**Edit `.env` with minimum required settings:**

```env
# MongoDB (local)
MONGODB_URL=mongodb://localhost:27017/studyai

# Pinecone (sign up at pinecone.io)
PINECONE_API_KEY=your-key-here
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=studyai-embeddings

# Google Gemini (free at makersuite.google.com)
GOOGLE_API_KEY=your-key-here

# JWT Secret (any random string 32+ chars)
SECRET_KEY=your-secret-key-change-this-min-32-characters

# CORS
CORS_ORIGINS=http://localhost:3000
```

### Create Directories

```powershell
New-Item -ItemType Directory -Force -Path uploads, logs
```

## 🚀 2. Start MongoDB (1 minute)

```powershell
# Start MongoDB service (Windows)
net start MongoDB

# Or run mongod directly
mongod --dbpath C:\data\db

# Verify it's running
mongosh
# Type: db.runCommand({ ping: 1 })
# Should see: { ok: 1 }
```

## 🎯 3. Create Pinecone Index (2 minutes)

1. Go to https://www.pinecone.io/
2. Sign up (free tier available)
3. Create new index:
   - **Name**: `studyai-embeddings`
   - **Dimensions**: `384`
   - **Metric**: `cosine`
4. Copy API key and environment name
5. Update `.env` file

## 🔑 4. Get Gemini API Key (2 minutes)

1. Go to https://makersuite.google.com/app/apikey
2. Click "Create API Key"
3. Copy the key
4. Update `.env` file

## ▶️ 5. Run the Application

```powershell
# Make sure you're in backend directory and venv is activated
python main.py
```

**You should see:**
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Connected to MongoDB successfully
INFO:     Pinecone connected: studyai-embeddings
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## ✅ 6. Test It!

### Open your browser:

**API Documentation**: http://localhost:8000/api/docs

**Health Check**: http://localhost:8000/health

### Test Registration:

1. Go to http://localhost:8000/api/docs
2. Expand `POST /api/v1/auth/register`
3. Click "Try it out"
4. Enter:
```json
{
  "email": "test@example.com",
  "username": "testuser",
  "password": "TestPass123",
  "full_name": "Test User"
}
```
5. Click "Execute"
6. Should get `200` response with tokens!

### Test Subject Creation:

1. Copy the `access_token` from registration response
2. Expand `POST /api/v1/subjects/`
3. Click "Try it out"
4. Click "Authorize" (padlock icon)
5. Paste token: `Bearer <your-token>`
6. Enter subject data:
```json
{
  "name": "Operating System",
  "code": "CS301",
  "semester": "Semester 5",
  "description": "OS concepts and implementation"
}
```
7. Click "Execute"
8. Subject created! ✅

## 🎉 Success!

Your backend is running! Now you can:

1. **Upload PDFs** via API
2. **Chat with your documents**
3. **Generate study materials**

---

## 🔧 Common Issues

### "MongoDB connection failed"
```powershell
# Start MongoDB
net start MongoDB

# Or check if it's running
tasklist | findstr mongod
```

### "Pinecone IndexNotFoundError"
- Go to Pinecone dashboard
- Create index with exact name: `studyai-embeddings`
- Dimensions: 384, Metric: cosine

### "Port 8000 already in use"
```powershell
# Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <process-id> /F

# Or use different port
uvicorn main:app --port 8001
```

---

## 📖 Next Steps

### For Development:
1. Check `SETUP_GUIDE.md` for detailed setup
2. Read `ARCHITECTURE_MONGODB_PINECONE.md` for system design
3. Review `PROJECT_STATUS.md` for features

### For Testing:
```powershell
# Test PDF upload
curl -X POST http://localhost:8000/api/v1/upload/ `
  -H "Authorization: Bearer <your-token>" `
  -F "file=@your-file.pdf" `
  -F "subject_id=<subject-id>"
```

### For Frontend:
- Frontend setup coming next!
- Will use Next.js + Tailwind + Shadcn UI

---

## 🆘 Need Help?

1. Check API docs: http://localhost:8000/api/docs
2. View logs: `backend/logs/app.log`
3. Test health: http://localhost:8000/health

---

**Happy Coding! 🚀**
