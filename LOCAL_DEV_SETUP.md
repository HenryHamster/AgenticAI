# Local Development Setup with Cloudflare Tunnels

This guide explains how to run multiple agents locally using Docker Compose and expose them via Cloudflare tunnels.

## Architecture

Each agent runs `agentbeats run_ctrl` internally on port 8010. Docker maps these to different external ports:

| Agent         | Internal Port | External Port | Purpose              |
|---------------|---------------|---------------|----------------------|
| green_agent   | 8010          | 8011          | Game Judge           |
| white_agent_1 | 8010          | 8012          | Player Agent 1       |
| white_agent_2 | 8010          | 8013          | Player Agent 2       |

## Prerequisites

1. Docker and Docker Compose installed
2. Cloudflare CLI (`cloudflared`) installed:
   ```bash
   # macOS
   brew install cloudflared
   
   # Or download from https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
   ```

## Quick Start (Automated)

Use the `start-local-tunnels.sh` script to automatically start all tunnels and generate the `.env.local` file:

### 1. Make the script executable (one-time)

```bash
chmod +x start-local-tunnels.sh
```

### 2. Start the tunnels

```bash
./start-local-tunnels.sh
```

This will:
- Start 3 Cloudflare tunnels (one for each agent)
- Wait for tunnel URLs to be assigned
- Write the URLs to `.env.local`
- Display the tunnel URLs
- Keep running to maintain the tunnels (Ctrl+C to stop)


### 4. Update environment variables (optional)

If you need the agents to know their public URLs for agent card discovery, create a `.env.local` file:

```bash
# .env.local
GREEN_AGENT_URL=https://your-green-tunnel.trycloudflare.com
GREEN_AGENT_URL_NO_PROTOCOL=your-green-tunnel.trycloudflare.com
WHITE_AGENT_1_URL=https://your-white1-tunnel.trycloudflare.com
WHITE_AGENT_1_URL_NO_PROTOCOL=your-white1-tunnel.trycloudflare.com
WHITE_AGENT_2_URL=https://your-white2-tunnel.trycloudflare.com
WHITE_AGENT_2_URL_NO_PROTOCOL=your-white2-tunnel.trycloudflare.com
HTTPS_ENABLED=true

# API Keys
OPENAI_API_KEY=your-key
GOOGLE_API_KEY=your-key
```


### 3. Start Docker containers (in another terminal)

```bash
docker compose -f docker-compose.local.yml --env-file .env.local up --build
```


## Verifying the Setup

Check each agent's status:

```bash
# Green Agent
curl http://localhost:8011/status

# White Agent 1
curl http://localhost:8012/status

# White Agent 2
curl http://localhost:8013/status
```

You can also open the controller link in your browser
[Green agent](http://localhost:8011)
[White agent 1](http://localhost:8012)
[White agent 2](http://localhost:8013)

## Stopping

```bash
docker compose -f docker-compose.local.yml down
```


## Troubleshooting

- **Port already in use**: Change the external ports in `docker-compose.local.yml` (e.g., 8021, 8022, 8023)
- **Container won't start**: Check logs with `docker compose -f docker-compose.local.yml logs <service_name>`
- **Cloudflare tunnel disconnects**: The free tunnels are temporary; restart the tunnel command to get a new URL
