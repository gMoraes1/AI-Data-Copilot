"""Adapter do Ollama (Llama 3) implementando a interface LLMProvider."""

import httpx

from app.core.config import Settings
from app.core.exceptions import LLMError
from app.core.logging import get_logger
from app.services.llm.base import LLMProvider

logger = get_logger(__name__)


class OllamaProvider(LLMProvider):
    """Chama um servidor Ollama local via API REST (/api/generate)."""

    def __init__(self, settings: Settings) -> None:
        self._base_url = settings.ollama_base_url.rstrip("/")
        self._model = settings.llm_model
        self._temperature = settings.llm_temperature
        self._timeout = settings.llm_timeout_seconds

    def complete(self, prompt: str, *, system: str | None = None) -> str:
        payload: dict = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": self._temperature},
        }
        if system:
            payload["system"] = system

        try:
            with httpx.Client(timeout=self._timeout) as client:
                response = client.post(f"{self._base_url}/api/generate", json=payload)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPError as exc:
            logger.error("Falha ao chamar o Ollama", extra={"error": str(exc)})
            raise LLMError(f"Erro ao contatar o Ollama: {exc}") from exc

        text = data.get("response")
        if not text:
            raise LLMError("Resposta vazia do Ollama.")
        return text.strip()
