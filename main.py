import time, asyncio
from fastapi import FastAPI, HTTPException, status
from app.schemas import UserRequest, UserResponse

app = FastAPI()

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


# Blocking vs Async Endpoint (Feel the difference)

# ❌ Blocking endpoint
@app.get("/blocking")
def blocking():
    print("blocking start")
    time.sleep(10)
    print("blocking end")
    return {"status": "blocking done"}

# ✅ Async endpoint
@app.get("/async")
async def async_endpoint():
    print("async start")
    await asyncio.sleep(10)
    print("async end")
    return {"status": "async done"}

@app.get("/ping")
def ping():
    print("ping")
    return {"ping": "pong"}
