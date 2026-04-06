# AI Agent Learning Journey

This repository documents my **day-by-day learning journey into AI Agent development**, following a structured roadmap. Each day focuses on understanding core concepts and implementing small, hands-on experiments using Python.

The goal of this repository is to build a strong foundation in agent-based systems through consistent practice, experimentation, and incremental improvements.

---

## 📅 Progress

### ✅ Day 1
- Environment setup (Python, virtual environment)
- Understanding what AI agents are and where they are used
- Basic project structure and tooling

### ✅ Day 2
- Built a simple FastAPI application to interact with an agent
- Learned how request handling works in FastAPI
- Used Pydantic models for request validation
- Tested endpoints using `curl`
- Understood basic concepts like ASGI servers and Uvicorn

### ✅ Day 3
- Path & query parameters
- Status codes
- Controller-style API design

### ✅ Day 4
- Async vs blocking
- Non-blocking FastAPI endpoints
- Why LLM calls must be async

### ✅ Day 5
- Service layer design
- LLM abstraction
- Async service calls

### ✅ Day 6
- LLM timeouts
- Error handling
- Resilient service design

### ✅ Day 7-8 — LLM Integration & Service Abstraction

#### What I built
- Integrated a real LLM using an async client
- Designed a clean service layer (`LLMService`) to abstract LLM interactions
- Exposed an API endpoint (`/ask`) powered by the LLM

#### Key Features
- Async LLM calls using `AsyncOpenAI`
- Timeout handling using `asyncio.wait_for`
- Controlled API usage with request limits
- Token usage optimization via `max_tokens`
- Mock mode support for safe local development

#### Architecture
Controller (FastAPI) → Service Layer (LLMService) → External LLM API

#### Key Design Decisions
- LLM is treated as an external dependency (like Stripe/Twilio)
- Service abstraction allows swapping providers without affecting API layer
- Errors are encapsulated using custom exceptions (`LLMServiceError`)
- Mock responses used to minimize API cost during development

#### Key Learnings
- LLM calls are I/O-bound and must be async
- Direct API calls from controllers lead to poor design
- Timeouts and failure handling are essential for production systems
- Cost control (tokens, request limits) is part of system design

#### Challenges Faced
- Handling API keys securely using environment variables
- Designing a unified interface for mock and real LLM calls
- Understanding where to apply timeouts correctly

#### Outcome
A production-ready foundation for integrating AI into backend systems with proper abstraction, error handling, and cost control.

### ✅ Day 9 — Prompt Engineering

#### What I learned
- Difference between system and user messages
- How to control LLM behavior using system prompts
- Importance of deterministic outputs (temperature=0)
- Designing structured responses (JSON output)
- https://www.promptingguide.ai/techniques/cot reference for more about Prompt Engineering

#### Key Insight
Prompts are not strings — they are contracts that define system behavior.

### ✅ Day 10 — Function Calling (Agents Begin Here)

#### What I built
- Integrated a real weather API (OpenWeatherMap) into the agent
- Implemented function calling — LLM decides when to call a tool
- Built a two-step LLM flow: first call decides tool usage, second call forms the final response

#### Key Features
- Tool definition using OpenAI function calling schema
- LLM-driven tool routing via `tool_choice="auto"`
- Real HTTP weather data fetched via `httpx`

#### Architecture
User → `/ask` → LLMService → Tool decision → WeatherService → Real API → LLMService → Response

#### Key Design Decisions
- Tool definitions live as a class-level constant (`TOOLS`) for easy extensibility
- WeatherService stays as a plain sync service — async wrapping handled at the call site
- System prompt explicitly instructs LLM to use tools — model won't call tools reliably without this

#### Key Learnings
- LLMs won't use tools unless the prompt explicitly instructs them to
- `asyncio.to_thread(fn, arg)` — function and arguments are passed separately, never call the function inline
- Two LLM calls are needed: one to decide the tool, one to form the final answer
- Prompt design and tool calling are tightly coupled

#### Challenges Faced
- LLM was answering weather questions from its own knowledge — fixed by updating system prompt
- `asyncio.to_thread` TypeError — was calling the function instead of passing it as a reference
- OpenWeatherMap API key takes ~10 min to activate after signup

#### Outcome
A working agent that routes user queries to real-world tools and responds with live data.
---

## 🛠️ Tech Stack
- Python
- FastAPI
- Uvicorn
- Pydantic

---

## 🎯 Purpose of This Repo
- Track daily learning progress
- Build practical understanding of AI agents
- Maintain clean documentation for future reference
- Share learning publicly for accountability and growth

---

## 🚧 Work in Progress
This repository is actively evolving. Code structure, patterns, and implementations will improve as I progress further in the roadmap.

---

## 📌 Note
Each commit represents daily progress. The focus is on learning and experimentation rather than production-ready code.
