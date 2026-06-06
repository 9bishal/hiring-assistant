# Evaluation Methodology

## Why This Is the Most Important Feature

Anyone can build agents that run. Very few measure whether they run *well*.

Adding an evaluation layer signals:
- You think about output quality, not just output existence
- You understand production AI monitoring
- You've seen real systems where model updates break things silently

This is exactly what separates 10-12 LPA candidates from the rest.

---

## The Two-Stage Resume Scoring

Before even reaching the LLM evaluator, the Resume Screener itself uses
a two-stage scoring pipeline — this is an evaluation-within-an-agent pattern.

```
Resume + JD
    │
    ├─── Stage 1: ChromaDB Semantic Similarity ──────── score: 0.0 → 1.0
    │    (sentence-transformers cosine distance)         (fast, cheap)
    │
    └─── Stage 2: LLM Deep Assessment ──────────────── score: 0.0 → 10.0
         (Groq LLaMA structured scoring)                 (thorough, qualitative)

Final Score = (LLM × 0.80) + (Semantic × 10 × 0.20)
```

**Why blend?**
Semantic search alone misses context — a resume packed with keywords but no
relevant experience scores high. LLM alone is slower and more expensive.
Blending gives accuracy with efficiency.

---

## The Pipeline Evaluator (LLM-as-Judge)

After all 4 agents complete, the Evaluator node runs 3 independent scoring calls:

### Evaluating the Job Analyzer
Criteria:
- **Completeness:** Are required and preferred skills clearly separated?
- **Accuracy:** Does the summary correctly reflect the JD?
- **Structure:** Is the output well-organized JSON?

Bad output (score 3-4): `required_skills: ["Python", "coding"]`
Good output (score 8-9): `required_skills: ["Python", "FastAPI", "PostgreSQL", "Docker"]`

---

### Evaluating the Resume Screener
Criteria:
- **Differentiation:** Are candidates scored meaningfully differently (not all 7s)?
- **Justification:** Are the listed strengths and gaps specific and relevant?
- **Reliability:** Are similar candidates scored similarly?

Bad output (score 3-4): All candidates scored 6-7 with generic gaps like "communication"
Good output (score 8-9): Clear spread (4.5 to 9.0) with technical, specific gaps

---

### Evaluating the Report Writer
Criteria:
- **Completeness:** Does it have all sections (summary, table, analysis, questions, recommendation)?
- **Clarity:** Is it professional and well-written?
- **Actionability:** Can a hiring manager use this in a meeting without reading source data?

---

## Overall Score Calculation

```python
overall = (analyzer_score × 0.20) + (screener_score × 0.40) + (writer_score × 0.40)
```

Weights reflect importance:
- Screener and Writer are the core deliverables (40% each)
- Analyzer is a utility step (20%)

---

## Interpreting Scores

| Score | Meaning | Action |
|-------|---------|--------|
| 9-10 | Excellent pipeline run | Ship it |
| 7-8  | Good, minor issues | Acceptable |
| 5-6  | Average, some gaps | Review prompts |
| 3-4  | Poor quality output | Debug agent prompts |
| 0-2  | Pipeline failure | Check API keys, model |

---

## Future Improvements

- **Threshold retry:** if `screener_score < 6`, re-run screener with feedback
- **Benchmark dataset:** 20 JDs + resumes with human-labeled ground truth; measure correlation
- **Longitudinal tracking:** log scores to CSV/DB; plot score trends over time
- **Inter-rater reliability:** run evaluator 3 times per output; report mean ± std
