from dataclasses import dataclass
from src.services.AiServicesBase import AiServicesBase #Using base temporarily, I assume we'll have a wrapper in the future which can pass in the right model
@dataclass
class PlayerClass:
    description: str
    def __init__(self, description):
        self.description=description

@dataclass
class PlayerValues:
    money: int
    health: int
    def __init__(self, money:int = 0, health:int = 100):
        if money < 0 or health < 0:
            raise ValueError("Money and health must be positive.")
        self.money = money
        self.health = health
    def update_money(self, change: int):
        self.money = max(self.money+change,0)
    def update_health(self, change: int):
        self.health = max(self.health+change,0)

PLAYER_CLASSES = {
    "human" : PlayerClass("Just an average human being.")
}

class Player:
    model: AiServicesBase
    values: PlayerValues
    player_class: PlayerClass
    position: tuple
    _responses: list[str]
    def __init__(self, position:tuple, player_class: str, model:str = "GPT4o"):
        self.model = AiServicesBase() #Temporary base model instantiation
        self.position = position
        self.player_class = PLAYER_CLASSES[player_class]
        self.values = PlayerValues()
    async def get_action(self,context):
        response = await self.model.ask_ai_response(context) #Assumes wrapper will have some additional context prompting
        self._responses.append(response)
        return response
