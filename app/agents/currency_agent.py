import asyncio
import json
from app.agents.base_agent import BaseAgent
from app.services.currency_service import CurrencyService
from app.logger import get_logger

logger = get_logger("currency_agent")

class CurrencyAgent(BaseAgent):
    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "currency_converter",
                "description": "Convert an amount from one currency to another",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "amount": {"type": "number"},
                        "from_currency": {"type": "string"},
                        "to_currency": {"type": "string"}
                    },
                    "required": ["amount", "from_currency", "to_currency"]
                }
            }
        }
    ]

    def __init__(self):
        super().__init__(
            name="CurrencyAgent",
            system_prompt=(
                "You are a currency specialist. "
                "You ONLY answer questions about currency conversion. "
                "Always use the currency_converter tool to fetch real rates. "
                "Never guess or estimate exchange rates."
            ),
            tools=self.TOOLS
        )
        self.currency_service = CurrencyService()

    async def run(self, query: str) -> str:
        logger.info(f"CurrencyAgent handling: {query[:60]}")

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

            logger.info(f"CurrencyAgent converting {args['amount']} {args['from_currency']} to {args['to_currency']}")
            tool_result = await asyncio.to_thread(
                self.currency_service.convert,
                args["amount"],
                args["from_currency"],
                args["to_currency"]
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
