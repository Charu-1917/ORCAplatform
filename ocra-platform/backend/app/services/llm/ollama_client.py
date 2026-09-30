"""
Client for a local Ollama server (https://ollama.com).

ORCA uses Ollama as its language model: it turns the agent telemetry
(weather, satellite, SciDL, routing, safety) into a short fisherman-friendly
answer. Everything runs locally; no cloud API key is needed.
"""

import time
import logging
from typing import Dict, Any, List, Optional

import httpx

from app.config import settings

logger = logging.getLogger("orca.ollama")


class OllamaUnavailable(Exception):
    """Raised when the Ollama server is not reachable or has no usable model."""


class OllamaClient:
    def __init__(self, base_url: str, model: str, fallback_models: List[str], timeout: float, keep_alive: str,
                 api_key: str = ""):
        self.base_url = base_url.rstrip("/")
        # When ORCA runs on Render, Ollama is reached through the PC's key-protected /gateway
        self.headers = {"ngrok-skip-browser-warning": "1"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"
        self.model = model
        self.fallback_models = fallback_models
        self.timeout = timeout
        self.keep_alive = keep_alive
        self._resolved_model: Optional[str] = None
        self._resolved_at = 0.0

    async def list_models(self) -> List[str]:
        async with httpx.AsyncClient(headers=self.headers, timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            return [m["name"] for m in resp.json().get("models", [])]

    async def resolve_model(self) -> str:
        """
        Picks the configured model if it is pulled, otherwise the first pulled
        model from the fallback list (llama / gemma family), otherwise any pulled model.
        The result is cached for 60 seconds so a newly pulled model is picked up.
        """
        if self._resolved_model and time.time() - self._resolved_at < 60:
            return self._resolved_model

        try:
            installed = await self.list_models()
        except Exception as exc:
            raise OllamaUnavailable(f"Ollama server not reachable at {self.base_url}: {exc}") from exc

        if not installed:
            raise OllamaUnavailable(f"Ollama is running but no model is pulled. Run: ollama pull {self.model}")

        def is_installed(name: str) -> Optional[str]:
            for inst in installed:
                if inst == name or inst == f"{name}:latest":
                    return inst
            return None

        chosen = None
        for candidate in [self.model] + self.fallback_models:
            chosen = is_installed(candidate)
            if chosen:
                break
        if not chosen:
            family = [m for m in installed if m.startswith(("llama", "gemma"))]
            chosen = family[0] if family else installed[0]

        if chosen != self.model and chosen != f"{self.model}:latest":
            logger.warning(f"Configured OLLAMA_MODEL '{self.model}' not pulled; using '{chosen}' instead.")

        self._resolved_model = chosen
        self._resolved_at = time.time()
        return chosen

    async def chat(self, messages: List[Dict[str, str]], temperature: float = 0.3, max_tokens: int = 600) -> Dict[str, Any]:
        model = await self.resolve_model()
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": self.keep_alive,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "num_ctx": 4096,
            },
        }
        data = None
        for attempt in (1, 2):
            try:
                async with httpx.AsyncClient(headers=self.headers, timeout=httpx.Timeout(self.timeout, connect=5.0)) as client:
                    resp = await client.post(f"{self.base_url}/api/chat", json=payload)
                    resp.raise_for_status()
                    data = resp.json()
                break
            except httpx.HTTPStatusError as exc:
                # A 5xx usually means Ollama's model runner crashed (e.g. a GPU/CUDA error);
                # Ollama restarts the runner on the next request, so retry once.
                if attempt == 1 and exc.response.status_code >= 500:
                    logger.warning(f"Ollama returned {exc.response.status_code}; retrying once.")
                    continue
                self._resolved_model = None
                raise OllamaUnavailable(f"Ollama chat request failed: {exc}") from exc
            except httpx.HTTPError as exc:
                # Force re-resolution next time (model may have been removed / server restarted)
                self._resolved_model = None
                raise OllamaUnavailable(f"Ollama chat request failed: {exc}") from exc

        content = (data.get("message") or {}).get("content", "").strip()
        if not content:
            raise OllamaUnavailable("Ollama returned an empty reply.")
        return {"model": model, "content": content}

    async def warmup(self) -> None:
        """
        Loads the model into memory in the background at server start, so the
        first chat does not pay the (multi-minute on small GPUs) model load time.
        """
        try:
            model = await self.resolve_model()
            async with httpx.AsyncClient(headers=self.headers, timeout=httpx.Timeout(self.timeout, connect=5.0)) as client:
                resp = await client.post(f"{self.base_url}/api/generate",
                                         json={"model": model, "keep_alive": self.keep_alive})
                resp.raise_for_status()
            logger.info(f"Ollama model '{model}' loaded and ready.")
        except Exception as exc:
            logger.warning(f"Ollama warm-up skipped: {exc}")

    async def status(self) -> Dict[str, Any]:
        try:
            installed = await self.list_models()
        except Exception as exc:
            return {"online": False, "base_url": self.base_url, "configured_model": self.model, "error": str(exc)}
        active = None
        try:
            active = await self.resolve_model()
        except OllamaUnavailable:
            pass
        return {
            "online": True,
            "base_url": self.base_url,
            "configured_model": self.model,
            "active_model": active,
            "installed_models": installed,
        }


ollama_client = OllamaClient(
    base_url=settings.OLLAMA_BASE_URL,
    model=settings.OLLAMA_MODEL,
    fallback_models=settings.OLLAMA_FALLBACK_MODELS,
    timeout=settings.OLLAMA_TIMEOUT,
    keep_alive=settings.OLLAMA_KEEP_ALIVE,
    api_key=settings.OLLAMA_API_KEY,
)
