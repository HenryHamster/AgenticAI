#!/bin/bash
# Complete script to start all agents and expose them via cloudflared

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  Starting All Agents for Roguelike Scenario${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Load environment variables from .env file
if [ -f .env ]; then
    echo -e "${YELLOW}Loading environment variables from .env file...${NC}"
    set -a  # automatically export all variables
    source .env
    set +a
    echo -e "${GREEN}✓ Environment variables loaded${NC}"
    echo ""
else
    echo -e "${YELLOW}⚠ No .env file found${NC}"
    echo "  Create a .env file with your API keys:"
    echo "  OPENAI_API_KEY=your-key-here"
    echo "  GOOGLE_API_KEY=your-key-here"
    echo ""
fi

# Check if required API keys are set
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${RED}✗ OPENAI_API_KEY not set (needed for Green Agent)${NC}"
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo -e "${RED}✗ GOOGLE_API_KEY not set (needed for Purple Agents)${NC}"
fi

echo ""

# Create logs directory
mkdir -p logs

# Step 1: Kill any existing agents
echo -e "${YELLOW}Step 1: Killing existing agents on ports 9009, 9018, 9019...${NC}"
lsof -ti:9009,9018,9019 | xargs kill -9 2>/dev/null || echo "  No existing agents found"
sleep 2
echo -e "${GREEN}✓ Ports cleared${NC}"
echo ""

# Step 2: Kill any existing cloudflared tunnels
echo -e "${YELLOW}Step 2: Killing existing cloudflared tunnels...${NC}"
pkill -f "cloudflared tunnel" 2>/dev/null || echo "  No existing tunnels found"
sleep 1
echo -e "${GREEN}✓ Tunnels cleared${NC}"
echo ""

# Step 3: Start the agents
echo -e "${YELLOW}Step 3: Starting agents...${NC}"

# Start Green Agent (port 9009)
venv/bin/python scenarios/roguelike/green_agent.py --host 0.0.0.0 --port 9009 > logs/green_agent.log 2>&1 &
GREEN_PID=$!
echo $GREEN_PID > logs/green_agent.pid
echo -e "${GREEN}  ✓ Green Agent started (PID: $GREEN_PID)${NC}"
sleep 1

# Start Purple Agent 1 (port 9018)
venv/bin/python scenarios/roguelike/purple_agent.py --host 0.0.0.0 --port 9018 > logs/purple_agent_1.log 2>&1 &
PURPLE1_PID=$!
echo $PURPLE1_PID > logs/purple_agent_1.pid
echo -e "${GREEN}  ✓ Purple Agent 1 started (PID: $PURPLE1_PID)${NC}"
sleep 1

# Start Purple Agent 2 (port 9019)
venv/bin/python scenarios/roguelike/purple_agent.py --host 0.0.0.0 --port 9019 > logs/purple_agent_2.log 2>&1 &
PURPLE2_PID=$!
echo $PURPLE2_PID > logs/purple_agent_2.pid
echo -e "${GREEN}  ✓ Purple Agent 2 started (PID: $PURPLE2_PID)${NC}"
echo ""

# Wait a bit for agents to fully start
echo -e "${YELLOW}Waiting for agents to initialize...${NC}"
sleep 3

# Step 4: Create cloudflared tunnels
echo -e "${YELLOW}Step 4: Creating cloudflared tunnels...${NC}"

if ! command -v cloudflared &> /dev/null; then
    echo -e "${RED}✗ cloudflared not found${NC}"
    echo "  Install with: brew install cloudflared"
    echo ""
    echo -e "${YELLOW}Agents are running on:${NC}"
    echo "  http://localhost:9009 (Green Agent)"
    echo "  http://localhost:9018 (Purple Agent 1)"
    echo "  http://localhost:9019 (Purple Agent 2)"
    exit 0
fi

# Start cloudflared tunnel for Green Agent
cloudflared tunnel --url http://localhost:9009 > logs/cloudflared_green.log 2>&1 &
TUNNEL_GREEN_PID=$!
echo $TUNNEL_GREEN_PID > logs/tunnel_green.pid
echo -e "${GREEN}  ✓ Tunnel for Green Agent started (PID: $TUNNEL_GREEN_PID)${NC}"
sleep 2

# Start cloudflared tunnel for Purple Agent 1
cloudflared tunnel --url http://localhost:9018 > logs/cloudflared_purple1.log 2>&1 &
TUNNEL_PURPLE1_PID=$!
echo $TUNNEL_PURPLE1_PID > logs/tunnel_purple1.pid
echo -e "${GREEN}  ✓ Tunnel for Purple Agent 1 started (PID: $TUNNEL_PURPLE1_PID)${NC}"
sleep 2

# Start cloudflared tunnel for Purple Agent 2
cloudflared tunnel --url http://localhost:9019 > logs/cloudflared_purple2.log 2>&1 &
TUNNEL_PURPLE2_PID=$!
echo $TUNNEL_PURPLE2_PID > logs/tunnel_purple2.pid
echo -e "${GREEN}  ✓ Tunnel for Purple Agent 2 started (PID: $TUNNEL_PURPLE2_PID)${NC}"
echo ""

# Wait for tunnels to establish
echo -e "${YELLOW}Waiting for tunnels to establish (5 seconds)...${NC}"
sleep 5

# Step 5: Extract and display public URLs
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}✅ All agents started and exposed!${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

echo -e "${BLUE}Local Endpoints:${NC}"
echo "  Green Agent:      http://localhost:9009"
echo "  Purple Agent 1:   http://localhost:9018"
echo "  Purple Agent 2:   http://localhost:9019"
echo ""

echo -e "${BLUE}Public URLs (extracting from cloudflared logs):${NC}"
echo ""

# Extract URLs from cloudflared logs
sleep 2
if grep -q "trycloudflare.com" logs/cloudflared_green.log; then
    GREEN_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' logs/cloudflared_green.log | head -1)
    echo -e "${GREEN}  Green Agent:      $GREEN_URL${NC}"
else
    echo -e "${YELLOW}  Green Agent:      Waiting for URL...${NC}"
fi

if grep -q "trycloudflare.com" logs/cloudflared_purple1.log; then
    PURPLE1_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' logs/cloudflared_purple1.log | head -1)
    echo -e "${GREEN}  Purple Agent 1:   $PURPLE1_URL${NC}"
else
    echo -e "${YELLOW}  Purple Agent 1:   Waiting for URL...${NC}"
fi

if grep -q "trycloudflare.com" logs/cloudflared_purple2.log; then
    PURPLE2_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' logs/cloudflared_purple2.log | head -1)
    echo -e "${GREEN}  Purple Agent 2:   $PURPLE2_URL${NC}"
else
    echo -e "${YELLOW}  Purple Agent 2:   Waiting for URL...${NC}"
fi

echo ""
echo -e "${BLUE}Process IDs:${NC}"
echo "  Green Agent:      $GREEN_PID"
echo "  Purple Agent 1:   $PURPLE1_PID"
echo "  Purple Agent 2:   $PURPLE2_PID"
echo "  Tunnel Green:     $TUNNEL_GREEN_PID"
echo "  Tunnel Purple 1:  $TUNNEL_PURPLE1_PID"
echo "  Tunnel Purple 2:  $TUNNEL_PURPLE2_PID"
echo ""

echo -e "${BLUE}Logs Directory:${NC}"
echo "  $SCRIPT_DIR/logs"
echo ""

echo -e "${YELLOW}To view logs in real-time:${NC}"
echo "  tail -f logs/*.log"
echo ""

echo -e "${YELLOW}To view public URLs (if not shown above):${NC}"
echo "  cat logs/cloudflared_green.log | grep trycloudflare.com"
echo "  cat logs/cloudflared_purple1.log | grep trycloudflare.com"
echo "  cat logs/cloudflared_purple2.log | grep trycloudflare.com"
echo ""

echo -e "${YELLOW}To stop all agents and tunnels:${NC}"
echo "  ./stop_agents.sh"
echo ""

echo -e "${YELLOW}To test the setup:${NC}"
echo "  python scenarios/roguelike/trigger_game.py"
echo ""

