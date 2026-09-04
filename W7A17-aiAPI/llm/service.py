from fastapi import HTTPException

from llm import quarantine
from llm.client import LLMClient, load_prompt, user_message
from llm.pipeline import ParseError, parse_result, repair_message
from llm.schema import Source, TriageResult


class TriageService:
    def __init__(self, stub_mode: bool, client: LLMClient, prompt_version: str, quarantine_path: str):
        self.stub_mode = stub_mode
        self.client = client
        self.prompt_version = prompt_version
        self.quarantine_path = quarantine_path

    def triage(self, text: str) -> tuple[TriageResult, Source]:
        system_prompt = load_prompt(self.prompt_version)
        messages = [{"role": "user", "content": user_message(text)}]

        raw, stats = self.client.complete(system_prompt, messages)
        try:
            return parse_result(raw), Source.MODEL
        except ParseError as first_error:
            reason = str(first_error)

        messages = messages + [
            {"role": "assistant", "content": raw},
            repair_message(raw, reason),
        ]
        repaired, stats = self.client.complete(system_prompt, messages)
        try:
            return parse_result(repaired), Source.MODEL
        except ParseError as second_error:
            quarantine.record(
                self.quarantine_path,
                text=text,
                raw_answer=repaired,
                reason=str(second_error),
                prompt_version=self.prompt_version,
                model=stats["model"],
            )
            raise HTTPException(
                status_code=422,
                detail=f"The model could not produce a valid answer after one repair attempt ({second_error})",
            ) from second_error
