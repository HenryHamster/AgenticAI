# Agent Management Scripts - Quick Start

Three simple scripts to manage your roguelike agents:

## 🚀 Start All Agents

```bash
./start_agents.sh
```

This script will:
1. ✅ Kill any existing agents on ports 9009, 9018, 9019
2. ✅ Kill any existing cloudflared tunnels
3. ✅ Start 3 agents (1 Green + 2 Purple)
4. ✅ Create cloudflared tunnels to expose them publicly
5. ✅ Display all local and public URLs

## 🛑 Stop All Agents

```bash
./stop_agents.sh
```

This script will:
1. ✅ Stop all running agents gracefully
2. ✅ Force kill any remaining processes on the ports
3. ✅ Stop all cloudflared tunnels
4. ✅ Optionally clean up log files

## 🔗 Show URLs

```bash
./show_urls.sh
```

This script displays:
- Local endpoints (localhost URLs)
- Public URLs (cloudflared tunnel URLs)

## 📋 Agents Started

| Agent | Port | URL |
|-------|------|-----|
| Green Agent (RoguelikeJudge) | 9009 | http://localhost:9009 |
| Purple Agent 1 (Player 1) | 9018 | http://localhost:9018 |
| Purple Agent 2 (Player 2) | 9019 | http://localhost:9019 |

## 📝 Logs

All logs are saved in the `logs/` directory:

```bash
# View all logs in real-time
tail -f logs/*.log

# View specific agent
tail -f logs/green_agent.log
tail -f logs/purple_agent_1.log
tail -f logs/purple_agent_2.log

# View cloudflared tunnels
tail -f logs/cloudflared_*.log
```

## 🧪 Testing

After starting agents, test them with:

```bash
python scenarios/roguelike/trigger_game.py
```

Or test individual endpoints:

```bash
curl http://localhost:9009/health  # Green agent
curl http://localhost:9018/health  # Purple agent 1
curl http://localhost:9019/health  # Purple agent 2
```

## 🔑 API Keys Setup

### Option 1: Using .env file (RECOMMENDED)

Create a `.env` file in the backend directory:

```bash
cp env.example .env
# Then edit .env with your actual API keys
```

Your `.env` file should contain:

```bash
OPENAI_API_KEY=your-openai-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
```

The `start_agents.sh` script will **automatically load** these variables!

### Option 2: Export manually

```bash
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"
```

Or add to your `~/.zshrc`:

```bash
echo 'export OPENAI_API_KEY="your-openai-key"' >> ~/.zshrc
echo 'export GOOGLE_API_KEY="your-google-key"' >> ~/.zshrc
source ~/.zshrc
```

## 🔧 Troubleshooting

### Ports already in use
```bash
./stop_agents.sh  # This will clean up everything
./start_agents.sh  # Then start fresh
```

### Can't see public URLs
```bash
./show_urls.sh  # Wait a few seconds and run again
cat logs/cloudflared_*.log | grep trycloudflare  # Or check logs directly
```

### Agents not responding
```bash
tail -f logs/*.log  # Check logs for errors
```

## 📦 What's Running

After `./start_agents.sh`:
- 3 Python agent processes (background)
- 3 Cloudflared tunnel processes (background)
- All PIDs saved in `logs/*.pid`

You can safely close your terminal - everything runs in the background!

