"""
Repository layer for game session CRUD operations.
Provides a clean interface between the Game class and the database.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import json

from src.database.models import GameSession, Turn
from src.database.db import get_db_manager
from src.app.Game import Game


class GameRepository:
    """Repository for managing game session persistence."""
    
    def __init__(self, db_manager=None):
        """
        Initialize repository.
        
        Args:
            db_manager: Optional DatabaseManager instance (uses global if None)
        """
        self.db_manager = db_manager or get_db_manager()
    
    def save_game(
        self, 
        game: Game, 
        session_name: Optional[str] = None,
        session_id: Optional[int] = None
    ) -> GameSession:
        """
        Save a Game instance to the database.
        
        Args:
            game: Game instance to save
            session_name: Optional name for the game session
            session_id: If provided, updates existing session; otherwise creates new
            
        Returns:
            GameSession database model
        """
        with self.db_manager.session_scope() as db_session:
            if session_id is not None:
                # Update existing session
                game_session = db_session.query(GameSession).filter(
                    GameSession.id == session_id
                ).first()
                
                if game_session is None:
                    raise ValueError(f"Game session with id {session_id} not found")
                
                # Update the game state
                game_state_json = game.save()
                game_session.game_state = game_state_json
                game_session.updated_at = datetime.utcnow()
                
                # Update metadata from the state
                game_state_dict = json.loads(game_state_json)
                if "players" in game_state_dict:
                    game_session.num_players = len(game_state_dict["players"])
                
            else:
                # Create new session
                game_state_json = game.save()
                game_state_dict = json.loads(game_state_json)
                
                game_session = GameSession(
                    name=session_name,
                    game_state=game_state_json,
                    turn_count=0,
                    num_players=len(game_state_dict.get("players", {}))
                )
                db_session.add(game_session)
            
            db_session.flush()  # Ensure ID is generated
            db_session.refresh(game_session)  # Load all attributes
            db_session.expunge(game_session)  # Detach but keep loaded attributes
            return game_session
    
    def load_game(self, session_id: int) -> Game:
        """
        Load a Game instance from the database.
        
        Args:
            session_id: ID of the game session to load
            
        Returns:
            Game instance
            
        Raises:
            ValueError: If session not found
        """
        with self.db_manager.session_scope() as db_session:
            game_session = db_session.query(GameSession).filter(
                GameSession.id == session_id
            ).first()
            
            if game_session is None:
                raise ValueError(f"Game session with id {session_id} not found")
            
            # Parse the game state
            game_state_dict = json.loads(game_session.game_state)
            
            # Extract player and dm info
            player_info = game_state_dict.get("players", {})
            dm_info = game_state_dict.get("dm", {})
            
            # Create Game instance
            game = Game(player_info, dm_info=dm_info)
            
            # Load the full state (including tiles)
            game.load(game_state_dict)
            
            return game
    
    def get_session(self, session_id: int) -> Optional[GameSession]:
        """
        Get a GameSession by ID.
        
        Args:
            session_id: ID of the session
            
        Returns:
            GameSession or None if not found
        """
        with self.db_manager.session_scope() as db_session:
            game_session = db_session.query(GameSession).filter(
                GameSession.id == session_id
            ).first()
            if game_session:
                db_session.expunge(game_session)
            return game_session
    
    def list_sessions(
        self, 
        limit: int = 100, 
        offset: int = 0,
        order_by: str = "updated_at"
    ) -> List[GameSession]:
        """
        List all game sessions.
        
        Args:
            limit: Maximum number of sessions to return
            offset: Number of sessions to skip
            order_by: Field to order by (created_at, updated_at, id)
            
        Returns:
            List of GameSession instances
        """
        with self.db_manager.session_scope() as db_session:
            query = db_session.query(GameSession)
            
            # Apply ordering
            if order_by == "created_at":
                query = query.order_by(GameSession.created_at.desc())
            elif order_by == "updated_at":
                query = query.order_by(GameSession.updated_at.desc())
            elif order_by == "id":
                query = query.order_by(GameSession.id.desc())
            
            sessions = query.limit(limit).offset(offset).all()
            # Expunge all sessions so they can be accessed outside the session
            for session in sessions:
                db_session.expunge(session)
            return sessions
    
    def delete_session(self, session_id: int) -> bool:
        """
        Delete a game session.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if deleted, False if not found
        """
        with self.db_manager.session_scope() as db_session:
            game_session = db_session.query(GameSession).filter(
                GameSession.id == session_id
            ).first()
            
            if game_session is None:
                return False
            
            db_session.delete(game_session)
            return True
    
    def update_session_metadata(
        self,
        session_id: int,
        name: Optional[str] = None,
        turn_count: Optional[int] = None
    ) -> Optional[GameSession]:
        """
        Update session metadata without modifying game state.
        
        Args:
            session_id: ID of the session
            name: New name for the session
            turn_count: New turn count
            
        Returns:
            Updated GameSession or None if not found
        """
        with self.db_manager.session_scope() as db_session:
            game_session = db_session.query(GameSession).filter(
                GameSession.id == session_id
            ).first()
            
            if game_session is None:
                return None
            
            if name is not None:
                game_session.name = name
            if turn_count is not None:
                game_session.turn_count = turn_count
            
            game_session.updated_at = datetime.utcnow()
            
            db_session.expunge(game_session)
            return game_session
    
    def get_session_count(self) -> int:
        """
        Get the total number of game sessions.
        
        Returns:
            Number of sessions in database
        """
        with self.db_manager.session_scope() as db_session:
            return db_session.query(GameSession).count()
    
    # ==================== Turn Management Methods ====================
    
    def save_turn(
        self,
        game: Game,
        session_id: int,
        turn_number: int,
        verdict: Optional[str] = None
    ) -> Turn:
        """
        Save a turn snapshot to the database.
        
        Args:
            game: Game instance with current state
            session_id: ID of the game session
            turn_number: Turn number (1-indexed)
            verdict: Optional verdict/narration for this turn
            
        Returns:
            Turn database model
            
        Raises:
            ValueError: If session not found
        """
        with self.db_manager.session_scope() as db_session:
            # Verify session exists
            game_session = db_session.query(GameSession).filter(
                GameSession.id == session_id
            ).first()
            
            if game_session is None:
                raise ValueError(f"Game session with id {session_id} not found")
            
            # Create turn record
            game_state_json = game.save()
            
            turn = Turn(
                game_session_id=session_id,
                turn_number=turn_number,
                game_state=game_state_json,
                verdict=verdict
            )
            
            db_session.add(turn)
            
            # Update session turn count
            game_session.turn_count = max(game_session.turn_count or 0, turn_number)
            game_session.updated_at = datetime.utcnow()
            
            db_session.flush()
            db_session.refresh(turn)  # Load all attributes
            db_session.expunge(turn)  # Detach but keep loaded attributes
            return turn
    
    def get_turns(
        self,
        session_id: int,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Turn]:
        """
        Get all turns for a game session.
        
        Args:
            session_id: ID of the game session
            limit: Maximum number of turns to return (None for all)
            offset: Number of turns to skip
            
        Returns:
            List of Turn instances ordered by turn_number
        """
        with self.db_manager.session_scope() as db_session:
            query = db_session.query(Turn).filter(
                Turn.game_session_id == session_id
            ).order_by(Turn.turn_number.asc())
            
            if offset > 0:
                query = query.offset(offset)
            if limit is not None:
                query = query.limit(limit)
            
            turns = query.all()
            # Expunge all turns so they can be accessed outside the session
            for turn in turns:
                db_session.expunge(turn)
            return turns
    
    def get_turn(self, session_id: int, turn_number: int) -> Optional[Turn]:
        """
        Get a specific turn by turn number.
        
        Args:
            session_id: ID of the game session
            turn_number: Turn number to retrieve
            
        Returns:
            Turn instance or None if not found
        """
        with self.db_manager.session_scope() as db_session:
            turn = db_session.query(Turn).filter(
                Turn.game_session_id == session_id,
                Turn.turn_number == turn_number
            ).first()
            if turn:
                db_session.expunge(turn)
            return turn
    
    def get_latest_turn(self, session_id: int) -> Optional[Turn]:
        """
        Get the most recent turn for a session.
        
        Args:
            session_id: ID of the game session
            
        Returns:
            Latest Turn instance or None if no turns exist
        """
        with self.db_manager.session_scope() as db_session:
            turn = db_session.query(Turn).filter(
                Turn.game_session_id == session_id
            ).order_by(Turn.turn_number.desc()).first()
            if turn:
                db_session.expunge(turn)
            return turn
    
    def load_game_from_turn(self, session_id: int, turn_number: int) -> Game:
        """
        Load a Game instance from a specific turn's state.
        
        Args:
            session_id: ID of the game session
            turn_number: Turn number to load
            
        Returns:
            Game instance with state from that turn
            
        Raises:
            ValueError: If turn not found
        """
        turn = self.get_turn(session_id, turn_number)
        
        if turn is None:
            raise ValueError(f"Turn {turn_number} not found for session {session_id}")
        
        # Parse the game state from the turn
        game_state_dict = json.loads(turn.game_state)
        
        # Extract player and dm info
        player_info = game_state_dict.get("players", {})
        dm_info = game_state_dict.get("dm", {})
        
        # Create Game instance
        game = Game(player_info, dm_info=dm_info)
        
        # Load the full state (including tiles)
        game.load(game_state_dict)
        
        return game
    
    def get_turn_count(self, session_id: int) -> int:
        """
        Get the number of turns recorded for a session.
        
        Args:
            session_id: ID of the game session
            
        Returns:
            Number of turns
        """
        with self.db_manager.session_scope() as db_session:
            return db_session.query(Turn).filter(
                Turn.game_session_id == session_id
            ).count()
    
    def delete_turns_after(self, session_id: int, turn_number: int) -> int:
        """
        Delete all turns after a specific turn number.
        Useful for implementing turn rollback.
        
        Args:
            session_id: ID of the game session
            turn_number: Delete all turns after this number
            
        Returns:
            Number of turns deleted
        """
        with self.db_manager.session_scope() as db_session:
            deleted_count = db_session.query(Turn).filter(
                Turn.game_session_id == session_id,
                Turn.turn_number > turn_number
            ).delete()
            
            # Update session turn count
            game_session = db_session.query(GameSession).filter(
                GameSession.id == session_id
            ).first()
            
            if game_session:
                game_session.turn_count = turn_number
                game_session.updated_at = datetime.utcnow()
            
            return deleted_count
