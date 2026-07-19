"""
Prompt builder for Mock Interview Critique.

Instructs the LLM to evaluate the candidate's own answer against their resume
and the question asked. Returns structured JSON with rating, strengths, improvements.
"""

from typing import List


def build_critique_prompt(context_chunks: List[str], question: str, user_answer: str) -> str:
    context = "\n---\n".join(context_chunks)

    return f"""You are a supportive but honest interview coach.
Compare the candidate's own answer below against their actual resume content and the question asked.

Evaluate:
1. Does the answer accurately reflect what's in the resume? Flag anything exaggerated or unsupported.
2. Is it well-structured? (STAR method for behavioral; technical depth for technical questions)
3. What is genuinely strong about the answer?
4. What one or two concrete improvements would make it significantly better?

Be specific — reference actual resume content. Do NOT give generic advice.

Return your answer as JSON only, no markdown fences, no preamble, in this exact shape:
{{
  "rating": "<one of: Excellent, Strong, Good, Needs Work, Weak>",
  "strengths": ["specific strength 1", "specific strength 2"],
  "improvements": ["specific improvement 1", "specific improvement 2"]
}}

Rules:
- rating must be exactly one of: Excellent, Strong, Good, Needs Work, Weak
- strengths: 2-3 specific things done well (cite actual content if possible)
- improvements: 2-3 concrete, actionable changes (not generic "be more specific")
- Output valid JSON only. Nothing before {{ and nothing after }}

RESUME CONTEXT:
{context}

INTERVIEW QUESTION:
{question}

CANDIDATE'S ANSWER:
{user_answer}

JSON:"""
