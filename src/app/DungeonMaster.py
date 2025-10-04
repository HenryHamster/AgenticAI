from src.app.Tile import Tile
from src.database.fileManager import Savable
from typing import override
class DungeonMaster(Savable):
    model:str
    def __init__(self, model: str = "GPT4o", loaded_data: dict | None = None):
        self.model = model
        if loaded_data is not None:
            self.load(loaded_data)
    def generate_tile(self, position:tuple[int,int] = (0,0)):
        generated_description = "INSERT SOME API CALL w/ context"
        return Tile(generated_description, position)
    def update_tile(self, tile: Tile, event: str):
        tile.update_description("INSERT SOME API CALL w/ context and event to generate new tile description")
    async def respond_actions(self, info: dict) -> str:
        raise Exception("Response not implemented.")
    @override
    def save(self):
        return Savable.toJSON({"model": self.model})
    @override
    def load(self, loaded_data):
        if isinstance(loaded_data, str):
            loaded_data = Savable.fromJSON(loaded_data)
        self.model = loaded_data.get("model", self.model)
