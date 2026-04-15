import os
import json

from fastapi import FastAPI, HTTPException, status
from app.services.llm_service import LLMService, LLMServiceError
from app.services.prompt_service import PromptService, PromptServiceError
from app.services.planner_service import PlannerService
from app.schemas import UserRequest, UserResponse
from app.services.rag_service import RAGService
from app.schemas import StructuredResponse
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
llm_service = LLMService(use_mock=use_mock)
prompt_service = llm_service.prompt_service
planner_service = PlannerService()
rag_service = RAGService()

@app.get("/plan")
async def plan_and_execute(q: str):
    try:
        # Step 1: generate plan
        steps = await planner_service.plan(q)
        print(f"📋 Plan: {json.dumps(steps, indent=2)}")

        # Step 2: execute plan
        result = await llm_service.execute_plan(q, steps)

        return {
            "question": q,
            "plan": steps,
            "steps_executed": result["steps"],
            "final_answer": result["final_answer"]
        }

    except LLMServiceError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/rag")
async def rag_ask(q: str):
    chunks = rag_service.retrieve(q)

    context = "\n\n".join(chunks)

    answer = await llm_service.complete_with_context(q, context)

    return {
        "question": q,
        "context_used": chunks,
        "answer": answer
    }

@app.get("/ask")
async def ask(q: str):
    try:
        answer = await llm_service.complete(q)
        return {"answer": answer}
    except LLMServiceError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/ask/structured")
async def ask_structured(q: str):
    try:
        result = await llm_service.complete_structured(q)
        return result
    except LLMServiceError as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/prompts")
def list_prompts():
    return prompt_service.list_variants()

@app.post("/prompts/activate/{key}")
def activate_prompt(key: str):
    try:
        prompt_service.set_active(key)
        return {"status": "activated", "active": key}
    except PromptServiceError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/prompts/add")
def add_prompt(key: str, name: str, system_prompt: str,
               temperature: float = 0.2, max_tokens: int = 200):
    try:
        prompt_service.add_variant(key, name, system_prompt, temperature, max_tokens)
        return {"status": "added", "key": key}
    except PromptServiceError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/memory/clear")
def clear_memory():
    llm_service.memory.clear()
    return {"status": "memory cleared"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/user", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserRequest):
    return UserResponse(
        name=user.name.title(),
        email=user.email.lower(),
        is_adult=(user.age or 0) >= 18
    )

@app.get("/users/{user_id}")
def get_user(user_id: int, verbose: bool = False):
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id"
        )

    user = {
        "name": "Vayu",
        "email": "vayu@mail.com",
        "is_adult": True
    }

    return user if verbose else {"name": user["name"]}

@app.get("/search")
def search_users(q: str, limit: int = 10):
    return {
        "query": q,
        "limit": limit,
        "results": []
    }

@app.get("/ping")
def ping():
    return {"ping": "pong"}
