# Agentic AI

## Overview
THis projectis a text-led roguelike economy simulator where large-language-model agents explore a shared tile grid, trade, and compete to grow their wealth. Each tile carries a concise natural-language description that is fed back into the model loop so that actions can continuously reshape the world narrative (e.g., a forest tile becomes scorched after being burned).

## Core Agents
- **Green Agent (Controller / Dungeon Master):** bootstraps the map, orchestrates economic events, and adjudicates every player action before updating global state.
- **White Agents (Players):** submit short, turn-based intentions, track private stats such as health and inventory, and navigate the grid to pursue profit.

## Turn Cycle
1. Players propose single-sentence actions for the current turn.
2. The controller batches and resolves the actions against the shared world model.
3. Updated tile descriptions and personal stats are broadcast to every participant.
4. The loop repeats until the scenario ends or a win condition is satisfied.

The baseline objective is wealth maximization within a dynamic local economy, though alternative victory conditions can be layered on top of the turn loop.

## Project Structure
- `Main.py`: entry point that will wire together the game loop and orchestration logic.
- `src/Game.py`: placeholder for the main simulation driver.
- `src/Agent.py`: planned interface to the LLM backends used for both controller and player agents.
- `src/FileManager.py`: specification for persisting world state via coordinate-to-description hashes.
- `data/Agentic AI Master File.txt`: design document detailing the MVP concept and agent responsibilities.
- `playground.ipynb`: scratchpad for rapid prototyping and experimentation.

## Current Implementation Status

### Architecture Overview
The project has evolved into a modular, service-oriented architecture with clear separation of concerns:

#### Core Services (`src/services/`)
- **SessionHandler**: Manages game sessions, action execution, and state persistence
- **AiServicesBase**: Abstract base class for AI service implementations
- **Environment Services**: Handles game state, actions, and environment interactions

#### AI Service Layer (`src/services/aiServices/`)
- **OpenAI Service**: Implementation for OpenAI GPT models
- **Claude Service**: Implementation for Anthropic Claude models
- Both services extend the base `AiServicesBase` class for consistent interface

#### Application Layer (`src/app/`)
- **Game.py**: High-level game management functions (create_session, do_action, etc.)
- **FileManager.py**: Handles save system and ground truth management

#### Configuration (`src/core/`)
- **settings.py**: Comprehensive configuration management for game mechanics and AI settings

### Key Data Structures

#### Session Management
```python
@dataclass
class Session:
    id: str
    ai_service: list[AiServicesBase]
    history: list[Action]
```

#### Action System
```python
@dataclass
class Action:
    id: str
    message: str
    functions: list[function]
    response: str
    done: bool
    error: str
    success: bool
    game_state: GameState
    next_game_state: GameState
    ai_service: AiServicesBase
    timestamp: str
```

#### Game State
```python
@dataclass
class GameState:
    id: str
    state: dict
    x: int
    y: int
```

### Configuration System
The project includes a robust configuration system with:
- **GameConfig**: Game mechanics (max turns, world size, starting stats)
- **AIConfig**: AI service settings (API keys, models, temperature)
- Environment variable support for sensitive data
- Automatic directory creation for saves and data

### Current Development State
- ✅ **Architecture**: Well-structured service-oriented design
- ✅ **Configuration**: Comprehensive settings management
- ✅ **Data Models**: Core data structures defined
- ✅ **AI Integration**: Base classes and service interfaces ready
- 🔄 **Implementation**: Core methods need completion (AI service implementations, game loop)
- 🔄 **Testing**: No test suite currently implemented
- 🔄 **Documentation**: Basic structure in place, needs expansion

### Technical Dependencies
- Python dataclasses for clean data modeling
- Environment variable management for API keys
- Modular design supporting multiple AI providers
- Session-based state management with action history

## Next Steps
- Complete AI service implementations in `src/services/aiServices/`
- Implement the game loop and turn orchestration in `src/app/Game.py`
- Finish the persistence layer in `src/app/FileManager.py`
- Add comprehensive error handling and validation
- Implement automated testing suite
- Create example scenarios and gameplay documentation
