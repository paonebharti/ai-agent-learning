import json
import asyncio
from openai import AsyncOpenAI
from app.services.llm_service import LLMServiceError


class PlannerService:
    PLANNER_SYSTEM_PROMPT = """
        You are a planning assistant. Given a user query, break it down into a list of clear,
        sequential steps needed to answer it fully.

        Return ONLY a JSON array of steps. Each step must have:
        - "step": step number (integer)
        - "task": what needs to be done (string)
        - "tool": which tool to use — one of: "get_weather", "currency_converter", "none"
        - "input": the input needed for the tool, or null if no tool

        Example output:
        [
        {"step": 1, "task": "Get weather in Delhi", "tool": "get_weather", "input": {"city": "Delhi"}},
        {"step": 2, "task": "Convert temperature to Fahrenheit", "tool": "none", "input": null}
        ]

        Return ONLY the JSON array. No explanation, no markdown, no extra text.
        """

    def __init__(self):
        self.client = AsyncOpenAI()

    async def plan(self, query: str) -> list:
        try:
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": self.PLANNER_SYSTEM_PROMPT},
                        {"role": "user", "content": query}
                    ],
                    temperature=0,
                    max_tokens=500
                ),
                timeout=10
            )

            raw = response.choices[0].message.content.strip()
            steps = json.loads(raw)
            return steps

        except json.JSONDecodeError:
            raise LLMServiceError("Planner returned invalid JSON")
        except asyncio.TimeoutError:
            raise LLMServiceError("Planner timed out")
        except Exception as e:
            raise LLMServiceError(f"Planner failed: {str(e)}")
