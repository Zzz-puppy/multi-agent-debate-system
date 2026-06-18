"""Long-term memory using Chroma vector DB for debate knowledge retrieval."""

import os
import uuid
from typing import List

import chromadb
from chromadb.config import Settings


class LongTermRAGMemory:
    """Stores and retrieves historical debate knowledge via RAG."""

    def __init__(self, persist_dir: str = "data/chroma_db"):
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )
        self.collection = self.client.get_or_create_collection(
            name="debate_history",
            metadata={"hnsw:space": "cosine"},
        )

    def store_debate(
        self, topic: str, summary: str, pro_arguments: List[str],
        con_arguments: List[str], teacher_score: dict, teacher_comment: str,
    ) -> str:
        doc_id = str(uuid.uuid4())
        content = (
            f"辩题: {topic}\n摘要: {summary}\n"
            f"正方论点: {'; '.join(pro_arguments)}\n"
            f"反方论点: {'; '.join(con_arguments)}\n"
            f"评分: {teacher_score}\n评语: {teacher_comment}"
        )
        self.collection.add(
            documents=[content],
            metadatas=[{
                "topic": topic,
                "winner": teacher_score.get("winner", ""),
                "pro_score": teacher_score.get("pro", 0),
                "con_score": teacher_score.get("con", 0),
            }],
            ids=[doc_id],
        )
        return doc_id

    def search_similar(self, query: str, n_results: int = 3) -> List[dict]:
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
            )
        except Exception:
            return []
        docs = []
        if results and results.get("documents") and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                docs.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results.get("metadatas") else {},
                })
        return docs

    def count(self) -> int:
        return self.collection.count()
