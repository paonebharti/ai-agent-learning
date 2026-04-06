from typing import List, Dict

def average(nums: List[int]) -> float:
    return sum(nums) / len(nums)

def normalize_user(user: Dict[str, str]) -> Dict[str, str]:
    return {
        "name": user["name"].strip().title(),
        "email": user["email"].lower()
    }