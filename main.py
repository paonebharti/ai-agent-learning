import os
import json

from fastapi import FastAPI, HTTPException, status
from app.services.llm_service import LLMService, LLMServiceError
from app.services.planner_service import PlannerService
from app.schemas import UserRequest, UserResponse
from app.services.rag_service import RAGService
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

use_mock = os.getenv("USE_MOCK_LLM", "false").lower() == "true"
llm_service = LLMService(use_mock=use_mock)
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
