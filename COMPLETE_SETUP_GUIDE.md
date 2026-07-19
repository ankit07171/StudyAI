# 🚀 Complete AI Study Assistant Setup Guide

## Overview

This guide will help you run both the **backend** (FastAPI) and **frontend** (Next.js) together.

---

## ✅ Prerequisites

- Python 3.13+
- Node.js 18+
- MongoDB (local or Atlas)
- Pinecone account
- Google Gemini API key

---

## 📦 Part 1: Backend Setup

### 1. Navigate to backend
```powershell
cd backend
```

### 2. Create and activate virtual environment
```powershell
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install dependencies
```powershell
pip install -r requirements.txt
```

### 4. Configure `.env`
```powershell
# Copy example
Copy-Item .env.example .env

# Edit .env with your values
notepad .env
```

**Required values:**
- `MONGODB_URL` - Your MongoDB connection string (encode special characters!)
- `SECRET_KEY` - Random 32+ character string
- `GOOGLE_API_KEY` - Google Gemini API key
- `PINECONE_API_KEY` - Pinecone API key
- `SMTP_USER` & `SMTP_PASSWORD` - Gmail credentials

### 5. Create directories
```powershell
New-Item -ItemType Directory -Force -Path uploads, logs
```

### 6. Start MongoDB
```powershell
net start MongoDB
```

### 7. Run backend
```powershell
python main.py
```

**Backend will run on:** http://localhost:8000

**API Docs:** http://localhost:8000/api/docs

---

## 🎨 Part 2: Frontend Setup

### 1. Open new terminal and navigate to frontend
```powershell
cd frontend
```

### 2. Install dependencies
```powershell
npm install
```

### 3. Configure `.env.local`
Already created with:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

### 4. Run frontend
```powershell
npm run dev
```

**Frontend will run on:** http://localhost:3000

---

## 🧪 Testing the Application

### 1. Open Frontend
Visit: http://localhost:3000

### 2. Register a User
1. Click "Get Started" or "Sign Up"
2. Fill in registration form
3. Submit

### 3. Login
1. Use registered credentials
2. Click "Sign In"

### 4. Test API
Visit backend docs: http://localhost:8000/api/docs

---

## 📊 Architecture

```
┌─────────────────┐         ┌──────────────────┐
│                 │         │                  │
│  Next.js        │────────▶│  FastAPI         │
│  Frontend       │  HTTP   │  Backend         │
│  Port: 3000     │  API    │  Port: 8000      │
│                 │◀────────│                  │
└─────────────────┘         └──────────────────┘
                                    │
                        ┌───────────┼───────────┐
                        │           │           │
                   ┌────▼────┐ ┌───▼────┐ ┌───▼─────┐
                   │ MongoDB │ │Pinecone│ │  Gemini │
                   │  Atlas  │ │ Vector │ │   API   │
                   └─────────┘ └────────┘ └─────────┘
```

---

## 🔧 Development Workflow

### Terminal 1: Backend
```powershell
cd backend
.\.venv\Scripts\activate
python main.py
```

### Terminal 2: Frontend
```powershell
cd frontend
npm run dev
```

### View logs
- Backend: `backend/logs/app.log`
- Frontend: Terminal output

---

## 🎯 Quick Test Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 3000
- [ ] MongoDB connected
- [ ] Pinecone connected
- [ ] Can access http://localhost:3000
- [ ] Can access http://localhost:8000/api/docs
- [ ] Can register a new user
- [ ] Can login with credentials
- [ ] Token stored in localStorage

---

## 🐛 Common Issues

### Port 8000 already in use
```powershell
netstat -ano | findstr :8000
taskkill /PID <process-id> /F
```

### Port 3000 already in use
```powershell
netstat -ano | findstr :3000
taskkill /PID <process-id> /F
# Or use different port
npm run dev -- -p 3001
```

### MongoDB connection error
- Check if MongoDB is running: `mongosh`
- Verify connection string in `.env`
- Encode special characters in password (@ becomes %40)

### CORS error
- Backend must be running before frontend
- Check `CORS_ORIGINS` in backend `.env`
- Should include `http://localhost:3000`

---

## 📝 API Endpoints Available

### Authentication
- POST `/api/v1/auth/register` - Register user
- POST `/api/v1/auth/login` - Login user
- GET `/api/v1/users/me` - Get current user

### Subjects
- POST `/api/v1/subjects/` - Create subject
- GET `/api/v1/subjects/` - List subjects
- GET `/api/v1/subjects/{id}` - Get subject
- PUT `/api/v1/subjects/{id}` - Update subject
- DELETE `/api/v1/subjects/{id}` - Delete subject

### Other Endpoints (501 Not Implemented)
- Upload, Chat, Notes, Quiz, etc.

---

## ✨ Next Development Steps

1. **Complete Frontend Pages:**
   - Registration page
   - Dashboard
   - Subject detail page
   - PDF upload interface

2. **Implement Backend Endpoints:**
   - PDF upload & processing
   - Chat with RAG
   - Notes generation
   - Quiz generation

3. **Connect Everything:**
   - Upload PDFs from frontend
   - Chat interface
   - Display generated content

---

## 🎉 Success Indicators

You're all set when you see:

**Backend:**
```
INFO:     Connected to MongoDB successfully
INFO:     Pinecone connected: studyai-embeddings
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Frontend:**
```
▲ Next.js 15.1.3
- Local:        http://localhost:3000
✓ Ready in 2.5s
```

**Browser:**
- Beautiful dark theme landing page
- Working login/register forms
- API calls successful

---

**Both systems are ready! Start building amazing features! 🚀**
