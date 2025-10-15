from src.app.Tile import Tile
from src.database.fileManager import Savable
from src.app.Utils import format_request
from src.services.aiServices.wrapper import AIWrapper
from src.services.responseParser.dataModels import GameResponse
from src.core.settings import AIConfig
class DungeonMaster(Savable):
    model:str
    def __init__(self, model: str = "gpt-4.1-nano", loaded_data: dict | None = None):
        self.model = model
        if loaded_data is not None:
            self.load(loaded_data)
    def generate_tile(self, position:tuple[int,int] = (0,0), context: dict | None = None) -> Tile:
        generated_description = AIWrapper.ask(format_request(AIConfig.tile_prompt, {"position": position}), self.model, "DungeonMaster")
        return Tile(generated_description, position)
    def update_tile(self, tile: Tile, event: str):
        tile.update_description(AIWrapper.ask(format_request(AIConfig.tile_update_prompt, {"current_tile_description": tile.description, "event": event}), self.model, "DungeonMaster"))
    def respond_actions(self, info: dict) -> GameResponse:
        structured_response = AIWrapper.ask(
            format_request(AIConfig.dm_prompt, info), 
            self.model, 
            "DungeonMaster", 
            structured_output = GameResponse
            )
        return structured_response
    def save(self):
        return Savable.toJSON({"model": self.model})
    def load(self, loaded_data):
        if isinstance(loaded_data, str):
            loaded_data = Savable.fromJSON(loaded_data)
        self.model = loaded_data.get("model", self.model)
