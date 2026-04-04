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

### Day 7-8 — LLM Integration & Service Abstraction

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
