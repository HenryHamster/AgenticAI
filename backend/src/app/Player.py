from dataclasses import dataclass
from typing import Optional, Dict, List
from typing_extensions import override
from database.fileManager import Savable
from core.settings import AIConfig, GameConfig
from src.services.Utils import format_request
from src.services.aiServices.wrapper import AIWrapper
from src.services.AiServicesBase import AiServicesBase
from schema.playerModel import PlayerModel, PlayerValuesModel
from schema.characterModel import CharacterTemplate, load_character_template, CharacterState as CharState

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
    UID: str
    values: PlayerValues
    player_class: PlayerClass
    position: tuple[int,int]
    _responses: list[str]
    character_template: Optional[CharacterTemplate]
    character_template_name: Optional[str]  # Store the template name for serialization
    current_abilities: List[str]
    resource_pools: Dict[str, int]
    skill_cooldowns: Dict[str, int]
    experience: int
    level: int
    invalid_action_count: int
    total_action_count: int
    _negotiation_messages: list[str]


    def __init__(self, UID, position:tuple[int,int] = (0,0), player_class: str = "human", model:str = "gpt-4.1-mini", chat_id:str = "DefaultID", character_template_name: Optional[str] = None, **kwargs):
        self.model = model
        self.UID = UID
        self.position = position
        self.agent_prompt: str = ""
        if player_class not in PLAYER_CLASSES:
            raise ValueError(f"Invalid player class {player_class}")
        self.player_class = PLAYER_CLASSES[player_class]

        self.values = PlayerValues(player=self)
        self._responses = []

        self.character_template = None
        self.character_template_name = character_template_name  # Store the template name
        self.current_abilities = []
        self.resource_pools = {}
        self.skill_cooldowns = {}
        self.experience = 0
        self.level = 1
        self.invalid_action_count = 0
        self.total_action_count = 0
        self._negotiation_messages = []

        if character_template_name:
            try:
                self.character_template = load_character_template(character_template_name)
                self.current_abilities = self.character_template.get_level_1_abilities()
                self.resource_pools = self.character_template.resource_pools.copy()
                for item in self.character_template.starting_equipment:
                    self.values.add_inventory([item])
            except Exception as e:
                print(f"[Player] Warning: Could not load character template '{character_template_name}': {e}")
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
        response = ""
        if self.character_template:
            enriched_context = self._enrich_context_with_character_data(context)
            response = AIWrapper.ask(format_request(prompt, enriched_context), self.model, self.UID)
        else:
            response = AIWrapper.ask(format_request(prompt, context), self.model, self.UID)
        self._responses.append(response)
        return response

    def _enrich_context_with_character_data(self, context: dict) -> dict:
        if not self.character_template:
            return context

        enriched = context.copy()
        enriched['character_name'] = self.UID
        enriched['race'] = self.character_template.race
        enriched['character_class'] = self.character_template.character_class
        enriched['current_level'] = self.level

        attrs = self.character_template.base_attributes
        for attr in ['STR', 'DEX', 'INT', 'WIS', 'CON', 'CHA']:
            val = getattr(attrs, attr)
            enriched[attr] = val
            enriched[f'{attr}_mod'] = attrs.get_modifier(attr)

        resource_lines = []
        for resource, amount in self.resource_pools.items():
            resource_lines.append(f"  - {resource}: {amount}")
        enriched['resource_status'] = '\n'.join(resource_lines) if resource_lines else "  - No special resources"

        return enriched

    def unlock_skill(self, skill_name: str):
        if skill_name not in self.current_abilities:
            self.current_abilities.append(skill_name)
            print(f"[Player {self.UID}] Unlocked skill: {skill_name}")

    def check_level_up(self) -> Optional[List[str]]:
        if not self.character_template:
            return None

        XP_THRESHOLDS = [
            0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
            85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
        ]

        if self.level >= 20:
            return None

        if self.experience >= XP_THRESHOLDS[self.level]:
            self.level += 1
            attrs = self.character_template.base_attributes
            newly_unlocked = self.character_template.get_available_skills(
                self.level, self.current_abilities, attrs
            )
            new_skill_names = [skill.name for skill in newly_unlocked]

            for skill_name in new_skill_names:
                self.unlock_skill(skill_name)

            return new_skill_names

        return None

    def update_resources(self, changes: Dict[str, int]):
        for resource, change in changes.items():
            current = self.resource_pools.get(resource, 0)
            self.resource_pools[resource] = max(0, current + change)

    def update_cooldowns(self, turn_delta: int = 1):
        for skill in list(self.skill_cooldowns.keys()):
            self.skill_cooldowns[skill] = max(0, self.skill_cooldowns[skill] - turn_delta)
            if self.skill_cooldowns[skill] == 0:
                del self.skill_cooldowns[skill]

    def set_cooldown(self, skill_name: str, turns: int):
        if turns > 0:
            self.skill_cooldowns[skill_name] = turns
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
        player_data = {
            "uid": self.UID,
            "position": list(self.position),
            "model": self.model,
            "player_class": self.player_class.name,
            "values": Savable.fromJSON(self.values.save()),
            "responses": list(getattr(self, "_responses", [])),
            "character_template_name": self.character_template_name,  # Use the stored template name
            "current_abilities": list(self.current_abilities),
            "resource_pools": dict(self.resource_pools),
            "skill_cooldowns": dict(self.skill_cooldowns),
            "experience": self.experience,
            "level": self.level,
            "invalid_action_count": self.invalid_action_count,
            "total_action_count": self.total_action_count,
            "agent_prompt": getattr(self, "agent_prompt", "")
        }

        player_model = PlayerModel(**player_data)
        return Savable.toJSON(player_model.model_dump())
        
    def get_open_context(self) -> dict:
        """Get the open (visible to other players) context for the player."""
        open_context = {
            "uid": self.UID,
            "position": list(self.position),
            "player_class": self.player_class.name,
            "values": Savable.fromJSON(self.values.save()),
            "responses": self._responses[-1] if self._responses else ""
        }
        return open_context
    @override
    def load(self, loaded_data: dict | str | None = None, player_id: str | None = None):
        """Load player from data dict or JSON string. Players are loaded from game state, not database."""
        if isinstance(loaded_data, str):
            loaded_data = Savable.fromJSON(loaded_data)

        if not loaded_data:
            raise ValueError("No data provided to load")

        if 'UID' in loaded_data and 'uid' not in loaded_data:
            loaded_data['uid'] = loaded_data['UID']

        try:
            player_model = PlayerModel(**loaded_data)
        except Exception as e:
            raise ValueError(f"Invalid player data format: {str(e)}")

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

        # Store the template name
        self.character_template_name = player_model.character_template_name
        
        if player_model.character_template_name:
            try:
                self.character_template = load_character_template(player_model.character_template_name)
            except Exception as e:
                print(f"[Player] Warning: Could not load character template '{player_model.character_template_name}': {e}")
                self.character_template = None
        else:
            self.character_template = None

        self.current_abilities = list(player_model.current_abilities)
        self.resource_pools = dict(player_model.resource_pools)
        self.skill_cooldowns = dict(player_model.skill_cooldowns)
        self.experience = player_model.experience
        self.level = player_model.level
        self.invalid_action_count = getattr(player_model, 'invalid_action_count', 0)
        self.total_action_count = getattr(player_model, 'total_action_count', 0)
        # Load responses
        self._responses = list(player_model.responses)
        
        # Initialize negotiation messages (not persisted, so always start fresh)
        if not hasattr(self, '_negotiation_messages'):
            self._negotiation_messages = []



