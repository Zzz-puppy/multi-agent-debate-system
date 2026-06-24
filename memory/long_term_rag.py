"""Long-term memory using Chroma vector DB for debate knowledge retrieval."""

import os
import uuid
from typing import List
import chromadb
from chromadb.config import Settings


class LongTermRAGMemory:
    def __init__(self, persist_dir: str = "data/chroma_db"):
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir, settings=Settings(anonymized_telemetry=False))
        self.collection = self.client.get_or_create_collection(name="debate_history", metadata={"hnsw:space":"cosine"})

    def store_debate(self, topic: str, summary: str, pro_arguments: List[str], con_arguments: List[str], teacher_score: dict, teacher_comment: str) -> str:
        doc_id = str(uuid.uuid4())
        self.collection.add(documents=[f"辩题: {topic}\n摘要: {summary}\n正方论点: {'; '.join(pro_arguments)}\n反方论点: {'; '.join(con_arguments)}\n评分: {teacher_score}\n评语: {teacher_comment}"],
            metadatas=[{"topic":topic,"winner":teacher_score.get("winner",""),"pro_score":teacher_score.get("pro",0),"con_score":teacher_score.get("con",0)}], ids=[doc_id])
        return doc_id

    def search_similar(self, query: str, n_results: int = 3) -> List[dict]:
        try:
            results = self.collection.query(query_texts=[query], n_results=n_results)
        except Exception:
            return []
        return [{"content":doc,"metadata":(results["metadatas"][0][i] if results.get("metadatas") else {})} for i,doc in enumerate(results["documents"][0])] if results and results.get("documents") and results["documents"][0] else []

    def count(self) -> int:
        return self.collection.count()
