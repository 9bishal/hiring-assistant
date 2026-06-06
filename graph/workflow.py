"""
graph/workflow.py
=================
THE LANGGRAPH WORKFLOW — Connects all 4 agents into a pipeline

Flow:
  START
    │
    ▼
  Job Analyzer      ← parses the JD into structured requirements
    │
    ▼
  Resume Screener   ← scores all resumes (ChromaDB + LLM)
    │
    ▼
  Question Generator← generates tailored interview questions
    │
    ▼
  Report Writer     ← produces the final hiring report
    │
    ▼
  Evaluator         ← scores all agent outputs (LLM-as-Judge)
    │
    ▼
  END

How to explain to HR:
  "I used LangGraph's StateGraph to connect the 4 agents as nodes.
   Each agent is a pure Python function — no inheritance, no complex
   class hierarchies. The StateGraph handles execution order, state
   passing, and supports memory through MemorySaver checkpointing.
   The graph is explicit and visual — you can see exactly how data
   flows through the system."
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from graph.state import HiringState
from agents.job_analyzer import job_analyzer_agent
from agents.resume_screener import resume_screener_agent
from agents.question_generator import question_generator_agent
from agents.report_writer import report_writer_agent
from evaluation.evaluator import evaluator_node


def build_graph():
    """Builds and compiles the hiring assistant workflow."""

    graph = StateGraph(HiringState)

    # ── Register all nodes ────────────────────────────────────────────────
    graph.add_node("job_analyzer",         job_analyzer_agent)
    graph.add_node("resume_screener",      resume_screener_agent)
    graph.add_node("question_generator",   question_generator_agent)
    graph.add_node("report_writer",        report_writer_agent)
    graph.add_node("evaluator",            evaluator_node)

    # ── Entry point ───────────────────────────────────────────────────────
    graph.set_entry_point("job_analyzer")

    # ── Sequential edges ──────────────────────────────────────────────────
    graph.add_edge("job_analyzer",       "resume_screener")
    graph.add_edge("resume_screener",    "question_generator")
    graph.add_edge("question_generator", "report_writer")
    graph.add_edge("report_writer",      "evaluator")
    graph.add_edge("evaluator",          END)

    # ── Memory (session persistence) ──────────────────────────────────────
    memory = MemorySaver()
    return graph.compile(checkpointer=memory)


# Single instance reused across the app
hiring_graph = build_graph()
