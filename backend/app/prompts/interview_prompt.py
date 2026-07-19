"""
Prompt builder for Interview Question Generation.

The LLM must generate questions grounded in the resume content.
It must NOT invent skills or experiences not present in the context.
"""

from typing import List, Dict, Any

CATEGORY_INSTRUCTIONS = {
    "technical": (
        "Generate technical interview questions about the candidate's specific technologies, "
        "tools, languages, frameworks, and technical projects mentioned in their resume."
    ),
    "hr": (
        "Generate HR/behavioral interview questions relevant to the candidate's background, "
        "career transitions, motivations, and experiences shown in their resume."
    ),
    "project": (
        "Generate questions about the specific projects listed in the candidate's resume — "
        "their role, technical decisions, challenges faced, and outcomes."
    ),
    "behavioral": (
        "Generate STAR-format behavioral interview questions based on the candidate's "
        "work experiences, achievements, and responsibilities listed in the resume."
    ),
}


def build_interview_prompt(
    category: str,
    count: int,
    chunks: List[Dict[str, Any]],
) -> str:
    context = "\n\n---\n\n".join(chunk["text"] for chunk in chunks)
    category_instruction = CATEGORY_INSTRUCTIONS.get(
        category,
        "Generate relevant interview questions based on the resume."
    )

    return f"""You are an expert interviewer. {category_instruction}

RULES:
- Generate EXACTLY {count} questions, numbered 1 to {count}.
- Base every question on skills, experiences, or projects actually present in the RESUME CONTEXT below.
- Do NOT invent skills, technologies, or experiences not mentioned in the resume.
- Output ONLY the numbered list of questions. No preamble, no answers, no explanations.
- Each question should be on its own line.

RESUME CONTEXT:
{context}

INTERVIEW QUESTIONS ({category.upper()} — {count} questions):"""
