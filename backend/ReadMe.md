# Agentic AI

> A turn-based, tile-centric economy simulator where LLM-powered agents explore, trade, and compete under a shared Dungeon Master.

## Overview

Agentic AI orchestrates a roguelike-inspired economy in which autonomous player agents pursue wealth while a Dungeon Master agent curates the world. Every tile holds a concise description; whenever an action occurs, the description feeds back into the loop so that later turns reflect accumulated history (e.g., a forest tile becomes “scorched” after a fire spell). The current implementation emphasizes modularity, making it easier to plug in different AI providers, persistence layers, or orchestration strategies as the game evolves.

## Gameplay Loop

1. Player agents submit succinct intentions for the current turn.
2. The Dungeon Master evaluates the combined actions, updates shared state, and narrates outcomes.
3. Updated tile descriptions and per-player stats propagate back to every agent.
4. The loop repeats until a win condition or scenario terminates.

Wealth maximization is the baseline objective, but alternative victory conditions can be layered on top.

## Core Components

- **Game (`src/app/Game.py`)**  
  - Builds the world by having the Dungeon Master procedurally generate tiles for the configured radius.  
  - Manages asynchronous turn execution with `asyncio.gather`, cycling through a configurable number of verdict passes before committing state updates.  
  - Implements the `Savable` interface for snapshotting players, tiles, and Dungeon Master state via `FileManager`.

- **Dungeon Master (`src/app/DungeonMaster.py`)**  
  - Wraps `AIWrapper` calls to request tile descriptions, narrate action resolutions, and update tiles when events occur.

- **Player (`src/app/Player.py`)**  
  - Maintains identity, position, stats, class descriptors, and recent responses.  
  - Uses `AIWrapper` to request actions within a formatted context (tiles in vision range, prior verdict summary, etc.).  
  - Enforces world bounds through `GameConfig.world_size` and persists via `Savable`.

- **AI Wrapper + Services (`src/services/aiServices/`)**  
  - `AIWrapper` multiplexes model identifiers to the appropriate provider, caching conversations per `chat_id`.  
  - `OpenAiService` and `ClaudeService` encapsulate LangChain clients for OpenAI GPT and Claude models, sharing history handling, structured output hooks, and reset utilities.  
  - Both rely on `AiServicesBase` for interface consistency and dynamic Pydantic model generation from dict schemas.

- **Response Parsing (`src/services/responseParser/`)**  
  - `DnDResponseParser` extracts JSON fragments from LLM replies, validates against schema defaults, and returns normalized character/world state plus original narrative.  
  - Schemas (`schema.py`, `dataModels.py`) provide the blueprint for both validation and structured-output hints.

- **Persistence (`src/database/`)**  
  - **SQLite Database**: SQLAlchemy-based ORM for game state persistence with support for multiple game sessions
    - `models.py`: Database models including `GameSession` and `Turn` for storing complete game state and history
    - `db.py`: Database engine and session management with transaction support
    - `game_repository.py`: Repository pattern providing CRUD operations (save_game, load_game, save_turn, list_sessions, etc.)
  - **Legacy File-based**: Original JSON file persistence (preserved for compatibility)
    - `Savable` mixin standardizes `.save()`/`.load()` conversions to JSON through helper methods
    - `FileManager` offers read/write utilities for JSON blobs and `Savable` instances with consistent UTF-8 encoding

- **Configuration (`src/core/settings.py`)**  
  - `GameConfig` governs world size, vision radius, turn counts, and ensures save/data directories exist.  
  - `AIConfig` captures API keys, default models, temperature settings, and the canonical schema instruction appended to AI prompts.

## Setup

### Prerequisites
- Python 3.10+ (LangChain providers currently target modern Python releases)
- Access to at least one supported LLM provider (OpenAI or Anthropic)

### Installation

```bash
python -m venv .venv
.\.venv\Scripts\activate        # Windows PowerShell
pip install -r requirements.txt
```

### Environment Variables

Configure provider credentials before running anything that hits an external API:

- `OPENAI_API_KEY` - OpenAI API key
- `CLAUDE_API_KEY` - Anthropic Claude API key

Optional overrides (if you extend AIConfig) can be introduced via additional env vars or by editing settings.py.

Running the Game Loop
There is no CLI entry point yet. To experiment:

```python

from src.app.Game import Game

player_info = {"player-1": {"position": [0, 0], "UID": "player-1"}}
game = Game(player_info)

# For demonstration; real usage should persist state and handle DM verdicts.
game.step()

```

You will need valid API keys for whichever models you target, since DungeonMaster and Player both defer to AIWrapper.ask.

### Using the Database Layer (NEW)

Persist game state to SQLite:

```python
from src.database.game_repository import GameRepository
from src.app.Game import Game

# Create and save a game
player_info = {"player1": {"position": [0, 0], "UID": "player1", "model": "mock"}}
game = Game(player_info)

repo = GameRepository()
session = repo.save_game(game, session_name="My Game")
print(f"Saved with ID: {session.id}")

# Load the game
loaded_game = repo.load_game(session.id)

# List all games
all_sessions = repo.list_sessions()
```

See `examples/database_usage.py` for comprehensive examples and `src/database/README.md` for full documentation.

Testing
The testing/ directory contains exploratory scripts:

- `testing/test_parser.py` - Response parser tests (no API calls required)
- `testing/test_openai_integration.py` - OpenAI integration tests (skips if no API key)
- `testing/test_database.py` - Database layer tests (NEW)

Execute them with:

```bash
python3 testing/test_parser.py
python3 testing/test_openai_integration.py
python3 testing/test_database.py
```

Project Status
✅ Modular service-oriented architecture (Game/Dungeon Master/Player abstractions)
✅ Unified AI service wrapper with LangChain providers
✅ Response parsing pipeline + schemas
✅ Persistence helpers via Savable + FileManager
✅ SQLite database layer with SQLAlchemy ORM for multi-session support
✅ Turn-by-turn history tracking with replay and rollback capabilities
✅ Repository pattern for game state CRUD operations
✅ Complete verdict handling in Game.handle_verdict
🔄 Environment/session management scaffolds (stateServices/GameState.py, SessionHandler.py, EnviormentHandler.py) are empty
🔄 AI services reference config attributes (openai_max_tokens, claude_max_tokens, *_timeout) that are not yet defined in AIConfig
🔄 Error handling, validation, and story/event orchestration remain rudimentary
🔄 Automated test coverage is limited to parser, integration, and database tests
Roadmap
Flesh out GameState, session orchestration, and environment services to support multi-session persistence and richer tile mechanics.
Finalize verdict handling in Game.handle_verdict, ensuring player stats and tile descriptions update coherently.
Align AIConfig with the parameters expected by AI service implementations (token limits, timeouts, retries).
Introduce robust exception handling and retry/backoff logic across AI calls.
Build a CLI or web driver so humans can monitor sessions or play alongside agents.
Expand automated testing: mock AI services, validate persistence, and cover the async turn cycle.
Document sample scenarios and provide scripted demonstrations using stubbed AI responses for offline testing.
Reference Materials
Design brief: data/Agentic AI Master File.txt
Notes and TODOs: inline comments within src/app/Game.py, Player.py, and service stubs
This README reflects repository contents as of October 2025; update it alongside future refactors to keep onboarding smooth.


