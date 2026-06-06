# 🧑‍💼 AI Hiring Assistant — Multi-Agent System

> **4 specialized AI agents + ChromaDB semantic search + LLM-as-Judge evaluation**

**Live Demo:** [your-app.streamlit.app](#) ← update after deploy
**GitHub:** [github.com/yourusername/hiring-assistant](#)

---

## What it does

Upload a job description + multiple resumes → 4 AI agents collaborate to screen
candidates, generate tailored interview questions, and produce a hiring report.

```
JD + Resumes
     │
     ▼
🔍 Job Analyzer      →  Extracts required/preferred skills, experience, role summary
     │
     ▼
📊 Resume Screener   →  ChromaDB semantic similarity + LLM deep assessment → Score 0-10
     │
     ▼
❓ Question Gen      →  6 personalized interview questions per shortlisted candidate
     │
     ▼
📝 Report Writer     →  Full hiring report: rankings, analysis, recommendations
     │
     ▼
⭐ Evaluator         →  LLM-as-Judge scores each agent output independently
```

---

## Impressive Features (10-12 LPA signal)

| Feature | Why it matters |
|---------|---------------|
| **Two-stage screening** | ChromaDB vector similarity + LLM deep assessment — mirrors enterprise ATS |
| **Semantic search** | Catches skill synonyms ("built ML models" ≈ "developed machine learning pipelines") |
| **Personalized questions** | Questions probe each candidate's specific gaps, not generic questions |
| **LLM-as-Judge evaluation** | Independent quality scoring — production AI monitoring pattern |
| **Typed shared state** | `HiringState` TypedDict — every agent's I/O is explicit and testable |
| **Session memory** | LangGraph MemorySaver — sessions are isolated and persistent |

---

## File Structure

```
hiring-assistant/
├── agents/
│   ├── job_analyzer.py        ← Agent 1: parse JD into structured requirements
│   ├── resume_screener.py     ← Agent 2: ChromaDB + LLM candidate scoring
│   ├── question_generator.py  ← Agent 3: personalized interview questions
│   └── report_writer.py       ← Agent 4: full hiring report
├── graph/
│   ├── state.py               ← HiringState TypedDict (shared memory)
│   └── workflow.py            ← LangGraph StateGraph + MemorySaver
├── tools/
│   ├── pdf_parser.py          ← PyMuPDF PDF text extraction
│   └── vector_store.py        ← ChromaDB semantic search
├── evaluation/
│   └── evaluator.py           ← LLM-as-Judge scoring node
├── docs/
│   ├── ARCHITECTURE.md        ← Deep technical breakdown
│   ├── HOW_TO_EXPLAIN.md      ← Interview prep (read before every interview)
│   ├── EVALUATION.md          ← Evaluation methodology
│   └── SETUP.md               ← Local + deployment setup
├── app.py                     ← Streamlit UI
├── test_run.py                ← Terminal test (run first)
└── requirements.txt
```

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Orchestration | **LangGraph** StateGraph |
| LLM | **Groq** LLaMA 3.3 70B (free) |
| Semantic Search | **ChromaDB** + sentence-transformers |
| PDF Parsing | **PyMuPDF** (fitz) |
| Evaluation | **LLM-as-Judge** pattern |
| UI | **Streamlit** + Plotly |
| Memory | **LangGraph MemorySaver** |

---

## Quick Start

```bash
git clone https://github.com/yourusername/hiring-assistant
cd hiring-assistant
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # add GROQ_API_KEY
python test_run.py          # test pipeline in terminal
streamlit run app.py        # launch UI
```

---

## Key Metrics

- Screens N resumes in ~30-45 seconds (3 resumes)
- Two-stage scoring: vector similarity + LLM assessment
- Shortlist threshold: score ≥ 6.0 / 10
- Generates 6 personalized questions per shortlisted candidate
- Overall pipeline score via weighted LLM-as-Judge evaluation
