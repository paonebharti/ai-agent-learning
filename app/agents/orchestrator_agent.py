import asyncio
from app.agents.base_agent import BaseAgent
from app.agents.weather_agent import WeatherAgent
from app.agents.currency_agent import CurrencyAgent
from app.logger import get_logger

logger = get_logger("orchestrator_agent")

class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="OrchestratorAgent",
            system_prompt=(
                "You are an orchestrator. Analyze the user query and decide which specialist agents to invoke.\n"
                "Respond ONLY with a valid JSON object, no markdown, no explanation.\n\n"
                "Available agents: weather, currency\n\n"
                "Return:\n"
                '{"agents": ["weather"], "reasoning": "query is about weather"}\n'
                '{"agents": ["currency"], "reasoning": "query is about currency"}\n'
                '{"agents": ["weather", "currency"], "reasoning": "query needs both"}\n'
                '{"agents": [], "reasoning": "query needs neither"}'
            )
        )
        self.weather_agent = WeatherAgent()
        self.currency_agent = CurrencyAgent()

    async def run(self, query: str) -> str:
        logger.info(f"Orchestrator received: {query[:60]}")

        # step 1 — decide which agents to invoke
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": query}
        ]

        decision_raw = await self._complete(messages)

        try:
            import json
            decision = json.loads(
                decision_raw.strip().replace("```json", "").replace("```", "").strip()
            )
        except Exception:
            logger.error(f"Orchestrator failed to parse decision: {decision_raw}")
            return "I was unable to process your request."

        agents_to_run = decision.get("agents", [])
        reasoning = decision.get("reasoning", "")
        logger.info(f"Orchestrator decision: {agents_to_run} | reasoning: {reasoning}")

        if not agents_to_run:
            return await self._complete([
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query}
            ])

        # step 2 — run selected agents concurrently
        tasks = {}
        if "weather" in agents_to_run:
            tasks["weather"] = self.weather_agent.run(query)
        if "currency" in agents_to_run:
            tasks["currency"] = self.currency_agent.run(query)

        results = await asyncio.gather(*tasks.values())
        agent_results = dict(zip(tasks.keys(), results))

        logger.info(f"Agent results collected: {list(agent_results.keys())}")

        # step 3 — synthesize final answer
        context = "\n\n".join([
            f"{agent.upper()} AGENT:\n{result}"
            for agent, result in agent_results.items()
        ])

        synthesis_messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant. "
                    "Synthesize the following specialist agent responses into one clear, concise answer."
                )
            },
            {
                "role": "user",
                "content": f"Original query: {query}\n\nAgent responses:\n{context}"
            }
        ]

        final = await self._complete(synthesis_messages)
        logger.info(f"Orchestrator synthesized final answer")
        return final
