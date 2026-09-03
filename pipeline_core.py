"""
pipeline_core.py
=================
Unified Operational Pipeline — Academic Guidance Portal (SVU)
واجهة الدخول التي تستدعيها app.py (Streamlit).

تتطابق تماماً مع الواجهات الفعلية للوكلاء المعرفين:
  - KnowledgeRetrievalAgent.execute_retrieval()
        يُرجع: source_type, local_chunks, has_local_data,
               web_fallback_used, web_evidence, best_score
  - KnowledgeSufficiencyAgent.evaluate_sufficiency()
        يُرجع: is_sufficient, has_local_data, has_web_data,
               local_count, status_message
  - ResponseGenerationAgent.generate_response()
        يُرجع نص الإجابة جاهزاً وموثقاً بحسب لغة المدخلات.
"""

import re

from src.agents.retrieval_agent import KnowledgeRetrievalAgent
from src.agents.sufficiency_agent import KnowledgeSufficiencyAgent
from src.agents.generation_agent import ResponseGenerationAgent, ABSTENTION_TEXT_AR, ABSTENTION_TEXT_EN
from src.llm.llm_provider import LLMProvider


# ==========================================
# Language Router (كشف اللغة باستخدام regex)
# ==========================================
def detect_language(query: str) -> tuple:
    """
    يُرجع (lang_str, lang_code):
      lang_str  : "Arabic" | "English"  (للعرض في الحالة status)
      lang_code : "ar" | "en"           (تُستهلك من ResponseGenerationAgent)
    """
    is_arabic = bool(re.search(r"[\u0600-\u06FF]", query))
    return ("Arabic", "ar") if is_arabic else ("English", "en")


# ==========================================
# Query Translation Layer
# ==========================================
def translate_query_to_english(query: str) -> tuple:
    """
    يترجم الاستعلام العربي فقط إلى الإنجليزية قبل الاسترجاع المحلي.
    يُرجع: (translated_query, provider_used)
    """
    provider = LLMProvider()

    messages = [
        {
            "role": "system",
            "content": (
                "You are a precise academic query translator. "
                "Translate the user's Arabic academic query into English. "
                "Return ONLY the English translation. "
                "Do not explain, summarize, answer, or add information."
            )
        },
        {
            "role": "user",
            "content": query
        }
    ]

    translated_query, provider_used = provider.generate(
        messages=messages,
        temperature=0.0,
        max_tokens=200
    )

    translated_query = translated_query.strip()

    if not translated_query:
        raise RuntimeError("Arabic query translation returned empty text.")

    return translated_query, provider_used


# ==========================================
# Unified Pipeline Entry Point
# ==========================================
def run_unified_pipeline(user_query: str) -> dict:
    retrieval_agent = KnowledgeRetrievalAgent()
    sufficiency_agent = KnowledgeSufficiencyAgent()
    generation_agent = ResponseGenerationAgent()

    # 1. Language Router
    query_lang_str, query_lang_code = detect_language(user_query)

    # 2. Query Translation Layer
    # المستندات المحلية باللغة الإنجليزية فقط، لذلك يُترجم الاستعلام العربي إلى الإنجليزية قبل FAISS.
    retrieval_query = user_query
    translation_provider = "N/A"

    if query_lang_code == "ar":
        try:
            retrieval_query, translation_provider = translate_query_to_english(
                user_query
            )
        except Exception as translation_error:
            return {
                "answer": ABSTENTION_TEXT_AR,
                "source": "N/A - Query Translation Failure",
                "status": {
                    "Query Language": query_lang_str,
                    "Retrieval Query Language": "English",
                    "Translation Provider": "Unavailable",
                    "Similarity Threshold": retrieval_agent.score_threshold,
                    "Best Local Score": None,
                    "Sufficiency Status": "Query translation failed.",
                    "Local Retrieval": "Not Attempted",
                    "Web Fallback": "Not Used",
                    "Response Status": "Translation Failed",
                    "Translation Error": str(translation_error),
                },
            }

    # 3. Knowledge Retrieval Agent
    retrieval_result = retrieval_agent.execute_retrieval(
        retrieval_query,
        top_k=5,
        original_query=user_query
    )

    # 4. Knowledge Sufficiency Agent
    sufficiency_result = sufficiency_agent.evaluate_sufficiency(
        retrieval_result
    )

    base_status = {
        "Query Language": query_lang_str,
        "Retrieval Query Language": "English",
        "Translation Provider": translation_provider,
        "Similarity Threshold": retrieval_agent.score_threshold,
        "Best Local Score": retrieval_result.get("best_score"),
        "Sufficiency Status": sufficiency_result["status_message"],
    }

    # 5. Deterministic Abstention
    if not sufficiency_result["is_sufficient"]:
        return {
            "answer": (
                ABSTENTION_TEXT_AR
                if query_lang_code == "ar"
                else ABSTENTION_TEXT_EN
            ),
            "source": "N/A - Insufficient Evidence",
            "status": {
                **base_status,
                "Local Retrieval": "Insufficient",
                "Web Fallback": "No Evidence",
                "Response Status": "Abstained",
            },
        }

    # 6. Response Generation Agent
    answer_text = generation_agent.generate_response(
        query=user_query,
        retrieval_output=retrieval_result,
        user_lang=query_lang_code,
    )

    generation_provider = generation_agent.last_provider_used

    # 7. Source Attribution and Final Status
    if sufficiency_result["has_local_data"]:
        local_chunks = retrieval_result.get("local_chunks", [])
        source_names = []
        for chunk in local_chunks:
            name = chunk.get("metadata", {}).get("source", "")
            if name and name not in source_names:
                source_names.append(name)
        source_attr = ", ".join(source_names) if source_names else "Local Vector Store (FAISS)"
        status = {
            **base_status,
            "Local Retrieval": "Sufficient",
            "Web Fallback": "Not Used",
            "Response Status": "Success",
            "Generation Provider": generation_provider,
        }
    else:
        source_attr = "svuonline.org (Official Web Fallback)"
        status = {
            **base_status,
            "Local Retrieval": "Insufficient",
            "Web Fallback": "Used",
            "Response Status": "Success",
            "Generation Provider": generation_provider,
        }

    return {
        "answer": answer_text,
        "source": source_attr,
        "status": status,
    }
