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

- **Persistence (`src/database/fileManager.py`)**  
  - `Savable` mixin standardizes `.save()`/`.load()` conversions to JSON through helper methods.  
  - `FileManager` offers read/write utilities for JSON blobs and `Savable` instances with consistent UTF-8 encoding.

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
Environment Variables
Configure provider credentials before running anything that hits an external API:

OPENAI_API_KEY
CLAUDE_API_KEY
Optional overrides (if you extend AIConfig) can be introduced via additional env vars or by editing settings.py.

Running the Game Loop
There is no CLI entry point yet. To experiment:

```python

from src.app.Game import Game

player_info = {"player-1": {"position": [0, 0], "UID": "player-1"}}
game = Game(player_info)

# For demonstration; real usage should persist state and handle DM verdicts.
await game.step()

```

You will need valid API keys for whichever models you target, since DungeonMaster and Player both defer to AIWrapper.ask.

Testing
The testing/ directory contains exploratory scripts:

testing/test_parser.py exercises the response parser against canned responses, no API calls required.
testing/test_openai_integration.py demonstrates structured output parsing for OpenAI; it skips live calls if OPENAI_API_KEY isn’t set.
Execute them with:

```bash

python testing/test_parser.py
python testing/test_openai_integration.py
(Expect the OpenAI integration script to fail gracefully when API keys are absent or incompatible with the configured model/structured-output flow.)
```

Project Status
✅ Modular service-oriented architecture (Game/Dungeon Master/Player abstractions)
✅ Unified AI service wrapper with LangChain providers
✅ Response parsing pipeline + schemas
✅ Persistence helpers via Savable + FileManager
🔄 Game verdict handling (Game.handle_verdict) still needs implementation
🔄 Environment/session management scaffolds (stateServices/GameState.py, SessionHandler.py, EnviormentHandler.py) are empty
🔄 AI services reference config attributes (openai_max_tokens, claude_max_tokens, *_timeout) that are not yet defined in AIConfig
🔄 Error handling, validation, and story/event orchestration remain rudimentary
🔄 Automated test coverage is limited to parser and integration demos
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


