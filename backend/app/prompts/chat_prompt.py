"""
Prompt builder for Resume Chat.

Strict grounding: the LLM is told ONLY to answer from the provided context.
If it can't find the answer, it must say so — not invent content.
"""

from typing import List, Dict, Any


def build_chat_prompt(question: str, chunks: List[Dict[str, Any]]) -> str:
    context = "\n\n---\n\n".join(chunk["text"] for chunk in chunks)

    return f"""You are an assistant that answers questions strictly based on the resume content provided below.

RULES:
- Answer ONLY using information from the RESUME CONTEXT below.
- If the answer is not in the context, say: "I don't have enough information in this resume to answer that."
- Do NOT invent skills, experiences, or details not present in the context.
- Be concise and factual.
- Do not add opinions or suggestions unless asked.

RESUME CONTEXT:
{context}

QUESTION:
{question}

ANSWER:"""
