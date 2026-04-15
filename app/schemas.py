from pydantic import BaseModel
from typing import Optional, List

class UserRequest(BaseModel):
    name: str
    email: str
    age: Optional[int] = None

class UserResponse(BaseModel):
    name: str
    email: str
    is_adult: bool

class WeatherOutput(BaseModel):
    city: str
    condition: str
    temperature_celsius: float
    humidity_percent: int
    summary: str

class CurrencyOutput(BaseModel):
    from_currency: str
    to_currency: str
    original_amount: float
    converted_amount: float
    summary: str

class GeneralOutput(BaseModel):
    answer: str
    confidence: str  # "high", "medium", "low"
    topics: List[str]

class StructuredResponse(BaseModel):
    query_type: str  # "weather", "currency", "general"
    data: dict
    raw_answer: str
