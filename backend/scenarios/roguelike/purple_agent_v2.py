"""Purple Agent - ADK Multi-Agent Ensemble Implementation"""
import argparse
import uvicorn
import json
import os
import httpx
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from starlette.routing import Route

load_dotenv()

from google.adk.agents import Agent, SequentialAgent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
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

    # Sub-agent 1: Aggressive strategy
    aggressive_agent = Agent(
        name="aggressive",
        model="gemini-2.5-pro",
        description="Aggressive wealth-focused player",
        instruction="You prioritize wealth above all. Take risks for high rewards. Suggest ONE bold action.",
        output_key="aggressive_action"
    )

    # Sub-agent 2: Defensive strategy
    defensive_agent = Agent(
        name="defensive",
        model="gemini-2.5-pro",
        description="Defensive survival-focused player",
        instruction="You prioritize survival. Avoid risks, prefer safe steady gains. Suggest ONE safe action.",
        output_key="defensive_action"
    )

    # Sub-agent 3: Explorer strategy
    explorer_agent = Agent(
        name="explorer",
        model="gemini-2.5-pro",
        description="Exploration-focused player",
        instruction="You prioritize discovering new areas and opportunities. Suggest ONE exploration action.",
        output_key="explorer_action"
    )

    # Coordinator agent: Picks the best action from the three
    coordinator = Agent(
        name="coordinator",
        model="gemini-2.5-pro",
        description="Picks the best action",
        instruction="""You are the coordinator. You receive three suggested actions:

- Aggressive: {aggressive_action}
- Defensive: {defensive_action}
- Explorer: {explorer_action}

Evaluate which action is BEST given the current game state. Consider:
1. Current health (if low, prefer defensive)
2. Current wealth (if high, can take more risks)
3. Game progress (early game = explore, late game = consolidate)

Output ONLY the single best action sentence. No explanation."""
    )

    # Sequential agent: runs sub-agents then coordinator picks best
    agent = SequentialAgent(
        name="player",
        description="Multi-agent ensemble player",
        sub_agents=[aggressive_agent, defensive_agent, explorer_agent, coordinator]
    )

    # Use public URL if provided
    if args.card_url:
        base_url = args.card_url.rstrip('/')
    else:
        base_url = f"http://{args.host}:{args.port}"

    agent_url = os.getenv("AGENT_URL")

    player_skill = AgentSkill(
        id="roguelike_player_ensemble",
        name="Roguelike Player Ensemble",
        description="Multi-agent ensemble: 3 strategy agents (aggressive, defensive, explorer) + coordinator that picks the best action.",
        tags=["game", "strategy", "roguelike", "a2a", "ensemble"],
        examples=[
            "Move north to explore the unknown tile",
            "Search this area for hidden resources",
            "Trade goods with the merchant for profit"
        ]
    )

    card = AgentCard(
        name="player_ensemble",
        description=AGENT_DESCRIPTION,
        url=agent_url,
        version="2.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
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
                                "agent_url": agent_url,
                                "card_url": f"{base_url}/.well-known/agent-card.json",
                                "card_content": card_dict
                            }
                        )
                except Exception as e:
                    print(f"Failed to signal ready: {e}")

            return JSONResponse({"success": True, "message": "reset successful"})
        except Exception as e:
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    app.routes.append(Route("/status", status))
    app.routes.append(Route("/reset", reset, methods=["POST"]))
    app.routes.append(Route("/.well-known/agent-card.json", agent_card_endpoint))

    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
