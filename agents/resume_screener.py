import os
import json
import uuid
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import HiringState, CandidateResult
from tools.vector_store import store_resumes, semantic_search

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

# Shortlist threshold — candidates scoring below this are filtered out
SHORTLIST_THRESHOLD = 6.0


def _screen_one_resume(
    resume_text:      str,
    resume_name:      str,
    required_skills:  list,
    preferred_skills: list,
    experience_needed: str,
    role_summary:     str,
) -> CandidateResult:
    """Score a single resume using the LLM."""

    response = llm.invoke([
        SystemMessage(content="""You are a senior technical recruiter.
Score a candidate's resume against job requirements.

Return ONLY valid JSON — no explanation, no markdown fences.

Format:
{
  "score":     7.5,
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "gaps":      ["gap 1", "gap 2"],
  "summary":   "One sentence verdict on this candidate."
}

Score guide:
  9-10 = Exceptional fit, hire immediately
  7-8  = Strong fit, definitely interview
  5-6  = Partial fit, worth a screen call
  3-4  = Weak fit, significant gaps
  0-2  = Not suitable"""),

        HumanMessage(content=f"""
Role Summary: {role_summary}
Required Skills: {', '.join(required_skills)}
Preferred Skills: {', '.join(preferred_skills)}
Experience Needed: {experience_needed}

Resume ({resume_name}):
{resume_text[:3000]}

Score this candidate.
""")
    ])

    raw  = response.content.strip().strip("```json").strip("```").strip()
    data = json.loads(raw)

    return CandidateResult(
        name      = resume_name,
        score     = float(data.get("score", 5.0)),
        strengths = data.get("strengths", []),
        gaps      = data.get("gaps", []),
        summary   = data.get("summary", ""),
    )


def resume_screener_agent(state: HiringState) -> dict:
    """
    Screens all resumes against job requirements.

    Step 1: Store all resumes in ChromaDB, do semantic search
            to get initial similarity ranking.
    Step 2: LLM deep-scores each candidate.
    Step 3: Sort by score, shortlist candidates above threshold.
    """

    session_id = str(uuid.uuid4())[:8]

    # ── Step 1: Semantic similarity ranking with ChromaDB ─────────────────
    store_resumes(
        session_id = session_id,
        names      = state["resume_names"],
        texts      = state["resume_texts"],
    )

    semantic_rankings = semantic_search(
        session_id = session_id,
        query      = state["job_description"],
        top_k      = len(state["resume_names"]),
    )

    # Create a name → semantic_score lookup
    semantic_scores = {r["name"]: r["score"] for r in semantic_rankings}

    # ── Step 2: LLM deep assessment for each candidate ────────────────────
    all_candidates = []

    for name, text in zip(state["resume_names"], state["resume_texts"]):
        result = _screen_one_resume(
            resume_text       = text,
            resume_name       = name,
            required_skills   = state["required_skills"],
            preferred_skills  = state["preferred_skills"],
            experience_needed = state["experience_needed"],
            role_summary      = state["role_summary"],
        )

        # Blend LLM score (80%) + semantic score (20%) for final score
        semantic = semantic_scores.get(name, 0.5) * 10   # scale 0-1 to 0-10
        blended  = round((result["score"] * 0.80) + (semantic * 0.20), 1)
        result["score"] = blended

        all_candidates.append(result)

    # ── Step 3: Sort by score, shortlist top candidates ───────────────────
    all_candidates.sort(key=lambda x: x["score"], reverse=True)
    shortlisted = [c for c in all_candidates if c["score"] >= SHORTLIST_THRESHOLD]

    return {
        "all_candidates": all_candidates,
        "shortlisted":    shortlisted,
    }
