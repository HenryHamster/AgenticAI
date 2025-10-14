"""
FastAPI routes for game management
"""

from fastapi import APIRouter

router = APIRouter()

# Global game storage (in production, use a proper database)
@router.get("/")
async def get_root():
    return {"message": "Hello, World!"}