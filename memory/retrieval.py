import json
import numpy as np
from .models import Memory


def cosine_search(
    query_embedding: list[float],
    memories,
) -> list[tuple[Memory, float]]:
    """Score every Memory object against a query embedding using cosine similarity.

    Args:
        query_embedding: embedding vector for the user's query.
        memories: queryset or list of Memory objects to score.

    Returns:
        List of (Memory, score) tuples, sorted by score descending.
        Memories with an empty or missing embedding are skipped.
    """
    a = np.array(query_embedding, dtype=float)
    results = []

    for m in memories:
        try:
            stored = json.loads(m.embedding_json)
        except (TypeError, ValueError):
            continue
            
        if not stored:
            continue
        b = np.array(stored, dtype=float)
        # Skip stale embeddings produced by a different embedding model
        # (dimension mismatch would crash np.dot).
        if b.shape[0] != a.shape[0]:
            continue
        den = np.linalg.norm(a) * np.linalg.norm(b)
        sim = float(np.dot(a, b) / den) if den != 0 else 0.0
        results.append((m, sim))

    results.sort(key=lambda x: x[1], reverse=True)
    return results
