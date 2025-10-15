from dataclasses import dataclass
from src.database.fileManager import Savable
from src.core.settings import AIConfig, GameConfig
from src.app.Utils import format_request
from src.services.aiServices.wrapper import AIWrapper
from src.services.AiServicesBase import AiServicesBase

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
        if self.money < 0:
            raise ValueError("Money is below zero.")
    def update_health(self, change: int):
        self.health = max(self.health+change,0)
    def save(self) -> str:
        return Savable.toJSON({"money": self.money, "health": self.health})
    def load(self,loaded_data:str | dict):
        loaded_data = loaded_data if isinstance(loaded_data, dict) else Savable.fromJSON(loaded_data)
        self.money = loaded_data["money"]
        self.health = loaded_data["health"]

PLAYER_CLASSES = {
    "human" : PlayerClass("human","A confident, exceptionally powerful human being.")
}

class Player(Savable):
    model: str
    UID: str #User ID (string)
    values: PlayerValues
    player_class: PlayerClass
    position: tuple[int,int]
    _responses: list[str]
    def __init__(self, UID, position:tuple[int,int] = (0,0), player_class: str = "human", model:str = "gpt-4.1-nano", chat_id:str = "DefaultID"): #Force UID to exist
        self.model = model
        self.UID = UID
        self.position = position
        if player_class not in PLAYER_CLASSES:
            raise ValueError(f"Invalid player class {player_class}")
        self.player_class = PLAYER_CLASSES[player_class]

        self.values = PlayerValues()
        self._responses = []
    def get_action(self,context: dict) -> str:
        response = AIWrapper.ask(format_request(AIConfig.player_prompt, context), self.model,self.UID)
        self._responses.append(response)
        return response
    #region: Accessor functions
    def get_UID(self) -> str:
        return self.UID
    def get_position(self) -> tuple[int,int]:
        return self.position
    def get_model(self) -> AiServicesBase:
        return AIWrapper._get_service(self.model,self.UID)
    def get_class(self) -> PlayerClass:
        return self.player_class
    def get_responses_history(self) -> list[str]:
        return self._responses
    def get_values(self) -> PlayerValues:
        return self.values
    #endregion
    #region: Modifier functions
    def update_position(self, change: tuple[int,int]):
        if (self.position[0]+change[0] < -GameConfig.world_size or self.position[0]+change[0] > GameConfig.world_size or
            self.position[1]+change[1] < -GameConfig.world_size or self.position[1]+change[1] > GameConfig.world_size):
            raise ValueError("Position change out of world bounds.")
        self.position = (self.position[0]+change[0],self.position[1]+change[1])
    #endregion

    def save(self) -> str:
        data = {
            "position": list(self.position),  # JSON-friendly
            "UID": self.UID,
            "model": self.model,
            "player_class": self.player_class.name,          # store the key, not the object
            "values": Savable.fromJSON(self.values.save()),  # dict, not string
#            "responses": list(getattr(self, "_responses", [])),
        }
        return Savable.toJSON(data)
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
        self.UID = loaded_data.get("UID", "INVALID")
        self.model = loaded_data.get("model", "INVALID")
        self.values = getattr(self, "values", PlayerValues())
        self.values.load(Savable.toJSON(v_dict))

        # responses
#        self._responses = list(loaded_data.get("responses", []))