# Coolify Deployment Guide - Separate Agent Containers

This guide explains how to deploy AgenticAI agents to Coolify using the **AgentBeats integration pattern**. Each agent runs in its own Docker container with the `earthshaker` controller for lifecycle management.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        Coolify / Cloud Run                          │
│                                                                     │
│  ┌─────────────────────────────┐  ┌─────────────────────────────┐  │
│  │     Green Agent Container    │  │     White Agent Container    │  │
│  │                              │  │                              │  │
│  │  ┌────────────────────────┐ │  │  ┌────────────────────────┐ │  │
│  │  │  AgentBeats Controller │ │  │  │  AgentBeats Controller │ │  │
│  │  │  (earthshaker)         │ │  │  │  (earthshaker)         │ │  │
│  │  │  - /status             │ │  │  │  - /status             │ │  │
│  │  │  - /reset              │ │  │  │  - /reset              │ │  │
│  │  │  - Agent proxy         │ │  │  │  - Agent proxy         │ │  │
│  │  └──────────┬─────────────┘ │  │  └──────────┬─────────────┘ │  │
│  │             │               │  │             │               │  │
│  │  ┌──────────▼─────────────┐ │  │  ┌──────────▼─────────────┐ │  │
│  │  │    Green Agent         │ │  │  │    White Agent         │ │  │
│  │  │    (run.sh → :9009)    │ │  │  │    (run.sh → :9018)    │ │  │
│  │  │    Game Judge          │ │  │  │    Player Agent        │ │  │
│  │  └────────────────────────┘ │  │  └────────────────────────┘ │  │
│  │                              │  │                              │  │
│  │  Port: 8080                  │  │  Port: 8081                  │  │
│  └─────────────────────────────┘  └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## AgentBeats Integration

This deployment follows the [AgentBeats integration pattern](https://agentbeats.org):

1. **AgentBeats Controller** (`earthshaker`) - Manages agent lifecycle
2. **run.sh** - Defines how to start the agent
3. **Procfile** - Entry point for cloud deployments

Each agent container:
- Exposes a controller API for status/reset
- Proxies requests to the internal agent
- Supports automatic restart and health checks

## Endpoints

| Agent | URL | Description |
|-------|-----|-------------|
| Green Agent | `https://green.your-domain.com/` | Game judge/orchestrator |
| White Agent | `https://white.your-domain.com/` | Player agent |

Each agent exposes:
- `/status` - Agent health status
- `/reset` - Reset agent state
- `/.well-known/agent.json` - A2A agent card

## Deployment Steps

### Option 1: Deploy via Docker Compose (Recommended)

1. **Connect Repository** in Coolify
   - Go to **Projects** → **New Resource** → **Public/Private Repository**
   - Connect your GitHub/GitLab repository

2. **Configure Build Settings**
   - **Build Pack**: Docker Compose
   - **Docker Compose File**: `docker-compose.coolify.yml`
   - **Base Directory**: `/` (root of repository)

3. **Set Environment Variables**
   ```
   GREEN_AGENT_URL=https://green.your-domain.com
   WHITE_AGENT_URL=https://white.your-domain.com
   OPENAI_API_KEY=sk-your-openai-key
   GOOGLE_API_KEY=your-google-api-key
   CLAUDE_API_KEY=your-claude-key (optional)
   ```

4. **Configure Domains**
   - Add separate domains for each agent container
   - Coolify will automatically provision SSL

5. **Deploy**

### Option 2: Deploy Individual Agents

Deploy each agent as a separate service:

**Green Agent:**
```bash
# Build
docker build -f coolify/green_agent/Dockerfile -t green-agent .

# Run
docker run -p 8080:8080 \
  -e PUBLIC_URL=https://green.your-domain.com \
  -e OPENAI_API_KEY=your-key \
  green-agent
```

**White Agent:**
```bash
# Build
docker build -f coolify/white_agent/Dockerfile -t white-agent .

# Run
docker run -p 8081:8080 \
  -e PUBLIC_URL=https://white.your-domain.com \
  -e GOOGLE_API_KEY=your-key \
  white-agent
```

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `PUBLIC_URL` | Yes | Public URL for agent card discovery |
| `GREEN_AGENT_URL` | Yes* | Green agent public URL (docker-compose) |
| `WHITE_AGENT_URL` | Yes* | White agent public URL (docker-compose) |
| `OPENAI_API_KEY` | Yes | OpenAI API key for Green Agent |
| `GOOGLE_API_KEY` | Yes | Google API key for agents (Gemini) |
| `CLAUDE_API_KEY` | No | Anthropic API key (optional) |
| `CONTROLLER_PORT` | No | Controller port (default: 8080) |
| `HOST` | No | Bind host (default: 0.0.0.0) |

## Testing the Deployment

```bash
# Check Green Agent
curl https://green.your-domain.com/status

# Check White Agent  
curl https://white.your-domain.com/status

# Get agent cards
curl https://green.your-domain.com/.well-known/agent.json
curl https://white.your-domain.com/.well-known/agent.json

# Reset an agent
curl -X POST https://green.your-domain.com/reset
```

Expected status response:
```json
{
  "status": "server up, with agent running"
}
```

## Publishing to AgentBeats

Once deployed, publish your agents on AgentBeats:

1. Go to [AgentBeats](https://agentbeats.org)
2. Fill out the agent registration form
3. Enter your public controller URL:
   - Green Agent: `https://green.your-domain.com`
   - White Agent: `https://white.your-domain.com`

## Local Development
See [Local Dev Setup](../LOCAL_DEV_SETUP.md) for running this setup on docker compose locally.

## Viewing Logs

### In Coolify
- EarthShaker controller exposes the logs for the green and agents on the respective `/info` endpoint. You can view the logs by going to `https://green.your-domain.com/info` and `https://green.your-domain.com/info`, then click on the controller interface at the bottom, which will show you the logs.

## Troubleshooting

### Agent not starting
1. Check container logs: `docker logs <container>`
2. Verify `run.sh` is executable
3. Ensure API keys are set

### Controller not responding
1. Check PORT environment variable
2. Verify earthshaker is installed: `pip show earthshaker`

### Agent card not found
1. Verify PUBLIC_URL is set correctly
2. Check `/.well-known/agent.json` endpoint

## Files Reference

```
docker-compose.coolify.agents.yml          # Multi-container deployment

coolify/
├── README.md                       # This file
├── green_agent/
│   ├── Dockerfile                  # Green agent container
│   ├── run.sh                      # Agent launch script
│   ├── requirements.txt            # Python dependencies
│   └── Procfile                    # Cloud Run entry point
└── white_agent/
    ├── Dockerfile                  # White agent container
    ├── run.sh                      # Agent launch script
    ├── requirements.txt            # Python dependencies
    └── Procfile                    # Cloud Run entry point


backend/scenarios/roguelike/
├── green_agent.py                  # Green Agent implementation
└── purple_agent.py                 # Player agent implementation
```
