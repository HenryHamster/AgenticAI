# implements the AiServicesBase class for Claude

from src.services.AiServicesBase import AiServicesBase

class ClaudeService(AiServicesBase):
    def __init__(self, chat_id: str, history: list[dict]):
        super().__init__(chat_id, history)
