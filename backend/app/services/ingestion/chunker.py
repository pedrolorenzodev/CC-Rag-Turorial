from typing import List
from dataclasses import dataclass


@dataclass
class Chunk:
    content: str
    index: int
    metadata: dict


def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> List[Chunk]:
    """
    Split text into overlapping chunks.

    Args:
        text: The text to split
        chunk_size: Target size for each chunk in characters
        chunk_overlap: Number of characters to overlap between chunks

    Returns:
        List of Chunk objects
    """
    if not text or not text.strip():
        return []

    # Normalize whitespace
    text = " ".join(text.split())

    chunks = []
    start = 0
    index = 0

    while start < len(text):
        # Calculate end position
        end = start + chunk_size

        # If this isn't the last chunk, try to break at a sentence or word boundary
        if end < len(text):
            # Try to find a sentence boundary (., !, ?) within the last 20% of the chunk
            search_start = start + int(chunk_size * 0.8)
            best_break = -1

            for i in range(end, search_start, -1):
                if i < len(text) and text[i - 1] in ".!?" and (i == len(text) or text[i] == " "):
                    best_break = i
                    break

            # If no sentence boundary, try to find a word boundary
            if best_break == -1:
                for i in range(end, search_start, -1):
                    if i < len(text) and text[i] == " ":
                        best_break = i + 1
                        break

            if best_break != -1:
                end = best_break

        # Extract chunk
        chunk_text = text[start:end].strip()

        if chunk_text:
            chunks.append(
                Chunk(
                    content=chunk_text,
                    index=index,
                    metadata={
                        "start_char": start,
                        "end_char": end,
                    },
                )
            )
            index += 1

        # Move start position with overlap
        start = end - chunk_overlap
        if start >= end:
            start = end

    return chunks
