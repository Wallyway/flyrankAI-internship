import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import httpx

CASES_PATH = Path(__file__).resolve().parent / "cases.json"
BASE_URL = os.getenv("EVAL_BASE_URL", "http://localhost:8000")
PROMPT_VERSION = os.getenv("PROMPT_VERSION", "triage-v1")


def run():
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    category_hits = 0
    urgency_hits = 0
    failures = []

    with httpx.Client(base_url=BASE_URL, timeout=60.0) as client:
        for case in cases:
            try:
                response = client.post("/tasks/triage", json={"text": case["text"]})
            except httpx.HTTPError as error:
                failures.append((case["id"], f"request failed: {error}"))
                continue

            if response.status_code != 200:
                failures.append((case["id"], f"HTTP {response.status_code}: {response.text[:120]}"))
                continue

            body = response.json()
            expected = case["expected"]
            category_ok = body["category"] == expected["category"]
            urgency_ok = body["urgency"] == expected["urgency"]
            category_hits += category_ok
            urgency_hits += urgency_ok

            if not category_ok or not urgency_ok:
                got = f"{body['category']}/{body['urgency']}"
                want = f"{expected['category']}/{expected['urgency']}"
                failures.append((case["id"], f"expected {want}, got {got} (confidence {body['confidence']})"))

    total = len(cases)
    print(f"date            {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    print(f"prompt_version  {PROMPT_VERSION}")
    print(f"model           {os.getenv('LLM_MODEL', 'google/gemini-2.5-flash-lite')}")
    print()
    print(f"category        {category_hits} / {total}")
    print(f"urgency         {urgency_hits} / {total}")

    if failures:
        print()
        print("failures:")
        for case_id, detail in failures:
            print(f"  {case_id}: {detail}")

    return 0 if category_hits == total else 1


if __name__ == "__main__":
    sys.exit(run())
