"""
Shared LLM provider singleton.

All routes import `llm` from here instead of instantiating OllamaProvider directly.
Swapping to a different LLM backend = change one line here, zero changes in routes.
"""

from app.config import get_settings
from app.services.llm.base import LLMProvider
from app.services.llm.ollama_provider import OllamaProvider
from app.services.llm.openai_provider import OpenAIProvider

settings = get_settings()

# Module-level singleton — instantiated once when first imported
llm: LLMProvider

if settings.llm_provider.lower() == "openai":
    llm = OpenAIProvider()
else:
    llm = OllamaProvider()
