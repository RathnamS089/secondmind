from .tools import remember, recall, forget
from .llm import OllamaClient


class Agent:
    def __init__(self):
        self.llm = OllamaClient()
        self.top_k = 3

    def chat(self, user_message: str, conversation_history: list = None) -> dict:
        """Main entry point.

        Returns:
            {
                "response": str,          # text to show the user
                "memories_used": list,    # memory contents that were injected
                "tool_called": str|None   # "remember", "forget", or None
            }
        """

        # 1. Always retrieve relevant memories first (local, no LLM call yet).
        recalled = recall(user_message, top_k=self.top_k)

        memories_context = "\n".join(
            f"- [{m.id}] {m.content} (category: {m.category})"
            for m, _ in recalled
        ) if recalled else "No relevant memories."

        # 2. Tool definitions — only remember and forget for V0.
        #    recall_tool is intentionally excluded: the agent already injects
        #    relevant memories into the system prompt deterministically.
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "remember",
                    "description": (
                        "Store a new memory about the user. "
                        "Use when the user shares a preference, fact, or personal detail."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {"type": "string"},
                            "category": {"type": "string", "default": "general"},
                        },
                        "required": ["content"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "forget",
                    "description": (
                        "Delete a memory by its ID. "
                        "Use only when the user explicitly asks to forget something. "
                        "Memory IDs are shown in the context as [id]."
                    ),
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "memory_id": {"type": "integer"},
                        },
                        "required": ["memory_id"],
                    },
                },
            },
        ]

        # 3. Build message list for first LLM call.
        messages = [
            {
                "role": "system",
                "content": (
                    "You are SecondMind, a local-first personal AI memory assistant.\n\n"
                    f"Relevant memories about the user:\n{memories_context}\n\n"
                    "Rules:\n"
                    "- Use remember() when the user shares new personal information.\n"
                    "- Use forget() when the user explicitly asks to forget something. "
                    "Only use memory IDs shown above.\n"
                    "- If no tool is needed, answer using the memories above as context.\n"
                    "- Never invent memories. If you don't have the information, say so."
                ),
            },
            *((conversation_history or [])[-6:]),
            {"role": "user", "content": user_message},
        ]

        # 4. First LLM call — may or may not request a tool.
        raw = self.llm.chat(messages, tools=tools)

        # 5. Parse the Ollama response.
        #    Ollama tool-call shape:
        #    {"message": {"role": "assistant", "tool_calls": [
        #        {"function": {"name": "...", "arguments": {...}}}
        #    ]}}
        #    Normal reply shape:
        #    {"message": {"role": "assistant", "content": "..."}}
        message = raw.get("message", {})
        tool_calls = message.get("tool_calls")

        if tool_calls:
            # Take only the first tool call (Ollama returns a list).
            fn = tool_calls[0].get("function", {})
            tool_name = fn.get("name")
            args = fn.get("arguments", {})
        else:
            tool_name = None
            args = {}

        # 6. Execute the requested tool, then make a second LLM call for a
        #    natural language response.

        if tool_name == "remember":
            content = args.get("content", "")
            category = args.get("category", "general")
            remember(content, category)

            followup_raw = self.llm.chat([
                {
                    "role": "system",
                    "content": (
                        f"You just stored this memory: \"{content}\" (category: {category}). "
                        "Acknowledge it naturally and briefly."
                    ),
                },
                *((conversation_history or [])[-6:]),
                {"role": "user", "content": user_message},
            ])
            response_text = followup_raw["message"]["content"]
            return {
                "response": response_text,
                "memories_used": [m.content for m, _ in recalled],
                "tool_called": "remember",
            }

        elif tool_name == "forget":
            memory_id = args.get("memory_id")
            deleted = forget(memory_id)

            if deleted:
                response_text = f"Done — I've forgotten memory #{memory_id}."
            else:
                response_text = (
                    f"I couldn't find a memory with ID {memory_id}. "
                    "No changes were made."
                )
            return {
                "response": response_text,
                "memories_used": [m.content for m, _ in recalled],
                "tool_called": "forget",
            }

        else:
            # No tool called — normal conversational reply.
            # Re-use the same first-call response if the model already replied,
            # otherwise make a second call without tools.
            content = message.get("content", "").strip()
            if not content:
                followup_raw = self.llm.chat(messages)
                content = followup_raw["message"]["content"]

            return {
                "response": content,
                "memories_used": [m.content for m, _ in recalled],
                "tool_called": None,
            }