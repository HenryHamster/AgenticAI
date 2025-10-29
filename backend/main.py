"""
FastAPI main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
from api.greenAgentRoutes import router as green_agent_router

# Create FastAPI app instance
app = FastAPI(
    title="Agentic AI Game API",
    description="API for managing AI-powered games",
    version="1.0.0"
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")
app.include_router(green_agent_router, prefix="/api/agentic/v1")
