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
        instruction=(
            "You are a strategic adventurer in a roguelike economy game. Your goal is to maximize wealth.\n\n"
            "GAME RULES:\n"
            "- You can move (north/south/east/west), explore, search, rest, or use abilities\n"
            "- Exploring tiles reveals secrets and resources\n"
            "- Searching finds hidden treasures\n"
            "- Other players are competitors - you can cooperate or compete\n\n"
            "RESPONSE FORMAT:\n"
            "- During NEGOTIATION: Discuss strategy briefly (1-2 sentences)\n"
            "- During ACTION: State ONE specific action (e.g., 'I move north to explore the forest')\n\n"
            "Be strategic. Consider tile positions, other players, and your resources."
        ),
    )

    # Use public URL if provided
    if args.card_url:
        base_url = args.card_url.rstrip('/')
        logger.info(f"Using public URL from --card-url: {base_url}")
    else:
        base_url = os.getenv("AGENT_URL")
        logger.warning(f"Using environment variable URL (no --card-url provided): {base_url}")

    agent_url = os.getenv("AGENT_URL")

    card = AgentCard(
        name="player",
        description="Roguelike economy player",
        url=agent_url,
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[],
    )

    app = to_a2a(agent, agent_card=card)

    # Add status and reset endpoints
    async def status(request):
        return JSONResponse({"status": "server up, with agent running"})

    async def reset(request):
        try:
            body = await request.body()
            payload = json.loads(body) if body else {}

            # Signal ready to backend
            agent_id = payload.get("agent_id")
            backend_url = payload.get("backend_url")
            if agent_id and backend_url:
                # Replace localhost with agentbeats.org for production
                if "localhost" in backend_url:
                    backend_url = "https://agentbeats.org/api"
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        await client.put(
                            f"{backend_url}/agents/{agent_id}", json={"ready": True}
                        )
                except Exception:
                    pass

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

    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
