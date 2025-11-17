#Handles game logic and loop
from src.app.Player import Player
from src.app.Tile import Tile
from database.fileManager import FileManager, Savable
from src.app.DungeonMaster import DungeonMaster
from src.services.aiServices.wrapper import AIWrapper
from src.app.GameConditions import (
    GameConditionManager,
    MaxTurnsCondition,
    AllPlayersDeadCondition,
    CurrencyGoalCondition
)
from typing_extensions import override
import uuid
from api.apiDtoModel import GameResponse, CharacterState, WorldState
from schema.gameModel import GameModel, GameStateModel
from schema.playerModel import PlayerModel
from schema.tileModel import TileModel
from schema.dungeonMasterModel import DungeonMasterModel
from schema.turnModel import TurnModel
from schema.enums import GameStatus
from services.database.gameService import save_game_to_database, load_game_from_database
from services.database.turnService import save_turn_to_database, get_latest_turn_by_game_id
from core.settings import GameConfig

class Game(Savable):
    players: dict[str,Player]
    dm: DungeonMaster
    tiles: dict[tuple[int,int],Tile]
    current_turn_number: int
    world_size: int
    # Decomposed verdict components
    verdict_character_state: list[CharacterState]
    verdict_world_state: WorldState | None
    verdict_narrative_result: str
    # Game condition management
    condition_manager: GameConditionManager
    is_game_over: bool
    game_over_reason: str | None

    def __init__(self, player_info:dict[str,dict], dm_info:dict | None = None, world_size: int | None = None, verbose_level: int = 0):
        AIWrapper.reset("DungeonMaster")
        self.dm = DungeonMaster()
        self.dm.load(dm_info if dm_info is not None else {})
        self.players = {}
        self.current_turn_number = 0
        # Use provided world_size or fallback to GameConfig default
        self.world_size = world_size if world_size is not None else GameConfig.world_size
        # Verbose level: 0=non-verbose, 1=verbose, 2=full_verbose
        self.verbose_level = verbose_level
        # Initialize verdict components
        self.verdict_character_state = []
        self.verdict_world_state = None
        self.verdict_narrative_result = ""
        self.last_round_history: list[dict[str, Any]] = []
        # Initialize game condition manager
        self.condition_manager = GameConditionManager()
        self.is_game_over = False
        self.game_over_reason = None
        # Add default conditions
        self.condition_manager.add_condition(MaxTurnsCondition())
        self.condition_manager.add_condition(AllPlayersDeadCondition())
        self.condition_manager.add_condition(CurrencyGoalCondition())
        for uid, pdata in player_info.items():
            if not isinstance(pdata, dict):
                raise ValueError(f"Player info for {uid} must be a dict, got {type(pdata)}")
            AIWrapper.reset(uid)
            p = Player(uid)
            p.load(pdata)
            if p.UID != uid:
                p.UID = uid  # enforce key ↔ object UID consistency
            self.players[uid] = p
        self.tiles = {(i, j): self.dm.generate_tile((i,j)) for i in range(-self.world_size, self.world_size + 1) for j in range(-self.world_size, self.world_size + 1)}
        # Reset all AI histories after initialization to ensure clean state
        AIWrapper.reset("DungeonMaster")
        for uid in self.players.keys():
            AIWrapper.reset(uid)
    def step(self):
        # Check if game is already over
        if self.is_game_over:
            print(f"[Game] Game is already over: {self.game_over_reason}")
            return
        
        player_responses, verdict = {}, ""
        negotiation_history: list[dict[str,str]] = []
        sorted_uids = sorted(self.players.keys())
        print(f"narrative: {self.verdict_narrative_result}")
        
        # Negotiation phase: players discuss before committing to actions
        for negotiation_round in range(GameConfig.num_negotiation_rounds):
            negotiation_messages = {
                UID: self.players[UID].get_negotiation_message(
                    self._build_player_context(UID, sorted_uids, negotiation_history)
                )
                for UID in sorted_uids
            }
            negotiation_history.append(negotiation_messages)
            print(f"negotiation_round_{negotiation_round + 1}: {negotiation_messages}")
        
        # Action phase: players commit to final actions after negotiation
        player_responses = {
            UID: self.players[UID].get_action(
                self._build_player_context(UID, sorted_uids, negotiation_history)
            )
            for UID in sorted_uids
        }
        print(f"final_actions: {player_responses}")
        
        verdict = self.dm.respond_actions({"Players": {UID: self.players[UID].save() for UID in sorted_uids},"Responses": player_responses, "Past Verdict": verdict, "tiles": self._get_tiles_full_payload()})    
        self.handle_verdict(verdict)
        self.current_turn_number += 1
        
        # Check win/end conditions after processing the turn
        self._check_game_conditions()
        
        # Print player state after each step
        print(f"\n[Player State] Turn {self.current_turn_number}:")
        for uid in sorted(self.players.keys()):
            player = self.players[uid]
            inventory_str = ", ".join(player.values.inventory) if player.values.inventory else "empty"
            print(f"  {uid}: health={player.values.health}, wealth={player.values.money}, "
                  f"inventory=[{inventory_str}], position={player.position}")
        
        self.save()  # Save state after each turn
    def _check_game_conditions(self) -> None:
        """Check all game end/win conditions and update game state accordingly."""
        result = self.condition_manager.check_conditions(self)
        if result is not None:
            condition, reason = result
            self.is_game_over = True
            self.game_over_reason = reason
            
            # Update game status based on condition type
            if isinstance(condition, CurrencyGoalCondition):
                self.status = GameStatus.COMPLETED
                winner_info = condition.get_winner_info(self)
                if winner_info:
                    # Store the top winner's UID as winner_player_name
                    self.winner_player_name = winner_info['top_winner_uid']
            elif isinstance(condition, AllPlayersDeadCondition):
                self.status = GameStatus.COMPLETED
                self.winner_player_name = None
            elif isinstance(condition, MaxTurnsCondition):
                # Game ended by max turns - find richest player as winner
                self.status = GameStatus.COMPLETED
                if self.players:
                    richest = max(self.players.items(), key=lambda x: x[1].values.money)
                    self.winner_player_name = richest[0]
            
            print(f"[Game] Game ended: {reason}")
    
    @staticmethod
    def _tile_payload(tile: Tile) -> dict:
        """Plain-Python view of a tile for prompts/serialization."""
        return tile.clean_to_dict() #Prevents player from seeing secrets
    @staticmethod
    def _full_tile_payload(tile: Tile) -> dict:
        """Plain-Python view of a tile for prompts/serialization."""
        return tile.to_dict() #Prevents player from seeing secrets
    
    @override
    def save(self) -> str:
        # Convert players to PlayerModel format
        players_data = {}
        for uid, player in self.players.items():
            player_data = Savable.fromJSON(player.save())
            players_data[uid] = PlayerModel(**player_data)
        
        # Convert DM to DungeonMasterModel format
        dm_data = Savable.fromJSON(self.dm.save())
        dm_model = DungeonMasterModel(**dm_data)
        
        # Convert tiles to TileModel format
        tiles_data = []
        for (x, y), val in self.tiles.items():
            tile = val[0] if isinstance(val, tuple) else val  # handle (Tile, ...) cases
            # Convert Secret objects to dicts for TileModel
            secrets = [secret.to_dict() for secret in tile.secrets]
            tiles_data.append(
                TileModel(
                    position=[int(x), int(y)],
                    description=getattr(tile, "description", ""),
                    secrets=secrets,
                    terrainType=getattr(tile, "terrainType", "plains"),
                    terrainEmoji=getattr(tile, "terrainEmoji", "🌾"),
                )
            )
        
        # Create game state for this turn
        game_state = GameStateModel(
            players=players_data,
            dm=dm_model,
            tiles=tiles_data,
            player_responses={uid: player.get_responses_history()[-1] if player.get_responses_history() else "" 
                            for uid, player in self.players.items()},
            dungeon_master_verdict=self.dm.get_responses_history()[-1] if self.dm.get_responses_history() else "",
            # Include decomposed verdict components
            character_state_change=self.verdict_character_state,
            world_state_change=self.verdict_world_state,
            narrative_result=self.verdict_narrative_result,
            # Include game over state
            is_game_over=self.is_game_over,
            game_over_reason=self.game_over_reason
        )
        
        # Create/update game metadata (without game_state)
        game_id = getattr(self, 'game_id', str(uuid.uuid4()))
        # Determine status based on game_over state
        if self.is_game_over:
            status = getattr(self, 'status', GameStatus.COMPLETED)
        else:
            status = getattr(self, 'status', GameStatus.ACTIVE)
        
        game_data = GameModel(
            id=game_id,
            name=getattr(self, 'name', 'Untitled Game'),
            description=getattr(self, 'description', ''),
            status=status,
            model=getattr(self, 'model', 'mock'),
            world_size=self.world_size,
            winner_player_name=getattr(self, 'winner_player_name', None),
            currency_target=getattr(self, 'currency_target', None),
            max_turns=getattr(self, 'max_turns', None),
            total_players=getattr(self, 'total_players', None),
            game_duration=getattr(self, 'game_duration', None)
        )
        
        # Save game metadata to database
        saved_id = save_game_to_database(game_data)
        
        # Create turn model with game state
        turn_data = TurnModel(
            game_id=game_id,
            turn_number=self.current_turn_number,
            game_state=game_state
        )
        
        # Save turn to database
        turn_id = save_turn_to_database(turn_data)
        
        # Return JSON string for compatibility (include turn info)
        result = game_data.model_dump()
        result['current_turn_number'] = self.current_turn_number
        result['latest_turn_id'] = turn_id
        return Savable.toJSON(result)
    
    @override
    def load(self, loaded_data: dict | str | None = None, game_id: str | None = None):
        # If game_id is provided, load from database using lib function
        if game_id:
            try:
                # Load game metadata
                game_model = load_game_from_database(game_id)
                
                # Load latest turn to get game state
                try:
                    latest_turn = get_latest_turn_by_game_id(game_id)
                    game_state = latest_turn.game_state
                    self.current_turn_number = latest_turn.turn_number
                except ValueError:
                    # No turns found, initialize with empty state
                    game_state = GameStateModel()
                    self.current_turn_number = 0
                    
            except ValueError as e:
                raise ValueError(f"Failed to load game {game_id}: {str(e)}")
        else:
            # Handle string input (legacy support or direct data load)
            if isinstance(loaded_data, str):
                loaded_data = Savable.fromJSON(loaded_data)
            
            if not loaded_data:
                raise ValueError("No data provided to load")
            
            # Check if this is new format (without game_state) or old format (with game_state)
            if 'game_state' in loaded_data:
                # Legacy format with game_state embedded
                try:
                    game_model = GameModel(**{k: v for k, v in loaded_data.items() if k != 'game_state'})
                    game_state = GameStateModel(**loaded_data['game_state'])
                    self.current_turn_number = loaded_data.get('current_turn_number', 0)
                except Exception as e:
                    raise ValueError(f"Invalid game data format: {str(e)}")
            else:
                # New format without game_state
                try:
                    game_model = GameModel(**loaded_data)
                    # Try to load from latest turn
                    try:
                        latest_turn = get_latest_turn_by_game_id(game_model.id)
                        game_state = latest_turn.game_state
                        self.current_turn_number = latest_turn.turn_number
                    except ValueError:
                        # No turns found
                        game_state = GameStateModel()
                        self.current_turn_number = 0
                except Exception as e:
                    raise ValueError(f"Invalid game data format: {str(e)}")
        
        # Load players
        self.players = {}
        for uid, player_data in game_state.players.items():
            if hasattr(player_data, 'model_dump'):
                player_dict = player_data.model_dump()
            else:
                player_dict = player_data
            
            # Handle legacy field names (UID -> uid)
            if 'UID' in player_dict and 'uid' not in player_dict:
                player_dict['uid'] = player_dict['UID']
            
            p = Player(uid)
            p.load(player_dict)
            if p.UID != uid:
                p.UID = uid  # enforce key ↔ object UID consistency
            self.players[uid] = p

        # Load DM
        self.dm = DungeonMaster()
        dm_data = game_state.dm.model_dump() if hasattr(game_state.dm, 'model_dump') else game_state.dm
        self.dm.load(dm_data)

        # Load tiles
        tiles_map: dict[tuple[int, int], Tile] = {}
        for tile_data in game_state.tiles:
            if hasattr(tile_data, 'model_dump'):
                tile_dict = tile_data.model_dump()
            else:
                tile_dict = tile_data
            
            t = Tile.from_dict(tile_dict)
            tiles_map[(t.position[0], t.position[1])] = t
        self.tiles = tiles_map
        
        # Store game metadata
        self.game_id = game_model.id
        self.name = game_model.name
        self.description = game_model.description
        self.status = game_model.status
        self.model = getattr(game_model, 'model', 'mock')
        self.world_size = getattr(game_model, 'world_size', GameConfig.world_size)
        self.winner_player_name = getattr(game_model, 'winner_player_name', None)
        self.currency_target = getattr(game_model, 'currency_target', None)
        self.max_turns = getattr(game_model, 'max_turns', None)
        self.total_players = getattr(game_model, 'total_players', None)
        self.game_duration = getattr(game_model, 'game_duration', None)
        
        # Load game over state from game_state
        self.is_game_over = getattr(game_state, 'is_game_over', False)
        self.game_over_reason = getattr(game_state, 'game_over_reason', None)
        
        # Reinitialize condition manager after loading
        self.condition_manager = GameConditionManager()
        self.condition_manager.add_condition(MaxTurnsCondition())
        self.condition_manager.add_condition(AllPlayersDeadCondition())
        self.condition_manager.add_condition(CurrencyGoalCondition())

    def get_viewable_tiles(self,position:tuple[int,int], vision:int = 1) -> list[Tile]:
        tiles = []
        for x in range(-vision,vision+1):
            for y in range(-vision+x,vision-x+1):
                tiles.append(self.get_tile((position[0]+x,position[1]+y)))
        return tiles
    
    def _get_viewable_tiles_payload(self,position:tuple[int,int], vision:int = 1) -> list[dict]:
        return [self._tile_payload(t) for t in self.get_viewable_tiles(position, vision)]
    
    def _get_tiles_full_payload(self) -> list[dict]:
        return [self._full_tile_payload(t) for t in self.tiles.values()]

    def _build_player_context(self, uid: str, sorted_uids: list[str], negotiation_history: list[dict[str,str]]) -> dict:
        """Build sanitized context for a player request."""
        player = self.players[uid]
        tiles_payload = self._get_viewable_tiles_payload(player.position, GameConfig.player_vision)
        
        # Format negotiation history as a list of messages per round
        formatted_negotiation_history = []
        for round_messages in negotiation_history:
            formatted_round = [round_messages[other_uid] for other_uid in sorted_uids]
            formatted_negotiation_history.append(formatted_round)
        
        context = {
            "Self": player.save(),
            "Players (excluding self)": {
                other_uid: self.players[other_uid].save()
                for other_uid in sorted_uids
                if other_uid != uid
            },
            "tiles": tiles_payload,
            "uid": uid,
            "position": player.position,
            "negotiation_history": formatted_negotiation_history,
            "previous_turn_narrative": self.verdict_narrative_result,
        }
        return context
    def _get_responses_at_frame(self, frame:int) -> dict[str,str]:
        responses = {}
        for uid, player in self.players.items():
            hist = player.get_responses_history()
            if hist and len(hist) > frame:
                responses[uid] = hist[frame]
        if self.dm._responses and len(self.dm._responses) > frame:
            responses["DM"] = self.dm._responses[frame]
        return responses
    
    def handle_verdict(self, verdict: GameResponse | dict | str | None):
        """
        Apply a DM verdict to game state.
        - Accepts GameResponse (pydantic), dict-like, or JSON string.
        - Supports multiple players via CharacterState entries keyed by uid.
        - Ignores/records unknown or false UIDs without raising.
        - Clamps negative money/health to 0.
        - Applies world_state_change tile updates when present.
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
        except Exception as E:
            raise ValueError(f"Failed to parse verdict into GameResponse: {E}.")

        if parsed is None or not isinstance(getattr(parsed, "character_state_change", None), list):
            return #Don't throw errors if state is empty

        # --- Apply per-player character updates ---
        unknown_uids: list[str] = []
        for cs in parsed.character_state_change:
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

            # Inventory changes (process add first, then remove)
            try:
                inventory_add = getattr(cs, "inventory_add", None)
                if inventory_add is not None and isinstance(inventory_add, list):
                    player.values.add_inventory(inventory_add)
            except Exception as e:
                print(f"[handle_verdict] Error processing inventory_add for {uid}: {e}")

            try:
                inventory_remove = getattr(cs, "inventory_remove", None)
                if inventory_remove is not None and isinstance(inventory_remove, list):
                    player.values.remove_inventory(inventory_remove)
            except Exception as e:
                print(f"[handle_verdict] Error processing inventory_remove for {uid}: {e}")

        if unknown_uids:
            print(f"[handle_verdict] Ignored unknown UIDs: {sorted(set(unknown_uids))}")

        # --- Apply world updates to tiles if provided ---
        ws = getattr(parsed, "world_state_change", None)
        tiles_payload = getattr(ws, "tiles", None) if ws else None
        if tiles_payload:
            for td in tiles_payload:
                try:
                    if isinstance(td, dict):
                        pos = list(td["position"])
                        desc = td.get("description", "")
                        secrets = [(str(k), int(v)) for k, v in td.get("secrets", [])]
                    else:
                        pos = list(getattr(td, "position"))
                        desc = getattr(td, "description", "")
                        secrets = [(str(k), int(v)) for k, v in getattr(td, "secrets", [])]

                    key = (int(pos[0]), int(pos[1]))
                    t = self.tiles[key]
                    t.update_description(desc)
                    t.update_secrets(secrets)
                except Exception:
                    continue
        
        # --- Store decomposed verdict components for persistence ---
        self.verdict_character_state = getattr(parsed, "character_state_change", [])
        self.verdict_world_state = getattr(parsed, "world_state_change", None)
        self.verdict_narrative_result = getattr(parsed, "narrative_result", "")
    
    #Accessor functions
    def get_tile(self, position: tuple[int,int]) -> Tile:
        if abs(position[0]) > self.world_size or abs(position[1]) > self.world_size:
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
    def get_game_status(self) -> dict:
        """Get current game status including win/end conditions."""
        return {
            'is_game_over': self.is_game_over,
            'game_over_reason': self.game_over_reason,
            'status': getattr(self, 'status', 'active'),
            'current_turn': self.current_turn_number,
            'max_turns': getattr(self, 'max_turns', None),
            'winner': getattr(self, 'winner_player_name', None)
        }
