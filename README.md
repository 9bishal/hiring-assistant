# 🧑‍💼 AI Hiring Assistant — Multi-Agent Recruitment System

> **A production-oriented multi-agent AI system that automates resume screening, candidate evaluation, interview question generation, and hiring recommendations using LLMs, semantic search, and agent orchestration.**

**GitHub:** https://github.com/9bishal/hiring-assistant

---

## Overview

The AI Hiring Assistant streamlines the recruitment workflow by combining specialized AI agents, semantic resume search, and LLM-based candidate evaluation.

Recruiters can upload a Job Description (JD) along with multiple resumes. The system automatically analyzes job requirements, ranks candidates, generates personalized interview questions, and produces a comprehensive hiring report.

### Workflow

```text
Job Description + Resumes
           │
           ▼
🔍 Job Analyzer Agent
   └─ Extracts required skills, preferred skills,
      experience requirements, and role summary

           ▼
📊 Resume Screener Agent
   └─ ChromaDB semantic matching
   └─ LLM-based candidate assessment
   └─ Candidate scoring (0–10)

           ▼
❓ Interview Question Generator
   └─ Generates personalized technical and behavioral
      questions based on candidate strengths and gaps

           ▼
📝 Hiring Report Generator
   └─ Candidate rankings
   └─ Skill-gap analysis
   └─ Hiring recommendations

           ▼
⭐ Evaluation Layer
   └─ LLM-as-Judge evaluates agent outputs for quality,
      consistency, and decision reliability
```

---

## Key Features

### Multi-Agent Architecture

The system utilizes four specialized AI agents, each responsible for a specific stage of the hiring process:

* Job Requirement Analysis
* Resume Screening & Ranking
* Interview Question Generation
* Hiring Report Creation

### Semantic Resume Matching

Uses ChromaDB vector search and sentence embeddings to identify relevant candidates based on semantic similarity rather than exact keyword matches.

Examples:

* "Built ML models" ≈ "Developed machine learning pipelines"
* "RAG application" ≈ "Retrieval-Augmented Generation system"
* "LLM Agent" ≈ "AI workflow automation"

### Two-Stage Candidate Evaluation

1. Vector Similarity Search

   * Fast semantic candidate retrieval

2. LLM-Based Assessment

   * Deep evaluation of skills, experience, project relevance, and job fit

### Personalized Interview Questions

Generates candidate-specific questions targeting:

* Skill gaps
* Resume claims
* Project experience
* Role-specific competencies

### LLM-as-Judge Evaluation

Implements an evaluation layer that independently scores agent outputs based on:

* Accuracy
* Completeness
* Relevance
* Consistency

This mirrors modern AI evaluation and observability practices used in production systems.

### Persistent Workflow State

* Typed shared state using `TypedDict`
* Agent communication through LangGraph state management
* Session persistence using MemorySaver

---

## Project Structure

```text
hiring-assistant/
├── agents/
│   ├── job_analyzer.py
│   ├── resume_screener.py
│   ├── question_generator.py
│   └── report_writer.py
│
├── graph/
│   ├── state.py
│   └── workflow.py
│
├── tools/
│   ├── pdf_parser.py
│   └── vector_store.py
│
├── evaluation/
│   └── evaluator.py
│
├── app.py
├── test_run.py
├── requirements.txt
└── README.md
```

---

## Technology Stack

| Component       | Technology            |
| --------------- | --------------------- |
| Agent Framework | LangGraph             |
| LLM Provider    | Groq (Llama 3.3 70B)  |
| Vector Database | ChromaDB              |
| Embeddings      | Sentence Transformers |
| PDF Processing  | PyMuPDF               |
| Evaluation      | LLM-as-Judge          |
| Frontend        | Streamlit             |
| Visualization   | Plotly                |
| Memory          | LangGraph MemorySaver |

---

## Getting Started

```bash
git clone https://github.com/9bishal/hiring-assistant.git

cd hiring-assistant

python -m venv venv
source venv/bin/activate

pip install -r requirements.txt

# Add your API key
cp .env.example .env

python test_run.py

streamlit run app.py
```

---

## Performance Highlights

* Processes multiple resumes automatically
* Semantic candidate matching using vector search
* Candidate scoring on a 0–10 scale
* Automated candidate shortlisting
* Personalized interview question generation
* End-to-end hiring report generation
* Independent AI evaluation of workflow outputs

---

## Skills Demonstrated

* Multi-Agent Systems
* Agent Orchestration with LangGraph
* Retrieval-Augmented Generation (RAG)
* Vector Databases & Semantic Search
* LLM Application Development
* Prompt Engineering
* AI Evaluation Frameworks
* Workflow State Management
* Streamlit Application Development
* Production AI System Design
