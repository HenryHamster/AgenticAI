"""Purple Agent - ADK Implementation"""
import argparse
import uvicorn
import json
import httpx
from dotenv import load_dotenv
from starlette.responses import JSONResponse
from starlette.routing import Route

load_dotenv()

from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from a2a.types import AgentCapabilities, AgentCard

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
        instruction="You are a strategic player. Maximize wealth by exploring tiles and making smart decisions. Respond with ONE short action sentence like 'Move north to explore' or 'Search for resources'."
    )

    # Use public URL if provided
    if args.card_url:
        base_url = args.card_url.rstrip('/')
    else:
        base_url = f"http://{args.host}:{args.port}"

    card = AgentCard(
        name="player",
        description="Roguelike economy player",
        url=base_url,
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[]
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
                            f"{backend_url}/agents/{agent_id}",
                            json={"ready": True}
                        )
                except Exception:
                    pass

            return JSONResponse({"success": True, "message": "reset successful"})
        except Exception as e:
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    app.routes.append(Route("/status", status))
    app.routes.append(Route("/reset", reset, methods=["POST"]))

    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
