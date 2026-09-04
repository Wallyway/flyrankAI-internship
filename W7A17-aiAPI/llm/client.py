import json
from pathlib import Path

from openai import OpenAI

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(version: str) -> str:
    return (PROMPTS_DIR / f"{version}.md").read_text(encoding="utf-8")


def user_message(text: str) -> str:
    return json.dumps({"task_text": text}, ensure_ascii=False)


class LLMClient:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: float):
        self.model = model
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=0,
        )

    def complete(self, system_prompt: str, messages: list[dict]) -> tuple[str, dict]:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[{"role": "system", "content": system_prompt}] + messages,
        )
        usage = response.usage
        stats = {
            "model": response.model,
            "input_tokens": getattr(usage, "prompt_tokens", 0),
            "output_tokens": getattr(usage, "completion_tokens", 0),
        }
        return response.choices[0].message.content or "", stats
