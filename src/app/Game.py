#Handles game logic and loop
from src.app.Player import Player
from src.app.Tile import Tile
from src.database.fileManager import FileManager
from src.app.DungeonMaster import DungeonMaster

#region Static Variables
PLAYER_NUM = 1
WORLD_SIZE = 2 #2D
#endregion

class Game:
    #region Variables
    players: list[Player]
    dm: DungeonMaster
    file_manager: FileManager
    tiles: dict[Tile] #Tuple key
    #endregion
    def __init__(self):
        self.dm = DungeonMaster()
        self.file_manager = FileManager()
        self.players = [Player() for _ in range(PLAYER_NUM)]
        self.tiles = {(i, j): self.dm.generate_tile() for i in range(-WORLD_SIZE, WORLD_SIZE + 1) for j in range(-WORLD_SIZE, WORLD_SIZE + 1)}
    def step(self):
        player_responses = [p.get_action({"Tile":self.tiles[p.position]}) for p in self.players]
        verdict = self.dm.respond_actions(player_responses)
        self.handle_verdict(verdict)
        self.save_data()
    def save_data(self):
        self.file_manager.save("game_data", {"players": self.players, "dm": self.dm, "tiles": self.tiles})
        pass
    def handle_verdict(self,verdict:dict):
        pass