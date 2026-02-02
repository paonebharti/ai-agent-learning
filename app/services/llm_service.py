import asyncio

class LLMService:
    async def generate(self, prompt: str) -> str:
        await asyncio.sleep(2)  # simulate LLM latency
        return f"[LLM response to]: {prompt}"
