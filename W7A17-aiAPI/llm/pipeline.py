import json
import re

from pydantic import ValidationError

from llm.schema import TriageResult

FENCE_PATTERN = re.compile(r"^\s*```(?:json)?\s*(.*?)\s*```\s*$", re.DOTALL)


def strip_fence(text: str) -> str:
    match = FENCE_PATTERN.match(text or "")
    if match:
        return match.group(1)
    return (text or "").strip()


def extract_object(text: str) -> str:
    stripped = strip_fence(text)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end < start:
        raise ParseError("no JSON object found in the model answer")
    return stripped[start : end + 1]


def parse_result(text: str) -> TriageResult:
    candidate = extract_object(text)
    try:
        payload = json.loads(candidate)
    except json.JSONDecodeError as error:
        raise ParseError(f"answer is not valid JSON: {error.msg}") from error
    if not isinstance(payload, dict):
        raise ParseError("answer is valid JSON but not an object")
    try:
        return TriageResult.model_validate(payload)
    except ValidationError as error:
        raise ParseError(describe(error)) from error


def describe(error: ValidationError) -> str:
    parts = []
    for item in error.errors():
        field = ".".join(str(piece) for piece in item["loc"]) or "body"
        parts.append(f"{field}: {item['msg']}")
    return "; ".join(parts)


def repair_message(broken: str, reason: str) -> dict:
    return {
        "role": "user",
        "content": (
            "Your previous answer was rejected for this reason: "
            f"{reason}\n\nYour previous answer was:\n{broken}\n\n"
            "Return only corrected JSON matching the schema. "
            "No prose, no code fence, no extra fields."
        ),
    }


class ParseError(Exception):
    pass
