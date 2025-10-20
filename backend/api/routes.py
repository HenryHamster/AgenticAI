"""
FastAPI routes for game management
"""

from fastapi import APIRouter, HTTPException, Response
from lib.database.gameService import get_game_run_from_database, create_game_from_database

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/games/create")
async def create_game():
    try:
        game_id = create_game_from_database("test_game")
        return {"game_id": game_id, "status": "created"}
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

