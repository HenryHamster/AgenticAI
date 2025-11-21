#!/bin/bash
# Script to display public URLs for running agents

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
echo -e "${BLUE}  Agent URLs${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

echo -e "${BLUE}Local Endpoints:${NC}"
echo "  Green Agent:      http://localhost:9009"
echo "  Purple Agent 1:   http://localhost:9018"
echo "  Purple Agent 2:   http://localhost:9019"
echo ""

if [ ! -d "logs" ]; then
    echo -e "${RED}✗ No logs directory found. Are agents running?${NC}"
    exit 1
fi

echo -e "${BLUE}Public URLs:${NC}"
echo ""

# Extract URLs from cloudflared logs
if [ -f "logs/cloudflared_green.log" ]; then
    GREEN_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' logs/cloudflared_green.log | head -1)
    if [ -n "$GREEN_URL" ]; then
        echo -e "${GREEN}  Green Agent:      $GREEN_URL${NC}"
    else
        echo -e "${YELLOW}  Green Agent:      URL not available yet${NC}"
    fi
else
    echo -e "${RED}  Green Agent:      Not running${NC}"
fi

if [ -f "logs/cloudflared_purple1.log" ]; then
    PURPLE1_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' logs/cloudflared_purple1.log | head -1)
    if [ -n "$PURPLE1_URL" ]; then
        echo -e "${GREEN}  Purple Agent 1:   $PURPLE1_URL${NC}"
    else
        echo -e "${YELLOW}  Purple Agent 1:   URL not available yet${NC}"
    fi
else
    echo -e "${RED}  Purple Agent 1:   Not running${NC}"
fi

if [ -f "logs/cloudflared_purple2.log" ]; then
    PURPLE2_URL=$(grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' logs/cloudflared_purple2.log | head -1)
    if [ -n "$PURPLE2_URL" ]; then
        echo -e "${GREEN}  Purple Agent 2:   $PURPLE2_URL${NC}"
    else
        echo -e "${YELLOW}  Purple Agent 2:   URL not available yet${NC}"
    fi
else
    echo -e "${RED}  Purple Agent 2:   Not running${NC}"
fi

echo ""

