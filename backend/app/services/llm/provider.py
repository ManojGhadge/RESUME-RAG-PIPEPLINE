"""
Shared LLM provider singleton.

All routes import `llm` from here instead of instantiating OllamaProvider directly.
Swapping to a different LLM backend = change one line here, zero changes in routes.
"""

from app.services.llm.ollama_provider import OllamaProvider

# Module-level singleton — instantiated once when first imported
llm: OllamaProvider = OllamaProvider()
