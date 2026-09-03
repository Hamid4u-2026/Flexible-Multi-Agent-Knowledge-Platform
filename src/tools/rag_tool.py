import os
import json
from typing import List, Dict, Any
import faiss
from langchain_community.vectorstores import FAISS
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

class SVUKnowledgeRetriever:
    """
    Actual FAISS Vector Store Retriever for SVU Documents.
    Reads index.faiss and index_metadata.json directly.
    """
    def __init__(self, index_dir: str = "data/processed/faiss_index"):
        self.index_dir = index_dir
        self.embeddings = HuggingFaceEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True}
        )
        self.vector_store = self._load_custom_faiss()

    def _load_custom_faiss(self) -> FAISS:
        faiss_path = os.path.join(self.index_dir, "index.faiss")
        metadata_path = os.path.join(self.index_dir, "index_metadata.json")

        if not os.path.exists(faiss_path) or not os.path.exists(metadata_path):
            raise FileNotFoundError(f"FAISS files missing in {self.index_dir}")

        index = faiss.read_index(faiss_path)

        with open(metadata_path, "r", encoding="utf-8") as f:
            metadata_list = json.load(f)

        docstore = InMemoryDocstore()
        index_to_docstore_id = {}

        for idx, item in enumerate(metadata_list):
            doc_id = str(idx)
            content = item.get("text", "")
            meta = {k: v for k, v in item.items() if k != "text"}

            doc = Document(
                page_content=content,
                metadata=meta
            )
            docstore.add({doc_id: doc})
            index_to_docstore_id[idx] = doc_id

        return FAISS(
            embedding_function=self.embeddings,
            index=index,
            docstore=docstore,
            index_to_docstore_id=index_to_docstore_id
        )

    def search_local_faiss(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        docs_and_scores = self.vector_store.similarity_search_with_score(query, k=top_k)
        results = []
        for doc, score in docs_and_scores:
            results.append({
                "content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)
            })
        return results
