from dataclasses import dataclass
from typing import Optional, Dict
from app.core.config import settings


@dataclass
class ProviderConfig:
    base_url: str
    api_key: str
    extra_headers: Optional[Dict[str, str]] = None


def get_provider_config() -> ProviderConfig:
    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise ValueError(
                "OPENAI_API_KEY is required when LLM_PROVIDER=openai. "
                "Add it to your .env file."
            )
        return ProviderConfig(
            base_url="https://api.openai.com/v1",
            api_key=settings.openai_api_key,
        )
    elif settings.llm_provider == "openrouter":
        if not settings.openrouter_api_key:
            raise ValueError(
                "OPENROUTER_API_KEY is required when LLM_PROVIDER=openrouter. "
                "Get your key at https://openrouter.ai and add it to your .env file."
            )
        headers = {}
        if settings.openrouter_site_url:
            headers["HTTP-Referer"] = settings.openrouter_site_url
        if settings.openrouter_app_name:
            headers["X-Title"] = settings.openrouter_app_name
        return ProviderConfig(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key,
            extra_headers=headers or None,
        )
    elif settings.llm_provider == "ollama":
        return ProviderConfig(
            base_url=settings.ollama_base_url,
            api_key="ollama",
        )
    elif settings.llm_provider == "lmstudio":
        return ProviderConfig(
            base_url=settings.lmstudio_base_url,
            api_key="lm-studio",
        )
    else:
        raise ValueError(
            f"Unknown LLM provider: {settings.llm_provider}. "
            f"Valid options: openai, openrouter, ollama, lmstudio"
        )
