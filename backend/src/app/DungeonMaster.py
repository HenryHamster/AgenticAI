from src.app.Tile import Tile
from database.fileManager import Savable
from src.services.Utils import format_request
from src.services.aiServices.wrapper import AIWrapper
from api.apiDtoModel import GameResponse
from core.settings import AIConfig
from typing import Dict, Optional
from typing_extensions import override
from schema.tileModel import TileModel
from schema.characterModel import load_character_template

class DungeonMaster(Savable):
    model:str
    _responses: list[str]
    def __init__(self, model: str = "gpt-4.1-mini", loaded_data: dict | None = None):
        self.model = model
        self._responses = []
        if loaded_data is not None:
            self.load(loaded_data)
    def generate_tile(self, position:tuple[int,int] = (0,0), context: dict | None = None) -> Tile:
        generated_description = AIWrapper.ask(format_request(AIConfig.tile_prompt, {"position": position}), self.model, "DungeonMaster", structured_output = TileModel)
        return Tile(generated_description.description, position, secrets = generated_description.secrets, terrainType=generated_description.terrainType, terrainEmoji=generated_description.terrainEmoji)
    def update_tile(self, tile: Tile, event: str):
        tile.update_description(AIWrapper.ask(format_request(AIConfig.tile_update_prompt, {"current_tile_description": tile.description, "event": event}), self.model, "DungeonMaster"))
    def respond_actions(self, info: dict) -> GameResponse:
        enriched_info = self._enrich_info_with_character_templates(info)
        # print("info:", info)
        # print("enriched_info:", enriched_info)
        # print("formatted info:", format_request(AIConfig.dm_prompt, info))
        structured_response = AIWrapper.ask(
            format_request(AIConfig.dm_prompt, enriched_info),
            self.model,
            "DungeonMaster",
            structured_output = GameResponse
        )
        self._responses.append(str(structured_response))
        return structured_response

    def _enrich_info_with_character_templates(self, info: dict) -> dict:
        enriched = info.copy()

        character_templates = {}
        if 'Players' in info:
            for uid, player_data in info['Players'].items():
                try:
                    if isinstance(player_data, str):
                        import json
                        player_data = json.loads(player_data)

                    template_name = player_data.get('character_template_name')
                    if template_name:
                        template = load_character_template(template_name)
                        character_templates[uid] = {
                            'race': template.race,
                            'character_class': template.character_class,
                            'racial_traits': [
                                {'name': trait.name, 'description': trait.description, 'effect': trait.mechanical_effect}
                                for trait in template.racial_traits
                            ],
                            'base_attributes': template.base_attributes.to_dict(),
                            'all_skills': [
                                {
                                    'name': skill.name,
                                    'description': skill.description,
                                    'unlock_level': skill.unlock_level,
                                    'prerequisites': skill.prerequisites,
                                    'attribute_requirements': skill.attribute_requirements,
                                    'resource_cost': skill.resource_cost,
                                    'cooldown_turns': skill.cooldown_turns,
                                    'effect': skill.effect_description,
                                    'damage_formula': skill.damage_formula
                                }
                                for skill in template.skills
                            ],
                            'current_state': {
                                'level': player_data.get('level', 1),
                                'experience': player_data.get('experience', 0),
                                'current_abilities': player_data.get('current_abilities', []),
                                'resource_pools': player_data.get('resource_pools', {}),
                                'skill_cooldowns': player_data.get('skill_cooldowns', {}),
                                'inventory': player_data.get('values', {}).get('inventory', [])
                            }
                        }
                    else:
                        print(f"[DM] Warning: Player {uid} has no character template")
                except Exception as e:
                    print(f"[DM] Warning: Could not load template for player {uid}: {e}")

        enriched['character_templates'] = character_templates
        return enriched
    def get_responses_history(self) -> list[str]:
        return self._responses
    @override
    def save(self):
        return Savable.toJSON({"model": self.model})
    @override
    def load(self, loaded_data):
        if isinstance(loaded_data, str):
            loaded_data = Savable.fromJSON(loaded_data)
        self.model = loaded_data.get("model", self.model)
