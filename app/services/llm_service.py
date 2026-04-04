import asyncio
from openai import AsyncOpenAI


class LLMServiceError(Exception):
    pass


class LLMService:
    def __init__(self, use_mock: bool = False):
        self.client = AsyncOpenAI()
        self.use_mock = use_mock

        self.request_count = 0
        self.max_requests = 20  # safety limit

    async def complete(self, prompt: str) -> str:
        if self.request_count >= self.max_requests:
            raise LLMServiceError("LLM usage limit reached")

        self.request_count += 1

        try:
            if self.use_mock:
                print("🟡 USING MOCK LLM")
                return await self._mock_response(prompt)

            print("🟢 USING REAL LLM API")

            # ✅ REAL LLM call with timeout
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2,
                    max_tokens=100
                ),
                timeout=5
            )

            return response.choices[0].message.content

        except asyncio.TimeoutError:
            raise LLMServiceError("LLM request timed out")

        except Exception as e:
            raise LLMServiceError(f"LLM failed: {str(e)}")

    async def _mock_response(self, prompt: str) -> str:
        await asyncio.sleep(1)
        return f"[MOCK RESPONSE]: {prompt}"

    async def generate(self, prompt: str) -> str:
        try:
            # simulate timeout-prone external call
            await asyncio.wait_for(self._call_llm(prompt), timeout=3)
            return f"[LLM response to]: {prompt}"
        except asyncio.TimeoutError:
            raise LLMServiceError("LLM request timed out")

    async def _call_llm(self, prompt: str):
        await asyncio.sleep(5)  # simulate slow LLM
