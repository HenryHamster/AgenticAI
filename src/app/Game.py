#Handles game logic and loop
from src.app.Player import Player
from src.app.Tile import Tile
from src.database.fileManager import FileManager, Savable
from src.app.DungeonMaster import DungeonMaster
from typing import override
import json
from src.services.responseParser.dataModels import GameResponse, CharacterState, WorldState
import asyncio
from src.core.settings import GameConfig

class Game(Savable):
    players: dict[str,Player]
    dm: DungeonMaster
    file_manager: FileManager
    tiles: dict[tuple[int,int],Tile]

    def __init__(self, player_info:dict[str,dict], dm_info:dict | None = None):
        self.dm = DungeonMaster()
        self.dm.load(dm_info if dm_info is not None else {})
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
    def step(self):
        player_responses, verdict = [], ""
        sorted_uids = sorted(self.players.keys())
        for _ in range(GameConfig.num_responses):
            player_responses = {
                UID: self.players[UID].get_action({"Self":self.players[UID].save(), "Players (excluding self)": {id: self.players[id].save() for id in sorted_uids if id != UID}, "tiles": self._get_viewable_tiles_payload(self.players[UID].position, GameConfig.player_vision),
                              "verdict": verdict, "uid": UID, "position": self.players[UID].position})
                for UID in sorted_uids
            }
            verdict = self.dm.respond_actions({"Players": {UID: self.players[UID].save() for UID in sorted_uids},"Responses": player_responses, "Past Verdict": verdict})    
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
    def handle_verdict(self, verdict: GameResponse | dict | str | None):
        """
        Apply a DM verdict to game state.
        - Accepts GameResponse (pydantic), dict-like, or JSON string.
        - Supports multiple players via CharacterState entries keyed by uid.
        - Ignores/records unknown or false UIDs without raising.
        - Clamps negative money/health to 0.
        - Applies world_state tile updates when present.
        """
        if verdict is None:
            return

        # --- Coerce input into a GameResponse safely (pydantic v1/v2 compatible) ---
        def _pyd_parse_dict(model_cls, data: dict):
            # v2: model_validate, v1: parse_obj
            if hasattr(model_cls, "model_validate"):
                return model_cls.model_validate(data)  # pydantic v2
            return model_cls.parse_obj(data)          # pydantic v1

        def _pyd_parse_json(model_cls, data: str):
            # v2: model_validate_json, v1: parse_raw
            if hasattr(model_cls, "model_validate_json"):
                return model_cls.model_validate_json(data)  # pydantic v2
            return model_cls.parse_raw(data)                # pydantic v1

        parsed: GameResponse | None = None
        try:
            if isinstance(verdict, GameResponse):
                parsed = verdict
            elif isinstance(verdict, dict):
                parsed = _pyd_parse_dict(GameResponse, verdict)
            elif isinstance(verdict, str) and verdict.strip():
                parsed = _pyd_parse_json(GameResponse, verdict)
        except Exception as E:
            raise ValueError(f"Failed to parse verdict into GameResponse: {E}.")

        if parsed is None or not isinstance(getattr(parsed, "character_state", None), list):
            return #Don't throw errors if state is empty

        # --- Apply per-player character updates ---
        unknown_uids: list[str] = []
        for cs in parsed.character_state:
            # Tolerate entries that aren't CharacterState (e.g., dicts)
            try:
                if not isinstance(cs, CharacterState):
                    cs = _pyd_parse_dict(CharacterState, cs if isinstance(cs, dict) else cs.__dict__)
            except Exception:
                continue

            uid = getattr(cs, "uid", None)
            if not uid or uid == "INVALID":
                print(f"[handle_verdict] Ignored CharacterState with missing/invalid UID: {cs}")
                continue

            player = self.players.get(uid)
            if player is None:
                unknown_uids.append(uid)
                continue

            # Position (len 2, ints). Fall back to current if malformed.
            try:
                pos_raw = list(getattr(cs, "position_change", []))
                if len(pos_raw) >= 2:
                    new_pos = (int(pos_raw[0]), int(pos_raw[1]))
                else:
                    new_pos = (0,0)
            except Exception:
                new_pos = (0,0)

            # Money/Health (clamp to >= 0). Keep current if absent.
            try:
                money = getattr(cs, "money_change", player.values.money)
            except Exception:
                money = 0

            try:
                health = getattr(cs, "health_change", player.values.health)
            except Exception:
                health = 0

            player.update_position(new_pos)
            player.values.update_money(money)
            player.values.update_health(health)

        if unknown_uids:
            print(f"[handle_verdict] Ignored unknown UIDs: {sorted(set(unknown_uids))}")

        # --- Apply world updates to tiles if provided ---
        ws = getattr(parsed, "world_state", None)
        tiles_payload = getattr(ws, "tiles", None) if ws else None
        if tiles_payload:
            for td in tiles_payload:
                try:
                    if isinstance(td, dict):
                        t = Tile.from_dict(td)
                    else:
                        # Attribute-style fallback
                        pos_attr = list(getattr(td, "position")) #Throw exception when invalid position
                        desc_attr = getattr(td, "description", "")
                        t = Tile.from_dict({"position": pos_attr, "description": desc_attr})
                    self.tiles[(t.position[0], t.position[1])].update_description(t.description)
                except Exception:
                    continue
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
