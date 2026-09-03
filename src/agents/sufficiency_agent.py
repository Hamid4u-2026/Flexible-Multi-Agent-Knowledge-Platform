from typing import Dict, Any, List

class KnowledgeSufficiencyAgent:
    """
    Knowledge Sufficiency Assessment .
    Evaluates retrieved evidence (FAISS + Web) to determine if context
    is sufficient for Qwen2.5 generation without hallucination.
    """
    def __init__(self, min_local_chunks: int = 1, min_web_length: int = 50):
        self.min_local_chunks = min_local_chunks
        self.min_web_length = min_web_length

    def evaluate_sufficiency(self, retrieval_output: Dict[str, Any]) -> Dict[str, Any]:
        local_chunks: List[Dict[str, Any]] = retrieval_output.get("local_chunks", [])
        web_evidence: str = retrieval_output.get("web_evidence", "")

        has_local = len(local_chunks) >= self.min_local_chunks
        has_web = len(web_evidence) >= self.min_web_length and "No official evidence found" not in web_evidence

        is_sufficient = has_local or has_web

        status_message = "Sufficient context retrieved." if is_sufficient else "Insufficient evidence available."

        return {
            "is_sufficient": is_sufficient,
            "has_local_data": has_local,
            "has_web_data": has_web,
            "local_count": len(local_chunks),
            "status_message": status_message
        }
