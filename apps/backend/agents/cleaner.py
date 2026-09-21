import html
import json
import re
from typing import Any, Dict, List
from urllib.parse import urljoin

from loguru import logger

from core.config import settings
from core.llm_json import extract_records
from .base import BaseAgent

_PRICE_KEY = re.compile(r"(price|cost|amount|mrp|fee|salary|revenue|total)", re.I)
_PRICE_VAL = re.compile(r"^\s*(?P<c1>₹|Rs\.?|INR|\$|USD|€|EUR|£|GBP)?\s*(?P<num>\d[\d,]*(?:\.\d+)?)\s*(?P<c2>₹|Rs\.?|INR|\$|USD|€|EUR|£|GBP)?\s*$", re.I)
_URL_KEY = re.compile(r"(url|link|href|image|img|src)", re.I)
_WS = re.compile(r"\s+")
_CURRENCY = {"₹": "INR", "rs": "INR", "rs.": "INR", "inr": "INR", "$": "USD", "usd": "USD", "€": "EUR", "eur": "EUR", "£": "GBP", "gbp": "GBP"}


def clean_value(key: str, value: Any, base_url: str) -> Any:
    if isinstance(value, str):
        v = _WS.sub(" ", html.unescape(value)).strip()
        if v == "" or v.lower() in ("null", "none", "n/a", "nan", "undefined"):
            return None
        if base_url and _URL_KEY.search(key) and (v.startswith("/") or v.startswith("./") or v.startswith("../")):
            return urljoin(base_url, v)
        return v
    return value


def normalize_price(value: Any):
    """'₹1,299' -> (1299.0, 'INR'); anything that is not a clean price is returned unchanged."""
    if isinstance(value, str):
        m = _PRICE_VAL.match(value)
        if m:
            cur = (m.group("c1") or m.group("c2") or "").strip().lower()
            num = float(m.group("num").replace(",", ""))
            return (int(num) if num.is_integer() else num), _CURRENCY.get(cur)
    return value, None


def clean_records(records: List[Dict[str, Any]], base_url: str = "") -> List[Dict[str, Any]]:
    """Deterministic cleaning: whitespace/entity fixes, null normalisation, absolute URLs,
    numeric prices, junk-row removal and exact-duplicate removal. Never invents or drops real values."""
    out, seen = [], set()
    for rec in records:
        if not isinstance(rec, dict):
            continue
        row: Dict[str, Any] = {}
        for k, v in rec.items():
            key = _WS.sub(" ", str(k)).strip()
            if not key:
                continue
            val = clean_value(key, v, base_url)
            cur = None
            if _PRICE_KEY.search(key) and val is not None:
                num, cur = normalize_price(val)
                if cur:
                    val = num
            row[key] = val
            if cur:
                row.setdefault(f"{key}_currency" if key.lower() != "price" else "currency", cur)
        if not any(v not in (None, "", [], {}) for v in row.values()):
            continue
        fingerprint = json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)
        if fingerprint in seen:
            continue
        seen.add(fingerprint)
        out.append(row)
    return out


class CleanerAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="CleanerAgent")

    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        raw_data = input_data.get("extracted_data", [])
        target_url = input_data.get("target_url", "")
        if not raw_data:
            logger.warning(f"[{session_id}] No data provided to CleanerAgent.")
            input_data["cleaned_data"] = []
            return input_data

        cleaned = clean_records(raw_data, target_url)
        if getattr(settings, "CLEANER_MODE", "deterministic") == "llm":
            cleaned = await self._refine_with_llm(cleaned, target_url, session_id)
        logger.info(f"[{session_id}] Cleaned {len(raw_data)} -> {len(cleaned)} rows.")
        input_data["cleaned_data"] = cleaned
        input_data.pop("extracted_data", None)
        return input_data

    async def _refine_with_llm(self, rows, target_url, session_id):
        """Optional (CLEANER_MODE=llm). Any LLM failure keeps the deterministic result."""
        from ai.router import ai_router
        from prompts.cleaner_prompt import CLEANER_SYSTEM_PROMPT
        out: List[Dict[str, Any]] = []
        for i in range(0, len(rows), 60):
            chunk = rows[i:i + 60]
            try:
                text = await ai_router.generate(
                    task_category="cleaning",
                    prompt=f"Base URL: {target_url}\n\nRaw Data Array:\n{json.dumps(chunk, ensure_ascii=False)}",
                    system_prompt=CLEANER_SYSTEM_PROMPT, temperature=0.1)
                out.extend(extract_records(text) or chunk)
            except Exception as e:
                logger.warning(f"[{session_id}] LLM cleaning skipped for chunk: {e}")
                out.extend(chunk)
        return clean_records(out, target_url)


cleaner_agent = CleanerAgent()
