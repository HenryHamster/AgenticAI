from dataclasses import dataclass
from typing_extensions import override
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
    inventory: list[str]
    def __init__(self, money:int = 0, health:int = 100, player = None, inventory: list[str] | None = None):
        if money < 0 or health < 0:
            raise ValueError("Money and health must be positive.")
        self.money = money
        self.health = health
        self.inventory = inventory if inventory is not None else []
        self.player = player
    def update_money(self, change: int):
        self.money = max(self.money+change,0)
        if self.money < 0:
            raise ValueError("Money is below zero.")
    def update_health(self, change: int):
        self.health = max(self.health+change,0)
        if self.health <= 0 and self.player:
            self.player.handle_death()
    def add_inventory(self, items: list[str]):
        """Add items to inventory."""
        self.inventory.extend(items)
    def remove_inventory(self, items: list[str]):
        """Remove one instance of each item from inventory. Logs warning if item doesn't exist."""
        for item in items:
            try:
                self.inventory.remove(item)
            except ValueError:
                print(f"[PlayerValues] Warning: Attempted to remove item '{item}' that doesn't exist in inventory.")
    @override
    def save(self) -> str:
        # Create PlayerValuesModel for validation
        values_model = PlayerValuesModel(money=self.money, health=self.health, inventory=self.inventory)
        return Savable.toJSON(values_model.model_dump())
    
    @override
    def load(self, loaded_data: str | dict):
        loaded_data = loaded_data if isinstance(loaded_data, dict) else Savable.fromJSON(loaded_data)
        
        # Validate with PlayerValuesModel
        try:
            values_model = PlayerValuesModel(**loaded_data)
            self.money = values_model.money
            self.health = values_model.health
            self.inventory = getattr(values_model, "inventory", [])
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
    _negotiation_messages: list[str]
    def __init__(self, UID, position:tuple[int,int] = (0,0), player_class: str = "human", model:str = "gpt-4.1-mini", chat_id:str = "DefaultID"): #Force UID to exist
        self.model = model
        self.UID = UID
        self.position = position
        self.agent_prompt: str = ""
        if player_class not in PLAYER_CLASSES:
            raise ValueError(f"Invalid player class {player_class}")
        self.player_class = PLAYER_CLASSES[player_class]

        self.values = PlayerValues(player=self)
        self._responses = []
        self._negotiation_messages = []
    def _augment_prompt(self, base_prompt: str) -> str:
        if getattr(self, "agent_prompt", ""):
            extra = self.agent_prompt.strip()
            if extra:
                return f"{base_prompt}\n\nAgent-specific instructions:\n{extra}"
        return base_prompt
    def is_dead(self) -> bool:
        """Check if the player is dead (health <= 0)."""
        return self.values.health <= 0
    
    def handle_death(self) -> None:
        """
        Handle player death: convert money to secret on tile and set money to 0.
        This is called when the player dies to immediately remove their wealth.
        """
        self.values.money = 0
        print(f"[Player] {self.UID} died at {self.position}.")
    def get_negotiation_message(self, context: dict) -> str:
        """Get a negotiation message during the planning phase. This is discussion only, not a final action."""
        if self.is_dead():
            return "This player is dead."
        prompt = self._augment_prompt(AIConfig.negotiation_prompt)
        response = AIWrapper.ask(format_request(prompt, context), self.model, self.UID)
        self._negotiation_messages.append(response)
        return response
    def get_action(self,context: dict) -> str:
        if self.is_dead():
            return "This player is dead."
        prompt = self._augment_prompt(AIConfig.player_prompt)
        response = AIWrapper.ask(format_request(prompt, context), self.model,self.UID)
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
    def get_negotiation_history(self) -> list[str]:
        return self._negotiation_messages
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
            "responses": (
                [self._responses[-1]] if getattr(self, "_responses", None) else []
            ),
            "agent_prompt": getattr(self, "agent_prompt", ""),
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
        self.agent_prompt = getattr(player_model, "agent_prompt", "")
        
        # Load player class
        cls_key = player_model.player_class
        self.player_class = PLAYER_CLASSES.get(cls_key, PLAYER_CLASSES["human"])
        
        # Load values
        self.values = PlayerValues(player=self)
        self.values.load(Savable.toJSON(player_model.values.model_dump()))
        
        # Load responses
        self._responses = list(player_model.responses)
        
        # Initialize negotiation messages (not persisted, so always start fresh)
        if not hasattr(self, '_negotiation_messages'):
            self._negotiation_messages = []