# -*- coding: utf-8 -*-
"""
الذاكرة: قصيرة المدى (in-process) + طويلة المدى (ChromaDB محلي).
"""
import time
from collections import deque
from pathlib import Path

import chromadb
from config import DB_DIR
from ollama_client import embed


class ShortTermMemory:
    def __init__(self, maxlen: int = 20):
        self.buffer = deque(maxlen=maxlen)

    def add(self, role: str, content: str):
        self.buffer.append({"role": role, "content": content, "t": time.time()})

    def as_context(self) -> str:
        return "\n".join(f"[{m['role']}] {m['content']}" for m in self.buffer)


class LongTermMemory:
    def __init__(self, collection: str = "cowork_memory"):
        self.client = chromadb.PersistentClient(path=str(DB_DIR))
        self.col = self.client.get_or_create_collection(collection)

    def add(self, text: str, meta: dict | None = None, doc_id: str | None = None):
        vec = embed(text)
        doc_id = doc_id or f"doc_{int(time.time()*1000)}"
        # Chroma كيرفض metadata = {} فارغة تماماً — خاصها فيها غير مفتاح واحد الأقل
        safe_meta = meta if meta else {"source": "chat"}
        self.col.add(ids=[doc_id], embeddings=[vec], documents=[text], metadatas=[safe_meta])

    def search(self, query: str, k: int = 5) -> list[str]:
        vec = embed(query)
        res = self.col.query(query_embeddings=[vec], n_results=k)
        docs = res.get("documents", [[]])
        return docs[0] if docs else []

    def ingest_file(self, path: Path, chunk_size: int = 800):
        try:
            text = path.read_text(errors="ignore")
        except Exception:
            return 0
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        n = 0
        for i, c in enumerate(chunks):
            if c.strip():
                self.add(c, meta={"source": str(path), "chunk": i})
                n += 1
        return n
