import asyncio

class LLMServiceError(Exception):
    pass

class LLMService:
    async def generate(self, prompt: str) -> str:
        try:
            # simulate timeout-prone external call
            await asyncio.wait_for(self._call_llm(prompt), timeout=3)
            return f"[LLM response to]: {prompt}"
        except asyncio.TimeoutError:
            raise LLMServiceError("LLM request timed out")

    async def _call_llm(self, prompt: str):
        await asyncio.sleep(5)  # simulate slow LLM
