# Coolify Deployment Guide - Multi-Agent Container

This guide explains how to deploy the AgenticAI agents (1 Green Agent + 2 Purple Agents) to Coolify in a single Docker container with sub-URL routing.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Container                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │                  nginx (port 80)                 │   │
│  │                                                  │   │
│  │  /green/*   → Green Agent (port 9009)           │   │
│  │  /purple1/* → Purple Agent 1 (port 9018)        │   │
│  │  /purple2/* → Purple Agent 2 (port 9019)        │   │
│  │  /health    → Health check endpoint             │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│  │ Green Agent  │ │ Purple Agent │ │ Purple Agent │    │
│  │   :9009      │ │   1 :9018    │ │   2 :9019    │    │
│  └──────────────┘ └──────────────┘ └──────────────┘    │
│                                                         │
│  Managed by: supervisord                               │
└─────────────────────────────────────────────────────────┘
```

## Endpoints

Once deployed, your agents will be available at:

| Agent | Endpoint | Description |
|-------|----------|-------------|
| Green Agent | `https://your-domain.com/green/` | Game judge/orchestrator |
| Purple Agent 1 | `https://your-domain.com/purple1/` | Player agent 1 |
| Purple Agent 2 | `https://your-domain.com/purple2/` | Player agent 2 |
| Health Check | `https://your-domain.com/health` | Container health status |

## Deployment Steps

### Option 1: Deploy via Coolify Git Repository

1. **Connect Repository**
   - In Coolify, go to **Projects** → **New Resource** → **Public/Private Repository**
   - Connect your GitHub/GitLab repository containing this code

2. **Configure Build Settings**
   - **Build Pack**: Docker Compose
   - **Docker Compose File**: `coolify/docker-compose.yml`
   - **Base Directory**: `/` (root of repository)

3. **Set Environment Variables**
   In Coolify's environment variables section, add:
   ```
   PUBLIC_URL=https://your-domain.com
   OPENAI_API_KEY=sk-your-openai-key
   GOOGLE_API_KEY=your-google-api-key
   CLAUDE_API_KEY=your-claude-key (optional)
   ```

4. **Configure Domain**
   - Add your domain in the **Domains** section
   - Coolify will automatically provision SSL via Let's Encrypt

5. **Deploy**
   - Click **Deploy** and wait for the build to complete

### Option 2: Deploy via Dockerfile Directly

1. **Create New Resource**
   - In Coolify: **Projects** → **New Resource** → **Docker Image**

2. **Configure Build**
   - **Dockerfile Location**: `coolify/Dockerfile`
   - **Build Context**: `/` (root of repository)

3. **Set Environment Variables** (same as Option 1)

4. **Configure Port**
   - Expose port **80** (nginx handles internal routing)

5. **Deploy**

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `PUBLIC_URL` | Yes | Your public domain URL (e.g., `https://agents.example.com`) |
| `OPENAI_API_KEY` | Yes | OpenAI API key for Green Agent |
| `GOOGLE_API_KEY` | Yes | Google API key for Purple Agents (Gemini) |
| `CLAUDE_API_KEY` | No | Anthropic API key (optional) |

## Testing the Deployment

After deployment, verify each agent is running:

```bash
# Check overall health
curl https://your-domain.com/health

# Check Green Agent
curl https://your-domain.com/green/status

# Check Purple Agent 1
curl https://your-domain.com/purple1/status

# Check Purple Agent 2
curl https://your-domain.com/purple2/status
```

Expected health response:
```json
{
  "status": "healthy",
  "agents": ["green", "purple1", "purple2"]
}
```

## Agent Card URLs

When registering agents with AgentBeats or other A2A systems, use these URLs:

- **Green Agent Card**: `https://your-domain.com/green/.well-known/agent.json`
- **Purple Agent 1 Card**: `https://your-domain.com/purple1/.well-known/agent.json`
- **Purple Agent 2 Card**: `https://your-domain.com/purple2/.well-known/agent.json`

## Local Testing

Before deploying to Coolify, test locally from the repository root:

```bash
# Build the image (from repo root)
docker build -f coolify/Dockerfile -t agenticai-agents .

# Run with environment variables
docker run -p 80:80 \
  -e PUBLIC_URL=http://localhost \
  -e OPENAI_API_KEY=your-key \
  -e GOOGLE_API_KEY=your-key \
  agenticai-agents

# Or use docker-compose (from repo root)
PUBLIC_URL=http://localhost \
OPENAI_API_KEY=your-key \
GOOGLE_API_KEY=your-key \
docker-compose -f coolify/docker-compose.yml up --build
```

## Viewing Logs

### In Coolify
- Go to your resource → **Logs** tab
- Select the container to view real-time logs

### Inside Container
```bash
# Supervisor logs
docker exec <container_id> cat /var/log/supervisord.log

# Individual agent logs
docker exec <container_id> cat /var/log/agents/green_agent.log
docker exec <container_id> cat /var/log/agents/purple_agent_1.log
docker exec <container_id> cat /var/log/agents/purple_agent_2.log

# Nginx logs
docker exec <container_id> cat /var/log/nginx/access.log
docker exec <container_id> cat /var/log/nginx/error.log
```

## Troubleshooting

### Agents not starting
1. Check supervisor logs: `docker exec <container> cat /var/log/supervisord.log`
2. Verify environment variables are set correctly
3. Ensure API keys are valid

### 502 Bad Gateway
1. Agent may still be starting - wait 15-30 seconds
2. Check individual agent logs for errors
3. Verify the agent process is running: `docker exec <container> supervisorctl status`

### Health check failing
1. Ensure port 80 is exposed
2. Check nginx is running: `docker exec <container> nginx -t`
3. Verify all agents are healthy via supervisor

## Scaling Considerations

This setup runs all agents in a single container. For production scaling:

1. **Horizontal Scaling**: Deploy multiple instances of this container behind a load balancer
2. **Separate Containers**: Split each agent into its own container for independent scaling
3. **Resource Limits**: Set CPU/memory limits in Coolify based on your workload

## Files Reference

```
coolify/
├── Dockerfile                 # Multi-agent Dockerfile
├── docker-compose.yml         # Docker Compose for Coolify
├── README.md                  # This file
└── docker/
    ├── nginx.conf            # Nginx reverse proxy config
    └── supervisord.conf      # Process manager config

backend/scenarios/roguelike/
├── green_agent.py            # Green Agent implementation
└── purple_agent.py           # Purple Agent implementation
```
