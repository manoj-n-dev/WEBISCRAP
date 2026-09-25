from typing import Any, Dict, List

from loguru import logger

from .base import BaseAgent


def _is_empty(v: Any) -> bool:
    return v is None or v == "" or v == [] or v == {}


def score_dataset(rows: List[Dict[str, Any]], expected_fields: List[str]) -> Dict[str, Any]:
    """Rule-based quality score (0-100): completeness, expected-field coverage, sparse rows."""
    n = len(rows)
    columns: List[str] = []
    for r in rows:
        for k in r:
            if k not in columns:
                columns.append(k)
    total_cells = max(1, n * max(1, len(columns)))
    filled = sum(0 if _is_empty(r.get(c)) else 1 for r in rows for c in columns)
    completeness = filled / total_cells

    expected = [f.lower().replace("_", "").replace(" ", "") for f in (expected_fields or [])]
    have = {c.lower().replace("_", "").replace(" ", "") for c in columns}
    coverage = (sum(1 for f in expected if any(f in h or h in f for h in have)) / len(expected)) if expected else 1.0

    sparse = [r for r in rows if columns and sum(0 if _is_empty(r.get(c)) else 1 for c in columns) < max(1, len(columns) / 2)]
    sparse_ratio = len(sparse) / n if n else 1
    score = round(100 * (0.6 * completeness + 0.3 * coverage + 0.1 * (1 - sparse_ratio)))
    notes = [f"{n} rows × {len(columns)} columns", f"{round(completeness * 100)}% of cells filled"]
    if expected and coverage < 1:
        notes.append(f"{round(coverage * 100)}% of the requested fields were found")
    if sparse:
        notes.append(f"{len(sparse)} sparse rows flagged")
    return {
        "confidence_score": max(0, min(100, score)),
        "validation_notes": "; ".join(notes) + ".",
        "flagged_rows_count": len(sparse),
        "is_valid": n > 0 and score >= 30,
    }


class ValidatorAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ValidatorAgent")

    async def _execute(self, input_data: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        cleaned_data = input_data.get("cleaned_data", [])
        if not cleaned_data:
            logger.warning(f"[{session_id}] No data provided to ValidatorAgent.")
            input_data["validation"] = {
                "confidence_score": 0, "validation_notes": "No data extracted.",
                "flagged_rows_count": 0, "is_valid": False,
            }
            return input_data
        input_data["validation"] = score_dataset(cleaned_data, input_data.get("expected_fields", []))
        logger.info(f"[{session_id}] Validation: {input_data['validation']}")
        return input_data


validator_agent = ValidatorAgent()
