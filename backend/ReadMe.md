# AgenticAI Backend

> Python backend for the AgenticAI roguelike economy simulator.

For full project setup (backend + frontend via Docker), see the [main README](../README.md).

## Overview

The backend serves two purposes:

1. **Backend Service** - FastAPI server providing REST APIs for the frontend to manage and view games
2. **AgentBeats Agents** - Autonomous AI agents (Green Agent + Purple Agents) that play the game via the A2A protocol

This README covers running the backend components independently. For the recommended Docker-based setup, refer to the main README.

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

## Running the Backend

There are two ways to run the backend:

### Option 1: Backend Service (FastAPI)

Run the backend as a standalone API server:

```bash
cd backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .\.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"

# Run the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000).

---

### Option 2: AgentBeats Agents

Run the AI agents for the A2A protocol (used with [AgentBeats](https://agentbeats.org)):

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY="your-openai-key"   # For Green Agent (DM)
export GOOGLE_API_KEY="your-google-key"   # For Purple Agents

# Run Green Agent (Game Judge)
python scenarios/roguelike/green_agent.py --host 0.0.0.0 --port 9009

# Run Purple Agent (Player) - in another terminal
python scenarios/roguelike/purple_agent.py --host 0.0.0.0 --port 9018
```

For detailed AgentBeats integration, see [scenarios/roguelike/README.md](scenarios/roguelike/README.md).

For AgentBeats controller setup and deployment, see [coolify/README.md](../coolify/README.md).

---

### Docker (Recommended)

For the easiest setup, use Docker Compose from the project root:

```bash
# Backend + Frontend app
docker compose up --build

# Or AgentBeats agents only
docker compose -f docker-compose.local.agents.yml --env-file .env.local up --build
```

See the [main README](../README.md) for complete Docker setup instructions.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes | OpenAI API key (GPT models, used by DM) |
| `GOOGLE_API_KEY` | Yes | Google API key (Gemini models, used by agents) |
| `CLAUDE_API_KEY` | No | Anthropic API key (optional) |

## Project Structure

```
backend/
├── main.py                      # FastAPI entry point
├── src/
│   ├── app/                     # Core game logic
│   │   ├── Game.py              # Turn-based game orchestration
│   │   ├── Player.py            # AI player agent wrapper
│   │   ├── DungeonMaster.py     # World generation & adjudication
│   │   └── Tile.py              # World grid locations
│   ├── services/                # AI integration & parsing
│   │   ├── aiServices/          # LLM provider wrappers
│   │   └── responseParser/      # JSON extraction from LLM output
│   └── database/                # Persistence utilities
├── scenarios/
│   └── roguelike/               # AgentBeats agent implementations
│       ├── green_agent.py       # Game Judge (DM)
│       ├── purple_agent.py      # Player Agent
│       └── agentbeats_lib/      # A2A protocol utilities
└── testing/                     # Test scripts
```

## Reference

- **AgentBeats Integration**: [scenarios/roguelike/README.md](scenarios/roguelike/README.md)
- **Design Document**: [data/Agentic AI Master File.txt](data/Agentic%20AI%20Master%20File.txt)

