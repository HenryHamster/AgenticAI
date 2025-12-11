#!/bin/bash
set -e

# AgentBeats controller sets HOST and AGENT_PORT environment variables
HOST="${HOST:-0.0.0.0}"
AGENT_PORT="${AGENT_PORT:-9009}"

echo "Starting Green Agent on ${HOST}:${AGENT_PORT}"

# Build command
CMD="python scenarios/roguelike/green_agent.py --host $HOST --port $AGENT_PORT"

# Add card-url if PUBLIC_URL is set (for agent card discovery)
if [ -n "$PUBLIC_URL" ]; then
    CMD="$CMD --card-url $PUBLIC_URL"
fi

exec $CMD
