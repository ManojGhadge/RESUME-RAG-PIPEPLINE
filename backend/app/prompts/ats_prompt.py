"""
Prompt builder for ATS Suggestions.

Uses the FULL resume text (from MySQL), not top-k retrieval.
Reason: a partial view would produce incomplete/misleading feedback.
"""


def build_ats_prompt(full_text: str) -> str:
    return f"""You are an expert resume reviewer with deep knowledge of Applicant Tracking Systems (ATS).
Analyze the resume below and provide specific, actionable improvement suggestions.

REVIEW THESE AREAS (cover each one):

1. QUANTIFIABLE METRICS
   - Identify bullet points that lack numbers/metrics (e.g., "improved performance" → "improved performance by 40%")
   - List 3–5 specific bullets that need metrics added.

2. ACTION VERBS
   - Flag weak or passive verbs (e.g., "responsible for", "helped with", "worked on")
   - Suggest stronger replacements (e.g., "led", "engineered", "reduced", "delivered")

3. ATS FORMATTING ISSUES
   - Note any formatting problems that ATS parsers struggle with:
     tables, columns, headers/footers, images, special characters, unusual fonts
   - Suggest plain-text alternatives.

4. KEYWORD GAPS
   - Based on the skills and experience mentioned, suggest 5–8 relevant technical keywords
     or industry terms that are missing but should be added to improve ATS matching.

5. SECTION COMPLETENESS
   - Check for missing standard sections: Summary/Objective, Skills, Education, Experience, Projects
   - Note any sections that are present but thin (too brief to be useful).

RULES:
- Be specific — reference actual content from the resume.
- Do NOT claim to give a real ATS score. This is qualitative analysis only.
- Keep the total response under 600 words.
- Use the section headers above exactly.

RESUME:
{full_text[:4000]}

ATS IMPROVEMENT SUGGESTIONS:"""
