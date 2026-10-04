import json
from django.conf import settings
from .models import Memory
from .llm import OllamaClient
from .retrieval import cosine_search


def remember(content: str, category: str = "general") -> Memory:
    """Embed content and save it as a new Memory row."""
    client = OllamaClient()
    embedding = client.embed(content)
    memory = Memory.objects.create(
        content=content,
        category=category,
        embedding_json=json.dumps(embedding),
    )
    return memory


def recall(query: str, top_k: int = 3) -> list[tuple[Memory, float]]:
    """Return the top_k most relevant memories for a query.

    Steps:
        1. Embed the query.
        2. Score every stored Memory via cosine similarity.
        3. Apply the RECALL_THRESHOLD from settings.
        4. Return up to top_k results, highest score first.
    """
    client = OllamaClient()
    query_embedding = client.embed(query)

    memories = Memory.objects.all()
    threshold = float(getattr(settings, "RECALL_THRESHOLD", "0.35"))

    # cosine_search returns ALL memories sorted; we filter and slice here.
    scored = cosine_search(query_embedding, memories)
    filtered = [(m, s) for m, s in scored if s >= threshold]
    return filtered[:top_k]


def forget(memory_id: int) -> bool:
    """Delete a Memory by its primary key.

    Returns True if the memory existed and was deleted.
    Returns False if no memory with that ID was found.
    """
    try:
        memory = Memory.objects.get(pk=memory_id)
        memory.delete()
        return True
    except Memory.DoesNotExist:
        return False