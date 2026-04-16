import re
from typing import Optional


class GuardrailViolation(Exception):
    """Raised when input or output fails a guardrail check."""
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(message)


class GuardrailService:

    MIN_INPUT_LENGTH = 2
    MAX_INPUT_LENGTH = 500

    BLOCKED_PATTERNS = [
        r"ignore\s+(all\s+)?previous\s+instructions",
        r"you\s+are\s+now\s+in\s+(developer|jailbreak|dan)\s+mode",
        r"pretend\s+you\s+(are|have\s+no)\s+(restrictions|rules|limits)",
        r"disregard\s+(your\s+)?(guidelines|rules|training)",
        r"act\s+as\s+(if\s+you\s+have\s+no|an?\s+unrestricted)",
    ]

    MAX_OUTPUT_LENGTH = 2000

    SENSITIVE_OUTPUT_PATTERNS = [
        r"\b(api[_\s]?key|secret[_\s]?key|password|bearer\s+token)\b",
        r"sk-[a-zA-Z0-9]{20,}",  # OpenAI key shape
    ]

    def validate_input(self, query: str) -> str:
        query = query.strip()

        if len(query) < self.MIN_INPUT_LENGTH:
            raise GuardrailViolation("Query is too short.", code="INPUT_TOO_SHORT")

        if len(query) > self.MAX_INPUT_LENGTH:
            raise GuardrailViolation(
                f"Query exceeds {self.MAX_INPUT_LENGTH} characters.", code="INPUT_TOO_LONG"
            )

        lower = query.lower()
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, lower):
                raise GuardrailViolation(
                    "Query contains disallowed content.", code="INPUT_BLOCKED_PATTERN"
                )

        return query

    def validate_output(self, response: str) -> str:
        if len(response) > self.MAX_OUTPUT_LENGTH:
            response = response[:self.MAX_OUTPUT_LENGTH] + "... [truncated]"

        lower = response.lower()
        for pattern in self.SENSITIVE_OUTPUT_PATTERNS:
            if re.search(pattern, lower):
                raise GuardrailViolation(
                    "Response contains potentially sensitive content.", code="OUTPUT_SENSITIVE"
                )

        return response
