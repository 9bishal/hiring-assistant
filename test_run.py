from graph.workflow import hiring_graph

# ── Sample Job Description ────────────────────────────────────────────────────
SAMPLE_JD = """
Job Title: Python Backend Engineer

We are looking for a Python Backend Engineer to join our AI product team.

Requirements:
- 2+ years of experience with Python and FastAPI or Django
- Strong understanding of REST API design
- Experience with PostgreSQL and Redis
- Familiarity with Docker and CI/CD pipelines
- Knowledge of LLM APIs (OpenAI, Groq, or similar) is a strong plus
- Experience with LangChain or LangGraph is highly preferred

Nice to have:
- Experience with vector databases (ChromaDB, Pinecone)
- Knowledge of RAG pipelines
- Open source contributions

Location: Bengaluru (hybrid). Salary: 8-12 LPA.
"""

# ── Sample Resumes (plain text) ───────────────────────────────────────────────
RESUMES = {
    "Ravi_Sharma.pdf": """
    Ravi Sharma | ravi@email.com | Bengaluru
    3 years Python experience. Built REST APIs with FastAPI and Django REST Framework.
    PostgreSQL, Redis, Docker. Deployed on AWS EC2 with GitHub Actions CI/CD.
    Integrated OpenAI and Groq APIs. Built a RAG pipeline with LangChain and ChromaDB.
    B.Tech CSE, NIT Trichy, 2021. CGPA: 8.2.
    """,

    "Priya_Nair.pdf": """
    Priya Nair | priya@email.com | Bengaluru
    2 years experience. Python, Flask, MySQL. Basic REST API development.
    No Docker or cloud experience. Familiar with Python scripting and data analysis.
    Used OpenAI API once in a college project.
    B.Sc Computer Science, Bangalore University, 2022.
    """,

    "Arjun_Mehta.pdf": """
    Arjun Mehta | arjun@email.com | Pune
    4 years backend experience. Expert in FastAPI, PostgreSQL, Redis.
    Extensive Docker and Kubernetes experience. CI/CD with Jenkins and GitHub Actions.
    Built LangGraph-based multi-agent systems. LangChain, ChromaDB, RAG pipelines.
    Contributed to 3 open source Python projects. B.Tech, IIT Bombay, 2020. CGPA: 9.1.
    """,
}

# ── Run ────────────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("  AI Hiring Assistant — Terminal Test")
print(f"  JD: Python Backend Engineer")
print(f"  Resumes: {len(RESUMES)}")
print("="*65 + "\n")

config = {"configurable": {"thread_id": "test-hiring-001"}}

for event in hiring_graph.stream(
    {
        "job_description": SAMPLE_JD,
        "resume_texts":    list(RESUMES.values()),
        "resume_names":    list(RESUMES.keys()),
    },
    config=config,
):
    node = list(event.keys())[0]
    print(f"✅  {node.upper()} complete")

# ── Results ───────────────────────────────────────────────────────────────────
s = hiring_graph.get_state(config).values

print("\n" + "="*65)
print("  JOB REQUIREMENTS EXTRACTED")
print("="*65)
print(f"  Required : {s.get('required_skills')}")
print(f"  Preferred: {s.get('preferred_skills')}")
print(f"  Experience: {s.get('experience_needed')}")

print("\n" + "="*65)
print("  CANDIDATE SCORES")
print("="*65)
for c in s.get("all_candidates", []):
    tag = "✅ SHORTLISTED" if c["score"] >= 6 else "❌"
    print(f"  {tag}  {c['name']}:  {c['score']}/10 — {c['summary']}")

print("\n" + "="*65)
print("  EVALUATION SCORES")
print("="*65)
print(f"  Job Analyzer   : {s.get('analyzer_score')} / 10")
print(f"  Resume Screener: {s.get('screener_score')} / 10")
print(f"  Report Writer  : {s.get('writer_score')}   / 10")
print(f"  Overall        : {s.get('overall_score')}  / 10")

print("\n" + "="*65)
print("  REPORT PREVIEW (first 500 chars)")
print("="*65)
print(s.get("hiring_report", "")[:500])
print("\n... Full report available in Streamlit UI\n")
