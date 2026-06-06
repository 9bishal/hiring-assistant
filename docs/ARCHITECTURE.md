# Architecture Deep Dive

## The Big Picture

4 agents + 1 evaluator, connected by a LangGraph StateGraph.
All agents read from and write to a single shared `HiringState` object.

```
                    ┌──────────────────────────────────┐
                    │          HiringState              │
                    │                                   │
                    │  job_description   (input)        │
                    │  resume_texts      (input)        │
                    │  resume_names      (input)        │
                    │                                   │
                    │  required_skills   ← Analyzer     │
                    │  preferred_skills  ← Analyzer     │
                    │  experience_needed ← Analyzer     │
                    │  role_summary      ← Analyzer     │
                    │                                   │
                    │  all_candidates    ← Screener     │
                    │  shortlisted       ← Screener     │
                    │                                   │
                    │  interview_questions ← QuestionGen│
                    │                                   │
                    │  hiring_report     ← Writer       │
                    │                                   │
                    │  analyzer_score    ← Evaluator    │
                    │  screener_score    ← Evaluator    │
                    │  writer_score      ← Evaluator    │
                    │  overall_score     ← Evaluator    │
                    └──────────────────────────────────┘
```

---

## The LangGraph Graph 

```python
graph = StateGraph(HiringState)

graph.add_node("job_analyzer",       job_analyzer_agent)
graph.add_node("resume_screener",    resume_screener_agent)
graph.add_node("question_generator", question_generator_agent)
graph.add_node("report_writer",      report_writer_agent)
graph.add_node("evaluator",          evaluator_node)

graph.set_entry_point("job_analyzer")

graph.add_edge("job_analyzer",       "resume_screener")
graph.add_edge("resume_screener",    "question_generator")
graph.add_edge("question_generator", "report_writer")
graph.add_edge("report_writer",      "evaluator")
graph.add_edge("evaluator",          END)
```

Every agent is just a Python function: `(state: HiringState) -> dict`
The dict it returns is merged into State automatically by LangGraph.

---

## Agent Breakdown

### Agent 1 — Job Analyzer
**Input:** `state["job_description"]`
**Process:** Single LLM call with a JSON-structured prompt
**Output:** `required_skills`, `preferred_skills`, `experience_needed`, `role_summary`
**Why separate:** Extracts requirements once — all downstream agents use these
structured fields instead of re-reading the raw JD text every time.

---

### Agent 2 — Resume Screener
**Input:** `resume_texts`, `resume_names`, `required_skills`, `preferred_skills`
**Process:** Two-stage pipeline

```
Stage 1: ChromaDB Semantic Search
  - Embed all resumes with sentence-transformers (all-MiniLM-L6-v2)
  - Embed the JD
  - Compute cosine similarity for each resume vs JD
  - Get initial semantic ranking

Stage 2: LLM Deep Assessment
  - For each resume, send to Groq LLM with structured scoring prompt
  - Score: 0-10 with strengths, gaps, and one-line verdict

Final Score = LLM score (80%) + semantic score (20%)
```

**Why two stages?**
- Semantic search is fast and catches vocabulary variation
- LLM assessment adds qualitative depth
- Combining both gives a more robust score than either alone

**Output:** `all_candidates` (sorted by score), `shortlisted` (score ≥ 6.0)

---

### Agent 3 — Question Generator
**Input:** `shortlisted`, `required_skills`, `role_summary`
**Process:** One LLM call per shortlisted candidate
**Output:** `interview_questions` — dict of `{ candidate_name: [6 questions] }`

Question breakdown per candidate:
- 3 technical questions validating their claimed strengths
- 2 gap-probing questions addressing their weaknesses
- 1 behavioural question for the role

---

### Agent 4 — Report Writer
**Input:** Everything in State (JD requirements + all candidates + questions)
**Process:** Single LLM call with a fully structured prompt template
**Output:** `hiring_report` — complete markdown document

---

### Evaluator — LLM-as-Judge
**Input:** Three key outputs (analyzer, screener, writer)
**Process:** 3 independent LLM scoring calls, one per agent
**Output:** `analyzer_score`, `screener_score`, `writer_score`, `overall_score`

---

## Tools

### tools/pdf_parser.py
Uses `PyMuPDF (fitz)` to extract text from PDF files.
- Handles multi-page PDFs
- Cleans whitespace
- Works on uploaded Streamlit files (bytes) and local paths

### tools/vector_store.py
Uses `ChromaDB` with `sentence-transformers` for semantic search.
- `store_resumes()` — embeds and stores all resumes for a session
- `semantic_search()` — finds resumes most similar to a query
- Session-isolated with unique collection IDs
- Returns cosine similarity scores (0-1)

---

## Memory

```python
memory = MemorySaver()
graph = graph.compile(checkpointer=memory)

config = {"configurable": {"thread_id": "unique-session-id"}}
```

Each hiring session gets a unique `thread_id`.
LangGraph serializes the full HiringState after every node.
You can resume any session by reusing its `thread_id`.
