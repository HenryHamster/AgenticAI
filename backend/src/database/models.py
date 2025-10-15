"""
SQLAlchemy models for game state persistence.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import json


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class GameSession(Base):
    """
    Represents a complete game session.
    
    Game state is stored in individual Turn records.
    """
    __tablename__ = "game_sessions"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Metadata
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=datetime.utcnow, 
        onupdate=datetime.utcnow
    )
    
    # Optional metadata fields
    turn_count: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    num_players: Mapped[Optional[int]] = mapped_column(Integer, default=0)
    
    # Relationship to turns
    turns: Mapped[List["Turn"]] = relationship("Turn", back_populates="game_session", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<GameSession(id={self.id}, name='{self.name}', turns={self.turn_count})>"


class Turn(Base):
    """
    Represents a single turn in a game session.
    
    Each turn stores the complete game state at the end of that turn,
    enabling turn-by-turn history tracking and replay functionality.
    """
    __tablename__ = "turns"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to game session
    game_session_id: Mapped[int] = mapped_column(Integer, ForeignKey("game_sessions.id"), nullable=False)
    
    # Turn metadata
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Game state snapshot at the end of this turn (JSON)
    game_state: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Relationship back to game session
    game_session: Mapped["GameSession"] = relationship("GameSession", back_populates="turns")
    
    def __repr__(self) -> str:
        return f"<Turn(id={self.id}, session_id={self.game_session_id}, turn={self.turn_number})>"
    
    def get_game_state_dict(self) -> dict:
        """Parse the JSON game_state into a Python dict."""
        return json.loads(self.game_state)
    
    def set_game_state_dict(self, state: dict):
        """Serialize a Python dict into the JSON game_state field."""
        self.game_state = json.dumps(state)
