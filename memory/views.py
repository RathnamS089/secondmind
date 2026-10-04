import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .agent import Agent
from .models import Memory
from .tools import remember, recall

logger = logging.getLogger(__name__)


def health(request):
    """GET /api/health/ — confirms Django is running."""
    return JsonResponse({"status": "ok"})


@require_http_methods(["POST"])
def chat(request):
    """POST /api/chat/"""
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Request body must be valid JSON."}, status=400)

    user_message = body.get("message", "").strip()
    if not user_message:
        return JsonResponse({"error": "message is required and must not be empty."}, status=400)

    try:
        agent = Agent()
        result = agent.chat(user_message)
    except RuntimeError as e:
        logger.error("Ollama error during chat: %s", e)
        return JsonResponse({"error": str(e)}, status=503)
    except Exception as e:
        logger.exception("Unexpected error during chat")
        return JsonResponse({"error": "An unexpected error occurred."}, status=500)

    return JsonResponse(result)


@require_http_methods(["GET", "POST"])
def memories(request):
    if request.method == "GET":
        qs = Memory.objects.order_by("-created_at").values(
            "id", "content", "category", "importance", "created_at"
        )
        return JsonResponse({"memories": list(qs)})
    elif request.method == "POST":
        try:
            body = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)
        
        content = body.get("content", "").strip()
        category = body.get("category", "General").strip()
        if not content:
            return JsonResponse({"error": "content is required"}, status=400)
            
        try:
            memory = remember(content, category)
            return JsonResponse({
                "success": True,
                "memory": {
                    "id": memory.id,
                    "content": memory.content,
                    "category": memory.category,
                    "created_at": memory.created_at.isoformat()
                }
            })
        except RuntimeError as e:
            return JsonResponse({"error": str(e)}, status=503)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["DELETE"])
def memory_delete(request, memory_id):
    """DELETE /api/memories/<id>/"""
    try:
        memory = Memory.objects.get(pk=memory_id)
        memory.delete()
        return JsonResponse({"deleted": memory_id})
    except Memory.DoesNotExist:
        return JsonResponse(
            {"error": f"Memory with id {memory_id} does not exist."}, status=404
        )

@require_http_methods(["POST"])
def recall_view(request):
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    
    query = body.get("query", "").strip()
    if not query:
        return JsonResponse({"error": "query is required"}, status=400)
        
    try:
        results = recall(query)
        formatted = []
        for mem, score in results:
            formatted.append({
                "id": mem.id,
                "content": mem.content,
                "category": mem.category,
                "score": round(score, 2)
            })
        return JsonResponse({"results": formatted})
    except RuntimeError as e:
        return JsonResponse({"error": str(e)}, status=503)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
