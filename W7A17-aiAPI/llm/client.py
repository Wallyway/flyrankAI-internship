import json
import time
from pathlib import Path

from fastapi import HTTPException
from openai import APIConnectionError, APIStatusError, APITimeoutError, OpenAI

from llm import retry

PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"


def load_prompt(version: str) -> str:
    return (PROMPTS_DIR / f"{version}.md").read_text(encoding="utf-8")


def user_message(text: str) -> str:
    return json.dumps({"task_text": text}, ensure_ascii=False)


class LLMClient:
    def __init__(self, base_url: str, api_key: str, model: str, timeout: float, max_attempts: int):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_attempts = max_attempts
        self._client = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            if not self.api_key:
                raise HTTPException(
                    status_code=503,
                    detail="LLM_API_KEY is not set. Add it to .env, or run with LLM_STUB=1 to skip the model.",
                )
            self._client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=self.timeout,
                max_retries=0,
            )
        return self._client

    def complete(self, system_prompt: str, messages: list[dict]) -> tuple[str, dict]:
        payload = [{"role": "system", "content": system_prompt}] + messages
        started = time.monotonic()
        client = self.client

        for attempt in range(1, self.max_attempts + 1):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    temperature=0,
                    messages=payload,
                )
            except APITimeoutError as error:
                if attempt == self.max_attempts:
                    raise HTTPException(
                        status_code=504,
                        detail=f"The model did not answer within {self.timeout:g}s",
                    ) from error
                retry.wait(attempt)
                continue
            except APIConnectionError as error:
                if attempt == self.max_attempts:
                    raise HTTPException(
                        status_code=504,
                        detail="Could not reach the model provider",
                    ) from error
                retry.wait(attempt)
                continue
            except APIStatusError as error:
                if not retry.is_retryable(error.status_code) or attempt == self.max_attempts:
                    raise HTTPException(
                        status_code=502,
                        detail=f"The model provider rejected the request (HTTP {error.status_code})",
                    ) from error
                retry.wait(attempt, getattr(error.response, "headers", None))
                continue

            usage = response.usage
            return response.choices[0].message.content or "", {
                "model": response.model,
                "input_tokens": getattr(usage, "prompt_tokens", 0) if usage else 0,
                "output_tokens": getattr(usage, "completion_tokens", 0) if usage else 0,
                "duration_ms": round((time.monotonic() - started) * 1000),
                "attempts": attempt,
            }

        raise HTTPException(status_code=502, detail="The model provider could not be reached")
