import uuid
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from graph.workflow import hiring_graph
from tools.pdf_parser import parse_pdf

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Hiring Assistant",
    page_icon="🧑‍💼",
    layout="wide",
)

# ── Session State ─────────────────────────────────────────────────────────────
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())
if "results" not in st.session_state:
    st.session_state.results = None

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🧑‍💼 AI Hiring Assistant")
st.caption(
    "**4 AI Agents** · LangGraph · Groq LLaMA 3.3 70B · "
    "ChromaDB Semantic Search · LLM-as-Judge Evaluation"
)

# ── Architecture expander ─────────────────────────────────────────────────────
with st.expander("📊 How it works — Agent Pipeline", expanded=False):
    st.markdown("""
```
Upload JD + Resumes
        │
        ▼
┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐   ┌──────────────────┐
│  Job Analyzer    │──▶│ Resume Screener  │──▶│ Question Gen     │──▶│  Report Writer   │
│                  │   │                  │   │                  │   │                  │
│ Extracts:        │   │ ChromaDB semantic│   │ 6 tailored       │   │ Full hiring      │
│ • Required skills│   │ similarity FIRST │   │ questions per    │   │ report with      │
│ • Preferred      │   │ Then LLM deep    │   │ shortlisted      │   │ rankings +       │
│ • Experience     │   │ assessment       │   │ candidate        │   │ recommendations  │
│ • Role summary   │   │ Score: 0–10      │   │ (strengths +     │   │                  │
└──────────────────┘   └──────────────────┘   │  gap probing)    │   └──────────────────┘
                                               └──────────────────┘           │
                                                                               ▼
                                                                    ┌──────────────────┐
                                                                    │   Evaluator      │
                                                                    │  LLM-as-Judge    │
                                                                    │  Scores 0–10     │
                                                                    │  per agent       │
                                                                    └──────────────────┘
```
**All agents share a single `HiringState` object — LangGraph passes it automatically.**
    """)

st.divider()

# ── Inputs ────────────────────────────────────────────────────────────────────
col_jd, col_res = st.columns([1, 1])

with col_jd:
    st.subheader("📋 Job Description")
    jd_input_method = st.radio(
        "Input method", ["Paste text", "Upload PDF"], horizontal=True, label_visibility="collapsed"
    )

    if jd_input_method == "Paste text":
        jd_text = st.text_area(
            "Paste the job description here",
            height=280,
            placeholder="e.g. We are looking for a Python Backend Engineer with 2+ years experience in FastAPI, PostgreSQL, Docker..."
        )
    else:
        jd_file = st.file_uploader("Upload JD (PDF)", type=["pdf"], key="jd_pdf")
        jd_text = ""
        if jd_file:
            jd_text = parse_pdf(jd_file.read())
            st.success(f"✅ JD parsed — {len(jd_text)} characters")
            with st.expander("Preview JD text"):
                st.text(jd_text[:500] + "...")

with col_res:
    st.subheader("📄 Resumes")
    resume_files = st.file_uploader(
        "Upload resumes (PDF) — up to 10",
        type=["pdf"],
        accept_multiple_files=True,
        key="resumes",
    )

    if resume_files:
        st.success(f"✅ {len(resume_files)} resume(s) uploaded")
        for f in resume_files:
            st.caption(f"• {f.name}")

st.divider()

# ── Run Button ────────────────────────────────────────────────────────────────
ready = bool(jd_text and jd_text.strip() and resume_files)

col_btn, col_hint = st.columns([1, 3])
with col_btn:
    run_btn = st.button("🚀 Run Hiring Pipeline", type="primary", disabled=not ready)
with col_hint:
    if not ready:
        st.caption("⬆️ Add a job description and at least one resume to continue.")

