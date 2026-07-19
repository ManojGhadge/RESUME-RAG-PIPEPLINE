"""
Ollama LLM provider — calls Ollama's local /api/generate endpoint.

Uses httpx (sync) with a generous timeout (Llama 3 8B can be slow on CPU).
Strips preamble from the response before returning.
"""

import logging
import httpx

from app.services.llm.base import LLMProvider
from app.core.exceptions import LLMError
from app.utils.text_utils import strip_llm_preamble
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Generous timeout: 8B model on CPU can take 60–300s for a long response (ATS review)
_TIMEOUT = httpx.Timeout(connect=10.0, read=300.0, write=10.0, pool=5.0)


class OllamaProvider(LLMProvider):
    """Calls Ollama's /api/generate with stream=False."""

    def __init__(self):
        self._url = f"{settings.ollama_url.rstrip('/')}/api/generate"
        self._model = settings.ollama_model
        logger.info(f"OllamaProvider ready: model={self._model}, url={self._url}")

    def generate(self, prompt: str) -> str:
        """
        Send prompt to Ollama, return cleaned response text.
        Raises LLMError on HTTP errors, timeouts, or empty responses.
        """
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,   # lower = more factual/grounded
                "top_p": 0.9,
                "num_predict": 1024,  # max tokens in response
            },
        }

        try:
            with httpx.Client(timeout=_TIMEOUT) as client:
                response = client.post(self._url, json=payload)
                response.raise_for_status()
        except httpx.TimeoutException:
            raise LLMError(
                "Ollama request timed out. The model may be slow or unavailable. "
                "Ensure Ollama is running: `ollama serve`"
            )
        except httpx.HTTPStatusError as e:
            raise LLMError(f"Ollama returned HTTP {e.response.status_code}: {e.response.text}")
        except httpx.ConnectError:
            raise LLMError(
                "Cannot connect to Ollama. Ensure it's running: `ollama serve`"
            )
        except Exception as e:
            raise LLMError(f"Unexpected error calling Ollama: {e}")

        data = response.json()
        text = data.get("response", "").strip()

        if not text:
            raise LLMError("Ollama returned an empty response.")

        # Strip preamble ("Sure, here are...", "Of course!", etc.)
        text = strip_llm_preamble(text)

        logger.debug(f"LLM response length: {len(text)} chars")
        return text
