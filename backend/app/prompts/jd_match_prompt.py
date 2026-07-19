"""
Prompt builder for JD Matching.

Instructs the LLM to return ONLY valid JSON — no preamble, no markdown fences.
The JSON is parsed defensively by parse_llm_json() in text_utils.
"""

from typing import List


def build_jd_match_prompt(context_chunks: List[str], jd_text: str) -> str:
    context = "\n---\n".join(context_chunks)

    return f"""Compare the candidate's resume content below against the job description.
Base your analysis ONLY on what is actually present in the resume — do not assume skills not shown.

Return your answer as JSON only, no other text, no markdown fences, in this exact shape:
{{
  "match_percentage": <integer 0-100>,
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill3", "skill4"],
  "suggestions": ["suggestion1", "suggestion2", "suggestion3"]
}}

Rules:
- match_percentage: honest estimate of how well the resume matches the JD requirements
- matching_skills: technologies/skills/experiences present in BOTH resume and JD
- missing_skills: JD requirements clearly NOT present in the resume
- suggestions: 3-5 specific, actionable things the candidate can do to improve their match
- Be honest — if a skill isn't in the resume, it goes in missing_skills
- Output valid JSON only. Nothing before the {{ and nothing after the }}

RESUME CONTEXT:
{context}

JOB DESCRIPTION:
{jd_text[:3000]}

JSON:"""
