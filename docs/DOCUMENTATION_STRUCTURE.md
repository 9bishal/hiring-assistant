# Documentation Structure

This project follows a **clean separation of concerns**: code is kept lean and focused, while explanations live in dedicated documentation files.

## Files → Documentation Mapping

### Agent Files
All agent files (`agents/*.py`) now contain **only executable code** with no lengthy docstrings. Instead, agent documentation is in:

📄 **`docs/AGENTS.md`** — Complete agent descriptions
- Agent 1: Job Analyzer
- Agent 2: Resume Screener  
- Agent 3: Question Generator
- Agent 4: Report Writer

Each agent section includes:
- What it does
- Why it's structured that way
- How to explain it to HR
- Input/Output state variables
- Key constants and thresholds

### Application Files
| File | Purpose | Doc Location |
|------|---------|--------------|
| `app.py` | Streamlit UI | `README.md` Features section |
| `test_run.py` | Terminal test script | This file (see below) |
| `graph/workflow.py` | LangGraph workflow orchestration | `docs/ARCHITECTURE.md` |
| `graph/state.py` | Shared state definition | `docs/ARCHITECTURE.md` |
| `evaluation/evaluator.py` | LLM-as-Judge evaluation | `docs/EVALUATION.md` |
| `tools/pdf_parser.py` | PDF parsing utility | `docs/SETUP.md` |
| `tools/vector_store.py` | ChromaDB integration | `docs/SETUP.md` |

### Other Documentation
- **`docs/ARCHITECTURE.md`** — System design, LangGraph workflow, state management
- **`docs/EVALUATION.md`** — How evaluation scoring works
- **`docs/SETUP.md`** — Environment setup, dependencies, configuration
- **`docs/HOW_TO_EXPLAIN.md`** — Talking points for non-technical stakeholders

## Why This Structure?

✅ **Cleaner code** — No massive docstrings at the top of files  
✅ **Easier navigation** — All agent info in one place  
✅ **Better for GitHub** — Professional documentation structure  
✅ **No code duplication** — Explanations are written once  
✅ **Easy to keep updated** — Update docs independently from code

## Quick Reference

To understand **Agent 2 (Resume Screener)**:
- → Read `docs/AGENTS.md` → "Agent 2 — Resume Screener" section
- → Then look at `agents/resume_screener.py` code

To understand **how the workflow orchestrates agents**:
- → Read `docs/ARCHITECTURE.md` → "Workflow" section
- → Then look at `graph/workflow.py` code

To understand **evaluation scoring**:
- → Read `docs/EVALUATION.md`
- → Then look at `evaluation/evaluator.py` code

## Testing

**Terminal test** (no PDFs needed):
```bash
python test_run.py
```

This uses hardcoded sample JD + resume texts. Good for:
- Verifying the full pipeline works
- Testing without uploading files
- Development and debugging

**Streamlit UI**:
```bash
streamlit run app.py
```

---

**Last updated:** June 2026
