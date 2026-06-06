# Setup Guide

## Prerequisites
- Python 3.10+
- Free Groq API key → https://console.groq.com/keys

---

## Local Setup

```bash
# 1. Clone
git clone https://github.com/yourusername/hiring-assistant
cd hiring-assistant

# 2. Virtual environment
python -m venv venv
source venv/bin/activate      # Mac/Linux
# venv\Scripts\activate       # Windows

# 3. Install
pip install -r requirements.txt

# 4. API key
cp .env.example .env
# Open .env and set: GROQ_API_KEY=gsk_your_key

# 5. Terminal test (always run before UI)
python test_run.py

# 6. Launch UI
streamlit run app.py
# Opens at http://localhost:8501
```

---

## Deploying to Streamlit Cloud (Free)

1. Push to a **public** GitHub repo
2. Go to https://share.streamlit.io → New app
3. Select repo, set main file: `app.py`
4. Go to **Advanced → Secrets**, add:
   ```
   GROQ_API_KEY = "gsk_your_key"
   ```
5. Deploy — live URL in ~2 minutes

---

## Common Errors

### `ModuleNotFoundError: No module named 'fitz'`
```bash
pip install pymupdf
```

### `ModuleNotFoundError: No module named 'langchain_groq'`
```bash
pip install langchain-groq
```

### `chromadb error: collection already exists`
This is handled automatically. Each session uses a unique collection ID.

### `ImportError: cannot import name 'MemorySaver' from 'langgraph'`
```bash
pip install --upgrade langgraph
```
