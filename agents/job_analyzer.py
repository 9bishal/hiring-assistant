import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import HiringState

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)


def job_analyzer_agent(state: HiringState) -> dict:
    """
    Parses the job description into structured hiring criteria.
    """

    response = llm.invoke([
        SystemMessage(content="""You are an expert HR analyst.
Extract structured hiring requirements from a job description.

Return ONLY valid JSON — no explanation, no markdown fences.

Format:
{
  "required_skills":   ["skill1", "skill2"],
  "preferred_skills":  ["skill3", "skill4"],
  "experience_needed": "X-Y years",
  "role_summary":      "One paragraph plain-English summary of the role."
}"""),
        HumanMessage(content=f"Job Description:\n\n{state['job_description']}")
    ])

    # Strip markdown fences if present
    raw  = response.content.strip().strip("```json").strip("```").strip()
    data = json.loads(raw)

    return {
        "required_skills":   data.get("required_skills",   []),
        "preferred_skills":  data.get("preferred_skills",  []),
        "experience_needed": data.get("experience_needed", "Not specified"),
        "role_summary":      data.get("role_summary",      ""),
    }
