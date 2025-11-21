"""
Game initialization helper functions
Provides utilities for creating default game configurations
"""

from typing import Dict, Any
from src.app.Game import Game
from schema.enums import GameStatus


def create_default_player_info(
    num_players: int = 2, 
    model: str = "mock",
    starting_currency: int = 0,
    starting_health: int = 100
) -> Dict[str, Dict[str, Any]]:
    """
    Create default player configuration
    
    Args:
        num_players: Number of players to create (default: 2)
        model: AI model to use for players (default: "mock")
        starting_currency: Starting currency for each player (default: 0)
        starting_health: Starting health for each player (default: 100)
        
    Returns:
        Dictionary of player data keyed by UID
    """
    player_info = {}
    
    for i in range(num_players):
        uid = f"player{i}"
        player_info[uid] = {
            "position": [0, 0],
            "UID": uid,
            "model": model,
            "player_class": "human",
            "values": {"money": starting_currency, "health": starting_health},
            "responses": [],
            "agent_prompt": "",
        }
    
    return player_info


def create_player_info_from_configs(
    player_configs: list,
    model: str = "mock"
) -> Dict[str, Dict[str, Any]]:
    """
    Create player configuration from individual player configs

    Args:
        player_configs: List of player configuration objects with name, starting_health, starting_currency, character_class
        model: AI model to use for players (default: "mock")

    Returns:
        Dictionary of player data keyed by UID
    """
    player_info = {}

    for i, config in enumerate(player_configs):
        uid = config.name if hasattr(config, 'name') and config.name else f"player{i}"
        player_info[uid] = {
            "position": [0, 0],
            "UID": uid,
            "model": model,
            "player_class": "human",
            "values": {
                "money": config.starting_currency if hasattr(config, 'starting_currency') else 0,
                "health": config.starting_health if hasattr(config, 'starting_health') else 100
            },
            "responses": [],
            "character_template_name": config.character_class if hasattr(config, 'character_class') and config.character_class else None,
            "agent_prompt": getattr(config, 'agent_prompt', "") or ""
        }

    return player_info


def create_default_dm_info(model: str = "mock") -> Dict[str, str]:
    """
    Create default Dungeon Master configuration
    
    Args:
        model: AI model to use for DM (default: "mock")
        
    Returns:
        Dictionary with DM configuration
    """
    return {"model": model}


def initialize_game(
    game_id: str,
    player_info: Dict[str, Dict[str, Any]] = None,
    dm_info: Dict[str, str] = None,
    num_players: int = 2,
    world_size: int = 1,
    model: str = "mock",
    name: str = "Untitled Game",
    description: str = "",
    status: GameStatus = GameStatus.PENDING,
    currency_target: int = 1000,
    starting_currency: int = 0,
    starting_health: int = 100,
    max_turns: int = 10,
    player_configs: list = None,
):
    """
    Initialize a new Game instance with configuration
    
    Args:
        game_id: Unique identifier for the game
        player_info: Dictionary of player data (uses defaults if None)
        dm_info: Dungeon Master configuration (uses defaults if None)
        num_players: Number of players to create (default: 2)
        world_size: Size of the world grid (default: 1)
        model: AI model to use for players and DM (default: "mock")
        name: Game name
        description: Game description
        status: Initial game status
        currency_target: Win condition currency target (default: 1000)
        starting_currency: Starting currency for each player (default: 0)
        starting_health: Starting health for each player (default: 100)
        player_configs: List of individual player configurations (default: None)
        
    Returns:
        Configured Game instance
    """
    # Import here to avoid circular imports
    
    # Use defaults if not provided
    if player_info is None:
        # If individual player configs are provided, use them
        if player_configs is not None:
            player_info = create_player_info_from_configs(
                player_configs=player_configs,
                model=model
            )
        else:
            # Otherwise use default values
            player_info = create_default_player_info(
                num_players=num_players, 
                model=model,
                starting_currency=starting_currency,
                starting_health=starting_health
            )
    
    if dm_info is None:
        dm_info = create_default_dm_info(model=model)
    
    # Create the Game instance with world_size parameter
    game = Game(player_info=player_info, dm_info=dm_info, world_size=world_size)
    
    # Set game metadata
    game.game_id = game_id
    game.name = name
    game.description = description
    game.status = status
    game.model = model
    
    # Set new game configuration fields
    game.currency_target = currency_target
    game.total_players = num_players
    game.winner_player_name = None
    game.max_turns = max_turns
    game.game_duration = None
    
    return game
