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

### ✅ Day 14 — Embeddings + Vector Search (Concept)

#### What I learned
- Embeddings convert text into a list of numbers (a **vector**) that captures meaning
- Each number in the vector is called a **dimension** — OpenAI's default is 1536 dimensions
- Text with similar meaning produces numerically similar vectors, regardless of word count or length
- Similarity between vectors is measured using **cosine similarity** — a score between 0 and 1

#### Key Concepts

**Embedding vector**
Any text — whether 10 words or 5 paragraphs — gets compressed into the same fixed-size
vector (1536 dims). Length doesn't matter, meaning does.

**Cosine similarity**
Measures how close two vectors are in space.
- Score close to 1.0 = very similar meaning
- Score close to 0.0 = very different meaning

**Chunking**
Splitting a large document into smaller pieces before embedding. The LLM does not decide
chunk size — you do. Common strategies:
- Fixed size (e.g. every 500 tokens)
- By paragraph (split on blank lines)
- By sentence (split on punctuation)

**RAG (Retrieval Augmented Generation)**
Instead of pasting an entire document into the LLM, you:
1. Split document into chunks and embed each one
2. Store embeddings in a vector DB
3. On each query, embed the question and find the most similar chunks
4. Inject only the relevant chunks into the LLM prompt

#### Rails Developer Mental Model
| Concept | Rails equivalent |
|---|---|
| Embedding | Converting a record into a searchable index |
| Vector DB | A database optimized for similarity search |
| Similarity search | Like WHERE but for meaning, not exact match |
| RAG | Like JOIN — fetching relevant context before responding |

#### Key Learnings
- A 10-word question and a 5-paragraph chunk both map to the same 1536-dimension space — length mismatch doesn't affect similarity
- Chunk size is a design decision you make, not something the LLM decides
- RAG solves the token limit problem — agents can now "search" thousands of documents without pasting everything into the prompt

#### Outcome
Strong conceptual foundation for Day 15 where we build a working RAG pipeline using ChromaDB and OpenAI embeddings.

### ✅ Day 15 — Simple RAG Pipeline

#### What I built
- Built a `RAGService` that embeds a knowledge base into ChromaDB at startup
- Implemented semantic search — converts user query to embedding and retrieves top 2 similar chunks
- Added `/rag` endpoint — retrieves relevant context then passes it to LLM for answering
- Added `complete_with_context()` to `LLMService` — separate method for context-grounded responses
- Agent correctly says "I don't have that information" when answer is not in the knowledge base

#### Architecture
User → `/rag` → RAGService (retrieve chunks) → LLMService (answer from context) → User

#### Indexing Flow (startup)
Knowledge base chunks → OpenAI embeddings → ChromaDB vector store

#### Query Flow (per request)
User question → embedding → ChromaDB similarity search → top 2 chunks → injected as context into LLM prompt → answer

#### Key Design Decisions
- `complete_with_context()` is separate from `complete()` — RAG bypasses memory and tools, it has a different responsibility
- `temperature=0` for RAG responses — answers must be grounded in context, not creative
- `top_k=2` — inject only the most relevant chunks, not everything, to stay within token limits
- System prompt explicitly instructs LLM to use only provided context — prevents hallucination
- ChromaDB runs locally — no external service needed during development

#### Chunk Size
In Day 15 we manually wrote each chunk — one topic per string, roughly 1-2 sentences each.
There was no explicit chunking logic because we controlled the knowledge base directly.

In a real RAG system loading a PDF or large document, chunk size is defined explicitly:
- `chunk_size` — max characters or tokens per chunk (e.g. 500)
- `chunk_overlap` — repeated characters at the boundary edge of adjacent chunks to avoid
  losing context when a fixed-size splitter cuts mid-sentence

Chunk size is always a design decision you make — the LLM does not decide it.

#### Topic vs Idea vs Context
These three terms mean different things in RAG:

- **Topic** — the broad subject a chunk is about (e.g. "Refunds", "Shipping")
- **Idea** — one complete thought within a topic (e.g. "Refunds take 7 days")
- **Context** — the retrieved chunks combined and injected into the LLM prompt to answer from

One topic can contain multiple ideas. One document can have many topics.
You chunk by topic or idea. You retrieve context. The LLM answers from context.

#### Chunk Overlap — Clarification
Chunk overlap does NOT mean mixing different topics together. It means repeating a few
characters at the boundary edge of the same topic — only needed when a fixed-size splitter
blindly cuts at character count and splits a sentence in half.

When splitting by paragraph, overlap is less critical because paragraphs naturally end at
complete thoughts.

#### Where does `collection.query()` come from?
We never wrote a `query()` method ourselves. It is a built-in method provided by ChromaDB on
every `Collection` object — similar to how ActiveRecord gives you `where()` and `find()` on
every Rails model without you writing them.

ChromaDB built-in collection methods:
- `collection.add()` — store documents + embeddings
- `collection.query()` — find most similar documents by embedding
- `collection.get()` — fetch documents by ID
- `collection.delete()` — remove documents
- `collection.update()` — update existing documents

ChromaDB handles all the similarity math (cosine similarity, ranking, top K) internally.

#### Key Learnings
- Both the query and the chunks map to the same 1536-dimension vector space — length mismatch doesn't matter
- Chunk by topic or idea — one complete thought per chunk keeps retrieval clean
- Chunk overlap protects boundaries, not mixes topics
- RAG and memory serve different purposes — memory tracks conversation, RAG retrieves external knowledge
- Grounding the LLM in context with `temperature=0` dramatically reduces hallucination
- Never use a method without knowing where it comes from — understand if it's yours or the library's

#### Outcome
A working RAG pipeline that retrieves semantically relevant knowledge and answers user questions
accurately from a local vector store — without hallucinating answers outside its knowledge base.

---

## 🛠️ Tech Stack

### Core Framework
- **FastAPI** — web framework, API layer
- **Uvicorn** — ASGI server that runs FastAPI
- **Pydantic** — request/response validation and schemas

### LLM & AI
- **openai (AsyncOpenAI)** — LLM calls via GPT-4o-mini
- **openai (OpenAI sync)** — embedding generation via text-embedding-3-small
- **chromadb** — local vector store for RAG

### External APIs
- **OpenWeatherMap API** — real weather data
- **ExchangeRate API** — real currency conversion

### HTTP & Async
- **httpx** — sync HTTP client for external API calls (WeatherService, CurrencyService)
- **asyncio** — async/await, timeout handling, thread pool via `asyncio.to_thread`

### Configuration & Environment
- **python-dotenv** — loads `.env` file for API keys

### Storage
- **json (stdlib)** — file-based memory persistence

### Language
- **Python 3.12**

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
