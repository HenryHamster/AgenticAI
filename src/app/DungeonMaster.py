from src.app.Tile import Tile
class DungeonMaster:
    def __init__(self, model:str = "GPT4o"):
        pass
    def generate_tile(self):
        generated_description = "INSERT SOME API CALL w/ context"
        return Tile(generated_description)
    def update_tile(self, tile: Tile, event):
        tile.description = "INSERT SOME API CALL w/ context"
    def respond_actions(self, actions: list[str]):
        pass