"""
OpenAI LLM provider — calls OpenAI's Chat Completions API.
Uses httpx (sync) to send prompt requests.
"""

import logging
import httpx

from app.services.llm.base import LLMProvider
from app.core.exceptions import LLMError
from app.utils.text_utils import strip_llm_preamble
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# OpenAI API Timeout: typically chat models respond within 10-30 seconds
_TIMEOUT = httpx.Timeout(connect=10.0, read=60.0, write=10.0, pool=5.0)


class OpenAIProvider(LLMProvider):
    """Calls OpenAI's Chat Completions API."""

    def __init__(self):
        self._url = "https://api.openai.com/v1/chat/completions"
        self._model = settings.openai_model
        self._api_key = settings.openai_api_key
        logger.info(f"OpenAIProvider ready: model={self._model}")

    def generate(self, prompt: str) -> str:
        """
        Send prompt to OpenAI, return cleaned response text.
        Raises LLMError on HTTP errors, timeouts, or empty responses.
        """
        if not self._api_key:
            raise LLMError(
                "OpenAI API Key is missing. Please set the OPENAI_API_KEY environment variable."
            )

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self._model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
        }

        try:
            with httpx.Client(timeout=_TIMEOUT) as client:
                response = client.post(self._url, headers=headers, json=payload)
                response.raise_for_status()
        except httpx.TimeoutException:
            raise LLMError("OpenAI request timed out.")
        except httpx.HTTPStatusError as e:
            # Attempt to extract OpenAI's specific error message if available
            try:
                err_data = e.response.json()
                err_msg = err_data.get("error", {}).get("message", e.response.text)
            except Exception:
                err_msg = e.response.text
            raise LLMError(f"OpenAI returned HTTP {e.response.status_code}: {err_msg}")
        except httpx.ConnectError:
            raise LLMError("Cannot connect to OpenAI API endpoint. Check your network connection.")
        except Exception as e:
            raise LLMError(f"Unexpected error calling OpenAI: {e}")

        data = response.json()
        try:
            text = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError):
            raise LLMError(f"Malformed response format from OpenAI API: {data}")

        if not text:
            raise LLMError("OpenAI returned an empty response.")

        # Strip preamble ("Sure, here are...", "Of course!", etc.)
        text = strip_llm_preamble(text)

        logger.debug(f"OpenAI response length: {len(text)} chars")
        return text
