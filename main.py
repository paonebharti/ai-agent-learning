from fastapi import FastAPI
from app.schemas import UserRequest, UserResponse

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/user", response_model=UserResponse)
def create_user(user: UserRequest):
    return UserResponse(
        name=user.name.title(),
        email=user.email.lower(),
        is_adult=(user.age or 0) >= 18
    )