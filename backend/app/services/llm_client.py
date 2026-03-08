import os
from typing import Dict

import requests
from dotenv import load_dotenv

# Load .env file early to ensure configuration is available
load_dotenv()


class LLMClient:
    """
    Wrapper for local Llama3.1 LLM inference API.
    
    Expects a local LLM server running at http://localhost:8000
    (e.g., Ollama, LocalAI, or custom inference server)
    """

    def __init__(self) -> None:
        # Local LLM server endpoint
        self.base_url = os.getenv("LOCAL_LLM_URL", "http://localhost:8000")
        self.generate_endpoint = f"{self.base_url}/generate"
        
        print(f"[LLMClient] Initializing with local LLM at: {self.base_url}")
        
        # Test connection to local LLM
        try:
            response = requests.post(
                self.generate_endpoint,
                json={
                    "prompt": "test",
                    "max_tokens": 1,
                    "temperature": 0.7,
                },
                timeout=5
            )
            if response.status_code == 200:
                print(f"[LLMClient] Successfully connected to local LLM server")
                self._model = True  # Mark as configured
            else:
                print(f"[LLMClient] ERROR: Local LLM server returned status {response.status_code}")
                self._model = None
        except requests.exceptions.ConnectionError as e:
            print(f"[LLMClient] ERROR: Cannot connect to local LLM at {self.base_url}")
            print(f"[LLMClient] Make sure your local LLM server is running")
            print(f"[LLMClient] Error: {e}")
            self._model = None
        except Exception as e:
            print(f"[LLMClient] ERROR: {type(e).__name__}: {e}")
            self._model = None

    def is_configured(self) -> bool:
        return self._model is not None

    def generate_text(self, prompt: str, temperature: float = 0.4, max_tokens: int = 2000) -> str:
        if not self._model:
            # Fallback stub for when local LLM is not available
            return f"""ALIGNED RESUME

SUMMARY:
Based on the job description provided, this is a placeholder for the aligned resume.

EXPERIENCE:
[Resume content would be aligned here by the LLM]

SKILLS:
[Skills would be matched to job requirements]

Note: Local LLM server is not available. Please ensure:
1. Your local LLM (Llama3.1) is running on {self.base_url}
2. The /generate endpoint is accessible
3. GPU is properly configured

To start a local LLM, you can use:
- Ollama: ollama run llama2 (then pull llama3.1)
- LocalAI: localai start
- vLLM: python -m vllm.entrypoints.openai.api_server --model meta-llama/Llama-2-7b-hf
"""
        
        try:
            print(f"[LLMClient] Sending prompt to local LLM (max_tokens={max_tokens})...")
            
            payload = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40
            }
            
            response = requests.post(
                self.generate_endpoint,
                json=payload,
                timeout=300  # 5 minutes timeout for long generations
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("generated_text", "")
                tokens = result.get("tokens_generated", 0)
                time_ms = result.get("inference_time_ms", 0)
                
                print(f"[LLMClient] Successfully generated {tokens} tokens in {time_ms}ms")
                return generated_text
            else:
                error_msg = f"Local LLM returned status {response.status_code}"
                print(f"[LLMClient] ERROR: {error_msg}")
                print(f"[LLMClient] Response: {response.text[:200]}")
                return f"[ERROR] {error_msg}"
                
        except requests.exceptions.Timeout:
            print(f"[LLMClient] ERROR: Request timed out after 5 minutes")
            return "[ERROR] Request timed out - LLM response took too long"
        except requests.exceptions.ConnectionError as e:
            print(f"[LLMClient] ERROR: Connection failed to {self.generate_endpoint}")
            return f"[ERROR] Cannot connect to local LLM: {str(e)[:100]}"
        except Exception as e:
            print(f"[LLMClient] ERROR: {type(e).__name__}: {e}")
            return f"[ERROR] Failed to generate text: {str(e)[:100]}"


llm_client_singleton: LLMClient | None = None


def get_llm_client() -> LLMClient:
    global llm_client_singleton
    if llm_client_singleton is None:
        llm_client_singleton = LLMClient()
    return llm_client_singleton

