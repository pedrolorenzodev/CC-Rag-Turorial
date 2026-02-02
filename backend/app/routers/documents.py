import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from pydantic import BaseModel
from supabase import create_client

from app.middleware.auth import get_current_user, User

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".txt", ".md", ".pdf", ".json", ".csv"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


class DocumentResponse(BaseModel):
    id: str
    filename: str
    status: str
    error_message: Optional[str] = None
    chunk_count: int
    created_at: str


def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database configuration missing",
        )
    return create_client(url, key)


def validate_file(file: UploadFile) -> None:
    """Validate file extension and size."""
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
):
    """Upload a document for processing."""
    validate_file(file)

    client = get_supabase_client()

    # Read file content
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB",
        )

    # Generate unique storage path
    file_ext = os.path.splitext(file.filename)[1]
    storage_path = f"{user.id}/{uuid.uuid4()}{file_ext}"

    # Upload to Supabase Storage
    try:
        client.storage.from_("documents").upload(
            path=storage_path,
            file=content,
            file_options={"content-type": file.content_type or "application/octet-stream"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}",
        )

    # Create document record
    doc_response = (
        client.table("documents")
        .insert(
            {
                "user_id": user.id,
                "filename": file.filename,
                "storage_path": storage_path,
                "status": "pending",
            }
        )
        .execute()
    )

    if not doc_response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create document record",
        )

    doc = doc_response.data[0]
    return DocumentResponse(
        id=doc["id"],
        filename=doc["filename"],
        status=doc["status"],
        error_message=doc.get("error_message"),
        chunk_count=doc.get("chunk_count", 0),
        created_at=doc["created_at"],
    )


@router.get("", response_model=List[DocumentResponse])
async def list_documents(user: User = Depends(get_current_user)):
    """List all documents for the current user."""
    client = get_supabase_client()

    response = (
        client.table("documents")
        .select("*")
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
    )

    return [
        DocumentResponse(
            id=doc["id"],
            filename=doc["filename"],
            status=doc["status"],
            error_message=doc.get("error_message"),
            chunk_count=doc.get("chunk_count", 0),
            created_at=doc["created_at"],
        )
        for doc in response.data
    ]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, user: User = Depends(get_current_user)):
    """Get a specific document."""
    client = get_supabase_client()

    response = (
        client.table("documents")
        .select("*")
        .eq("id", document_id)
        .eq("user_id", user.id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    doc = response.data[0]
    return DocumentResponse(
        id=doc["id"],
        filename=doc["filename"],
        status=doc["status"],
        error_message=doc.get("error_message"),
        chunk_count=doc.get("chunk_count", 0),
        created_at=doc["created_at"],
    )


@router.delete("/{document_id}")
async def delete_document(document_id: str, user: User = Depends(get_current_user)):
    """Delete a document and its chunks."""
    client = get_supabase_client()

    # Get document to verify ownership and get storage path
    response = (
        client.table("documents")
        .select("*")
        .eq("id", document_id)
        .eq("user_id", user.id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    doc = response.data[0]

    # Delete from storage
    try:
        client.storage.from_("documents").remove([doc["storage_path"]])
    except Exception:
        pass  # Continue even if storage deletion fails

    # Delete document (chunks cascade delete automatically)
    client.table("documents").delete().eq("id", document_id).execute()

    return {"message": "Document deleted"}


@router.post("/{document_id}/process")
async def process_document(document_id: str, user: User = Depends(get_current_user)):
    """Trigger processing for a document."""
    from app.services.ingestion import process_document as ingest_document

    client = get_supabase_client()

    # Get document to verify ownership
    response = (
        client.table("documents")
        .select("*")
        .eq("id", document_id)
        .eq("user_id", user.id)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    doc = response.data[0]

    if doc["status"] == "processing":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document is already being processed",
        )

    # Update status to processing
    client.table("documents").update({"status": "processing"}).eq("id", document_id).execute()

    # Process document (this runs synchronously for now)
    try:
        await ingest_document(document_id, user.id)
        return {"message": "Document processed successfully"}
    except Exception as e:
        # Update status to failed
        client.table("documents").update(
            {"status": "failed", "error_message": str(e)}
        ).eq("id", document_id).execute()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Processing failed: {str(e)}",
        )
