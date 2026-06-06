import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from graph.state import HiringState

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.3,    # slightly creative for varied questions
    api_key=os.getenv("GROQ_API_KEY"),
)


def _generate_questions_for_candidate(
    candidate:        dict,
    required_skills:  list,
    role_summary:     str,
) -> list[str]:
    """Generate tailored interview questions for one candidate."""

    response = llm.invoke([
        SystemMessage(content="""You are an expert technical interviewer.
Generate exactly 6 personalized interview questions for a candidate.

Rules:
- 3 questions that validate their STRENGTHS (technical depth questions)
- 2 questions that probe their GAPS (how they'd handle missing skills)
- 1 behavioural question based on the role

Make questions SPECIFIC to this candidate — not generic.
Return as a numbered list. No preamble."""),

        HumanMessage(content=f"""
Role: {role_summary}
Required Skills: {', '.join(required_skills)}

Candidate: {candidate['name']}
Score: {candidate['score']}/10
Strengths: {', '.join(candidate['strengths'])}
Gaps: {', '.join(candidate['gaps'])}
Summary: {candidate['summary']}

Generate 6 tailored interview questions:
""")
    ])

    # Parse numbered list into clean question strings
    lines     = response.content.strip().splitlines()
    questions = []
    for line in lines:
        line = line.strip()
        if line and (line[0].isdigit() or line.startswith("-")):
            # Remove leading numbering like "1." or "-"
            cleaned = line.lstrip("0123456789.-) ").strip()
            if cleaned:
                questions.append(cleaned)

    return questions[:6]   # cap at 6


def question_generator_agent(state: HiringState) -> dict:
    """
    Generates personalized interview questions for every shortlisted candidate.
    """

    interview_questions = {}

    for candidate in state["shortlisted"]:
        questions = _generate_questions_for_candidate(
            candidate        = candidate,
            required_skills  = state["required_skills"],
            role_summary     = state["role_summary"],
        )
        interview_questions[candidate["name"]] = questions

    return {"interview_questions": interview_questions}
