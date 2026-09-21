"""Single source of truth for CSV / XLSX / JSON / Markdown export (used by /api/export/*)."""
import io
import json
import re
from datetime import datetime
from typing import Any, Dict, List

import pandas as pd

EXPORT_EXT = {"csv": "csv", "excel": "xlsx", "json": "json", "markdown": "md"}
EXPORT_MEDIA = {
    "csv": "text/csv; charset=utf-8",
    "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "json": "application/json; charset=utf-8",
    "markdown": "text/markdown; charset=utf-8",
}
_PLAIN_NUMBER = re.compile(r"^([+-]?\d[\d,]*(\.\d+)?%?|[+-]+)$")   # numbers, or a lone "-" placeholder
_MAX_CELL = 32000  # Excel hard limit is 32,767 chars per cell


def flatten_value(v: Any) -> Any:
    """Nested lists/dicts -> readable text instead of Python repr ("['a', 'b']")."""
    if v is None:
        return None
    if isinstance(v, float) and v != v:            # NaN
        return None
    if isinstance(v, (list, tuple, set)):
        return "; ".join(str(flatten_value(i)) if not isinstance(i, (dict, list)) else json.dumps(i, ensure_ascii=False) for i in v)
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False)
    return v


def sanitize_for_export(v: Any) -> Any:
    """CSV/Excel formula-injection guard that does NOT corrupt legitimate values.
    Plain numbers such as '-5' or '+1,200.50' are left untouched; '=…', '@…', tab/CR and
    '+'/'-' followed by non-numeric content are neutralised with a leading apostrophe."""
    if not isinstance(v, str) or not v:
        return v
    if v[0] in ("=", "@", "\t", "\r"):
        return "'" + v
    if v[0] in ("+", "-") and not _PLAIN_NUMBER.match(v.strip()):
        return "'" + v
    return v


def build_frame(dataset: List[Any]) -> pd.DataFrame:
    rows: List[Dict[str, Any]] = [r if isinstance(r, dict) else {"value": r} for r in dataset]
    columns: List[str] = []
    seen = set()
    for r in rows:                                   # union of keys, first-seen order (not just row 0)
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                columns.append(str(k))
    data = [{str(k): flatten_value(v) for k, v in r.items()} for r in rows]
    return pd.DataFrame(data, columns=columns, dtype=object)   # object dtype keeps ints as ints (no 5 -> 5.0)


def to_csv_bytes(df: pd.DataFrame) -> bytes:
    safe = df.apply(lambda col: col.map(sanitize_for_export))
    # UTF-8 BOM: without it Excel opens Telugu/Hindi/₹ text as garbage.
    return ("\ufeff" + safe.to_csv(index=False, lineterminator="\r\n")).encode("utf-8")


def to_xlsx_bytes(df: pd.DataFrame) -> bytes:
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "WEBISCRAP"
    headers = list(df.columns)
    ws.append(headers)
    for row in df.itertuples(index=False, name=None):
        clean = []
        for v in row:
            if v is None or (isinstance(v, float) and v != v):
                clean.append(None)
            elif isinstance(v, str):
                clean.append(v[:_MAX_CELL])
            else:
                clean.append(v.item() if hasattr(v, "item") else v)
        ws.append(clean)

    header_fill = PatternFill("solid", fgColor="1477F5")
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
        cell.alignment = Alignment(vertical="center")
    for row in ws.iter_rows(min_row=2):
        for cell in row:
            if isinstance(cell.value, str) and cell.value.startswith("="):
                cell.data_type = "s"                 # store as text: never evaluated as a formula
    for idx, name in enumerate(headers, start=1):
        sample = [len(str(name))] + [len(str(v)) for v in df.iloc[:200, idx - 1].tolist() if v is not None]
        ws.column_dimensions[get_column_letter(idx)].width = min(max(sample) + 2, 60)
    ws.freeze_panes = "A2"
    if len(df):
        ws.auto_filter.ref = ws.dimensions
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def to_json_bytes(df: pd.DataFrame) -> bytes:
    records = json.loads(df.to_json(orient="records", force_ascii=False))
    return json.dumps(records, ensure_ascii=False, indent=2).encode("utf-8")


def to_markdown_bytes(df: pd.DataFrame) -> bytes:
    safe = df.apply(lambda col: col.map(lambda v: v.replace("|", "\\|").replace("\n", " ") if isinstance(v, str) else v))
    return safe.fillna("").to_markdown(index=False).encode("utf-8")


def render_export(fmt: str, dataset: List[Any]) -> bytes:
    df = build_frame(dataset)
    if fmt == "csv":
        return to_csv_bytes(df)
    if fmt == "excel":
        return to_xlsx_bytes(df)
    if fmt == "json":
        return to_json_bytes(df)
    if fmt == "markdown":
        return to_markdown_bytes(df)
    raise ValueError(f"Unsupported export format: {fmt}")


def export_filename(fmt: str) -> str:
    return f"webiscrap_export_{datetime.now().strftime('%Y%m%d_%H%M')}.{EXPORT_EXT[fmt]}"
