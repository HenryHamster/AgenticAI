from src.app.Tile import Tile
from database.fileManager import Savable
from src.services.Utils import format_request
from src.services.aiServices.wrapper import AIWrapper
from api.apiDtoModel import GameResponse
from core.settings import AIConfig
from typing import override
from schema.tileModel import TileModel

class DungeonMaster(Savable):
    model:str
    _responses: list[str]
    def __init__(self, model: str = "gpt-4.1-nano", loaded_data: dict | None = None):
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
        structured_response = AIWrapper.ask(
            format_request(AIConfig.dm_prompt, info), 
            self.model, 
            "DungeonMaster", 
            structured_output = GameResponse
            )
        self._responses.append(str(structured_response))
        return structured_response
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
