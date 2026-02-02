from typing import List
import openai

from app.services.llm.config import get_provider_config
from app.core.config import settings

EMBEDDING_MODEL = "text-embedding-3-small"


def get_embedding_client() -> openai.OpenAI:
    """Get an OpenAI client configured for embeddings."""
    # Embeddings typically use OpenAI directly, but can also go through OpenRouter
    config = get_provider_config()

    # For OpenRouter, we need to use a different approach
    # OpenRouter supports embeddings via their API
    if settings.llm_provider == "openrouter":
        return openai.OpenAI(
            api_key=config.api_key,
            base_url="https://openrouter.ai/api/v1",
            default_headers=config.extra_headers,
        )

    # For OpenAI or local providers
    return openai.OpenAI(
        api_key=config.api_key,
        base_url=config.base_url,
        default_headers=config.extra_headers,
    )


def generate_embeddings(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts.

    Args:
        texts: List of text strings to embed

    Returns:
        List of embedding vectors (each is a list of floats)
    """
    if not texts:
        return []

    client = get_embedding_client()

    # OpenRouter uses different model names for embeddings
    model = EMBEDDING_MODEL
    if settings.llm_provider == "openrouter":
        model = "openai/text-embedding-3-small"

    response = client.embeddings.create(
        model=model,
        input=texts,
    )

    # Sort by index to ensure order matches input
    sorted_data = sorted(response.data, key=lambda x: x.index)
    return [item.embedding for item in sorted_data]


def generate_embedding(text: str) -> List[float]:
    """
    Generate embedding for a single text.

    Args:
        text: Text string to embed

    Returns:
        Embedding vector as a list of floats
    """
    embeddings = generate_embeddings([text])
    return embeddings[0] if embeddings else []
