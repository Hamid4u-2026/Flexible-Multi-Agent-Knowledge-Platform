import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class GroqLLM:
    def __init__(self, model_name: str = "openai/gpt-oss-20b"):
        self.model_name = model_name

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is missing.")

        self.client = Groq(api_key=api_key)

    def generate(self, messages, temperature=0.1, max_tokens=500):
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            reasoning_effort="low",
            max_completion_tokens=max_tokens
        )

        return response.choices[0].message.content.strip()
