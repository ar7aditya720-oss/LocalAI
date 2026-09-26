from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import httpx
import urllib.request
import json
import asyncio

class BaseModelAdapter(ABC):
    @abstractmethod
    async def generate(self, prompt: str, model_name: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        pass

    @abstractmethod
    async def list_models(self) -> List[Dict[str, Any]]:
        pass

class OllamaAdapter(BaseModelAdapter):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")

    async def list_models(self) -> List[Dict[str, Any]]:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    models = []
                    for m in data.get("models", []):
                        name = m.get("name", "")
                        details = m.get("details", {})
                        models.append({
                            "name": name,
                            "size_gb": round(m.get("size", 0) / (1024**3), 2),
                            "quantization": details.get("quantization_level", "Unknown"),
                            "family": details.get("family", "LLM"),
                            "context_length": details.get("context_length", 4096),
                            "status": "Ready (Local GPU)"
                        })
                    return models
        except Exception as e:
            print(f"[OllamaAdapter] List models exception: {e}")
        return []

    async def generate(
        self,
        prompt: str,
        model_name: str = "llama3.1:latest",
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        payload = {
            "model": model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                # Low temperature = factual, grounded, no hallucination
                "temperature": kwargs.get("temperature", 0.15),
                # Enough tokens for a solid response
                "num_predict": kwargs.get("max_tokens", 600),
                # Penalize repetition strongly to avoid bluffing loops
                "repeat_penalty": 1.3,
                # top_p nucleus sampling — keeps it focused
                "top_p": 0.85,
                # top_k — narrows token selection further
                "top_k": 30,
            }
        }
        if system_prompt:
            payload["system"] = system_prompt

        # Primary attempt
        res = await self._send_request(payload)
        if res and "[LocalAI Adapter Error]" not in res:
            return res

        # Fallback to llama3.2:latest
        if model_name != "llama3.2:latest":
            payload["model"] = "llama3.2:latest"
            res_fallback = await self._send_request(payload)
            if res_fallback and "[LocalAI Adapter Error]" not in res_fallback:
                return res_fallback

        return res or "[LocalAI] No response from local model."

    async def _send_request(self, payload: dict) -> str:
        """Sends inference request to Ollama — httpx primary, urllib fallback."""
        url = f"{self.base_url}/api/generate"

        # Method 1: Async httpx — 60s timeout for larger responses
        try:
            timeout_cfg = httpx.Timeout(60.0, connect=5.0)
            async with httpx.AsyncClient(timeout=timeout_cfg) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    output = resp.json().get("response", "").strip()
                    if output:
                        return output
        except Exception as e:
            print(f"[OllamaAdapter httpx]: {e} — switching to urllib fallback...")

        # Method 2: Sync urllib in thread pool — 60s timeout
        def _urllib_sync():
            try:
                data_bytes = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    url, data=data_bytes, headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=60) as r:
                    if r.status == 200:
                        return json.loads(r.read().decode("utf-8")).get("response", "").strip()
            except Exception as ex:
                return f"[LocalAI Adapter Error]: {ex}"
            return ""

        try:
            return await asyncio.to_thread(_urllib_sync)
        except Exception as ex2:
            return f"[LocalAI Adapter Error]: {ex2}"
