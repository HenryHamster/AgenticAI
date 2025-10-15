"""
Database engine and session management for SQLite.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager
from pathlib import Path
from typing import Generator
import os

from src.database.models import Base


class DatabaseManager:
    """Manages SQLite database connections and sessions."""
    
    def __init__(self, db_path: str = "data/game_state.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file (relative or absolute)
        """
        self.db_path = db_path
        
        # Ensure the directory exists
        db_dir = Path(db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
        
        # Create engine with SQLite
        # Use StaticPool for SQLite to avoid connection issues
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=False  # Set to True for SQL query logging
        )
        
        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )
        
        # Create tables if they don't exist
        self.create_tables()
    
    def create_tables(self):
        """Create all tables defined in models."""
        Base.metadata.create_all(bind=self.engine)
    
    def drop_tables(self):
        """Drop all tables (use with caution)."""
        Base.metadata.drop_all(bind=self.engine)
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            SQLAlchemy Session instance
        """
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope for database operations.
        
        Usage:
            with db_manager.session_scope() as session:
                # perform operations
                session.add(obj)
        
        Yields:
            Database session that auto-commits on success or rolls back on error
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def reset_database(self):
        """Drop and recreate all tables (destructive operation)."""
        self.drop_tables()
        self.create_tables()


# Global database manager instance (singleton pattern)
_db_manager: DatabaseManager | None = None


def get_db_manager(db_path: str = "data/game_state.db") -> DatabaseManager:
    """
    Get or create the global database manager instance.
    
    Args:
        db_path: Path to SQLite database file
        
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
    return _db_manager


def get_session() -> Session:
    """
    Get a new database session from the global manager.
    
    Returns:
        SQLAlchemy Session instance
    """
    return get_db_manager().get_session()
