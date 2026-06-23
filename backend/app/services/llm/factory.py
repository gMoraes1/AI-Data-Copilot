"""Factory que seleciona a implementação de LLMProvider a partir das settings."""

from functools import lru_cache

from app.core.config import Settings, get_settings
from app.services.llm.base import LLMProvider
from app.services.llm.fake import FakeLLMProvider
from app.services.llm.ollama import OllamaProvider


def build_llm_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "fake":
        return FakeLLMProvider()
    return OllamaProvider(settings)


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Dependency do FastAPI: provider singleton baseado na configuração."""
    return build_llm_provider(get_settings())
