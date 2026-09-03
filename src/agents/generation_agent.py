import sys
import os
from typing import Dict, Any
import requests
from src.llm.llm_provider import LLMProvider

ABSTENTION_TEXT_AR = "لم يتم العثور على أدلة كافية في مصادر المعرفة المتاحة."
ABSTENTION_TEXT_EN = "Insufficient evidence found in the available knowledge sources."


class ResponseGenerationAgent:
    """
    Generates grounded responses using local Qwen2.5-3B-Instruct model
    based strictly on evidence retrieved by KnowledgeRetrievalAgent.
    """
    def __init__(self, api_url: str = "http://127.0.0.1:1234/v1/chat/completions", model_name: str = "qwen2.5-3b-instruct"):
        self.api_url = api_url
        self.model_name = model_name

    def generate_response(self, query: str, retrieval_output: Dict[str, Any], user_lang: str = "ar") -> str:
        target_abstention = ABSTENTION_TEXT_AR if user_lang == "ar" else ABSTENTION_TEXT_EN

        has_local = retrieval_output.get("has_local_data", False)

        # 1. Deterministic Extraction of Context
        if has_local:
            chunks = retrieval_output.get("local_chunks", [])
            extracted_texts = []
            for c in chunks:
                if isinstance(c, dict):
                    text = c.get('content') or c.get('page_content') or c.get('text') or ''
                    if text:
                        extracted_texts.append(text)
                elif isinstance(c, str):
                    extracted_texts.append(c)
            context_text = "\n\n".join(extracted_texts).strip()

            source_names = []
            for chunk in chunks:
                if isinstance(chunk, dict):
                    name = chunk.get("metadata", {}).get("source", "")
                    if name and name not in source_names:
                        source_names.append(name)

            source_type = ", ".join(source_names) if source_names else "Local Vector Store (FAISS)"
        else:
            context_text = str(retrieval_output.get('web_evidence', '')).strip()
            source_type = "svuonline.org (Official Web Fallback)"

        # Absolute Guard
        if not context_text or len(context_text) < 15:
            return target_abstention

        # 2. Enhanced Flexible Academic Guidance Prompt
        system_instruction = (
            "You are an academic guidance assistant for the Syrian Virtual University (SVU).\n"
            "INSTRUCTIONS:\n"
            f"1. Always respond in {'Standard Arabic' if user_lang == 'ar' else 'English'}.\n"
            "2. Note: The Provided Context may be in English or Arabic. Translate and synthesize the information accurately if needed.\n"
            "3. Answer the query using ALL relevant information available in the Provided Context. If the context contains partial lists or specific programs, present them clearly as the available details from the documents.\n"
            "4. Do NOT use outside knowledge or make up unmentioned details, but DO answer as completely as possible using what is in the Provided Context.\n"
            f"5. ONLY if the Provided Context contains NO information or is completely irrelevant to the query, reply strictly with: '{target_abstention}'.\n"
            f"6. End your response with: '{'مصدر المعلومات' if user_lang == 'ar' else 'Information Source'}: {source_type}'."
        )

        user_content = f"User Query: {query}\n\nProvided Context:\n{context_text}"

        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.1,
            "max_tokens": 700
        }

        try:
            provider = LLMProvider(
                local_api_url=self.api_url,
                local_model=self.model_name
            )

            raw_text, provider_used = provider.generate(
                messages=payload["messages"],
                temperature=payload["temperature"],
                max_tokens=payload["max_tokens"]
            )
            self.last_provider_used = provider_used

            if raw_text.strip() == target_abstention.strip():
                return target_abstention

            return raw_text

        except Exception as e:
            return f"[Connection Failure]: All LLM providers unavailable. Details: {str(e)}"