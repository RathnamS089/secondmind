import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from .models import Memory

class MemoryAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.memory = Memory.objects.create(
            content="Test memory",
            category="general",
            embedding_json="[0.1, 0.2, 0.3]"
        )

    def test_health_endpoint(self):
        response = self.client.get(reverse('health'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_chat_missing_message(self):
        response = self.client.post(
            reverse('chat'),
            data=json.dumps({}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    @patch('memory.views.Agent')
    def test_chat_success(self, MockAgent):
        mock_instance = MockAgent.return_value
        mock_instance.chat.return_value = {
            "response": "Hello world",
            "memories_used": [],
            "tool_called": None
        }
        
        response = self.client.post(
            reverse('chat'),
            data=json.dumps({"message": "Hello"}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["response"], "Hello world")

    def test_memory_list(self):
        response = self.client.get(reverse('memory-list'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("memories", data)
        self.assertEqual(len(data["memories"]), 1)
        self.assertEqual(data["memories"][0]["content"], "Test memory")
        # Ensure embedding is NOT exposed
        self.assertNotIn("embedding_json", data["memories"][0])

    def test_memory_delete(self):
        response = self.client.delete(reverse('memory-delete', args=[self.memory.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Memory.objects.count(), 0)

    def test_memory_delete_not_found(self):
        response = self.client.delete(reverse('memory-delete', args=[9999]))
        self.assertEqual(response.status_code, 404)
        self.assertIn("error", response.json())
