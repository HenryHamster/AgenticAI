#!/usr/bin/env python3
"""
Reset the database to match the current schema.

This script drops and recreates all tables. USE WITH CAUTION - all data will be lost.

Usage:
    python3 scripts/reset_database.py
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.database.db import get_db_manager


def main():
    print("\n" + "="*60)
    print("Database Reset Utility")
    print("="*60)
    print("\n⚠️  WARNING: This will delete all existing game data!")
    
    response = input("\nType 'yes' to confirm: ")
    
    if response.lower() != 'yes':
        print("Operation cancelled.")
        return
    
    print("\nResetting database...")
    
    try:
        db_manager = get_db_manager()
        db_manager.reset_database()
        
        print("✅ Database reset successfully!")
        print(f"\nDatabase location: {db_manager.db_path}")
        print("Tables have been recreated with the current schema.")
        
    except Exception as e:
        print(f"\n❌ Error resetting database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