# ── Run Pipeline ──────────────────────────────────────────────────────────────
if run_btn and ready:

    # Parse all resumes
    resume_texts = []
    resume_names = []
    for f in resume_files:
        text = parse_pdf(f.read())
        resume_texts.append(text)
        resume_names.append(f.name.replace(".pdf", ""))

    config = {"configurable": {"thread_id": st.session_state.thread_id}}

    # ── Live progress ─────────────────────────────────────────────────────
    node_labels = {
        "job_analyzer":       ("🔍", "Job Analyzer",        "Extracting requirements from JD..."),
        "resume_screener":    ("📊", "Resume Screener",     f"Screening {len(resume_names)} resumes with ChromaDB + LLM..."),
        "question_generator": ("❓", "Question Generator",  "Generating tailored interview questions..."),
        "report_writer":      ("📝", "Report Writer",       "Writing hiring recommendation report..."),
        "evaluator":          ("⭐", "Evaluator",           "Scoring agent outputs (LLM-as-Judge)..."),
    }

    # Status cards row
    status_slots = {k: None for k in node_labels}
    card_cols = st.columns(5)
    for i, (key, (icon, label, _)) in enumerate(node_labels.items()):
        status_slots[key] = card_cols[i].empty()
        status_slots[key].info(f"{icon} **{label}**\n\nWaiting...")

    with st.status("Hiring pipeline running...", expanded=True) as pipeline_status:
        for event in hiring_graph.stream(
            {
                "job_description": jd_text.strip(),
                "resume_texts":    resume_texts,
                "resume_names":    resume_names,
            },
            config=config,
        ):
            node_name = list(event.keys())[0]
            if node_name in node_labels:
                icon, label, desc = node_labels[node_name]
                st.write(f"{icon} **{label}** — {desc}")
                status_slots[node_name].success(f"{icon} **{label}**\n\n✅ Done")

        pipeline_status.update(label="✅ Pipeline complete!", state="complete")

    # Store results
    st.session_state.results = hiring_graph.get_state(config).values
    st.rerun()

