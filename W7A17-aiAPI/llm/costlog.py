import json
import sys
from datetime import datetime, timezone


def emit(prompt_version: str, stats: dict, repairs: int, outcome: str):
    line = {
        "event": "llm_call",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "prompt_version": prompt_version,
        "model": stats.get("model"),
        "input_tokens": stats.get("input_tokens", 0),
        "output_tokens": stats.get("output_tokens", 0),
        "duration_ms": stats.get("duration_ms", 0),
        "attempts": stats.get("attempts", 1),
        "repairs": repairs,
        "outcome": outcome,
    }
    print(json.dumps(line), file=sys.stdout, flush=True)
