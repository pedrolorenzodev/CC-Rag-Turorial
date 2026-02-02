import os
from typing import Optional, AsyncGenerator
from langsmith import traceable
from langsmith.wrappers import wrap_openai
import openai

# Lazy initialization of OpenAI client
_client = None


def get_client():
    """Get or create the LangSmith-wrapped OpenAI client."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _base_client = openai.OpenAI(api_key=api_key)
        _client = wrap_openai(_base_client)
    return _client


SYSTEM_PROMPT = """You are a helpful AI assistant. You can help users with a variety of tasks including answering questions, providing information, and assisting with problem-solving.

Be concise but thorough in your responses. If you're unsure about something, say so. If a question is unclear, ask for clarification.

When answering questions based on uploaded documents, cite the relevant information from the files."""

# Default model - GPT-4o-mini (cost-effective and fast)
DEFAULT_MODEL = "gpt-4o-mini"


@traceable(name="create_response")
def create_response(
    user_input: str,
    previous_response_id: Optional[str] = None,
    vector_store_id: Optional[str] = None,
    stream: bool = True,
):
    """
    Create a response using OpenAI Responses API.

    Args:
        user_input: The user's message
        previous_response_id: ID of the previous response for conversation continuity
        vector_store_id: Vector store ID for file_search tool
        stream: Whether to stream the response
    """
    client = get_client()
    model = os.getenv("LLM_MODEL", DEFAULT_MODEL)

    # Build the request parameters
    params = {
        "model": model,
        "input": user_input,
        "stream": stream,
        "store": True,  # Store the response for conversation continuity
        "instructions": SYSTEM_PROMPT,
    }

    # Add previous response for conversation continuity
    if previous_response_id:
        params["previous_response_id"] = previous_response_id

    # Add file_search tool if vector store is available
    if vector_store_id:
        params["tools"] = [
            {
                "type": "file_search",
                "vector_store_ids": [vector_store_id],
            }
        ]

    return client.responses.create(**params)


async def stream_response(
    messages: list[dict],
    previous_response_id: Optional[str] = None,
    vector_store_id: Optional[str] = None,
) -> AsyncGenerator[tuple[str, Optional[str]], None]:
    """
    Stream a response from OpenAI Responses API and yield chunks.

    Args:
        messages: List of messages (only the last user message is used,
                  conversation history is managed via previous_response_id)
        previous_response_id: ID of the previous response for conversation continuity
        vector_store_id: Vector store ID for file_search tool

    Yields:
        Tuples of (content_chunk, response_id)
        response_id is only set on the final chunk
    """
    # Get the last user message
    user_message = messages[-1]["content"] if messages else ""

    response_stream = create_response(
        user_input=user_message,
        previous_response_id=previous_response_id,
        vector_store_id=vector_store_id,
        stream=True,
    )

    response_id = None
    for event in response_stream:
        # Handle different event types from the Responses API
        if event.type == "response.output_text.delta":
            yield (event.delta, None)
        elif event.type == "response.completed":
            response_id = event.response.id
            yield ("", response_id)


def create_vector_store(name: str) -> str:
    """
    Create a new vector store for file_search.

    Args:
        name: Name for the vector store

    Returns:
        The vector store ID
    """
    client = get_client()
    vector_store = client.vector_stores.create(name=name)
    return vector_store.id


def upload_file_to_vector_store(vector_store_id: str, file_path: str) -> str:
    """
    Upload a file to a vector store.

    Args:
        vector_store_id: The vector store ID
        file_path: Path to the file to upload

    Returns:
        The file ID
    """
    client = get_client()

    # Upload the file
    with open(file_path, "rb") as f:
        file = client.files.create(file=f, purpose="assistants")

    # Add file to vector store
    client.vector_stores.files.create(
        vector_store_id=vector_store_id,
        file_id=file.id,
    )

    return file.id
