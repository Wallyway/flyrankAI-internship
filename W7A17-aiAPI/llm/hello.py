import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    base_url=os.environ["LLM_BASE_URL"],
    api_key=os.environ["LLM_API_KEY"],
    timeout=30.0,
    max_retries=0,
)

response = client.chat.completions.create(
    model=os.environ["LLM_MODEL"],
    messages=[{"role": "user", "content": "Reply with exactly the word: ready"}],
)

answer = response.choices[0].message.content
print(answer)

usage = response.usage
print(f"model={response.model} input_tokens={usage.prompt_tokens} output_tokens={usage.completion_tokens}")

if "ready" not in (answer or "").lower():
    sys.exit(1)
