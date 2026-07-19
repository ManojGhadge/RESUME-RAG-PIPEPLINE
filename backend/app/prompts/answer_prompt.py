"""
Prompt builder for "Answer this question" — first-person grounded sample answers.

The candidate's voice: "I worked on...", "In my role at...", etc.
Must say honestly if the resume lacks detail — no invention.
"""

from typing import List, Dict, Any


def build_answer_prompt(question: str, chunks: List[Dict[str, Any]]) -> str:
    context = "\n\n---\n\n".join(chunk["text"] for chunk in chunks)

    return f"""You are helping a job candidate prepare a strong, honest answer to an interview question.
Write a first-person sample answer AS THE CANDIDATE, using only details from their resume.

RULES:
- Write in first person ("I built...", "In my role at...", "I led a team of...").
- Use ONLY details present in the RESUME CONTEXT below.
- If the resume doesn't contain enough information to answer well, say:
  "My resume doesn't include enough detail to fully answer this, but based on what's there: [brief answer]."
- Do NOT invent experiences, technologies, or metrics not mentioned in the resume.
- Be specific — cite actual projects, companies, or technologies from the context.
- Keep the answer to 150–250 words.

RESUME CONTEXT:
{context}

INTERVIEW QUESTION:
{question}

CANDIDATE'S ANSWER (first person):"""
