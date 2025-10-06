from src.app.Tile import Tile
from src.database.fileManager import Savable
from src.app.Utils import format_request
from src.services.aiServices.wrapper import AIWrapper
from typing import override
class DungeonMaster(Savable):
    model:str
    def __init__(self, model: str = "GPT4o", loaded_data: dict | None = None):
        self.model = model
        if loaded_data is not None:
            self.load(loaded_data)
    def generate_tile(self, position:tuple[int,int] = (0,0)):
        generated_description = AIWrapper.ask(format_request("", {"position": position}), self.model, "DungeonMaster")
        return Tile(generated_description, position)
    def update_tile(self, tile: Tile, event: str):
        tile.update_description(AIWrapper.ask(format_request("", {"current_tile_description": tile.description, "event": event}), self.model, "DungeonMaster"))
    async def respond_actions(self, info: dict) -> str:
        return AIWrapper.ask(format_request("", info), self.model, "DungeonMaster")
    @override
    def save(self):
        return Savable.toJSON({"model": self.model})
    @override
    def load(self, loaded_data):
        if isinstance(loaded_data, str):
            loaded_data = Savable.fromJSON(loaded_data)
        self.model = loaded_data.get("model", self.model)
