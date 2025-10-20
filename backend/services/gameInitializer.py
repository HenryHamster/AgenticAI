"""
Game initialization helper functions
Provides utilities for creating default game configurations
"""

from typing import Dict, Any


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
            "responses": []
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
    status: str = "active",
    currency_target: int = 1000,
    starting_currency: int = 0,
    starting_health: int = 100
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
        
    Returns:
        Configured Game instance
    """
    # Import here to avoid circular imports
    from src.app.Game import Game
    
    # Use defaults if not provided
    if player_info is None:
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
    
    # Set new game configuration fields
    game.currency_target = currency_target
    game.total_players = num_players
    game.winner_player_name = None
    game.number_of_turns = None
    game.game_duration = None
    
    return game
