#!/bin/bash
# Script to stop all agents and cloudflared tunnels

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
echo -e "${BLUE}  Stopping All Agents and Tunnels${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Step 1: Stop agents by PID files
echo -e "${YELLOW}Step 1: Stopping agents...${NC}"

if [ -d "logs" ]; then
    for pid_file in logs/*.pid; do
        if [ -f "$pid_file" ]; then
            PID=$(cat "$pid_file")
            NAME=$(basename "$pid_file" .pid)
            
            if kill -0 $PID 2>/dev/null; then
                kill $PID 2>/dev/null
                echo -e "${GREEN}  ✓ Stopped $NAME (PID: $PID)${NC}"
            else
                echo -e "${YELLOW}  ℹ $NAME (PID: $PID) not running${NC}"
            fi
            
            rm "$pid_file"
        fi
    done
else
    echo -e "${YELLOW}  No PID files found${NC}"
fi

# Step 2: Force kill any remaining processes on ports
echo ""
echo -e "${YELLOW}Step 2: Force killing processes on ports 9009, 9018, 9019...${NC}"
KILLED=$(lsof -ti:9009,9018,9019 2>/dev/null | xargs kill -9 2>/dev/null && echo "true" || echo "false")
if [ "$KILLED" = "true" ]; then
    echo -e "${GREEN}  ✓ Force killed remaining processes${NC}"
else
    echo -e "${GREEN}  ✓ No remaining processes on ports${NC}"
fi

# Step 3: Stop cloudflared tunnels
echo ""
echo -e "${YELLOW}Step 3: Stopping cloudflared tunnels...${NC}"
KILLED_TUNNELS=$(pkill -f "cloudflared tunnel" 2>/dev/null && echo "true" || echo "false")
if [ "$KILLED_TUNNELS" = "true" ]; then
    echo -e "${GREEN}  ✓ Stopped all cloudflared tunnels${NC}"
else
    echo -e "${GREEN}  ✓ No cloudflared tunnels running${NC}"
fi

# Step 4: Ask about log cleanup
echo ""
echo -e "${YELLOW}Step 4: Log cleanup${NC}"
if [ -d "logs" ] && [ "$(ls -A logs/*.log 2>/dev/null)" ]; then
    read -p "Do you want to delete log files? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f logs/*.log
        echo -e "${GREEN}  ✓ Logs deleted${NC}"
    else
        echo -e "${YELLOW}  ℹ Logs kept${NC}"
    fi
else
    echo -e "${GREEN}  ✓ No logs to clean${NC}"
fi

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}✅ All agents and tunnels stopped${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

