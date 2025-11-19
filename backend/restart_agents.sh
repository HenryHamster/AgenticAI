#!/bin/bash
# Quick restart script for agents

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}  Restarting All Agents${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# Stop agents
echo -e "${YELLOW}Stopping agents...${NC}"
./stop_agents.sh

echo ""
echo -e "${YELLOW}Waiting 2 seconds...${NC}"
sleep 2
echo ""

# Start agents
echo -e "${YELLOW}Starting agents with new code...${NC}"
./start_agents.sh

echo ""
echo -e "${GREEN}✅ Restart complete!${NC}"

