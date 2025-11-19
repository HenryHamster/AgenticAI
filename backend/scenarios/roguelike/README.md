# Roguelike Economy → AgentBeats Integration

Turn-based economy simulator integrated with AgentBeats platform. Two LLM agents compete to maximize wealth.

## Overview

This integration uses:
- **Green Agent**: Game orchestrator (judges battles)
- **Purple Agents**: Player agents (participate in battles)
- **AgentBeats Backend**: Manages battle lifecycle, agent coordination, and result tracking

## File Roles

### `green_agent.py` - Battle Orchestrator
A2A server implementing `GreenAgent` interface.

**Responsibilities:**
- Receives battle notifications from AgentBeats
- Initializes game with configured parameters
- Runs turn loop: collect player actions → DM adjudication → state updates
- Submits turn events and final results to AgentBeats
- Handles duplicate battle notifications
- Signals ready state after reset

**Key Methods:**
- `validate_request()`: Validates battle has required roles and config
- `run_eval()`: Main game loop execution
- `/reset`: Endpoint for AgentBeats to reset agent state
- `/notify`: Endpoint for AgentBeats to send battle notifications
- `/status`: Health check endpoint

### `purple_agent.py` - Player Agent
Google ADK agent wrapped in A2A protocol.

**Responsibilities:**
- Receives game context (stats, position, visible tiles)
- Returns single action string per turn
- Signals ready state after reset

**Key Methods:**
- `/reset`: Signals ready to AgentBeats backend
- `/status`: Health check endpoint

### `agentbeats_lib/green_executor.py` - Battle Message Handler
Converts AgentBeats battle notifications to `EvalRequest` format.

**Responsibilities:**
- Receives `battle_start` or `battle_info` messages
- Fetches battle details from AgentBeats API
- Fetches opponent agent URLs
- Maps agent roles to agent IDs for winner reporting
- Attaches battle context to request

### `agentbeats_lib/tool_provider.py` - Agent Communication
Manages A2A communication with player agents.

**Responsibilities:**
- Maintains conversation state per agent
- Sends context to agents, receives actions
- Resets conversation history between battles

### `agentbeats_lib/models.py` - Data Models
Pydantic models for battle requests and results.

### `agentbeats_lib/client.py` - A2A Protocol Client
Low-level A2A message sending.

### `agentbeats_lib/client_cli.py` - Local Testing
CLI for testing green agent locally without AgentBeats.

### `trigger_game.py` - Local Test Entry Point
Runs scenario locally using `client_cli`.

### `scenario.toml` - Configuration
Defines agents and battle parameters.

---

## AgentBeats Battle Lifecycle

### Phase 1: Battle Creation (AgentBeats Backend)
1. User creates battle via AgentBeats UI
2. Backend validates green agent and opponent agents are unlocked
3. Battle created with state: `pending` → `queued`
4. Battle processor picks up from queue

### Phase 2: Agent Reset & Readiness
**AgentBeats sends:** `POST {launcher_url}/reset`
```json
{
  "signal": "reset",
  "agent_id": "uuid",
  "backend_url": "https://agentbeats.org/api",
  "extra_args": {}
}
```

**What happens:**
1. Green agent receives reset at `/reset` endpoint
2. Calls `_tool_provider.reset()` to clear conversation history
3. Signals ready: `PUT {backend_url}/agents/{agent_id}` with `{"ready": true}`
4. Purple agents do the same
5. AgentBeats polls every 5s until all agents ready (120s timeout)

### Phase 3: Battle Notification
**AgentBeats sends:** POST request to `/notify` endpoint
```json
POST {launcher_url}/notify
{
  "battle_id": "uuid",
  "backend_url": "https://agentbeats.org/api"
}
```

**What happens:**
1. Green agent's `/notify` endpoint receives the battle notification
2. Converts it to an A2A message with `battle_start` type
3. Sends A2A message to itself using the `send_message` client
4. `green_executor.py` receives the A2A message via `execute()` method
5. Fetches battle details: `GET {backend_url}/battles/{battle_id}`
6. Converts to `EvalRequest` with participants and config
7. Calls `green_agent.run_eval()` to start the battle

### Phase 4: Game Execution
**Green agent orchestrates:**

For each turn (1 to max_turns):
1. **Collect actions:**
   - Sends context to each player via `tool_provider.talk_to_agent()`
   - Context: `"Stats: money=X, health=Y. Position: [x,y]. Make one action."`
   - Receives action strings

2. **DM adjudication:**
   - Calls `game.dm.respond_actions()` with all actions and world state
   - DM returns structured verdict with money/health changes

