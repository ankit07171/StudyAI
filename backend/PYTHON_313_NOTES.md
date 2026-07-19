# 🐍 Python 3.13 Compatibility Notes

## ✅ Updated for Python 3.13

All dependencies have been updated to versions compatible with Python 3.13.

---

## 🔄 Key Changes from Original

### Pinecone Package Change

**Old (Python 3.8-3.12)**:
```
pinecone-client==3.0.2
```

**New (Python 3.13)**:
```
pinecone==5.0.1
```

**Important**: The package name changed from `pinecone-client` to `pinecone`

### API Changes in Pinecone v5

The initialization and usage also changed:

**Old API** (pinecone-client v3):
```python
import pinecone

pinecone.init(
    api_key="your-key",
    environment="us-west1-gcp"
)
index = pinecone.Index("index-name")
```

**New API** (pinecone v5) - ✅ Already Updated:
```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="your-key")
index = pc.Index("index-name")
```

---

## 📦 Pinecone Index Creation

### For Serverless (Recommended)

In Pinecone dashboard or via code:
- **Cloud**: AWS
- **Region**: us-east-1 (update in .env: `PINECONE_ENVIRONMENT=us-east-1`)
- **Dimensions**: 384
- **Metric**: cosine

**Updated .env**:
```env
PINECONE_ENVIRONMENT=us-east-1  # Changed from us-west1-gcp
```

---

## 🔧 Installation

```powershell
# Delete old virtual environment if it exists
Remove-Item -Recurse -Force venv

# Create fresh virtual environment
python -m venv venv

# Activate
.\venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

---

## 📋 All Updated Packages

| Package | Old Version | New Version | Notes |
|---------|-------------|-------------|-------|
| fastapi | 0.109.0 | 0.115.5 | Python 3.13 support |
| uvicorn | 0.27.0 | 0.32.1 | Updated |
| pydantic | 2.5.3 | 2.10.3 | Latest stable |
| motor | 3.3.2 | 3.6.0 | MongoDB async driver |
| beanie | 1.24.0 | 1.27.0 | MongoDB ODM |
| langchain | 0.1.4 | 0.3.13 | Major update |
| sentence-transformers | 2.3.1 | 3.3.1 | Python 3.13 compatible |
| **pinecone-client** | **3.0.2** | **Removed** | Deprecated |
| **pinecone** | **N/A** | **5.0.1** | New package |
| google-generativeai | 0.3.2 | 0.8.3 | Latest API |
| pymupdf | 1.23.21 | 1.24.14 | Updated |
| pillow | 10.2.0 | 11.0.0 | Latest |

---

## ⚠️ Removed Heavy Dependencies (Optional)

To reduce installation size and time, these are commented out:

```python
# transformers==4.46.3  # 2GB+ download
# torch==2.5.1          # 700MB+ download
```

**Why removed?**
- `sentence-transformers==3.3.1` includes lighter dependencies
- Only needed if you want to use custom transformer models
- Can be added later if needed

**If you need them**:
```powershell
pip install transformers torch
```

---

## 🔍 Verification

```powershell
# Check Python version
python --version
# Should show: Python 3.13.x

# Check Pinecone import
python -c "from pinecone import Pinecone; print('✅ Pinecone OK')"

# Check sentence-transformers
python -c "from sentence_transformers import SentenceTransformer; print('✅ Sentence Transformers OK')"

# Check all imports
python -c "import fastapi, motor, beanie, langchain, google.generativeai; print('✅ All imports OK')"
```

---

## 🚀 After Installation

1. **Update your .env**:
   ```env
   PINECONE_ENVIRONMENT=us-east-1  # New region for serverless
   ```

2. **Create Pinecone Index** (if not exists):
   - Go to https://app.pinecone.io/
   - Click "Create Index"
   - Name: `studyai-embeddings`
   - Dimensions: `384`
   - Metric: `cosine`
   - **Serverless**: AWS, us-east-1

3. **Run the application**:
   ```powershell
   python main.py
   ```

---

## 🐛 Troubleshooting

### Issue: `ImportError: cannot import name 'Pinecone'`

**Solution**: You installed old `pinecone-client` package
```powershell
pip uninstall pinecone-client
pip install pinecone==5.0.1
```

### Issue: `sentence-transformers` fails to install

**Solution**: Upgrade pip first
```powershell
python -m pip install --upgrade pip
pip install sentence-transformers==3.3.1
```

### Issue: `python-magic` fails on Windows

**Solution**: Use `python-magic-bin` instead (already in requirements.txt)
```powershell
pip install python-magic-bin==0.4.14
```

---

## ✅ Success Indicators

You'll know everything is working when:

1. ✅ All packages install without errors
2. ✅ `python main.py` starts without import errors
3. ✅ `/health` endpoint shows Pinecone stats
4. ✅ You can register a user
5. ✅ You can create a subject

---

## 📝 Summary

**Main Change**: `pinecone-client` → `pinecone` package

**New Region**: `us-west1-gcp` → `us-east-1` (serverless)

**All code updated**: ✅ `vector_store.py` already uses new API

**Ready to install**: Just run `pip install -r requirements.txt`
