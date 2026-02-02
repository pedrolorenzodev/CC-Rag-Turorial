import os
from typing import List, Optional
from dataclasses import dataclass
from supabase import create_client

from app.services.ingestion.embeddings import generate_embedding


@dataclass
class RetrievedChunk:
    id: str
    document_id: str
    content: str
    metadata: dict
    similarity: float


def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise ValueError("Supabase configuration missing")
    return create_client(url, key)


def retrieve_context(
    query: str,
    user_id: str,
    match_count: int = 5,
    similarity_threshold: float = 0.5,
) -> List[RetrievedChunk]:
    """
    Retrieve relevant context from the vector store.

    Args:
        query: The search query
        user_id: The user ID to filter chunks by
        match_count: Maximum number of chunks to return
        similarity_threshold: Minimum similarity score (0-1)

    Returns:
        List of retrieved chunks sorted by relevance
    """
    # Generate embedding for the query
    query_embedding = generate_embedding(query)

    if not query_embedding:
        return []

    client = get_supabase_client()

    # Call the match_chunks function
    response = client.rpc(
        "match_chunks",
        {
            "query_embedding": query_embedding,
            "match_count": match_count,
            "filter_user_id": user_id,
        },
    ).execute()

    if not response.data:
        return []

    # Filter by similarity threshold and convert to dataclass
    chunks = []
    for row in response.data:
        if row["similarity"] >= similarity_threshold:
            chunks.append(
                RetrievedChunk(
                    id=row["id"],
                    document_id=row["document_id"],
                    content=row["content"],
                    metadata=row["metadata"] or {},
                    similarity=row["similarity"],
                )
            )

    return chunks


def format_context_for_prompt(chunks: List[RetrievedChunk]) -> Optional[str]:
    """
    Format retrieved chunks into a context string for the LLM prompt.

    Args:
        chunks: List of retrieved chunks

    Returns:
        Formatted context string or None if no chunks
    """
    if not chunks:
        return None

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.metadata.get("filename", "Unknown source")
        context_parts.append(f"[Source {i}: {source}]\n{chunk.content}")

    return "\n\n---\n\n".join(context_parts)
