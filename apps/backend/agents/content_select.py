"""
Budget-aware HTML reduction for the extractor.

Why: the old minify_html() kept every attribute and the site chrome (header/nav/filters) and then cut the string at
MAX_HTML_CHARS from the TOP. On big listing pages (Amazon, Flipkart, ...) the product grid sits after that cut-off,
so the LLM saw only navigation and returned zero records -> the user got a misleading "couldn't access this URL".

This module is only used when the page is bigger than the budget (small pages are returned exactly as before).
PURE function: html in -> str out. No network, no I/O.
"""
import json
import re
from typing import List, Optional

from bs4 import BeautifulSoup, Tag

NOISE_TAGS = ["script", "style", "noscript", "svg", "iframe", "path", "link", "meta", "img", "video", "audio",
              "canvas", "map", "source", "picture"]            # identical to the legacy list
KEEP_ATTRS = {"href", "title", "aria-label", "alt", "datetime", "itemprop", "content"}
_SEMANTIC_CLASS = re.compile(r"^[a-z][a-z0-9_-]{2,30}$")       # drops hashed classes like _1AtVbE / css-1x9zq
MIN_ITEM_TEXT = 40
MIN_ITEMS = 4
MAX_LD_CHARS = 2500


def _ws(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def _collect_json_ld(soup: BeautifulSoup) -> str:
    out: List[str] = []
    for tag in soup.find_all("script", attrs={"type": re.compile(r"application/ld\+json", re.I)}):
        raw = (tag.string or tag.get_text() or "").strip()
        if not raw:
            continue
        try:
            out.append(json.dumps(json.loads(raw), ensure_ascii=False, separators=(",", ":")))
        except Exception:
            continue
        if sum(len(x) for x in out) > MAX_LD_CHARS:
            break
    return _ws(" ".join(out))[:MAX_LD_CHARS]


def _slim_attrs(tag: Tag) -> None:
    attrs = dict(tag.attrs or {})
    new = {}
    for k, v in attrs.items():
        if k in KEEP_ATTRS:
            new[k] = " ".join(v) if isinstance(v, list) else v
        elif k == "class":
            toks = [t for t in (v if isinstance(v, list) else v.split()) if _SEMANTIC_CLASS.match(t)][:3]
            if toks:
                new["class"] = " ".join(toks)[:40]
    tag.attrs = new


def _has_ancestor(tag: Tag, names: set) -> bool:
    return any(getattr(p, "name", None) in names for p in tag.parents)


def _find_dominant_cluster(root: Tag) -> Optional[List[Tag]]:
    """Parent whose same-tag children (text >= 40 chars, containing a link) hold the most text, with >= 4 items."""
    best, best_score = None, 0
    for parent in root.find_all(True):
        groups = {}
        for child in parent.find_all(True, recursive=False):
            txt = child.get_text(" ", strip=True)
            if len(txt) >= MIN_ITEM_TEXT and child.find("a", href=True):
                groups.setdefault(child.name, []).append((child, len(txt)))
        for _, items in groups.items():
            if len(items) >= MIN_ITEMS:
                score = sum(n for _, n in items)
                if score > best_score:
                    best, best_score = [c for c, _ in items], score
    return best


def smart_minify(html_content: str, max_chars: int) -> str:
    soup = BeautifulSoup(html_content, "lxml")
    ld = _collect_json_ld(soup)
    for t in soup(NOISE_TAGS):
        t.decompose()
    for t in soup.find_all(["nav", "footer", "aside"]):
        if not _has_ancestor(t, {"article", "li", "tr", "main"}):
            t.decompose()

    title = _ws(soup.title.get_text()) if soup.title else ""
    h1 = soup.find("h1")
    head_ctx = f"<title>{title[:160]}</title>" + (f"<h1>{_ws(h1.get_text())[:160]}</h1>" if h1 else "")

    cluster = _find_dominant_cluster(soup.body or soup)
    parts: List[str] = [head_ctx]
    if ld:
        parts.append(f'<script type="application/ld+json">{ld}</script>')
    budget = max_chars - sum(len(p) for p in parts) - 40

    if cluster:
        # keep table headers so columns stay meaningful
        first = cluster[0]
        if first.name == "tr":
            table = first.find_parent("table")
            thead = table.find("thead") if table else None
            if thead:
                _slim_all(thead)
                head_html = _ws(str(thead))
                parts.append(head_html[: max(0, budget // 5)])
                budget -= len(parts[-1])
        for item in cluster:
            _slim_all(item)
            s = _ws(str(item))
            if budget - len(s) < 0:
                if budget > 400:
                    parts.append(s[:budget])
                break
            parts.append(s)
            budget -= len(s)
        return _ws(" ".join(parts))[:max_chars]

    # No repeating cluster (article / single product page): slim attrs for the whole body, truncate as before
    root = soup.body or soup
    _slim_all(root)
    text = _ws(" ".join(parts) + " " + str(root))
    if len(text) > max_chars:
        text = text[:max_chars] + " <!-- TRUNCATED -->"
    return text


def _slim_all(root: Tag) -> None:
    _slim_attrs(root)
    for t in root.find_all(True):
        _slim_attrs(t)
