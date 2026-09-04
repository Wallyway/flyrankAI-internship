import json
from datetime import datetime, timezone
from pathlib import Path


def record(path: str, text: str, raw_answer: str, reason: str, prompt_version: str, model: str):
    entry = {
        "quarantined_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "prompt_version": prompt_version,
        "model": model,
        "input": text,
        "raw_answer": raw_answer,
        "error": reason,
    }
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
