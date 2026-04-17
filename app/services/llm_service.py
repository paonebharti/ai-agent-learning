import json
import asyncio

from openai import AsyncOpenAI
from app.logger import get_logger
from app.services.memory_service import MemoryService
from app.services.prompt_service import PromptService
from app.services.weather_service import WeatherService
from app.services.currency_service import CurrencyService

logger = get_logger("llm_service")

class LLMServiceError(Exception):
    pass

class LLMService:
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get current weather for a city",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "city": {"type": "string"}
                    },
                    "required": ["city"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "currency_converter",
                "description": "Convert an amount from one currency to another",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number"},
                        "from_currency": {"type": "string", "description": "e.g. USD, INR, EUR"},
                        "to_currency": {"type": "string", "description": "e.g. USD, INR, EUR"}
                    },
                    "required": ["amount", "from_currency", "to_currency"]
                }
            }
        }
    ]

    def __init__(self, use_mock: bool = False):
        self.client = AsyncOpenAI()
        self.use_mock = use_mock
        self.request_count = 0
        self.max_requests = 20
        self.weather_service = WeatherService()
        self.currency_service = CurrencyService()
        self.memory = MemoryService(
            max_messages=20,
            persist_path="memory.json"
        )
        self.prompt_service = PromptService()
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_requests = 0

    async def complete(self, prompt: str) -> str:
        if self.request_count >= self.max_requests:
            raise LLMServiceError("LLM usage limit reached")

        self.request_count += 1

        try:
            if self.use_mock:
                return await self._mock_response(prompt)

            active = self.prompt_service.get_active()
            self.memory.add_user_message(prompt)

            messages = [
                {"role": "system", "content": active["system_prompt"]}
            ] + self.memory.get_history()

            logger.info(f"LLM request | prompt: {prompt[:60]}")

            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=self.TOOLS,
                    tool_choice="auto",
                    temperature=active["temperature"],
                    max_tokens=active["max_tokens"]
                ),
                timeout=10
            )

            message = response.choices[0].message
            usage = response.usage

            logger.info(
                f"LLM response | tokens: prompt={usage.prompt_tokens} "
                f"completion={usage.completion_tokens} total={usage.total_tokens}"
            )
            self._track_usage(usage)

            if message.tool_calls:
                tool_call = message.tool_calls[0]
                logger.info(f"Tool called | {tool_call.function.name} args={tool_call.function.arguments}")

                tool_result = await self._handle_tool_call(tool_call)

                self.memory.add_tool_interaction(message, tool_call.id, tool_result)

                messages = [
                    {"role": "system", "content": active["system_prompt"]}
                ] + self.memory.get_history()

                final_response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=active["temperature"],
                        max_tokens=active["max_tokens"]
                    ),
                    timeout=10
                )

                answer = final_response.choices[0].message.content
                final_usage = final_response.usage
                logger.info(
                    f"LLM final response | tokens: prompt={final_usage.prompt_tokens} "
                    f"completion={final_usage.completion_tokens} total={final_usage.total_tokens}"
                )
                self._track_usage(final_usage)

            else:
                answer = message.content

            self.memory.add_assistant_message(answer)
            return answer

        except asyncio.TimeoutError:
            logger.error("LLM request timed out")
            raise LLMServiceError("LLM request timed out")

        except Exception as e:
            logger.error(f"LLM failed: {str(e)}")
            raise LLMServiceError(f"LLM failed: {str(e)}")

    async def complete_stream(self, prompt: str):
        if self.request_count >= self.max_requests:
            raise LLMServiceError("LLM usage limit reached")

        self.request_count += 1

        active = self.prompt_service.get_active()

        self.memory.add_user_message(prompt)

        messages = [
            {"role": "system", "content": active["system_prompt"]}
        ] + self.memory.get_history()

        stream = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=active["temperature"],
            max_tokens=active["max_tokens"],
            stream=True
        )

        full_response = ""

        async for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta
                yield delta

        self.memory.add_assistant_message(full_response)

    async def complete_with_context(self, prompt: str, context: str) -> str:
        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. "
                        "Answer the user's question using ONLY the context provided below. "
                        "If the answer is not in the context, say 'I don't have that information'. "
                        f"\n\nContext:\n{context}"
                    )
                },
                {"role": "user", "content": prompt}
            ]

            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0,
                    max_tokens=200
                ),
                timeout=10
            )

            return response.choices[0].message.content

        except asyncio.TimeoutError:
            raise LLMServiceError("LLM request timed out")

        except Exception as e:
            raise LLMServiceError(f"LLM failed: {str(e)}")

    async def _complete_internal(self, prompt: str) -> str:
        try:
            active = self.prompt_service.get_active()

            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": active["system_prompt"]},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=active["temperature"],
                    max_tokens=active["max_tokens"]
                ),
                timeout=10
            )

            return response.choices[0].message.content

        except asyncio.TimeoutError:
            raise LLMServiceError("LLM request timed out")

        except Exception as e:
            raise LLMServiceError(f"LLM failed: {str(e)}")

    async def execute_plan(self, query: str, steps: list) -> dict:
        results = []

        for step in steps:
            tool = step.get("tool")
            task = step.get("task")
            inp = step.get("input")

            print(f"⚙️ Step {step['step']}: {task}")

            if tool == "get_weather" and inp:
                result = await asyncio.to_thread(
                    self.weather_service.get_weather, inp["city"]
                )

            elif tool == "currency_converter" and inp:
                result = await asyncio.to_thread(
                    self.currency_service.convert,
                    inp["amount"],
                    inp["from_currency"],
                    inp["to_currency"]
                )

            else:
                # no tool — internal LLM call, no memory pollution
                result = await self._complete_internal(task)

            results.append({"step": step["step"], "task": task, "result": result})
            print(f"✅ Step {step['step']} result: {result}")

        # final synthesis — combine all results into one answer
        context = "\n".join([f"Step {r['step']} ({r['task']}): {r['result']}" for r in results])
        final = await self.complete_with_context(query, context)

        return {
            "steps": results,
            "final_answer": final
        }

    async def complete_structured(self, prompt: str) -> dict:
        try:
            active = self.prompt_service.get_active()

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a structured data assistant. "
                        "Analyze the user query and respond ONLY with a valid JSON object. "
                        "No markdown, no explanation, no extra text — just raw JSON.\n\n"
                        "If the query is about weather, return:\n"
                        '{"query_type": "weather", "city": "...", "condition": "...", '
                        '"temperature_celsius": 0.0, "humidity_percent": 0, "summary": "..."}\n\n'
                        "If the query is about currency, return:\n"
                        '{"query_type": "currency", "from_currency": "...", "to_currency": "...", '
                        '"original_amount": 0.0, "converted_amount": 0.0, "summary": "..."}\n\n'
                        "For anything else, return:\n"
                        '{"query_type": "general", "answer": "...", '
                        '"confidence": "high|medium|low", "topics": ["..."]}'
                    )
                },
                {"role": "user", "content": prompt}
            ]

            # first get tool result if needed
            tool_response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=self.TOOLS,
                    tool_choice="auto",
                    temperature=0,
                    max_tokens=300
                ),
                timeout=10
            )

            message = tool_response.choices[0].message

            # if tool was called, get real data first
            if message.tool_calls:
                tool_call = message.tool_calls[0]
                tool_result = await self._handle_tool_call(tool_call)

                messages.append(message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

                # now ask LLM to format tool result as structured JSON
                final = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=0,
                        max_tokens=300
                    ),
                    timeout=10
                )
                raw = final.choices[0].message.content
            else:
                raw = message.content

            # parse and validate JSON
            clean = raw.strip().replace("```json", "").replace("```", "").strip()
            parsed = json.loads(clean)
            return parsed

        except json.JSONDecodeError as e:
            raise LLMServiceError(f"LLM returned invalid JSON: {str(e)}")
        except asyncio.TimeoutError:
            raise LLMServiceError("LLM request timed out")
        except Exception as e:
            raise LLMServiceError(f"LLM failed: {str(e)}")

    async def _mock_response(self, prompt: str) -> str:
        await asyncio.sleep(1)
        return f"[MOCK RESPONSE]: {prompt}"

    async def _handle_tool_call(self, tool_call):
        function_name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        if function_name == "get_weather":
            return await asyncio.to_thread(
                self.weather_service.get_weather,
                args["city"]
            )

        if function_name == "currency_converter":
            return await asyncio.to_thread(
                self.currency_service.convert,
                args["amount"],
                args["from_currency"],
                args["to_currency"]
            )

        return "Unknown tool"

    def _track_usage(self, usage):
        self.total_prompt_tokens += usage.prompt_tokens
        self.total_completion_tokens += usage.completion_tokens
        self.total_requests += 1
