import asyncio
import json
from app.agents.base_agent import BaseAgent
from app.services.weather_service import WeatherService
from app.logger import get_logger

logger = get_logger("weather_agent")

class WeatherAgent(BaseAgent):
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
        }
    ]

    def __init__(self):
        super().__init__(
            name="WeatherAgent",
            system_prompt=(
                "You are a weather specialist. "
                "You ONLY answer questions about weather. "
                "Always use the get_weather tool to fetch real data. "
                "Never guess or estimate weather conditions."
            ),
            tools=self.TOOLS
        )
        self.weather_service = WeatherService()

    async def run(self, query: str) -> str:
        logger.info(f"WeatherAgent handling: {query[:60]}")

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query}
        ]

        response = await asyncio.wait_for(
            self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.TOOLS,
                tool_choice="auto",
                temperature=0.2,
                max_tokens=300
            ),
            timeout=10
        )

        message = response.choices[0].message

        if message.tool_calls:
            tool_call = message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            city = args["city"]

            logger.info(f"WeatherAgent calling get_weather for {city}")
            tool_result = await asyncio.to_thread(
                self.weather_service.get_weather, city
            )

            messages.append(message.model_dump(exclude_unset=True))
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": tool_result
            })

            final = await asyncio.wait_for(
                self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.2,
                    max_tokens=300
                ),
                timeout=10
            )

            return final.choices[0].message.content

        return message.content
