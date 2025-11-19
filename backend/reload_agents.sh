#!/bin/bash
# Hot reload agents WITHOUT closing cloudflared tunnels
# This preserves the public URLs

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  Hot Reloading Agents (Keeping Tunnels Alive)${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Load environment variables from .env file
if [ -f .env ]; then
    echo -e "${YELLOW}Loading environment variables from .env file...${NC}"
    set -a
    source .env
    set +a
    echo -e "${GREEN}✓ Environment variables loaded${NC}"
else
    echo -e "${YELLOW}⚠ No .env file found${NC}"
fi
echo ""

# Step 1: Kill only the Python agent processes (not cloudflared)
echo -e "${YELLOW}Step 1: Stopping Python agent processes...${NC}"

# Kill agents using PID files
if [ -f logs/green_agent.pid ]; then
    GREEN_PID=$(cat logs/green_agent.pid)
    kill $GREEN_PID 2>/dev/null && echo -e "${GREEN}  ✓ Stopped Green Agent (PID: $GREEN_PID)${NC}" || echo -e "${YELLOW}  ⚠ Green Agent already stopped${NC}"
fi

if [ -f logs/purple_agent_1.pid ]; then
    PURPLE1_PID=$(cat logs/purple_agent_1.pid)
    kill $PURPLE1_PID 2>/dev/null && echo -e "${GREEN}  ✓ Stopped Purple Agent 1 (PID: $PURPLE1_PID)${NC}" || echo -e "${YELLOW}  ⚠ Purple Agent 1 already stopped${NC}"
fi

if [ -f logs/purple_agent_2.pid ]; then
    PURPLE2_PID=$(cat logs/purple_agent_2.pid)
    kill $PURPLE2_PID 2>/dev/null && echo -e "${GREEN}  ✓ Stopped Purple Agent 2 (PID: $PURPLE2_PID)${NC}" || echo -e "${YELLOW}  ⚠ Purple Agent 2 already stopped${NC}"
fi

# Fallback: force kill any remaining Python agent processes on these ports
lsof -ti:9009 | xargs kill -9 2>/dev/null || true
lsof -ti:9018 | xargs kill -9 2>/dev/null || true
lsof -ti:9019 | xargs kill -9 2>/dev/null || true

sleep 2
echo -e "${GREEN}✓ All agent processes stopped${NC}"
echo ""

# Step 2: Extract existing cloudflared URLs (tunnels still running!)
echo -e "${YELLOW}Step 2: Extracting existing tunnel URLs...${NC}"

GREEN_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' logs/cloudflared_green.log | head -1 || echo "")
PURPLE1_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' logs/cloudflared_purple1.log | head -1 || echo "")
PURPLE2_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' logs/cloudflared_purple2.log | head -1 || echo "")

if [ -z "$GREEN_URL" ] || [ -z "$PURPLE1_URL" ] || [ -z "$PURPLE2_URL" ]; then
    echo -e "${RED}✗ Could not find all tunnel URLs!${NC}"
    echo "  Make sure cloudflared tunnels are running."
    echo "  Run ./start_agents.sh to start everything from scratch."
    exit 1
fi

echo -e "${GREEN}  ✓ Green:   $GREEN_URL${NC}"
echo -e "${GREEN}  ✓ Purple1: $PURPLE1_URL${NC}"
echo -e "${GREEN}  ✓ Purple2: $PURPLE2_URL${NC}"
echo ""

# Step 3: Restart agents with the SAME public URLs
echo -e "${YELLOW}Step 3: Starting agents with existing public URLs...${NC}"

# Archive old logs
mv logs/green_agent.log logs/green_agent.log.old 2>/dev/null || true
mv logs/purple_agent_1.log logs/purple_agent_1.log.old 2>/dev/null || true
mv logs/purple_agent_2.log logs/purple_agent_2.log.old 2>/dev/null || true

# Start Green Agent with same URL
venv/bin/python scenarios/roguelike/green_agent.py --host 0.0.0.0 --port 9009 --card-url "$GREEN_URL" > logs/green_agent.log 2>&1 &
GREEN_PID=$!
echo $GREEN_PID > logs/green_agent.pid
echo -e "${GREEN}  ✓ Green Agent started (PID: $GREEN_PID, URL: $GREEN_URL)${NC}"
sleep 1

# Start Purple Agent 1 with same URL
venv/bin/python scenarios/roguelike/purple_agent.py --host 0.0.0.0 --port 9018 --card-url "$PURPLE1_URL" > logs/purple_agent_1.log 2>&1 &
PURPLE1_PID=$!
echo $PURPLE1_PID > logs/purple_agent_1.pid
echo -e "${GREEN}  ✓ Purple Agent 1 started (PID: $PURPLE1_PID, URL: $PURPLE1_URL)${NC}"
sleep 1

# Start Purple Agent 2 with same URL
venv/bin/python scenarios/roguelike/purple_agent.py --host 0.0.0.0 --port 9019 --card-url "$PURPLE2_URL" > logs/purple_agent_2.log 2>&1 &
PURPLE2_PID=$!
echo $PURPLE2_PID > logs/purple_agent_2.pid
echo -e "${GREEN}  ✓ Purple Agent 2 started (PID: $PURPLE2_PID, URL: $PURPLE2_URL)${NC}"
echo ""

# Wait for agents to initialize
echo -e "${YELLOW}Waiting for agents to initialize...${NC}"
sleep 3

# Step 4: Verify agents are running
echo -e "${YELLOW}Step 4: Verifying agents...${NC}"

check_agent() {
    local port=$1
    local name=$2
    if lsof -ti:$port > /dev/null 2>&1; then
        echo -e "${GREEN}  ✓ $name is running on port $port${NC}"
        return 0
    else
        echo -e "${RED}  ✗ $name failed to start on port $port${NC}"
        return 1
    fi
}

ALL_OK=true
check_agent 9009 "Green Agent" || ALL_OK=false
check_agent 9018 "Purple Agent 1" || ALL_OK=false
check_agent 9019 "Purple Agent 2" || ALL_OK=false
echo ""

if [ "$ALL_OK" = true ]; then
    echo -e "${GREEN}============================================================${NC}"
    echo -e "${GREEN}✅ Hot reload complete! Tunnels preserved!${NC}"
    echo -e "${GREEN}============================================================${NC}"
    echo ""
    echo -e "${BLUE}Public URLs (UNCHANGED):${NC}"
    echo "  Green:   $GREEN_URL"
    echo "  Purple1: $PURPLE1_URL"
    echo "  Purple2: $PURPLE2_URL"
    echo ""
    echo -e "${YELLOW}Check logs:${NC}"
    echo "  tail -f logs/green_agent.log"
    echo "  tail -f logs/purple_agent_1.log"
    echo "  tail -f logs/purple_agent_2.log"
else
    echo -e "${RED}============================================================${NC}"
    echo -e "${RED}⚠ Some agents failed to start. Check logs:${NC}"
    echo -e "${RED}============================================================${NC}"
    echo "  tail -50 logs/green_agent.log"
    echo "  tail -50 logs/purple_agent_1.log"
    echo "  tail -50 logs/purple_agent_2.log"
fi
echo ""

