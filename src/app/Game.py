#Handles game logic and loop
from src.app.Player import Player
from src.app.Tile import Tile
from src.database.fileManager import FileManager, Savable
from src.app.DungeonMaster import DungeonMaster
from typing import override,overload
import json
import asyncio
from src.app.config import NUM_RESPONSES, PLAYER_NUM, WORLD_SIZE, PLAYER_VISION

class Game(Savable):
    players: dict[str,Player]
    dm: DungeonMaster
    file_manager: FileManager
    tiles: dict[tuple[int,int],Tile]

    def __init__(self, player_info:dict[str,dict]):
        self.dm = DungeonMaster()
        self.file_manager = FileManager()
        self.players = {}
        for uid, pdata in player_info.items():
            if not isinstance(pdata, dict):
                raise ValueError(f"Player info for {uid} must be a dict, got {type(pdata)}")
            p = Player(uid)
            p.load(pdata)
            if p.UID != uid:
                p.UID = uid  # enforce key ↔ object UID consistency
            self.players[uid] = p
        self.tiles = {(i, j): self.dm.generate_tile((i,j)) for i in range(-WORLD_SIZE, WORLD_SIZE + 1) for j in range(-WORLD_SIZE, WORLD_SIZE + 1)}
    async def step(self):
        player_responses, verdict = [], ""
        sorted_uids = sorted(self.players.keys())
        for _ in range(NUM_RESPONSES):
            player_responses = await asyncio.gather(*[
                self.players[UID].get_action({"Tiles": self.get_viewable_tiles(self.players[UID].position, PLAYER_VISION),
                              "Verdict": verdict, "UID": UID, "Position": self.players[UID].position})
                for UID in sorted_uids
            ]) #return_exception = True
            verdict = await self.dm.respond_actions({"Responses": player_responses, "Verdict": verdict})    
        self.handle_verdict(verdict)
    @override
    def save(self) -> str:
        return Savable.toJSON({
            "players": {UID: Savable.fromJSON(self.players[UID].save()) for UID in self.players.keys()},  # list of dicts
            "dm": Savable.fromJSON(self.dm.save()),                         # dict
            "tiles": {json.dumps(k): Savable.fromJSON(v.save())             # dict: "[x,y]" -> dict
                    for k, v in self.tiles.items()}
        })
    
    @override
    def load(self, loaded_data: dict | str):
        loaded_data = loaded_data if isinstance(loaded_data, dict) else Savable.fromJSON(loaded_data)
        self.players = {}
        for UID, pdata in loaded_data["players"].items():
            if not isinstance(pdata, dict):
                raise ValueError(f"Player data for {UID} must be a dict, got {type(pdata)}")
            if UID is None or UID == "INVALID":
                raise ValueError("Player UID is missing or invalid in loaded data.")
            p = Player(UID)
            p.load(pdata)
            self.players[UID] = p

        # dm
        self.dm = DungeonMaster()     # or your concrete type
        self.dm.load(loaded_data["dm"])

        # tiles
        self.tiles = {}
        for k_str, vdata in loaded_data["tiles"].items():
            key = tuple(json.loads(k_str))  # back to tuple
            tile = Tile()
            tile.load(vdata)
            if tile.position != key:
                tile.position = key
                print("Tiles possibly corrupted: position and key don't match.")
            self.tiles[key] = tile

    def get_viewable_tiles(self,position:tuple[int,int], vision:int = 1) -> list[Tile]:
        tiles = []
        for x in range(-vision,vision+1):
            for y in range(-vision+x,vision-x+1):
                tiles.append(self.get_tile((position[0]+x,position[1]+y)))
        return tiles
    def get_tile(self, position: tuple[int,int]) -> Tile:
        if abs(position[0]) > WORLD_SIZE or abs(position[1]) > WORLD_SIZE:
            return Tile("This is an invalid tile. You cannot interact with or enter this tile.", position=position)
        if position not in self.tiles:
            self.tiles[position] = self.dm.generate_tile(position)
        return self.tiles[position]
    def handle_verdict(self,verdict:str):
        pass