# ── Display Results ───────────────────────────────────────────────────────────
if st.session_state.results:
    r = st.session_state.results

    st.divider()
    st.subheader("📋 Results")

    all_candidates = r.get("all_candidates", [])
    shortlisted    = r.get("shortlisted", [])
    iq             = r.get("interview_questions", {})

    # ── Tab layout ────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏆 Shortlist",
        "📊 All Candidates",
        "❓ Interview Questions",
        "📝 Full Report",
        "⭐ Evaluation",
    ])

    # ── TAB 1: Shortlist ──────────────────────────────────────────────────
    with tab1:
        if shortlisted:
            st.success(f"**{len(shortlisted)} candidate(s) shortlisted** (score ≥ 6.0)")
            for i, c in enumerate(shortlisted, 1):
                score_color = "🟢" if c["score"] >= 8 else "🟡" if c["score"] >= 6 else "🔴"
                with st.expander(
                    f"{score_color} #{i}  {c['name']}  —  **{c['score']}/10**",
                    expanded=(i == 1)
                ):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**✅ Strengths**")
                        for s in c["strengths"]:
                            st.markdown(f"- {s}")
                    with col_b:
                        st.markdown("**⚠️ Gaps**")
                        for g in c["gaps"]:
                            st.markdown(f"- {g}")
                    st.info(f"**Verdict:** {c['summary']}")
        else:
            st.warning("No candidates scored 6.0 or above. Consider revising the requirements or uploading more resumes.")

    # ── TAB 2: All Candidates ─────────────────────────────────────────────
    with tab2:
        if all_candidates:
            # Table
            df = pd.DataFrame([{
                "Candidate":  c["name"],
                "Score":      c["score"],
                "Verdict":    "✅ Shortlisted" if c["score"] >= 6 else "❌ Not shortlisted",
                "Top Strength": c["strengths"][0] if c["strengths"] else "—",
                "Top Gap":      c["gaps"][0]      if c["gaps"]      else "—",
                "Summary":    c["summary"],
            } for c in all_candidates])

            st.dataframe(df, use_container_width=True, hide_index=True)

            # Score bar chart
            fig = go.Figure(go.Bar(
                x     = [c["name"] for c in all_candidates],
                y     = [c["score"] for c in all_candidates],
                text  = [f"{c['score']}/10" for c in all_candidates],
                textposition = "outside",
                marker_color = [
                    "#10B981" if c["score"] >= 8
                    else "#F59E0B" if c["score"] >= 6
                    else "#EF4444"
                    for c in all_candidates
                ],
            ))
            fig.add_hline(
                y=6, line_dash="dash", line_color="#6B7280",
                annotation_text="Shortlist threshold (6.0)"
            )
            fig.update_layout(
                title       = "Candidate Fit Scores",
                yaxis       = dict(range=[0, 10.5], title="Score"),
                xaxis_title = "Candidate",
                plot_bgcolor  = "rgba(0,0,0,0)",
                paper_bgcolor = "rgba(0,0,0,0)",
                height = 380,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── TAB 3: Interview Questions ────────────────────────────────────────
    with tab3:
        if iq:
            st.info("Questions are **personalized per candidate** — probing their specific gaps and validating their claimed strengths.")
            for name, questions in iq.items():
                with st.expander(f"❓ {name}", expanded=False):
                    for i, q in enumerate(questions, 1):
                        st.markdown(f"**{i}.** {q}")
        else:
            st.caption("No shortlisted candidates — no interview questions generated.")

    # ── TAB 4: Full Report ────────────────────────────────────────────────
    with tab4:
        report = r.get("hiring_report", "Report not generated.")
        st.markdown(report)
        st.download_button(
            label    = "📥 Download Report (.md)",
            data     = report,
            file_name = "hiring_report.md",
            mime     = "text/markdown",
        )

    # ── TAB 5: Evaluation ─────────────────────────────────────────────────
    with tab5:
        st.subheader("⭐ Pipeline Quality Scores — LLM-as-Judge")

        # Metric cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("🔍 Job Analyzer",    f"{r.get('analyzer_score', '—')} / 10")
        m2.metric("📊 Resume Screener", f"{r.get('screener_score', '—')} / 10")
        m3.metric("📝 Report Writer",   f"{r.get('writer_score',   '—')} / 10")
        m4.metric("⭐ Overall",         f"{r.get('overall_score',  '—')} / 10",
                  delta="Weighted avg")

        # Radar chart
        agents = ["Job Analyzer", "Resume Screener", "Report Writer"]
        scores = [
            r.get("analyzer_score", 0),
            r.get("screener_score", 0),
            r.get("writer_score",   0),
        ]

        fig2 = go.Figure(go.Scatterpolar(
            r     = scores + [scores[0]],
            theta = agents + [agents[0]],
            fill  = "toself",
            fillcolor = "rgba(59,130,246,0.2)",
            line  = dict(color="#3B82F6", width=2),
            name  = "Agent Scores",
        ))
        fig2.update_layout(
            polar = dict(radialaxis=dict(visible=True, range=[0, 10])),
            title = "Agent Quality Radar",
            height = 380,
            paper_bgcolor = "rgba(0,0,0,0)",
        )
        st.plotly_chart(fig2, use_container_width=True)

        st.info("""
**Scoring methodology (LLM-as-Judge):**
A separate LLM independently scores each agent's output on:
- **Job Analyzer:** completeness, accuracy, structure
- **Resume Screener:** differentiation, justification, reliability
- **Report Writer:** completeness, clarity, actionability

**Weights:** Analyzer 20% · Screener 40% · Writer 40%
        """)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("🧑‍💼 AI Hiring Assistant")
    st.markdown("""
**Pipeline:**
1. 🔍 Job Analyzer
2. 📊 Resume Screener
3. ❓ Question Generator
4. 📝 Report Writer
5. ⭐ Evaluator (LLM-Judge)

**Tech Stack:**
- LangGraph StateGraph
- Groq LLaMA 3.3 70B
- ChromaDB + Semantic Search
- PyMuPDF (PDF parsing)
- LLM-as-Judge Evaluation
- Streamlit + Plotly
    """)
    st.divider()
    if st.button("🔄 Start New Session"):
        st.session_state.thread_id = str(uuid.uuid4())
        st.session_state.results   = None
        st.rerun()
