from src.llm.local_llm import LocalLLM
from src.llm.groq_llm import GroqLLM


class LLMProvider:
    """
    Primary: LM Studio + Qwen2.5-3B
    Fallback: Groq + GPT-OSS 20B
    """

    def __init__(
        self,
        local_api_url: str = "http://127.0.0.1:1234/v1/chat/completions",
        local_model: str = "qwen2.5-3b-instruct",
        groq_model: str = "openai/gpt-oss-20b"
    ):
        self.local_llm = LocalLLM(
            api_url=local_api_url,
            model_name=local_model
        )

        self.groq_llm = GroqLLM(
            model_name=groq_model
        )

    def generate(
        self,
        messages,
        temperature=0.1,
        max_tokens=500,
        timeout=120
    ):
        # المحاولة الأولى: النموذج المحلي Qwen عبر LM Studio
        try:
            result = self.local_llm.generate(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout
            )

            if result:
                return result, "LM Studio — Qwen2.5-3B"

        except Exception as local_error:
            print(f"[LLM Provider] Local LLM failed: {local_error}")

        # المحاولة الثانية: Groq كمسار احتياطي
        try:
            result = self.groq_llm.generate(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )

            if result:
                return result, "Groq API — GPT-OSS 20B"

        except Exception as groq_error:
            print(f"[LLM Provider] Groq fallback failed: {groq_error}")

        raise RuntimeError(
            "Both LLM providers failed: LM Studio and Groq."
        )
