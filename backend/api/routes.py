"""
FastAPI routes for game management
"""

import asyncio
from fastapi import APIRouter, HTTPException, Response, Query
from services.database.gameService import get_game_run_from_database, save_game_to_database
from services.gameWorker import run_game_async
from services.gameInitializer import initialize_game

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/games/create")
async def create_game_endpoint(
    number_of_rounds: int = Query(default=10, ge=1, description="Number of game rounds to play"),
    number_of_players: int = Query(default=2, ge=1, le=10, description="Number of players in the game"),
    world_size: int = Query(default=1, ge=1, le=10, description="World size (grid extends from -size to +size)"),
    model_mode: str = Query(default="mock", regex="^(gpt-4\.1-nano|mock)$", description="AI model to use (gpt-4.1-nano or mock)")
):
    try:
        # Create a unique game ID
        import uuid
        game_id = f"game_{uuid.uuid4().hex[:8]}"
        
        # Initialize the game using gameInitializer with the specified parameters
        game = initialize_game(
            game_id=game_id,
            num_players=number_of_players,
            world_size=world_size,
            model=model_mode,
            name=f"Game {game_id}",
            description=f"Game with {number_of_players} players, {number_of_rounds} rounds, world size {world_size}"
        )
        
        # Save the initialized game to database
        game.save()
        
        # Trigger the game worker to run the game asynchronously
        # This runs in the background without blocking the API response
        asyncio.create_task(run_game_async(game_id=game_id, rounds=number_of_rounds, verbose=True))
        
        return {
            "game_id": game_id, 
            "status": "created",
            "message": "Game created and worker started. The game will run in the background.",
            "config": {
                "number_of_rounds": number_of_rounds,
                "number_of_players": number_of_players,
                "world_size": world_size,
                "model_mode": model_mode
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create game: {str(e)}")

@router.get("/game/{game_id}")
async def get_game_detail(game_id: str):
    try:
        game_run = get_game_run_from_database(game_id)
        return game_run.model_dump()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"Game not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get game: {str(e)}")

