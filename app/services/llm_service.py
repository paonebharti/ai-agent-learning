import asyncio
import json
from openai import AsyncOpenAI
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

    def __init__(self, use_mock: bool = False):
        self.client = AsyncOpenAI()
        self.use_mock = use_mock
        self.request_count = 0
        self.max_requests = 20  # safety limit
        self.weather_service = WeatherService()
        self.currency_service = CurrencyService()

    async def complete(self, prompt: str) -> str:
        if self.request_count >= self.max_requests:
            raise LLMServiceError("LLM usage limit reached")

        self.request_count += 1

        try:
            if self.use_mock:
                return await self._mock_response(prompt)

            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant with access to tools. "
                        "When the user asks about weather, you MUST use the get_weather tool. "
                        "When the user asks about currency conversion, use the currency_converter tool. "
                        "Never answer weather questions from your own knowledge."
                    )
                },
                {"role": "user", "content": prompt}
            ]

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

            if message.tool_calls:
                tool_call = message.tool_calls[0]

                tool_result = await self._handle_tool_call(tool_call)

                messages.append(message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result
                })

                final_response = await asyncio.wait_for(
                    self.client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages,
                        temperature=0.2,
                        max_tokens=100
                    ),
                    timeout=5
                )

                return final_response.choices[0].message.content

            return message.content

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
