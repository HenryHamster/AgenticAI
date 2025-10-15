"""
FastAPI routes for game management
"""

from fastapi import APIRouter, HTTPException, Response
from lib.database.game import get_game_run_from_database

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy"}

@router.get("/game/{id}")
async def get_game_detail(game_id: str):

    # Get game run from database
    game_run = get_game_run_from_database(game_id)

    return Response(status_code=200, content=game_run)

