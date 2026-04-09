import json
import asyncio
from openai import AsyncOpenAI
from app.services.memory_service import MemoryService
from app.services.weather_service import WeatherService
from app.services.currency_service import CurrencyService

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

    SYSTEM_PROMPT = (
        "You are a helpful assistant with access to tools. "
        "When the user asks about weather, use the get_weather tool. "
        "When the user asks about currency conversion, use the currency_converter tool. "
        "Never answer these questions from your own knowledge."
    )

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

    async def complete(self, prompt: str) -> str:
        if self.request_count >= self.max_requests:
            raise LLMServiceError("LLM usage limit reached")

        self.request_count += 1

        try:
            if self.use_mock:
                return await self._mock_response(prompt)
            
            # Step 1: add user message to memory
            self.memory.add_user_message(prompt)

            # Step 2: build messages — system prompt + full history
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ] + self.memory.get_history()

            # Step 3: first LLM call
            response = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    tools=self.TOOLS,
                    tool_choice="auto",
                    temperature=0.2,
                    max_tokens=100
                ),
                timeout=5
            )

            message = response.choices[0].message

            # Step 4: tool call handling
            if message.tool_calls:
                tool_call = message.tool_calls[0]

                tool_result = await self._handle_tool_call(tool_call)

                # save tool interaction to memory
                self.memory.add_tool_interaction(
                    message, tool_call.id, tool_result
                )

                # Step 5: second LLM call with tool result
                messages = [
                    {"role": "system", "content": self.SYSTEM_PROMPT}
                ] + self.memory.get_history()

                final_response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=0.2,
                        max_tokens=200
                    ),
                    timeout=10
                )

                answer = final_response.choices[0].message.content
            else:
                answer = message.content

            # Step 6: save assistant response to memory
            self.memory.add_assistant_message(answer)

            return answer

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
