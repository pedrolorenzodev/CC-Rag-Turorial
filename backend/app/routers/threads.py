import os
from fastapi import APIRouter, Depends, HTTPException, status
from supabase import create_client
from app.middleware.auth import get_current_user, User
from app.models.thread import Thread, ThreadCreate, ThreadUpdate, Message

router = APIRouter(prefix="/api/threads", tags=["threads"])


def get_user_client(user: User):
    """Create a Supabase client for database operations."""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database configuration missing",
        )
    return create_client(url, key)


@router.get("", response_model=list[Thread])
async def list_threads(user: User = Depends(get_current_user)):
    """List all threads for the current user."""
    client = get_user_client(user)
    response = (
        client.table("threads")
        .select("*")
        .eq("user_id", user.id)
        .order("updated_at", desc=True)
        .execute()
    )
    return response.data


@router.post("", response_model=Thread, status_code=status.HTTP_201_CREATED)
async def create_thread(
    thread_data: ThreadCreate, user: User = Depends(get_current_user)
):
    """Create a new thread."""
    client = get_user_client(user)
    response = (
        client.table("threads")
        .insert({"user_id": user.id, "title": thread_data.title})
        .execute()
    )
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create thread",
        )
    return response.data[0]


@router.get("/{thread_id}", response_model=Thread)
async def get_thread(thread_id: str, user: User = Depends(get_current_user)):
    """Get a specific thread."""
    client = get_user_client(user)
    response = (
        client.table("threads")
        .select("*")
        .eq("id", thread_id)
        .eq("user_id", user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found"
        )
    return response.data[0]


@router.patch("/{thread_id}", response_model=Thread)
async def update_thread(
    thread_id: str, thread_data: ThreadUpdate, user: User = Depends(get_current_user)
):
    """Update a thread."""
    client = get_user_client(user)
    update_data = thread_data.model_dump(exclude_unset=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No data to update"
        )

    response = (
        client.table("threads")
        .update(update_data)
        .eq("id", thread_id)
        .eq("user_id", user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found"
        )
    return response.data[0]


@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_thread(thread_id: str, user: User = Depends(get_current_user)):
    """Delete a thread."""
    client = get_user_client(user)
    response = (
        client.table("threads")
        .delete()
        .eq("id", thread_id)
        .eq("user_id", user.id)
        .execute()
    )
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found"
        )
    return None


@router.get("/{thread_id}/messages", response_model=list[Message])
async def get_messages(thread_id: str, user: User = Depends(get_current_user)):
    """Get all messages for a thread."""
    client = get_user_client(user)

    # First verify the thread belongs to the user
    thread_response = (
        client.table("threads")
        .select("id")
        .eq("id", thread_id)
        .eq("user_id", user.id)
        .execute()
    )
    if not thread_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found"
        )

    response = (
        client.table("messages")
        .select("*")
        .eq("thread_id", thread_id)
        .order("created_at", desc=False)
        .execute()
    )
    return response.data
