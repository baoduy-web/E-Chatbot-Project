"""Bộ truy hồi tri thức (Retriever) phục vụ Grounded Evidence RAG.

Tìm kiếm nội dung có liên quan từ kho dữ liệu đã thu thập của Bệnh viện E và Dược thư,
cung cấp nguồn URL và bằng chứng trích dẫn.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_DEFAULT_ARTICLES_DIR = Path(__file__).resolve().parents[2] / "data" / "hospital_e" / "articles"
_DEFAULT_MANIFEST = Path(__file__).resolve().parents[2] / "data" / "hospital_e" / "manifest.json"


@dataclass(frozen=True)
class SearchCitation:
    title: str
    url: str
    category: str
    snippet: str
    confidence: float


class KnowledgeRetriever:
    """Truy xuất tri thức từ kho tài liệu Bệnh viện E đã thu thập."""

    def __init__(self, articles_dir: Path | None = None, manifest_path: Path | None = None) -> None:
        self.articles_dir = articles_dir or _DEFAULT_ARTICLES_DIR
        self.manifest_path = manifest_path or _DEFAULT_MANIFEST
        self._documents: list[dict[str, str]] = []
        self._load_documents()

    def _load_documents(self) -> None:
        if self.manifest_path.exists():
            try:
                manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
                for item in manifest:
                    md_file = Path(item["md_path"])
                    if md_file.exists():
                        text = md_file.read_text(encoding="utf-8")
                        self._documents.append(
                            {
                                "id": item["id"],
                                "title": item["title"],
                                "category": item["category"],
                                "url": f"https://benhviene.com/trang-noi-dung/{item['id']}",
                                "content": text,
                            }
                        )
            except (OSError, json.JSONDecodeError):
                pass

    def search(self, query: str, top_k: int = 3) -> tuple[SearchCitation, ...]:
        """Tìm kiếm các đoạn văn bản phù hợp nhất với câu hỏi."""
        q_words = [w.lower() for w in query.split() if len(w) > 2]
        if not q_words:
            return ()

        scored: list[tuple[float, SearchCitation]] = []
        for doc in self._documents:
            content_lower = doc["content"].lower()
            title_lower = doc["title"].lower()

            matches = sum(1 for w in q_words if w in content_lower)
            title_matches = sum(2 for w in q_words if w in title_lower)
            total_score = matches + title_matches

            if total_score > 0:
                conf = min(1.0, total_score / (len(q_words) * 2))
                # Tìm đoạn trích chứa từ khóa đầu tiên tìm thấy
                snippet = doc["content"][:300].replace("\n", " ") + "..."
                for w in q_words:
                    pos = content_lower.find(w)
                    if pos != -1:
                        start = max(0, pos - 50)
                        end = min(len(doc["content"]), pos + 250)
                        snippet = "..." + doc["content"][start:end].replace("\n", " ").strip() + "..."
                        break

                citation = SearchCitation(
                    title=doc["title"],
                    url=doc["url"],
                    category=doc["category"],
                    snippet=snippet,
                    confidence=round(conf, 2),
                )
                scored.append((total_score, citation))

        scored.sort(key=lambda x: x[0], reverse=True)
        return tuple(c for _, c in scored[:top_k])


knowledge_retriever = KnowledgeRetriever()
