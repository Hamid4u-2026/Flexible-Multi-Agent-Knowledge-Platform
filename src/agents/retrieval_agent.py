from typing import Dict, Any
from src.tools.rag_tool import SVUKnowledgeRetriever
from src.tools.web_retriever import TrustedWebRetriever

DEFAULT_SCORE_THRESHOLD = 0.65


class KnowledgeRetrievalAgent:
    """
    Orchestrates Web Intent routing, local FAISS retrieval,
    and conditional trusted web fallback.
    """

    def __init__(
        self,
        index_dir: str = None,
        trusted_domain: str = "svuonline.org",
        score_threshold: float = DEFAULT_SCORE_THRESHOLD,
        **kwargs
    ):
        self.score_threshold = score_threshold

        if index_dir:
            self.local_retriever = SVUKnowledgeRetriever(index_dir=index_dir)
        else:
            self.local_retriever = SVUKnowledgeRetriever()

        self.web_retriever = TrustedWebRetriever(
            trusted_domain=trusted_domain
        )

    def execute_retrieval(
        self,
        query: str,
        top_k: int = 5,
        original_query: str = None
    ) -> Dict[str, Any]:

        # استخدام السؤال الأصلي لاكتشاف Web Intent.
        intent_query = original_query if original_query else query

        # ==================================================
        # 1. Web Intent Gate
        # ==================================================
        web_intent = self.web_retriever.detect_web_intent(intent_query)

        if web_intent:
            print(f"[Web Intent] Detected: {web_intent}")

            web_evidence = self.web_retriever.search_trusted_web(
                intent_query
            )

            if web_evidence and len(web_evidence.strip()) > 30:
                return {
                    "source_type": "web_intent",
                    "local_chunks": [],
                    "has_local_data": False,
                    "web_fallback_used": True,
                    "web_intent_detected": web_intent,
                    "web_evidence": web_evidence,
                    "best_score": 999.0
                }

            print("[Web Intent] Official page unavailable or empty.")

        # ==================================================
        # 2. Local FAISS Retrieval
        # ==================================================
        raw_local_results = self.local_retriever.search_local_faiss(
            query,
            top_k=top_k
        )

        filtered_chunks = []
        best_score = 999.0

        if raw_local_results:
            # في FAISS مع L2، القيمة الأصغر تعني تشابهًا أقوى.
            best_score = min(
                chunk.get("score", 999.0)
                for chunk in raw_local_results
            )

            for chunk in raw_local_results:
                if chunk.get("score", 999.0) <= self.score_threshold:
                    filtered_chunks.append(chunk)

        has_local_data = len(filtered_chunks) > 0

        # ==================================================
        # 3. Local Retrieval Success
        # ==================================================
        if has_local_data:
            return {
                "source_type": "local",
                "local_chunks": filtered_chunks,
                "has_local_data": True,
                "web_fallback_used": False,
                "web_intent_detected": "",
                "web_evidence": "",
                "best_score": best_score
            }

        # ==================================================
        # 4. Conditional Web Fallback
        # ==================================================
        web_evidence = self.web_retriever.search_trusted_web(
            intent_query
        )

        if web_evidence and len(web_evidence.strip()) > 30:
            return {
                "source_type": "web",
                "local_chunks": [],
                "has_local_data": False,
                "web_fallback_used": True,
                "web_intent_detected": "",
                "web_evidence": web_evidence,
                "best_score": best_score
            }

        # ==================================================
        # 5. Abstention Path
        # ==================================================
        return {
            "source_type": "none",
            "local_chunks": [],
            "has_local_data": False,
            "web_fallback_used": True,
            "web_intent_detected": "",
            "web_evidence": "",
            "best_score": best_score
        }
