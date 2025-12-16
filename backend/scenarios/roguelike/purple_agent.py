"""Purple Agent - ADK Implementation"""

import argparse
import uvicorn
import json
import logging
import os
import httpx
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from starlette.routing import Route

load_dotenv()

from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCapabilities, AgentCard
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("roguelike_judge")

from a2a.types import AgentCapabilities, AgentCard, AgentSkill

AGENT_DESCRIPTION = '''
## Your Role
You are a strategic player agent in a roguelike economy game. Your goal is to maximize your wealth while surviving.

## Game Rules
1. You start with initial money and health on a grid-based world.
2. Each turn, you can take ONE action: move (north/south/east/west), explore, search, trade, or interact with tiles.
3. The Dungeon Master (DM) will evaluate your actions and update your stats (money, health).
4. You compete against another player agent - the winner is whoever has the most wealth while still alive.
5. If your health drops to 0, you are eliminated.

## How to Play
- Respond with ONE short action sentence per turn
- Examples: "Move north to explore", "Search this tile for resources", "Trade with the merchant"
- Be strategic about risk vs reward - some tiles may be dangerous but lucrative
'''

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9018)
    parser.add_argument("--card-url", type=str, help="Public URL for agent card")
    args = parser.parse_args()

    agent = Agent(
        name="player",
        model="gemini-2.0-flash",
        description="Strategic player in roguelike economy game",
        instruction="You are a strategic player. Maximize wealth by exploring tiles and making smart decisions. Respond with ONE short action sentence like 'Move north to explore' or 'Search for resources'.",
    )

    # Use public URL if provided
    if args.card_url:
        base_url = args.card_url.rstrip('/')
        logger.info(f"Using public URL from --card-url: {base_url}")
    else:
        base_url = f"http://{args.host}:{args.port}"

    player_skill = AgentSkill(
        id="roguelike_player_action",
        name="Roguelike Player Action",
        description="Generate strategic actions to maximize wealth in a roguelike economy game. The agent receives game state (stats, position) and returns a single action.",
        tags=["game", "strategy", "roguelike", "a2a"],
        examples=[
            "Move north to explore the unknown tile",
            "Search this area for hidden resources",
            "Trade goods with the merchant for profit"
        ]
    )

    card = AgentCard(
        name="player",
        description="Roguelike economy player",
        url=agent_url,
        description=AGENT_DESCRIPTION,
        url=base_url,
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[],
        skills=[player_skill]
    )

    app = to_a2a(agent, agent_card=card)

    # Serialize agent card for registration
    card_dict = {
        "name": card.name,
        "description": card.description,
        "url": card.url,
        "version": card.version,
        "defaultInputModes": card.default_input_modes,
        "defaultOutputModes": card.default_output_modes,
        "capabilities": {"streaming": card.capabilities.streaming} if card.capabilities else {},
        "skills": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "tags": s.tags,
                "examples": s.examples
            } for s in (card.skills or [])
        ]
    }

    # Add status, reset, and agent-card endpoints
    async def status(request):
        return JSONResponse({"status": "server up, with agent running"})

    async def agent_card_endpoint(request):
        """Serve agent card at /.well-known/agent-card.json"""
        return JSONResponse(card_dict)

    async def reset(request):
        try:
            body = await request.body()
            payload = json.loads(body) if body else {}

            # Signal ready to backend with agent URL and card content
            agent_id = payload.get("agent_id")
            backend_url = payload.get("backend_url")
            if agent_id and backend_url:
                # Replace localhost with agentbeats.org for production
                if "localhost" in backend_url:
                    backend_url = "https://agentbeats.org/api"
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        # Send ready signal with agent URL and card content
                        await client.put(
                            f"{backend_url}/agents/{agent_id}",
                            json={
                                "ready": True,
                                "agent_url": base_url,
                                "card_url": f"{base_url}/.well-known/agent-card.json",
                                "card_content": card_dict
                            }
                        )
                except Exception as e:
                    print(f"Failed to signal ready: {e}")

            return JSONResponse({"success": True, "message": "reset successful"})
        except Exception as e:
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    app.routes.append(
        Route(
            "/", lambda request: JSONResponse({
                "capabilities": {"streaming": True},
                "defaultInputModes": ["text"],
                "defaultOutputModes": ["text"],
                "description": "Roguelike economy game judge",
                "name": "RoguelikeJudge",
                "preferredTransport": "JSONRPC",
                "protocolVersion": "0.3.0",
                "skills": [
                    {
                        "description": "Host a roguelike economy game to assess agent decision making.",
                        "examples": [
                            'Your task is to host a roguelike game to test the agents.\nYou should use the following env configuration:\n<env_config>\n{\n  "max_turns": 10,\n  "world_size": 10\n}\n</env_config>'
                        ],
                        "id": "host_roguelike_game",
                        "name": "Roguelike Game Hosting",
                        "tags": ["green agent", "roguelike", "hosting"],
                    }
                ],
                "url": agent_url,
                "version": "1.0.0",
            }),
        )
    )
    app.routes.append(Route("/status", status))
    app.routes.append(Route("/reset", reset, methods=["POST"]))
    app.routes.append(Route("/.well-known/agent-card.json", agent_card_endpoint))

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
