#Handles game logic and loop
from src.app.Player import Player
from src.app.Tile import Tile
from src.database.fileManager import FileManager, Savable
from src.app.DungeonMaster import DungeonMaster
from typing import override
import json
import asyncio
from src.core.settings import GameConfig

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
        self.tiles = {(i, j): self.dm.generate_tile((i,j)) for i in range(-GameConfig.world_size, GameConfig.world_size + 1) for j in range(-GameConfig.world_size, GameConfig.world_size + 1)}
    async def step(self):
        player_responses, verdict = [], ""
        sorted_uids = sorted(self.players.keys())
        for _ in range(GameConfig.num_responses):
            player_responses = await asyncio.gather(*[
                self.players[UID].get_action({"tiles": self._get_viewable_tiles_payload(self.players[UID].position, GameConfig.player_vision),
                              "verdict": verdict, "uid": UID, "position": self.players[UID].position})
                for UID in sorted_uids
            ]) #return_exception = True
            verdict = await self.dm.respond_actions({"Responses": player_responses, "Verdict": verdict})    
        self.handle_verdict(verdict)
    @staticmethod
    def _tile_payload(tile: Tile) -> dict:
        """Plain-Python view of a tile for prompts/serialization."""
        return tile.to_dict()
    
    @override
    def save(self) -> str:
        return Savable.toJSON({
            "players": {UID: Savable.fromJSON(self.players[UID].save()) for UID in self.players.keys()},  # list of dicts
            "dm": Savable.fromJSON(self.dm.save()),                         # dict
            "tiles": [t.to_dict() for t in self.tiles.values()]
        })
    
    @override
    def load(self, loaded_data: dict | str):
        loaded_data = loaded_data if isinstance(loaded_data, dict) else Savable.fromJSON(loaded_data)
        self.players = {}
        for UID, pdata in loaded_data.get("players", {}).items():
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
        tiles_map: dict[tuple[int, int], Tile] = {}
        for td in loaded_data.get("tiles", []):
            t = Tile.from_dict(td)
            tiles_map[(t.position[0], t.position[1])] = t
        self.tiles = tiles_map

    def get_viewable_tiles(self,position:tuple[int,int], vision:int = 1) -> list[Tile]:
        tiles = []
        for x in range(-vision,vision+1):
            for y in range(-vision+x,vision-x+1):
                tiles.append(self.get_tile((position[0]+x,position[1]+y)))
        return tiles
    def _get_viewable_tiles_payload(self,position:tuple[int,int], vision:int = 1) -> list[dict]:
        return [self._tile_payload(t) for t in self.get_viewable_tiles(position, vision)]
    def handle_verdict(self,verdict:str):
        raise NotImplementedError("handle_verdict must be implemented.")
    #Accessor functions
    def get_tile(self, position: tuple[int,int]) -> Tile:
        if abs(position[0]) > GameConfig.world_size or abs(position[1]) > GameConfig.world_size:
            return Tile("This is an invalid tile. You cannot interact with or enter this tile.", position=position)
        if position not in self.tiles:
            self.tiles[position] = self.dm.generate_tile(position)
        return self.tiles[position]
    def get_all_tiles(self) -> dict[tuple[int,int],Tile]:   
        return self.tiles   
    def get_player(self, UID: str) -> Player:   
        return self.players[UID]
    def get_all_players(self) -> dict[str,Player]:  
        return self.players
    def get_dm(self) -> DungeonMaster:  
        return self.dm