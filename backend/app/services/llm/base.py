"""
Abstract LLM provider interface.

Every route calls llm_provider.generate(prompt) — never Ollama directly.
Swapping to GPT-4/Claude/Gemini = one new file that implements this class.
Zero changes to routes, prompts, or services.
"""

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Base class for all LLM backends."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Send a prompt, return the generated text.
        Should raise LLMError on failure (not raw HTTP exceptions).
        """
        ...
