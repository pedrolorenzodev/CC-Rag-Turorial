import io
import os
from supabase import create_client

from app.services.ingestion.chunker import chunk_text
from app.services.ingestion.embeddings import generate_embeddings


def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise ValueError("Supabase configuration missing")
    return create_client(url, key)


def sanitize_text(text: str) -> str:
    """Remove null bytes and other problematic characters for PostgreSQL."""
    # Remove null bytes which PostgreSQL doesn't support
    text = text.replace("\x00", "")
    # Replace other problematic control characters (except newlines and tabs)
    import re
    text = re.sub(r'[\x01-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text


def extract_text_from_pdf(content: bytes) -> str:
    """Extract text from a PDF file using pypdf."""
    from pypdf import PdfReader

    reader = PdfReader(io.BytesIO(content))
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)

    return "\n\n".join(text_parts)


def extract_text_from_file(content: bytes, filename: str) -> str:
    """Extract text content from a file based on its extension."""
    ext = os.path.splitext(filename)[1].lower()

    if ext in [".txt", ".md"]:
        text = content.decode("utf-8")
    elif ext == ".json":
        text = content.decode("utf-8")
    elif ext == ".csv":
        text = content.decode("utf-8")
    elif ext == ".pdf":
        text = extract_text_from_pdf(content)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    # Sanitize text to remove null bytes and normalize whitespace
    return sanitize_text(text)


async def process_document(document_id: str, user_id: str) -> None:
    """
    Process a document: download, chunk, embed, and store in pgvector.

    Args:
        document_id: The ID of the document to process
        user_id: The ID of the user who owns the document
    """
    client = get_supabase_client()

    # Get document record
    doc_response = (
        client.table("documents")
        .select("*")
        .eq("id", document_id)
        .execute()
    )

    if not doc_response.data:
        raise ValueError("Document not found")

    doc = doc_response.data[0]

    try:
        # Download file from storage
        file_content = client.storage.from_("documents").download(doc["storage_path"])

        # Extract text
        text = extract_text_from_file(file_content, doc["filename"])

        if not text.strip():
            raise ValueError("No text content extracted from file")

        # Chunk the text
        chunks = chunk_text(text)

        if not chunks:
            raise ValueError("No chunks created from text")

        # Delete existing chunks for this document (in case of reprocessing)
        client.table("chunks").delete().eq("document_id", document_id).execute()

        # Generate embeddings in batches
        batch_size = 100
        total_chunks = 0

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i : i + batch_size]
            texts = [c.content for c in batch]

            # Generate embeddings for batch
            embeddings = generate_embeddings(texts)

            # Prepare chunk records
            chunk_records = []
            for j, (chunk, embedding) in enumerate(zip(batch, embeddings)):
                chunk_records.append(
                    {
                        "document_id": document_id,
                        "user_id": user_id,
                        "content": chunk.content,
                        "embedding": embedding,
                        "metadata": {
                            **chunk.metadata,
                            "filename": doc["filename"],
                        },
                        "chunk_index": chunk.index,
                    }
                )

            # Insert chunks
            client.table("chunks").insert(chunk_records).execute()
            total_chunks += len(chunk_records)

        # Update document status to completed
        client.table("documents").update(
            {
                "status": "completed",
                "chunk_count": total_chunks,
                "error_message": None,
            }
        ).eq("id", document_id).execute()

    except Exception as e:
        # Update document status to failed
        client.table("documents").update(
            {
                "status": "failed",
                "error_message": str(e),
            }
        ).eq("id", document_id).execute()
        raise
