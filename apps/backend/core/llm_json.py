"""Robust JSON extraction from LLM output (fences, prose around JSON, truncated arrays)."""
import json
import re
from typing import Any, List

from ai.errors import LLMInvalidOutputError

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.S | re.I)


def _strip(text: str) -> str:
    text = (text or "").strip()
    m = _FENCE.search(text)
    return m.group(1).strip() if m else text


def extract_json(text: str, expect: str = "object") -> Any:
    """Parse the first JSON object/array in `text`. Raises LLMInvalidOutputError if none is valid."""
    body = _strip(text)
    opener, closer = ("{", "}") if expect == "object" else ("[", "]")
    candidates = [body]
    start, end = body.find(opener), body.rfind(closer)
    if start != -1 and end > start:
        candidates.append(body[start:end + 1])
    for c in candidates:
        try:
            parsed = json.loads(c)
            if expect == "object" and isinstance(parsed, dict):
                return parsed
            if expect == "array" and isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            continue
    raise LLMInvalidOutputError("The AI returned an unreadable answer. Please try again.")


def extract_records(text: str) -> List[dict]:
    """Records from {"records":[...]} | [...] | a single object. If the output was cut off mid-array
    (token limit), salvage every COMPLETE object instead of discarding the whole chunk."""
    body = _strip(text)
    try:
        parsed = json.loads(body)
        if isinstance(parsed, list):
            return [r for r in parsed if isinstance(r, dict)]
        if isinstance(parsed, dict):
            for key in ("records", "data", "items", "rows", "results"):
                if isinstance(parsed.get(key), list):
                    return [r for r in parsed[key] if isinstance(r, dict)]
            return [parsed] if parsed else []
    except (json.JSONDecodeError, ValueError):
        pass
    # salvage: decode consecutive objects after the first '['
    start = body.find("[")
    if start == -1:
        raise LLMInvalidOutputError("The AI returned an unreadable answer. Please try again.")
    dec, i, out = json.JSONDecoder(), start + 1, []
    while i < len(body):
        while i < len(body) and body[i] in " \r\n\t,":
            i += 1
        if i >= len(body) or body[i] != "{":
            break
        try:
            obj, i = dec.raw_decode(body, i)
        except json.JSONDecodeError:
            break
        if isinstance(obj, dict):
            out.append(obj)
    if not out:
        raise LLMInvalidOutputError("The AI returned an unreadable answer. Please try again.")
    return out
