from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health, name="health"),
    path("chat/", views.chat, name="chat"),
    path("memories/", views.memories, name="memory-list"),
    path("memories/<int:memory_id>/", views.memory_delete, name="memory-delete"),
    path("recall/", views.recall_view, name="recall"),
]
