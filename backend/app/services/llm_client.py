import os
from typing import Dict

from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file early to ensure GOOGLE_API_KEY is available
load_dotenv()


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
            print("[LLMClient] WARNING: GOOGLE_API_KEY not found in environment")
            self._model = None
            return
        print(f"[LLMClient] Initializing with API key (first 10 chars): {api_key[:10]}...")
        genai.configure(api_key=api_key)
        
        # Use gemini-pro as it's the most stable and widely available model
        # If that doesn't work, we'll handle the error in generate_text()
        self._model = genai.GenerativeModel("gemini-pro")
        print("[LLMClient] Successfully initialized Gemini model: gemini-pro")

    def is_configured(self) -> bool:
        return self._model is not None

    def generate_text(self, prompt: str, temperature: float = 0.4) -> str:
        if not self._model:
            # Fallback stub for local dev without API key
            return f"[LLM stubbed output]\n\nPrompt was:\n{prompt[:1000]}"
        
        # Try with current model, fall back to alternatives if it fails
        models_to_try = [
            self._model,
            genai.GenerativeModel("gemini-pro"),
            genai.GenerativeModel("gemini-1.5-flash"),
            genai.GenerativeModel("gemini-1.5-pro"),
        ]
        
        last_error = None
        for model in models_to_try:
            try:
                print(f"[LLMClient] Attempting to generate with model...")
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=temperature,
                    ),
                )
                print(f"[LLMClient] Successfully generated content")
                return response.text or ""
            except Exception as e:
                last_error = e
                print(f"[LLMClient] Error with model: {type(e).__name__}: {str(e)[:100]}")
                continue
        
        # If all models fail, return a helpful stub that shows what was sent
        print(f"[LLMClient] WARNING: All models failed, returning stub response")
        print(f"[LLMClient] Last error: {last_error}")
        
        # Generate a simple stub response based on the prompt for testing
        return f"""ALIGNED RESUME

SUMMARY:
Based on the job description provided, here are key alignments:

EXPERIENCE:
[Aligned resume content would be generated here by the LLM if API key had proper access]

SKILLS:
[Skills would be aligned to job requirements]

Note: The LLM API key appears to be restricted. Please verify:
1. Your Google API key has proper permissions
2. Gemini models are enabled in your Google Cloud project
3. Your account has access to Generative AI models

Error: {str(last_error)[:200]}
"""


llm_client_singleton: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global llm_client_singleton
    if llm_client_singleton is None:
        llm_client_singleton = LLMClient()
    return llm_client_singleton

