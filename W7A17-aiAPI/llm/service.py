from llm.client import LLMClient, load_prompt, user_message


class TriageService:
    def __init__(self, stub_mode: bool, client: LLMClient, prompt_version: str):
        self.stub_mode = stub_mode
        self.client = client
        self.prompt_version = prompt_version

    def triage_raw(self, text: str) -> tuple[str, dict]:
        system_prompt = load_prompt(self.prompt_version)
        messages = [{"role": "user", "content": user_message(text)}]
        return self.client.complete(system_prompt, messages)
