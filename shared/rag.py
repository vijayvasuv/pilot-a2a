"""Lightweight local RAG — keyword search over KB markdown (no torch/Chroma required)."""

import json
import re
from pathlib import Path

from shared.config import KB_ROOT, PROJECT_ROOT

INDEX_PATH = PROJECT_ROOT / "data" / "kb_index.json"


def _chunk_text(text: str, chunk_size: int = 500, overlap: int = 80) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end].strip())
        start = end - overlap
    return [c for c in chunks if c]


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", text.lower()))


def ingest_kb(kb_root: Path | None = None) -> int:
    """Index all .md files under kb/login, kb/billing, kb/escalation."""
    root = kb_root or KB_ROOT
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    for agent_type in ("login", "billing", "escalation"):
        agent_dir = root / agent_type
        if not agent_dir.exists():
            continue
        for md_file in sorted(agent_dir.glob("*.md")):
            content = md_file.read_text(encoding="utf-8")
            for i, chunk in enumerate(_chunk_text(content)):
                records.append(
                    {
                        "id": f"{agent_type}/{md_file.stem}#{i}",
                        "content": chunk,
                        "agent_type": agent_type,
                        "source": md_file.name,
                        "title": md_file.stem.replace("-", " ").title(),
                    }
                )

    INDEX_PATH.write_text(json.dumps(records, indent=2), encoding="utf-8")
    return len(records)


def _load_index() -> list[dict]:
    if not INDEX_PATH.exists():
        ingest_kb()
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def search_kb(query: str, agent_type: str, top_k: int = 3) -> list[dict]:
    """Search KB filtered by agent type (login | billing | escalation)."""
    records = _load_index()
    query_tokens = _tokenize(query)

    candidates = records
    if agent_type in ("login", "billing"):
        candidates = [r for r in records if r["agent_type"] in (agent_type, "escalation")]
    elif agent_type == "escalation":
        candidates = [r for r in records if r["agent_type"] == "escalation"]

    scored: list[tuple[float, dict]] = []
    for record in candidates:
        doc_tokens = _tokenize(record["content"] + " " + record["title"])
        if not query_tokens:
            continue
        overlap = len(query_tokens & doc_tokens)
        if overlap == 0:
            continue
        score = overlap / len(query_tokens)
        scored.append((score, record))

    scored.sort(key=lambda x: x[0], reverse=True)
    hits: list[dict] = []
    for score, record in scored[:top_k]:
        hits.append(
            {
                "content": record["content"],
                "source": record["source"],
                "title": record["title"],
                "agent_type": record["agent_type"],
                "score": round(score, 3),
            }
        )
    return hits


def format_kb_results(results: list[dict]) -> str:
    if not results:
        return "No relevant knowledge base articles found."
    lines = ["Knowledge base results:"]
    for i, r in enumerate(results, 1):
        lines.append(
            f"{i}. [{r['title']}] (source: {r['source']}, relevance: {r['score']})\n{r['content']}"
        )
    return "\n\n".join(lines)
