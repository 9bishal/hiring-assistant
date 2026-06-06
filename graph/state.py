"""
graph/state.py
==============
THE SHARED STATE — Every agent reads from and writes to this object.

Think of it like a hiring folder on a shared drive:
  - Agent 1 (Job Analyzer)  adds the job requirements
  - Agent 2 (Screener)      adds candidate scores
  - Agent 3 (Interviewer)   adds interview questions
  - Agent 4 (Writer)        adds the final report

LangGraph passes this State between every node automatically.

How to explain to HR:
  "All agents share a single typed state object — AgentState.
   Each agent only touches the fields it owns. This makes the
   system modular: you can swap, test, or upgrade any agent
   independently without touching the others."
"""

from typing import TypedDict, List, Optional


class CandidateResult(TypedDict):
    """Stores one candidate's screening result."""
    name:       str           # resume filename
    score:      float         # fit score 0-10
    strengths:  List[str]     # matched skills/experience
    gaps:       List[str]     # missing requirements
    summary:    str           # 1-sentence verdict


class HiringState(TypedDict):
    # ── INPUT (provided by user) ───────────────────────────────────────────
    job_description:  str             # full JD text
    resume_texts:     List[str]       # parsed text of each resume
    resume_names:     List[str]       # filenames (for display)

    # ── AGENT 1 OUTPUT: Job Analyzer ──────────────────────────────────────
    required_skills:      List[str]   # must-have technical skills
    preferred_skills:     List[str]   # nice-to-have skills
    experience_needed:    str         # e.g. "2-4 years"
    role_summary:         str         # 1-paragraph role understanding

    # ── AGENT 2 OUTPUT: Resume Screener ───────────────────────────────────
    all_candidates:       List[CandidateResult]   # every candidate screened
    shortlisted:          List[CandidateResult]   # score >= 6.0

    # ── AGENT 3 OUTPUT: Interview Question Generator ───────────────────────
    # Dict: { candidate_name → list of questions }
    interview_questions:  dict

    # ── AGENT 4 OUTPUT: Report Writer ─────────────────────────────────────
    hiring_report:        str         # final markdown report

    # ── EVALUATION ────────────────────────────────────────────────────────
    analyzer_score:       Optional[float]
    screener_score:       Optional[float]
    writer_score:         Optional[float]
    overall_score:        Optional[float]
