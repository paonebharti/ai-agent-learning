# Agent Runbook

Operational reference for the AI agent. Use this when something is broken.

---

## How to Start the Agent

```bash
uvicorn main:app --reload         # development
uvicorn main:app --host 0.0.0.0 --port 8000  # production
```

## How to Verify It's Running

```bash
curl http://localhost:8000/health
# Expected: {"status": "ok"}

curl http://localhost:8000/ping
# Expected: {"ping": "pong"}
```

---

## Known Failure Modes

### 1. LLM Usage Limit Reached
- **Symptom:** `503` on `/ask` with `"LLM usage limit reached"`
- **Cause:** `max_requests` counter hit. Resets only on server restart.
- **Fix:** Restart the server. Long term — persist counter and implement per-user limits.

### 2. OpenAI API Timeout
- **Symptom:** `503` on `/ask` with `"LLM request timed out"`
- **Cause:** OpenAI took longer than 10 seconds to respond.
- **Fix:** Retry the request. If persistent, check https://status.openai.com

### 3. OpenAI API Key Invalid
- **Symptom:** `503` with `401 Unauthorized` in logs
- **Cause:** `OPENAI_API_KEY` in `.env` is missing or expired.
- **Fix:** Verify key in `.env`. Generate a new key at https://platform.openai.com/api-keys

### 4. Corrupted Memory
- **Symptom:** `503` on `/ask` with `Invalid type for messages[N]` in logs
- **Cause:** `memory.json` has a corrupted entry — plain string instead of message object.
- **Fix:** `DELETE /memory/clear` to reset memory.

### 5. Concurrent Request Memory Corruption (Known Bug)
- **Symptom:** `503` on `/ask` with `messages with role 'tool' must be a response to a preceding message with 'tool_calls'` in logs
- **Cause:** Shared `MemoryService` instance across concurrent requests. Tool interactions from one request corrupt memory context for another.
- **Fix:** `DELETE /memory/clear` to recover. Long term — isolate `MemoryService` per session_id.

### 6. Weather Service Failure
- **Symptom:** Tool call returns error string instead of weather data
- **Cause:** OpenWeatherMap API key invalid or rate limited.
- **Fix:** Verify `OPENWEATHERMAP_API_KEY` in `.env`. Check https://openweathermap.org/api

### 7. Currency Service Failure
- **Symptom:** Tool call returns error string instead of conversion data
- **Cause:** ExchangeRate API key invalid or rate limited.
- **Fix:** Verify `EXCHANGERATE_API_KEY` in `.env`.

---

## Useful Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /health` | Verify server is running |
| `GET /stats` | Token usage and estimated cost |
| `DELETE /memory/clear` | Reset conversation memory |
| `GET /prompts` | List prompt variants |
| `POST /prompts/activate/{key}` | Switch active prompt |

---

## Logs

- **Terminal** — live log output
- **agent.log** — persistent log file in project root
- Log level configurable via `LOG_LEVEL` in `.env` — `DEBUG` for verbose, `INFO` for normal

## Environment Variables

| Variable | Purpose |
|---|---|
| `OPENAI_API_KEY` | OpenAI API access |
| `OPENWEATHERMAP_API_KEY` | Weather tool |
| `EXCHANGERATE_API_KEY` | Currency tool |
| `USE_MOCK_LLM` | Set `true` to bypass OpenAI calls |
| `LOG_LEVEL` | Logging verbosity (`DEBUG` / `INFO`) |
