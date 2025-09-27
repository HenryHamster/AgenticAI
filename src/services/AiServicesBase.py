# dataclass for Ai Services. This will be used to create a base class for all Ai Services. Having the base methods
# will allow for easy extension and reuse of the Ai Services.
# possibly add create with the history of another AiService

from dataclasses import dataclass
from src.services.Action import Action

@dataclass
class AiServicesBase:
    chat_id: str
    history: list[dict]

    def __init__(self, chat_id: str, history: list[dict]):
        self.chat_id = chat_id
        self.history = history

    def ask_ai_response(self, action: Action):

        pass

    def delete_chat(self):
        pass

    def reset_history(self):
        pass

    def get_history(self):
        pass
