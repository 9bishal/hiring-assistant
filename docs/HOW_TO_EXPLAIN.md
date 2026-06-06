# How to Explain This Project in Interviews

> Read this the night before every interview. Practice the pitch out loud.

---

## 30-Second Pitch

> "I built an AI hiring assistant using LangGraph where 4 specialized agents
> collaborate to automate candidate screening. A Job Analyzer extracts structured
> requirements from the JD. A Resume Screener uses ChromaDB semantic search plus
> an LLM assessment to score every candidate from 0 to 10. A Question Generator
> creates 6 personalized interview questions per shortlisted candidate — specifically
> probing their identified gaps. And a Report Writer produces a complete hiring report.
> The whole pipeline is evaluated using the LLM-as-Judge pattern, which scores each
> agent's output quality independently. It's deployed on Streamlit with a live
> scoring dashboard."

---

## Q&A — Every Question You'll Get

---

### "Why LangGraph over just calling functions sequentially?"

> "Three main reasons. First, LangGraph handles state automatically — every agent
> gets the full HiringState without any manual passing. Second, it supports memory
> through checkpointing, so each hiring session is persisted and can be resumed.
> Third, it makes the system extensible — if I want to add a conditional edge
> that retries the screener when quality is low, that's just a few lines in
> LangGraph. In plain Python that's custom retry logic with manual state management."

---

### "Explain the two-stage screening pipeline."

> "The Resume Screener has two stages. Stage one is ChromaDB semantic search —
> I embed all resumes and the JD using sentence-transformers and compute cosine
> similarity. This gives a fast initial ranking and catches candidates who used
> different vocabulary for the same skills — like 'developed ML models' versus
> 'built machine learning pipelines'. Stage two is an LLM deep assessment — Groq
> LLaMA scores each resume against the extracted job requirements with structured
> strengths, gaps, and a verdict. The final score blends both: 80% LLM score plus
> 20% semantic score. This mirrors how enterprise ATS systems actually work."

---

### "What is HiringState and why TypedDict?"

> "HiringState is the shared memory object that flows through the entire pipeline.
> Every agent reads from it and writes back to it. I used TypedDict for three
> reasons: it gives static type checking so my IDE catches mistakes before runtime,
> it makes the data contract explicit — every agent knows exactly what fields exist
> and what types they are — and LangGraph's StateGraph requires a TypedDict for its
> state schema. It's essentially a typed API contract between agents."

---

### "How are the interview questions personalized?"

> "The Question Generator receives each shortlisted candidate's profile from State —
> specifically their strengths and gaps identified by the Screener. The LLM prompt
> instructs it to generate 3 questions that validate the claimed strengths with
> technical depth, 2 questions that probe the identified gaps to understand how
> the candidate would handle those weaknesses, and 1 behavioural question for the
> role. So if a candidate claimed strong Python experience but had no cloud deployment
> experience, they'd get a deep Python design question and a 'how would you approach
> deploying to AWS' gap question. It's not generic — it's tailored."

---

### "What is LLM-as-Judge and why did you add evaluation?"

> "LLM-as-Judge is a pattern where a separate, independent LLM call scores your
> system's output quality — not just whether it ran, but whether it ran WELL.
> I score the Job Analyzer on completeness and accuracy, the Resume Screener on
> score differentiation and justification quality, and the Report Writer on
> completeness and actionability. Most AI projects skip evaluation entirely. I added
> it because in production you need to know if your pipeline quality degrades — if
> a model update or prompt change makes the screener start producing undifferentiated
> scores, the evaluator catches it. It's the same principle used in OpenAI's evals
> framework and Anthropic's RLHF pipeline."

---

### "How would you scale this to production?"

> "Four changes. First, replace MemorySaver with PostgreSQL checkpointer for
> durable persistence across server restarts. Second, add async execution —
> screen all resumes in parallel instead of sequentially, which cuts latency
> by N-1 times for N resumes. Third, switch ChromaDB from in-memory to persistent
> client with a proper collection per company/job. Fourth, add LangSmith tracing
> for full observability — token counts, latency per node, error rates. For the
> API layer I'd wrap it in FastAPI with background tasks so the UI isn't blocked
> during pipeline execution."

---

### "Walk me through your code structure."

> "Five folders. `agents/` has one file per agent — each is a pure Python function
> that takes HiringState and returns a dict of updates, nothing more. `graph/` has
> `state.py` with the TypedDict and `workflow.py` which builds the LangGraph.
> `tools/` has the PDF parser using PyMuPDF and the ChromaDB wrapper — these are
> utilities that agents call, not agents themselves. `evaluation/` has the LLM-as-Judge
> evaluator that runs after all agents complete. And `app.py` is the Streamlit UI
> with 5 tabs: shortlist, all candidates with score chart, interview questions,
> full report, and evaluation dashboard with a radar chart."

---

## Numbers to Memorize

- **4 agents** + 1 evaluator node = **5 LangGraph nodes**
- **5 edges** connecting the nodes sequentially
- Resume scoring: **80% LLM + 20% semantic similarity**
- Shortlist threshold: **score ≥ 6.0 / 10**
- Questions per candidate: **6** (3 strength + 2 gap + 1 behavioural)
- Evaluation weights: **Analyzer 20% / Screener 40% / Writer 40%**
- Embeddings: **all-MiniLM-L6-v2** (sentence-transformers, runs locally, free)

---

## What to Demo in Interview

1. Open the live Streamlit URL
2. Paste a simple JD (2-3 lines is fine)
3. Upload 2-3 PDF resumes
4. Click Run — show agents executing step by step
5. Go to **Shortlist tab** — show the ranked candidates with scores
6. Go to **Interview Questions tab** — highlight that questions are personalized per candidate
7. Go to **Evaluation tab** — point to radar chart and explain LLM-as-Judge
8. Click Download Report

**Total demo: ~2 minutes. Keep it tight.**
