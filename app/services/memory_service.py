import json
import os

class MemoryService:
    def __init__(self, max_messages: int = 20, persist_path: str = None):
        self.history = []
        self.persist_path = persist_path
        self.max_messages = max_messages

        if self.persist_path:
            self._load()

    def add_user_message(self, content: str):
        self.history.append({"role": "user", "content": content})
        self._trim()
        self._save()

    def add_assistant_message(self, content: str):
        self.history.append({"role": "assistant", "content": content})
        self._trim()
        self._save()

    def add_tool_interaction(self, assistant_message, tool_call_id: str, tool_result: str):
        self.history.append(assistant_message)
        self.history.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": tool_result
        })
        self._trim()
        self._save()

    def get_history(self) -> list:
        return self.history.copy()

    def clear(self):
        self.history = []
        self._save()

    def _trim(self):
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages:]

    def _save(self):
        if not self.persist_path:
            return
        with open(self.persist_path, "w") as f:
            json.dump(self.history, f, indent=2, default=str)

    def _load(self):
        if not os.path.exists(self.persist_path):
            return
        try:
            with open(self.persist_path, "r") as f:
                self.history = json.load(f)
            print(f"🧠 Loaded {len(self.history)} messages from memory file")
        except Exception as e:
            print(f"⚠️ Could not load memory file: {e}")
            self.history = []