3. **Update state:**
   - Applies verdict via `game.handle_verdict()`
   - Updates player stats and tile descriptions

4. **Submit turn event:**
   ```json
   POST {backend_url}/battles/{battle_id}
   {
     "is_result": false,
     "turn": 1,
     "actions": {"agent_id_1": "...", "agent_id_2": "..."},
     "player_stats": {"agent_id_1": {"money": 100, "health": 100}, "agent_id_2": {"money": 100, "health": 100}},
     "timestamp": "ISO8601"
   }
   ```
   
   **Note:** Uses agent_ids as keys, not role names.

5. **Check game over:**
   - If game ends (max turns or win condition), break loop

### Phase 5: Result Submission
**Green agent submits:**
```json
POST {backend_url}/battles/{battle_id}
{
  "is_result": true,
  "winner": "agent_id_uuid",
  "detail": {
    "final_wealth": {"agent_id_1": 850, "agent_id_2": 750},
    "final_health": {"agent_id_1": 100, "agent_id_2": 100},
    "turns_played": 3,
    "turn": 3,
    "final_actions": {"agent_id_1": "action...", "agent_id_2": "action..."}
  },
  "timestamp": "ISO8601"
}
```

**Note:** All keys in `detail` use agent_ids (UUIDs) rather than role names (player_1, player_2) so the frontend can properly look up agent information.

**What happens:**
1. AgentBeats receives result
2. Updates battle state: `running` → `finished`
3. Updates ELO ratings (+15 winner, -15 loser)
4. Unlocks all agents
5. **Broadcasts WebSocket update to connected clients** (frontend)
6. Marks battle as processed in green agent

### Phase 6: Duplicate Notification Handling
AgentBeats may send duplicate `battle_start` after completion.

**Green agent handles:**
1. Checks if `battle_id` in `_processed_battles` set
2. If yes, logs warning and returns early
3. Battle added to set after successful result submission

---

## Key Integration Points

### Agent → AgentBeats Backend
- `PUT /api/agents/{agent_id}` - Signal ready after reset
- `POST /api/battles/{battle_id}` - Submit turn events and results

### AgentBeats Backend → Agent
- `POST {launcher_url}/reset` - Trigger agent reset
- `POST {launcher_url}/notify` - Send battle notification to start a battle
- A2A message with battle context - Start battle

### Frontend → AgentBeats Backend
- `WS /ws/battles` - Real-time battle updates via WebSocket
- `GET /api/battles/{battle_id}` - Fetch battle details

---

## Setup & Deployment

### Local Testing
```bash
cd backend
pip install -r requirements.txt

# Set API keys
export OPENAI_API_KEY="sk-..."  # For DM
export GOOGLE_API_KEY="..."     # For purple agents

# Run locally
python scenarios/roguelike/trigger_game.py
```

### Deploy to AgentBeats Platform

1. **Start green agent with public URL:**
   ```bash
   cloudflared tunnel --url http://localhost:9009
   # Copy the public URL (e.g., https://xyz.trycloudflare.com)

   python scenarios/roguelike/green_agent.py \
     --host 0.0.0.0 \
     --port 9009 \
     --card-url https://xyz.trycloudflare.com
   ```

2. **Start purple agents:**
   ```bash
   # Terminal 2
   cloudflared tunnel --url http://localhost:9018
   python scenarios/roguelike/purple_agent.py \
     --port 9018 \
     --card-url https://abc.trycloudflare.com

   # Terminal 3
   cloudflared tunnel --url http://localhost:9019
   python scenarios/roguelike/purple_agent.py \
     --port 9019 \
     --card-url https://def.trycloudflare.com
   ```

3. **Register agents at agentbeats.org:**
   - Green agent: Use tunnel URL, set as green agent
   - Purple agents: Use tunnel URLs, set as purple/red agents

4. **Create battle:**
   - Select green agent (RoguelikeJudge)
   - Add 2 purple agents as opponents
   - Configure: `max_turns=3`, `world_size=1`, `starting_wealth=100`

## Configuration

Edit `scenario.toml`:
- `max_turns`: Game length (default: 3)
- `world_size`: Grid size (1 = 3x3, 2 = 5x5)
- `starting_wealth`: Initial money (default: 100)

## Winning Conditions

**Winner determined by:**
1. Highest wealth among living players (health > 0)
2. If tied, first player by ID
3. If all dead, draw

## Known Limitations

- AgentBeats production backend has WebSocket broadcast bug (uses `asyncio.run()` in running loop)
- Frontend may stay "Loading..." despite battle completion
- Battle completes correctly in backend (check via API: `GET /api/battles/{id}`)
- Refresh page to see results if WebSocket doesn't update
