from dataclasses import dataclass
from typing import override
from database.fileManager import Savable
from core.settings import AIConfig, GameConfig
from src.services.Utils import format_request
from src.services.aiServices.wrapper import AIWrapper
from src.services.AiServicesBase import AiServicesBase
from schema.playerModel import PlayerModel, PlayerValuesModel

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
    @override
    def save(self) -> str:
        # Create PlayerValuesModel for validation
        values_model = PlayerValuesModel(money=self.money, health=self.health)
        return Savable.toJSON(values_model.model_dump())
    
    @override
    def load(self, loaded_data: str | dict):
        loaded_data = loaded_data if isinstance(loaded_data, dict) else Savable.fromJSON(loaded_data)
        
        # Validate with PlayerValuesModel
        try:
            values_model = PlayerValuesModel(**loaded_data)
            self.money = values_model.money
            self.health = values_model.health
        except Exception as e:
            raise ValueError(f"Invalid player values data: {str(e)}")

PLAYER_CLASSES = {
    "human" : PlayerClass("human","A very below average human being.")
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
            return
        self.position = (self.position[0]+change[0],self.position[1]+change[1])
    #endregion

    @override
    def save(self) -> str:
        """Save player as JSON string. Players are stored in game state, not in separate database table."""
        # Create PlayerModel for validation
        player_data = {
            "uid": self.UID,
            "position": list(self.position),
            "model": self.model,
            "player_class": self.player_class.name,
            "values": Savable.fromJSON(self.values.save()),
            "responses": list(getattr(self, "_responses", []))
        }
        
        # Validate with PlayerModel
        player_model = PlayerModel(**player_data)
        
        # Return JSON string for compatibility
        return Savable.toJSON(player_model.model_dump())
    
    @override
    def load(self, loaded_data: dict | str | None = None, player_id: str | None = None):
        """Load player from data dict or JSON string. Players are loaded from game state, not database."""
        # Handle string input
        if isinstance(loaded_data, str):
            loaded_data = Savable.fromJSON(loaded_data)
        
        if not loaded_data:
            raise ValueError("No data provided to load")
        
        # Handle legacy field names (UID -> uid)
        if 'UID' in loaded_data and 'uid' not in loaded_data:
            loaded_data['uid'] = loaded_data['UID']
        
        # Validate with PlayerModel
        try:
            player_model = PlayerModel(**loaded_data)
        except Exception as e:
            raise ValueError(f"Invalid player data format: {str(e)}")
        
        # Load basic properties
        self.position = tuple(player_model.position)
        self.UID = player_model.uid
        self.model = player_model.model
        
        # Load player class
        cls_key = player_model.player_class
        self.player_class = PLAYER_CLASSES.get(cls_key, PLAYER_CLASSES["human"])
        
        # Load values
        self.values = PlayerValues()
        self.values.load(Savable.toJSON(player_model.values.model_dump()))
        
        # Load responses
        self._responses = list(player_model.responses)