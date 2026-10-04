from django.db import models
class Memory(models.Model):
    content=models.TextField()
    category=models.CharField(max_length=32,default="general")
    embedding_json=models.TextField(default="[]")
    importance=models.FloatField(default=0.5)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"{self.category}:{self.content[:50]}"
# Create your models here.
