class MemoryService:
    def __init__(self, max_messages: int = 20):
        self.history = []
        self.max_messages = max_messages

    def add_user_message(self, content: str):
        self.history.append({"role": "user", "content": content})
        self._trim()

    def add_assistant_message(self, content: str):
        self.history.append({"role": "assistant", "content": content})
        self._trim()

    def add_tool_interaction(self, assistant_message, tool_call_id: str, tool_result: str):
        self.history.append(assistant_message)
        self.history.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": tool_result
        })
        self._trim()

    def get_history(self) -> list:
        return self.history.copy()

    def clear(self):
        self.history = []

    def _trim(self):
        # keep only last max_messages to avoid token overflow
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages:]
