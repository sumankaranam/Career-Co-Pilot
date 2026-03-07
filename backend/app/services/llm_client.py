import os
from typing import Dict

import google.generativeai as genai


class LLMClient:
    """
    Thin wrapper around Google Gemini.

    For local development without a key, you can stub calls by
    setting GOOGLE_API_KEY to an empty string and catching errors
    at call sites.
    """

    def __init__(self) -> None:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            self._model = None
            return
        genai.configure(api_key=api_key)
        # Model name can be adjusted by env var later
        self._model = genai.GenerativeModel("gemini-1.5-pro")

    def is_configured(self) -> bool:
        return self._model is not None

    def generate_text(self, prompt: str, temperature: float = 0.4) -> str:
        if not self._model:
            # Fallback stub for local dev without API key
            return f"[LLM stubbed output]\n\nPrompt was:\n{prompt[:1000]}"
        response = self._model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=temperature,
            ),
        )
        return response.text or ""


llm_client_singleton: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global llm_client_singleton
    if llm_client_singleton is None:
        llm_client_singleton = LLMClient()
    return llm_client_singleton

