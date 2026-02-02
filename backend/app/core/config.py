from pydantic_settings import BaseSettings
from typing import Literal, Optional


class Settings(BaseSettings):
    # Provider selection
    llm_provider: Literal["openai", "openrouter", "ollama", "lmstudio"] = "openrouter"
    llm_model: str = "anthropic/claude-3.5-sonnet"

    # API keys (only active provider's key required)
    openai_api_key: Optional[str] = None
    openrouter_api_key: Optional[str] = None

    # Local provider URLs (overridable)
    ollama_base_url: str = "http://localhost:11434/v1"
    lmstudio_base_url: str = "http://localhost:1234/v1"

    # OpenRouter extras
    openrouter_site_url: Optional[str] = None
    openrouter_app_name: Optional[str] = None

    # Observability
    langsmith_enabled: bool = True
    langsmith_api_key: Optional[str] = None
    langsmith_project: str = "rag-masterclass"

    # Supabase
    supabase_url: str
    supabase_anon_key: str
    supabase_service_role_key: str

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
