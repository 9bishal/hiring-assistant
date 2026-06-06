"""
evaluation/evaluator.py
=======================
THE EVALUATION LAYER — Scores each agent's output quality.

Uses the LLM-as-Judge pattern:
  A separate LLM call independently scores each agent's output 0-10.
  This gives an objective signal: not just "did it run" but "did it
  produce GOOD output".

How to explain to HR:
  "After the pipeline completes, an independent evaluator LLM scores
   the three key outputs: the JD analysis, the screening results, and
   the final report. This is the LLM-as-Judge pattern used in
   production AI quality monitoring. I track these scores to catch
   quality regressions — if the analyzer starts scoring below 7,
   something in the prompt or model changed."

Scoring weights (for overall score):
  Job Analyzer   → 20%  (structured extraction, relatively easy)
  Resume Screener→ 40%  (core of the system, most impactful)
  Report Writer  → 40%  (final deliverable, what stakeholders see)
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import HiringState

load_dotenv()

evaluator_llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)


def _score(label: str, content: str, criteria: str) -> float:
    """Score a piece of output 0-10 using LLM-as-Judge."""
    response = evaluator_llm.invoke([
        SystemMessage(content=f"""You are an AI output quality evaluator.
Score the output below from 0 to 10 based on:
{criteria}

Return ONLY a single number between 0 and 10. Nothing else.
Example: 8.5"""),
        HumanMessage(content=f"Output ({label}):\n\n{content[:1500]}")
    ])
    try:
        return round(min(max(float(response.content.strip().split()[0]), 0), 10), 1)
    except Exception:
        return 5.0


def evaluator_node(state: HiringState) -> dict:
    """Scores the three key agent outputs using LLM-as-Judge."""

    # Score Job Analyzer output
    analyzer_score = _score(
        label    = "Job Analysis",
        content  = f"Required: {state.get('required_skills')}\n"
                   f"Preferred: {state.get('preferred_skills')}\n"
                   f"Summary: {state.get('role_summary')}",
        criteria = (
            "1. Completeness: are required and preferred skills clearly separated?\n"
            "2. Accuracy: does the summary reflect the JD correctly?\n"
            "3. Structure: is the output well-organized?"
        )
    )

    # Score Resume Screener output
    screener_score = _score(
        label    = "Candidate Screening",
        content  = "\n".join([
            f"{c['name']}: {c['score']}/10 — {c['summary']}"
            for c in state.get("all_candidates", [])
        ]),
        criteria = (
            "1. Differentiation: are candidates meaningfully scored differently?\n"
            "2. Justification: are strengths and gaps specific and relevant?\n"
            "3. Reliability: do the scores seem consistent and fair?"
        )
    )

    # Score Report Writer output
    writer_score = _score(
        label    = "Hiring Report",
        content  = state.get("hiring_report", ""),
        criteria = (
            "1. Completeness: does it cover summary, rankings, analysis, questions?\n"
            "2. Clarity: is it well-written and professional?\n"
            "3. Actionability: can a hiring manager act on this report immediately?"
        )
    )

    overall_score = round(
        (analyzer_score * 0.20) +
        (screener_score * 0.40) +
        (writer_score   * 0.40),
        1
    )

    return {
        "analyzer_score": analyzer_score,
        "screener_score": screener_score,
        "writer_score":   writer_score,
        "overall_score":  overall_score,
    }
