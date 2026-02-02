import os
from fastapi import APIRouter, Depends, HTTPException, status
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from supabase import create_client

from app.middleware.auth import get_current_user, User
from app.services.openai_service import stream_response

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

    thread = thread_response.data[0]

    # Get vector store ID from thread or use default
    vector_store_id = thread.get("vector_store_id") or os.getenv("DEFAULT_VECTOR_STORE_ID")

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

    async def generate():
        full_response = ""
        response_id = None

        try:
            async for chunk, rid in stream_response(
                messages=messages,
                previous_response_id=thread.get("openai_thread_id"),
                vector_store_id=vector_store_id,
            ):
                if chunk:
                    full_response += chunk
                    # Encode newlines for SSE transmission (SSE uses \n as delimiter)
                    encoded_chunk = chunk.replace("\n", "\\n").replace("\r", "\\r")
                    yield {"event": "message", "data": encoded_chunk}
                if rid:
                    response_id = rid

            # Save assistant message
            client.table("messages").insert(
                {
                    "thread_id": thread_id,
                    "user_id": user.id,
                    "role": "assistant",
                    "content": full_response,
                    "metadata": {"response_id": response_id} if response_id else {},
                }
            ).execute()

            # Update thread with OpenAI response ID for conversation continuity
            if response_id:
                client.table("threads").update(
                    {"openai_thread_id": response_id}
                ).eq("id", thread_id).execute()

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
