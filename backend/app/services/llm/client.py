import logging
from typing import Generator, List, Optional
import openai
from langsmith.wrappers import wrap_openai
from langsmith import traceable

from app.core.config import settings
from app.services.llm.config import get_provider_config
from app.services.llm.types import ChatMessage

logger = logging.getLogger(__name__)

_client = None


def get_client() -> openai.OpenAI:
    global _client
    if _client is None:
        config = get_provider_config()
        base_client = openai.OpenAI(
            api_key=config.api_key,
            base_url=config.base_url,
            default_headers=config.extra_headers,
        )
        if settings.langsmith_enabled and settings.langsmith_api_key:
            _client = wrap_openai(base_client)
        else:
            _client = base_client
    return _client


SYSTEM_PROMPT = """You are a helpful AI assistant. You can help users with a variety of tasks including answering questions, providing information, and assisting with problem-solving.

Be concise but thorough in your responses. If you're unsure about something, say so. If a question is unclear, ask for clarification.

When answering questions based on uploaded documents, cite the relevant information from the sources provided."""


SYSTEM_PROMPT_WITH_CONTEXT = """You are a helpful AI assistant. The user has uploaded documents, and relevant excerpts have been retrieved and provided below.

IMPORTANT: You DO have access to the user's documents. The relevant content is provided in the "DOCUMENT EXCERPTS" section below. Use this information to answer the user's questions. Do NOT say you cannot see or access the documents - the content is right here in this prompt.

## DOCUMENT EXCERPTS

{context}

## END OF DOCUMENT EXCERPTS

Instructions:
- Answer questions using the document excerpts above
- Cite the source when referencing specific information
- If the excerpts don't contain relevant information for a specific question, say so and answer based on your general knowledge
- Be concise but thorough"""


@traceable(name="chat_completion")
def stream_chat(
    messages: List[ChatMessage],
    context: Optional[str] = None,
) -> Generator[str, None, None]:
    """Stream chat completion. Returns content chunks.

    Args:
        messages: List of chat messages
        context: Optional RAG context to include in the system prompt
    """
    client = get_client()

    # Use context-aware system prompt if context is provided
    if context:
        system_content = SYSTEM_PROMPT_WITH_CONTEXT.format(context=context)
        logger.info(f"Using RAG context in system prompt ({len(context)} chars)")
    else:
        system_content = SYSTEM_PROMPT
        logger.info("No RAG context provided, using default system prompt")

    full_messages = [
        {"role": "system", "content": system_content},
        *[{"role": m.role, "content": m.content} for m in messages],
    ]

    stream = client.chat.completions.create(
        model=settings.llm_model,
        messages=full_messages,
        stream=True,
    )

    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content
