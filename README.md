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

### ✅ Day 11 — Multi-tool Orchestration

- Added a second real-world service (CurrencyService)
- Extended TOOLS with a multi-parameter tool definition
- LLM now routes across multiple tools autonomously

### ✅ Day 12 — Agent Memory (Conversation History)

#### What I built
- Built a `MemoryService` to store conversation history in-memory
- Agent now remembers context across multiple `/ask` calls
- Tool interactions (both assistant tool call + tool result) are saved to memory
- Added `/memory/clear` endpoint to reset conversation without restarting server

#### Architecture
User → `/ask` → LLMService → MemoryService (inject history) → LLM → MemoryService (save response) → User

#### Key Design Decisions
- Memory is invisible to the LLM — it's injected silently as message history on every request
- System prompt is always prepended fresh — never stored in memory
- `max_messages=20` prevents context window overflow
- Tool interactions are always saved in pairs (assistant tool call + tool result) — breaking this pair causes LLM errors
- `get_history()` returns a copy to prevent external mutation of internal state
- Single responsibility — `_handle_tool_call` only executes tools, memory saving is handled by `complete()`

#### Key Learnings
- Memory is not a tool — it's internal bookkeeping the LLM never directly sees or calls
- LLM sees conversation history as just another part of `messages` array
- Tool call + tool result must always stay paired in history
- Memory grows with every turn — trimming is essential for long conversations

#### Challenges Faced
- Understanding why `add_tool_interaction` wasn't being called for non-tool queries — it only fires when LLM requests a tool, which is correct behavior
- Distinguishing between memory (internal) and tools (external capabilities)

#### Outcome
A stateful agent that remembers conversation context, handles tools correctly across turns, and maintains clean separation between memory management and tool execution.

### ✅ Day 13 (Bonus) — File-Based Memory Persistence

#### What I built
- Extended `MemoryService` to optionally persist conversation history to a JSON file
- Memory now survives server restarts
- `persist_path` is optional — passing `None` keeps original in-memory behavior

#### Key Design Decisions
- File persistence is opt-in via `persist_path` parameter — no breaking changes to existing behavior
- `_save()` is called after every mutation (add/clear) to keep file in sync
- `_load()` is called once at startup — fails gracefully if file doesn't exist or is corrupt
- `memory.json` added to `.gitignore` — conversation history is personal, not code

#### Key Learnings
- Separating concerns: persistence is a layer on top of memory, not mixed into it
- Graceful degradation — if the file is missing or corrupt, agent starts fresh without crashing
- Optional parameters keep backward compatibility clean

#### Outcome
Agent memory now persists across server restarts with zero changes to the rest of the codebase.
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
