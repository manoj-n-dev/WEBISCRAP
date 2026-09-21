"""Safe, LLM-driven dataset queries. The LLM only *describes* a filter (JSON); this module executes it on
the FULL dataset with pandas (no eval), so follow-ups work on thousands of rows without sending them all."""
import re
from typing import Any, Dict, List, Optional

import pandas as pd

MAX_RESULT_ROWS = 500
_NUM_STRIP = re.compile(r"[^\d.\-]")


def _to_numeric(series: pd.Series) -> pd.Series:
    if pd.api.types.is_numeric_dtype(series):
        return pd.to_numeric(series, errors="coerce")
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False).map(lambda s: _NUM_STRIP.sub("", s)), errors="coerce")


def _find_column(df: pd.DataFrame, name: Any) -> Optional[str]:
    if not isinstance(name, str):
        return None
    if name in df.columns:
        return name
    lowered = {str(c).lower().strip(): c for c in df.columns}
    return lowered.get(name.lower().strip())


def _is_mostly_numeric(series: pd.Series) -> bool:
    non_null = series.dropna()
    if non_null.empty:
        return False
    return _to_numeric(non_null).notna().mean() >= 0.8


def dataset_stats(rows: List[Dict[str, Any]], top_n: int = 5) -> Dict[str, Any]:
    """Compact per-column summary that lets the LLM answer whole-table questions (totals, averages, top values)."""
    df = pd.DataFrame(rows, dtype=object)
    stats: Dict[str, Any] = {}
    for col in df.columns:
        s = df[col]
        info: Dict[str, Any] = {"non_null": int(s.notna().sum())}
        if _is_mostly_numeric(s):
            n = _to_numeric(s).dropna()
            info.update(type="number", min=round(float(n.min()), 2), max=round(float(n.max()), 2),
                        mean=round(float(n.mean()), 2), sum=round(float(n.sum()), 2))
        else:
            vc = s.dropna().astype(str).value_counts().head(top_n)
            info.update(type="text", unique=int(s.dropna().astype(str).nunique()),
                        top={str(k)[:40]: int(v) for k, v in vc.items()})
        stats[str(col)] = info
    return stats


def apply_query(rows: List[Dict[str, Any]], spec: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not rows or not isinstance(spec, dict):
        return []
    df = pd.DataFrame(rows, dtype=object)
    mask = pd.Series(True, index=df.index)
    for f in (spec.get("filters") or [])[:8]:
        if not isinstance(f, dict):
            continue
        col = _find_column(df, f.get("column"))
        op = str(f.get("op", "")).lower().strip()
        val = f.get("value")
        if col is None or not op:
            continue
        s = df[col]
        try:
            if op in ("<", "<=", ">", ">=", "between"):
                n = _to_numeric(s)
                if op == "between" and isinstance(val, (list, tuple)) and len(val) == 2:
                    m = n.between(float(val[0]), float(val[1]))
                else:
                    v = float(val)
                    m = {"<": n < v, "<=": n <= v, ">": n > v, ">=": n >= v}.get(op, pd.Series(True, index=df.index))
            elif op in ("==", "=", "eq", "!=", "ne"):
                try:
                    m = _to_numeric(s) == float(val) if _is_mostly_numeric(s) else s.astype(str).str.strip().str.lower() == str(val).strip().lower()
                except (TypeError, ValueError):
                    m = s.astype(str).str.strip().str.lower() == str(val).strip().lower()
                if op in ("!=", "ne"):
                    m = ~m
            elif op in ("contains", "not_contains"):
                m = s.astype(str).str.contains(str(val), case=False, regex=False, na=False)
                if op == "not_contains":
                    m = ~m
            elif op == "startswith":
                m = s.astype(str).str.lower().str.startswith(str(val).lower(), na=False)
            elif op == "endswith":
                m = s.astype(str).str.lower().str.endswith(str(val).lower(), na=False)
            elif op == "in" and isinstance(val, (list, tuple)):
                wanted = {str(x).strip().lower() for x in val}
                m = s.astype(str).str.strip().str.lower().isin(wanted)
            elif op == "is_null":
                m = s.isna() | (s.astype(str).str.strip() == "")
            elif op == "not_null":
                m = s.notna() & (s.astype(str).str.strip() != "")
            else:
                continue
            mask &= m.fillna(False)
        except (TypeError, ValueError):
            continue
    out = df[mask]

    for srt in reversed((spec.get("sort") or [])[:3]):
        col = _find_column(out, srt.get("column")) if isinstance(srt, dict) else None
        if col is None:
            continue
        asc = str(srt.get("order", "asc")).lower() != "desc"
        key = _to_numeric(out[col]) if _is_mostly_numeric(out[col]) else out[col].astype(str).str.lower()
        out = out.assign(_k=key).sort_values("_k", ascending=asc, na_position="last", kind="stable").drop(columns="_k")

    try:
        limit = int(spec.get("limit") or MAX_RESULT_ROWS)
    except (TypeError, ValueError):
        limit = MAX_RESULT_ROWS
    out = out.head(max(1, min(limit, MAX_RESULT_ROWS)))

    cols = [c for c in (_find_column(out, c) for c in (spec.get("columns") or [])) if c]
    if cols:
        out = out[cols]
    return [{k: (None if pd.isna(v) else v) if not isinstance(v, (list, dict)) else v for k, v in r.items()}
            for r in out.to_dict(orient="records")]
