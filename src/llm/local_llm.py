import requests


class LocalLLM:
    def __init__(
        self,
        api_url: str = "http://127.0.0.1:1234/v1/chat/completions",
        model_name: str = "qwen2.5-3b-instruct"
    ):
        self.api_url = api_url
        self.model_name = model_name

    def generate(self, messages, temperature=0.1, max_tokens=500, timeout=120):
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        response = requests.post(
            self.api_url,
            json=payload,
            timeout=timeout
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"LM Studio API Error: HTTP {response.status_code}"
            )

        data = response.json()
        return data["choices"][0]["message"]["content"].strip()
