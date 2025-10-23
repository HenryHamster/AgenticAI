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
from schema.gameModel import GameModel, PlayerConfigModel
from schema.enums import GameStatus
from api.apiDtoModel import CreateGameRequest
from api.transformers import transform_game_for_frontend
from services.evaluationService import evaluate_game_responses

router = APIRouter()


@router.get("/health")
async def health_check():
    return {"status": "healthy"}


@router.post("/games/create")
async def create_game_endpoint(
    request: CreateGameRequest,
    background_tasks: BackgroundTasks,
):
    try:
        # Create a unique game ID
        game_id = f"game_{uuid.uuid4().hex[:8]}"
        
        # Extract game configuration
        game_config = request.game_config
        players = request.players
        number_of_players = len(players)
        

        # Convert player configs to PlayerConfigModel
        player_config_models = [
            PlayerConfigModel(
                name=p.name,
                starting_health=p.starting_health,
                starting_currency=p.starting_currency
            )
            for p in players
        ]
        
        # Create database entry with all configuration
        game_model = GameModel(
            id=game_id,
            name=f"{game_id}",
            description=f"Game with {number_of_players} players, world size {game_config.world_size}",
            status=GameStatus.PENDING,  # Game starts as pending, worker will activate it
            model=game_config.model_mode,
            world_size=game_config.world_size,
            currency_target=game_config.currency_target,
            total_players=number_of_players,
            max_turns=game_config.max_turns,
            player_configs=player_config_models,
            # Store default values for backward compatibility
            starting_currency=players[0].starting_currency if players else 0,
            starting_health=players[0].starting_health if players else 100,
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
                "game_config": game_config.model_dump(),
                "players": [p.model_dump() for p in players],
                "number_of_players": number_of_players,
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

@router.get("/game/eval/{game_id}")
async def evaluate_game(
    game_id: str
):
    try:
        return evaluate_game_responses(game_id, service_type="custom")
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"Game not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate game: {str(e)}")