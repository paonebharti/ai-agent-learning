from pydantic import BaseModel
from typing import Optional

class UserRequest(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    name: str
    email: str
    is_adult: bool
