# ✅ Required Setup - Minimal Configuration

This guide shows ONLY the required configurations to get the application running.

---

## 📋 Required Services (4 items)

1. ✅ **MongoDB** - Database
2. ✅ **Pinecone** - Vector database  
3. ✅ **Google Gemini** - AI/LLM
4. ✅ **Email (Gmail)** - Password reset

**Optional services (commented out)**:
- ❌ Google OAuth - For social login (not required)
- ❌ OpenAI API - Alternative LLM (not required)
- ❌ Anthropic API - Alternative LLM (not required)
- ❌ Redis - For caching (not required)
- ❌ Celery - Background tasks (not required)

---

## 🔧 Minimal .env Configuration

Create `backend/.env` with these values:

```env
# ============================================
# REQUIRED SETTINGS
# ============================================

# Application
APP_NAME=AI Study Assistant
DEBUG=True
API_VERSION=v1

# MongoDB (Local)
MONGODB_URL=mongodb://localhost:27017/studyai

# JWT Secret (generate random 32+ character string)
SECRET_KEY=change-this-to-a-random-32-character-string-minimum

# Google Gemini API (FREE)
# Get from: https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your-gemini-api-key-here

# Pinecone Vector DB
# Sign up at: https://www.pinecone.io/
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=studyai-embeddings

# Email (Gmail for password reset)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=AI Study Assistant

# CORS (Frontend URL)
CORS_ORIGINS=http://localhost:3000
```

---

## 📧 Email Setup (Gmail)

### Why needed?
- Send password reset emails to users

### Quick Setup:

1. **Enable 2-Step Verification**
   - Go to: https://myaccount.google.com/security
   - Click "2-Step Verification" → Turn On

2. **Generate App Password**
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Name it: "StudyAI"
   - Copy the 16-character password (e.g., `abcd efgh ijkl mnop`)

3. **Update .env**
   ```env
   SMTP_USER=youremail@gmail.com
   SMTP_PASSWORD=abcdefghijklmnop  # No spaces!
   EMAIL_FROM=youremail@gmail.com
   ```

**Important**: Use the App Password, NOT your regular Gmail password!

---

## 🧪 Test Email Configuration

```python
# test_email.py
import smtplib
from email.mime.text import MIMEText

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password"

msg = MIMEText("Test email works! ✅")
msg['Subject'] = "Test from StudyAI"
msg['From'] = SMTP_USER
msg['To'] = SMTP_USER

server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
server.starttls()
server.login(SMTP_USER, SMTP_PASSWORD)
server.send_message(msg)
server.quit()
print("✅ Email sent successfully!")
```

Run: `python test_email.py`

---

## 📦 Install Dependencies

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## ▶️ Run Application

```powershell
# Start MongoDB
net start MongoDB

# Run backend
python main.py
```

Visit: http://localhost:8000/health

---

## ✅ Verification Checklist

- [ ] MongoDB running (`mongosh` connects)
- [ ] Pinecone index created (dimension: 384)
- [ ] Google Gemini API key obtained
- [ ] Gmail App Password generated
- [ ] Test email sent successfully
- [ ] `.env` file created with all required values
- [ ] Dependencies installed
- [ ] Server starts without errors
- [ ] Health check returns "healthy"

---

## 🎯 Summary

**Total cost**: FREE (all services have free tiers)

**Setup time**: ~15 minutes

**Required files**:
- `backend/.env` (copy from `.env.example`)

**Not required**:
- ❌ Redis installation
- ❌ Celery setup
- ❌ Google OAuth setup
- ❌ OpenAI account
- ❌ Anthropic account

---

For detailed email troubleshooting, see `EMAIL_SETUP.md`
