#!/bin/bash
set -e

# AgentBeats controller sets HOST and AGENT_PORT environment variables
HOST="${HOST:-0.0.0.0}"
AGENT_PORT="${AGENT_PORT:-9018}"

echo "Starting White Agent on ${HOST}:${AGENT_PORT}"

# Build command - use relative path if running locally
if [ -n "$LOCAL" ]; then
    CMD="python ../../backend/scenarios/roguelike/purple_agent.py --host $HOST --port $AGENT_PORT"
else
    CMD="python scenarios/roguelike/purple_agent.py --host $HOST --port $AGENT_PORT"
fi

# Add card-url if AGENT_URL is set (for agent card discovery)
if [ -n "$AGENT_URL" ]; then
    CMD="$CMD --card-url $AGENT_URL"
fi

exec $CMD
