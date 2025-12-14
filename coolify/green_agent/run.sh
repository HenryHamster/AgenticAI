#!/bin/bash
set -e

# AgentBeats controller sets HOST and AGENT_PORT environment variables
HOST="${HOST:-0.0.0.0}"
AGENT_PORT="${AGENT_PORT:-9009}"

echo "Starting Green Agent on ${HOST}:${AGENT_PORT}"
# Build command - use relative path if running locally
if [ -n "$LOCAL" ]; then
    CMD="python ../../backend/scenarios/roguelike/green_agent.py --host $HOST --port $AGENT_PORT"
else
    CMD="python scenarios/roguelike/green_agent.py --host $HOST --port $AGENT_PORT"
fi


exec $CMD
