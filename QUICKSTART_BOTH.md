# ⚡ Quick Start - Run Both Backend & Frontend

## 🎯 Prerequisites Check

```powershell
# Check Python
python --version  # Should be 3.13+

# Check Node.js
node --version  # Should be 18+

# Check MongoDB
mongosh  # Should connect

# Check npm
npm --version
```

---

## 🚀 Quick Setup (5 minutes)

### Step 1: Backend Setup
```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure .env (edit with your values)
Copy-Item .env.example .env

# Create directories
New-Item -ItemType Directory -Force -Path uploads, logs

# Start backend
python main.py
```

**Leave this terminal running!**

---

### Step 2: Frontend Setup (New Terminal)
```powershell
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run frontend
npm run dev
```

**Leave this terminal running too!**

---

## ✅ Verify Everything Works

1. **Backend Check:**
   - Visit: http://localhost:8000/health
   - Should see: `{"status": "healthy"}`

2. **Frontend Check:**
   - Visit: http://localhost:3000
   - Should see: Beautiful landing page

3. **Test Login:**
   - Go to http://localhost:3000/auth/login
   - Try logging in

---

## 🎯 Create Your First User

### Option 1: Via Frontend
1. Visit: http://localhost:3000
2. Click "Get Started"
3. Fill registration form
4. Submit

### Option 2: Via API Docs
1. Visit: http://localhost:8000/api/docs
2. Expand `POST /api/v1/auth/register`
3. Click "Try it out"
4. Enter user data
5. Execute

### Option 3: Via curl
```powershell
curl -X POST http://localhost:8000/api/v1/auth/register `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "Test123!@#",
    "full_name": "Test User"
  }'
```

---

## 📊 System Status

### Both Running Successfully:

**Terminal 1 (Backend):**
```
INFO:     Connected to MongoDB successfully
INFO:     Pinecone connected
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Terminal 2 (Frontend):**
```
▲ Next.js 15.1.3
- Local:        http://localhost:3000
✓ Ready in 2.5s
```

---

## 🧪 Quick Test

1. **Register User:**
   - Frontend: http://localhost:3000
   - Click "Get Started"

2. **Login:**
   - Use registered credentials
   - Should redirect to dashboard

3. **Check Token:**
   - Open browser DevTools (F12)
   - Console: `localStorage.getItem('token')`
   - Should see JWT token

---

## 🛑 Stop Services

```powershell
# In each terminal, press:
Ctrl + C
```

---

## 🎉 You're All Set!

**Backend:** ✅ Running on port 8000  
**Frontend:** ✅ Running on port 3000  
**MongoDB:** ✅ Connected  
**Pinecone:** ✅ Connected  

**Next:** Start building features! 🚀
