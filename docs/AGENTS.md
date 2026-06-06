# AI Hiring Assistant — Agent Documentation

## Overview

This document describes the 4 AI agents that form the hiring pipeline and their key features.

---

## Agent 1 — Job Analyzer

**Location:** `agents/job_analyzer.py`

### What it does:
Reads the raw job description and extracts structured requirements:
- Required skills
- Preferred skills
- Experience needed
- Plain-English role summary

### Why this is its own agent:
Every other agent depends on a clean understanding of the JD. By doing this extraction once and storing it in State, we avoid re-parsing the JD in every downstream agent. Single source of truth.

### How to explain to HR:
> "The Job Analyzer reads the JD once and produces a structured requirements object — required skills, preferred skills, experience level. All downstream agents use this structured output rather than re-reading the raw JD. It's like having an HR specialist highlight the key criteria before screening starts."

### Input (from State):
- `job_description`

### Output (to State):
- `required_skills`
- `preferred_skills`
- `experience_needed`
- `role_summary`

---

## Agent 2 — Resume Screener

**Location:** `agents/resume_screener.py`

### What it does:
Scores every uploaded resume against the extracted job requirements. Uses ChromaDB semantic search FIRST to rank candidates by vector similarity, then uses the LLM to do a deep qualitative assessment of each resume.

### Impressive Feature:
**Two-stage screening pipeline:**
1. **Stage 1:** ChromaDB semantic similarity (fast, cheap)
2. **Stage 2:** LLM deep assessment per candidate (thorough, qualitative)

This mirrors how real enterprise ATS systems work.

### How to explain to HR:
> "I use a two-stage screening pipeline. First, ChromaDB ranks all resumes by semantic similarity to the JD using vector embeddings — this is fast and catches skill synonyms. Then the LLM does a deep qualitative assessment of each resume against the structured requirements from Agent 1. The final score combines both signals."

### Input (from State):
- `job_description`
- `resume_texts`
- `resume_names`
- `required_skills`
- `preferred_skills`
- `experience_needed`

### Output (to State):
- `all_candidates`
- `shortlisted`

### Key Constant:
- `SHORTLIST_THRESHOLD = 6.0` — Candidates scoring below this are filtered out

---

## Agent 3 — Question Generator

**Location:** `agents/question_generator.py`

### What it does:
Generates PERSONALIZED interview questions for each shortlisted candidate — not generic questions, but questions that specifically probe their identified gaps and validate their claimed strengths.

### Impressive Feature for 10-12 LPA:
Example workflow:
- **Candidate claims:** "5 years Python experience"
- **Gap identified:** "No cloud deployment experience"

**Generated questions:**
- "Walk me through your most complex Python project — what design patterns did you use?"
- "You haven't worked with AWS/GCP — how would you approach deploying an ML model to production?"

### How to explain to HR:
> "Agent 3 takes each shortlisted candidate's profile — their strengths AND gaps identified by the screener — and generates tailored interview questions. Technical questions validate their claimed skills. Gap-based questions probe areas of concern. This saves the hiring manager significant prep time."

### Question Breakdown (per candidate):
- **3 questions** that validate their STRENGTHS (technical depth questions)
- **2 questions** that probe their GAPS (how they'd handle missing skills)
- **1 behavioral question** based on the role

### Input (from State):
- `shortlisted`
- `required_skills`
- `role_summary`

### Output (to State):
- `interview_questions`

---

## Agent 4 — Report Writer

**Location:** `agents/report_writer.py`

### What it does:
Generates a comprehensive hiring report that includes:
- Candidate rankings
- Strengths/gaps breakdown
- Interview questions
- Evaluation scorecard with recommendations

### How to explain to HR:
> "Agent 4 synthesizes all the work from Agents 1–3 into a professional hiring report. It includes candidate rankings, detailed assessments, tailored interview questions, and an evaluation summary. This is the document you share with stakeholders."

### Input (from State):
- All state data (candidates, questions, evaluations, etc.)

### Output (to State):
- `hiring_report`

---

## Architecture Notes

- **Model:** Groq LLaMA 3.3 70B (via LangChain)
- **State Management:** LangGraph
- **Vector Storage:** ChromaDB
- **Web UI:** Streamlit

Each agent is a node in the LangGraph workflow and receives/updates the shared `HiringState` object.
