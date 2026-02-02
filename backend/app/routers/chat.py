import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from supabase import create_client

from app.middleware.auth import get_current_user, User
from app.services.llm import stream_chat, ChatMessage
from app.services.retrieval import retrieve_context
from app.services.retrieval.search import format_context_for_prompt

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/threads", tags=["chat"])


class ChatRequest(BaseModel):
    content: str


def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database configuration missing",
        )
    return create_client(url, key)


@router.post("/{thread_id}/chat")
async def chat(
    thread_id: str, request: ChatRequest, user: User = Depends(get_current_user)
):
    """
    Send a message and stream the AI response via SSE.
    Uses RAG to retrieve relevant context from user's documents.
    """
    client = get_supabase_client()

    # Verify thread belongs to user
    thread_response = (
        client.table("threads")
        .select("*")
        .eq("id", thread_id)
        .eq("user_id", user.id)
        .execute()
    )
    if not thread_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found"
        )

    # Save user message
    client.table("messages").insert(
        {
            "thread_id": thread_id,
            "user_id": user.id,
            "role": "user",
            "content": request.content,
        }
    ).execute()

    # Get conversation history
    messages_response = (
        client.table("messages")
        .select("role, content")
        .eq("thread_id", thread_id)
        .order("created_at", desc=False)
        .execute()
    )
    messages = messages_response.data

    # Convert to ChatMessage objects
    chat_messages = [
        ChatMessage(role=m["role"], content=m["content"])
        for m in messages
    ]

    # Retrieve relevant context from user's documents
    context = None
    try:
        logger.info(f"Retrieving context for user_id={user.id}, query={request.content[:50]}...")
        chunks = retrieve_context(
            query=request.content,
            user_id=user.id,
            match_count=5,
            similarity_threshold=0.3,
        )
        logger.info(f"Retrieved {len(chunks)} chunks")
        context = format_context_for_prompt(chunks)
        logger.info(f"Context length: {len(context) if context else 0} chars")
    except Exception as e:
        logger.error(f"Retrieval failed: {e}", exc_info=True)
        # If retrieval fails, continue without context
        pass

    async def generate():
        full_response = ""
        logger.info(f"Starting stream_chat with context={context is not None}, context_len={len(context) if context else 0}")

        try:
            for chunk in stream_chat(messages=chat_messages, context=context):
                full_response += chunk
                # Encode newlines for SSE transmission (SSE uses \n as delimiter)
                encoded_chunk = chunk.replace("\n", "\\n").replace("\r", "\\r")
                yield {"event": "message", "data": encoded_chunk}

            # Save assistant message
            client.table("messages").insert(
                {
                    "thread_id": thread_id,
                    "user_id": user.id,
                    "role": "assistant",
                    "content": full_response,
                }
            ).execute()

            # Update thread title if it's the first message
            if len(messages) == 1:
                title = request.content[:50] + ("..." if len(request.content) > 50 else "")
                client.table("threads").update({"title": title}).eq(
                    "id", thread_id
                ).execute()

            yield {"event": "done", "data": ""}

        except Exception as e:
            yield {"event": "error", "data": str(e)}

    return EventSourceResponse(generate())
