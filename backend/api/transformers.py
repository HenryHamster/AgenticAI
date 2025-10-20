"""
Data transformation utilities for converting backend models to frontend format
"""

import json
from typing import List, Dict, Any
from services.database.turnService import get_turns_by_game_id
from schema.gameModel import GameModel
from schema.dataModels import GameResponse


def transform_game_for_frontend(game: GameModel, include_turns: bool = False) -> Dict[str, Any]:
    """Transform backend GameModel to frontend GameRun format"""
    turns_data = []
    players_data = {}  # Changed to dictionary to match new format
    winner_id = None
    initial_tiles = []  # Changed from initial_board_state
    
    if include_turns:
        turns = get_turns_by_game_id(game.id)
        
        # Get initial tiles from first turn if available
        if turns and len(turns) > 0:
            first_turn = turns[0]
            # Store tiles in new flat array format
            for tile in first_turn.game_state.tiles:
                initial_tiles.append({
                    "position": tile.position,
                    "description": tile.description
                })
            
            # Get players from the first turn - store as dictionary
            for uid, player in first_turn.game_state.players.items():
                players_data[uid] = {
                    "uid": player.uid,
                    "model": "mock",  # Default model
                    "values": {
                        "money": player.values.money,
                        "health": player.values.health
                    },
                    "position": player.position,  # Keep as array [x, y]
                    "responses": player.responses,
                    "player_class": player.player_class,
                    # Legacy fields for backwards compatibility
                    "name": player.uid,
                    "emoji": "🧙",
                    "validityScore": 0,
                    "creativityScore": 0,
                    "isActive": player.values.health > 0
                }
        
        # Transform turns to new format
        for turn in turns:
            # Convert tiles to flat array
            tiles_array = [
                {
                    "position": tile.position,
                    "description": tile.description
                }
                for tile in turn.game_state.tiles
            ]
            
            # Convert players to dictionary
            players_dict = {}
            for uid, p in turn.game_state.players.items():
                players_dict[uid] = {
                    "uid": p.uid,
                    "model": "mock",
                    "values": {
                        "money": p.values.money,
                        "health": p.values.health
                    },
                    "position": p.position,  # Keep as array [x, y]
                    "responses": p.responses,
                    "player_class": p.player_class,
                    # Legacy fields
                    "name": p.uid,
                    "emoji": "🧙",
                    "validityScore": 0,
                    "creativityScore": 0,
                    "isActive": p.values.health > 0
                }
            
            # Convert verdict components to serializable format
            character_state_data = []
            for cs in turn.game_state.character_state_change:
                character_state_data.append({
                    "uid": cs.uid,
                    "money_change": cs.money_change,
                    "health_change": cs.health_change,
                    "position_change": cs.position_change
                })
            
            world_state_data = None
            if turn.game_state.world_state_change:
                world_state_data = {
                    "tiles": [
                        {
                            "position": tile.position,
                            "description": tile.description
                        }
                        for tile in turn.game_state.world_state_change.tiles
                    ]
                }
            
            turn_data = {
                "turnNumber": turn.turn_number,
                "tiles": tiles_array,
                "players": players_dict,
                "dungeon_master_verdict": turn.game_state.dungeon_master_verdict,
                # Decomposed verdict components
                "character_state_change": character_state_data,
                "world_state_change": world_state_data,
                "narrative_result": turn.game_state.narrative_result,
                "world_size": game.world_size,
                "board_size": 2 * game.world_size + 1,  # Calculate board dimensions
                # Legacy fields for backwards compatibility
                "actions": [],
                "boardState": transform_tiles_to_board(turn.game_state.tiles),
                "playerStates": list(players_dict.values())
            }
            turns_data.append(turn_data)
        
        # Find winner (player with highest currency or last alive)
        if turns and len(turns) > 0:
            last_turn = turns[-1]
            max_money = -1
            for player in last_turn.game_state.players.values():
                if player.values.money > max_money:
                    max_money = player.values.money
                    winner_id = player.uid
    
    return {
        "id": game.id,
        "startTime": game.created_at or game.updated_at or "2025-01-01T00:00:00",
        "endTime": game.updated_at or game.created_at or "2025-01-01T00:00:00",
        "winnerId": winner_id,
        "players": players_data,  # Now a dictionary
        "turns": turns_data,
        "targetCurrency": game.currency_target,
        "initialTiles": initial_tiles,  # New format
        # New game summary fields
        "winnerPlayerName": game.winner_player_name,
        "currencyTarget": game.currency_target,
        "maxTurns": game.max_turns,
        "totalPlayers": game.total_players,
        "gameDuration": game.game_duration,
        # Legacy field for backwards compatibility - use first turn's tiles if available
        "initialBoardState": transform_tiles_to_board(turns[0].game_state.tiles) if (include_turns and turns and len(turns) > 0) else [],
        # Include backend-specific fields for compatibility
        "name": game.name,
        "description": game.description,
        "status": game.status,
        "model": game.model,
        "world_size": game.world_size,
        "board_size": 2 * game.world_size + 1  # Calculate board dimensions
    }


def transform_tiles_to_board(tiles: List) -> List[List[Dict[str, Any]]]:
    """Transform backend tiles list to frontend board grid format"""
    if not tiles:
        return []
    
    # Find board dimensions
    max_x = max((t.position[0] for t in tiles), default=0)
    min_x = min((t.position[0] for t in tiles), default=0)
    max_y = max((t.position[1] for t in tiles), default=0)
    min_y = min((t.position[1] for t in tiles), default=0)
    
    # Create empty board
    width = max_x - min_x + 1
    height = max_y - min_y + 1
    board = [[None for _ in range(width)] for _ in range(height)]
    
    # Fill board with tiles
    for tile in tiles:
        x_idx = tile.position[0] - min_x
        y_idx = tile.position[1] - min_y
        board[y_idx][x_idx] = {
            "x": tile.position[0],
            "y": tile.position[1],
            "terrainType": "plains",  # Default, TileModel doesn't have type field
            "terrainEmoji": "🌾",  # Default, TileModel doesn't have emoji field
            "description": tile.description
        }
    
    return board
