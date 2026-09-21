"""Typed LLM errors. The API layer maps these to structured HTTP responses
(the frontend shows the 'AI limit reached' panel for LLM_RATE_LIMIT)."""
from typing import Optional, Dict, Any


class LLMError(Exception):
    code = "LLM_ERROR"
    http_status = 502

    def __init__(self, message: str = "The AI service could not complete the request.",
                 *, retry_after: Optional[int] = None, scope: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.retry_after = retry_after      # seconds until a retry is likely to succeed
        self.scope = scope                  # "minute" | "day" | None

    def to_detail(self) -> Dict[str, Any]:
        return {"code": self.code, "message": self.message,
                "retry_after": self.retry_after, "scope": self.scope}


class LLMRateLimitError(LLMError):
    code = "LLM_RATE_LIMIT"
    http_status = 429


class LLMRequestTooLargeError(LLMError):
    code = "LLM_REQUEST_TOO_LARGE"
    http_status = 422


class LLMUnavailableError(LLMError):
    code = "LLM_UNAVAILABLE"
    http_status = 503


class LLMInvalidOutputError(LLMError):
    code = "LLM_INVALID_OUTPUT"
    http_status = 502
