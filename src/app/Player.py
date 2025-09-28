from dataclasses import dataclass
from typing import overload,override
from src.database.fileManager import Savable
from src.services.AiServicesBase import AiServicesBase #Using base temporarily, I assume we'll have a wrapper in the future which can pass in the right model
@dataclass(frozen=True, slots=True)
class PlayerClass:
    name: str
    description: str

class PlayerValues(Savable):
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

    @override
    def save(self) -> str:
        return Savable.toJSON({"money": self.money, "health": self.health})
    @override
    def load(self,loaded_data:str | dict):
        loaded_data = loaded_data if isinstance(loaded_data, dict) else Savable.fromJSON(loaded_data)
        self.money = loaded_data["money"]
        self.health = loaded_data["health"]

PLAYER_CLASSES = {
    "human" : PlayerClass("human","Just an average human being.")
}

class Player(Savable):
    model: AiServicesBase
    values: PlayerValues
    player_class: PlayerClass
    position: tuple[int,int]
    _responses: list[str]
    def __init__(self, position:tuple[int,int] = (0,0), player_class: str = "human", model:str = "GPT4o"):
        self.model = AiServicesBase() #Temporary base model instantiation
        self.position = position
        if player_class not in PLAYER_CLASSES:
            raise ValueError(f"Invalid player class {player_class}")
        self.player_class = PLAYER_CLASSES[player_class]

        self.values = PlayerValues()
        self._responses = []
    async def get_action(self,context):
        response = await self.model.ask_ai_response(context) #Assumes wrapper will have some additional context prompting
        self._responses.append(response)
        return response
    
    @override
    def save(self) -> str:
        data = {
            "position": list(self.position),  # JSON-friendly
            "player_class": self.player_class.name,          # store the key, not the object
            "values": Savable.fromJSON(self.values.save()),  # dict, not string
            "responses": list(getattr(self, "_responses", [])),
        }
        return Savable.toJSON(data)
    @override
    def load(self, loaded_data: dict | str):
        loaded_data = loaded_data if isinstance(loaded_data, dict) else Savable.fromJSON(loaded_data)
        self.position = tuple(loaded_data.get("position", (0, 0)))

        # player_class by key (fallback to "human" if unknown)
        cls_key = loaded_data.get("player_class", "human")
        self.player_class = PLAYER_CLASSES.get(cls_key, PLAYER_CLASSES["human"])

        # values (accept dict or, defensively, a JSON string)
        v = loaded_data.get("values", {"money": 0, "health": 100})
        if isinstance(v, str):  # tolerate older saves
            v_dict = Savable.fromJSON(v)
        else:
            v_dict = v

        # PlayerValues.load expects a JSON string
        self.values = getattr(self, "values", PlayerValues())
        self.values.load(Savable.toJSON(v_dict))

        # responses
        self._responses = list(loaded_data.get("responses", []))