from dataclasses import dataclass
from typing import Callable
from src.services.GameState import GameState
from src.services.AiServicesBase import AiServicesBase

function = Callable[[], str]



@dataclass
class Action:
    id: str
    message: str
    functions: list[function]
    response: str
    done: bool
    error: str
    success: bool
    game_state: GameState
    next_game_state: GameState
    ai_service: AiServicesBase
    timestamp: str


    def __init__(self, id: str, message: str, functions: list[function]):
        self.id = id
        self.message = message
        self.functions = functions
        self.timestamp = ""
        self.response = ""
        self.done = False
        self.error = ""
        self.success = False
        self.game_state = None
        self.next_game_state = None
        self.ai_service = None
