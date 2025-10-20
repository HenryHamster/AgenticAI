"""
FastAPI routes for game management
"""

from typing import List, Dict, Any
import uuid
from fastapi import APIRouter, HTTPException, Response, Query, BackgroundTasks
from services.database.gameService import (
    get_game_run_from_database,
    save_game_to_database,
    get_all_games_from_database,
)
from services.gameWorker import run_game_async
from schema.gameModel import GameModel
from api.transformers import transform_game_for_frontend

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.post("/games/create")
async def create_game_endpoint(
    background_tasks: BackgroundTasks,
    number_of_players: int = Query(
        default=2, ge=1, le=10, description="Number of players in the game"
    ),
    world_size: int = Query(
        default=2,
        ge=1,
        le=10,
        description="World size (grid extends from -size to +size)",
    ),
    model_mode: str = Query(
        default="mock",
        regex="^(gpt-4\.1-nano|mock)$",
        description="AI model to use (gpt-4.1-nano or mock)",
    ),
    currency_target: int = Query(
        default=1000,
        ge=1,
        description="Currency target for win condition"
    ),
    starting_currency: int = Query(
        default=0,
        ge=0,
        description="Starting currency for each player"
    ),
    starting_health: int = Query(
        default=100,
        ge=1,
        description="Starting health for each player"
    ),
    max_turns: int = Query(
        default=10,
        ge=1,
        description="Maximum number of turns"
    ),
):
    try:
        # Create a unique game ID
        game_id = f"game_{uuid.uuid4().hex[:8]}"

        # Create database entry with all configuration
        # The worker will read this configuration and handle initialization
        game_model = GameModel(
            id=game_id,
            name=f"{game_id}",
            description=f"Game with {number_of_players} players, world size {world_size}",
            status="pending",  # Worker will change to 'active' after initialization
            model=model_mode,
            world_size=world_size,
            currency_target=currency_target,
            total_players=number_of_players,
            max_turns=max_turns,
            starting_currency=starting_currency,
            starting_health=starting_health,
        )
        
        # Save game configuration to database
        save_game_to_database(game_model)

        # Trigger the game worker to initialize and run the game asynchronously
        # Worker will fetch all configuration from database
        background_tasks.add_task(
            run_game_async,
            game_id=game_id,
            verbose=True,
        )

        return {
            "game_id": game_id,
            "status": "created",
            "message": "Game created and worker started. The game will run in the background.",
            "config": {
                "max_turns": max_turns,
                "number_of_players": number_of_players,
                "world_size": world_size,
                "model_mode": model_mode,
                "currency_target": currency_target,
                "starting_currency": starting_currency,
                "starting_health": starting_health,
            },
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create game: {str(e)}")


@router.get("/games")
async def get_all_games():
    """Get all games without their turns"""
    try:
        games = get_all_games_from_database()
        return [transform_game_for_frontend(game, include_turns=False) for game in games]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get games: {str(e)}")


@router.get("/game/{game_id}")
async def get_game_detail(
    game_id: str,
    include_turns: bool = Query(
        default=False, description="Include all game turns in the response"
    ),
):
    try:
        game_run = get_game_run_from_database(game_id)
        return transform_game_for_frontend(game_run, include_turns=include_turns)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"Game not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get game: {str(e)}")
