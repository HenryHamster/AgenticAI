import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, os.path.dirname(__file__))

import argparse
import uvicorn
import asyncio
import logging
import json
import httpx
import traceback
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types import TaskState, Part, TextPart, AgentCard, AgentCapabilities
from a2a.utils import new_agent_text_message
from starlette.responses import JSONResponse
from starlette.routing import Route

from agentbeats_lib.green_executor import GreenAgent, GreenExecutor
from agentbeats_lib.models import EvalRequest, EvalResult
from agentbeats_lib.tool_provider import ToolProvider

from src.app.Game import Game

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("roguelike_judge")


class RoguelikeJudge(GreenAgent):
    def __init__(self):
        self._required_roles = ["player_1", "player_2"]
        self._required_config_keys = ["max_turns", "world_size"]
        self._tool_provider = ToolProvider()
        self._processed_battles = set()  # Track completed battles

    def validate_request(self, request: EvalRequest) -> tuple[bool, str]:
        missing_roles = set(self._required_roles) - set(request.participants.keys())
        if missing_roles:
            return False, f"Missing roles: {missing_roles}"
        missing_config_keys = set(self._required_config_keys) - set(request.config.keys())
        if missing_config_keys:
            return False, f"Missing config keys: {missing_config_keys}"
        return True, "ok"

    async def run_eval(self, req: EvalRequest, updater: TaskUpdater) -> None:
        logger.info(f"!!! BATTLE START NOTIFICATION RECEIVED !!!")
        logger.info(f"Request: {req}")
        logger.info(f"Participants: {req.participants}")
        logger.info(f"Config: {req.config}")

        # Check for duplicate battle notification
        if hasattr(req, '_battle_id'):
            if req._battle_id in self._processed_battles:
                logger.warning(f"Battle {req._battle_id} already processed, ignoring duplicate notification")
                return

        try:
            # Init game
            max_turns = int(req.config["max_turns"])
            world_size = int(req.config["world_size"])
            starting_wealth = int(req.config.get("starting_wealth", 100))

            player_info = {
                "player_1": {"uid": "player_1", "position": [0, 0], "model": "mock", "player_class": "human",
                             "values": {"money": starting_wealth, "health": 100}, "responses": []},
                "player_2": {"uid": "player_2", "position": [0, 0], "model": "mock", "player_class": "human",
                             "values": {"money": starting_wealth, "health": 100}, "responses": []}
            }

            game = Game(player_info, {"model": "gpt-4o-mini"}, world_size)
            game.max_turns = max_turns

            # Run turns
            for turn in range(max_turns):
                await updater.update_status(TaskState.working, new_agent_text_message(f"Turn {turn + 1}/{max_turns}"))

                actions = {}
                for role in self._required_roles:
                    player = game.players[role]
                    context = f"Stats: money={player.values.money}, health={player.values.health}. Position: {player.position}. Make one action."

                    action = await self._tool_provider.talk_to_agent(context, str(req.participants[role]), new_conversation=False)
                    actions[role] = action
                    logger.info(f"{role}: {action}")

                # DM processes
                verdict = game.dm.respond_actions({
                    "Players": {uid: game.players[uid].save() for uid in game.players},
                    "Responses": actions,
                    "Past Verdict": "",
                    "tiles": game._get_tiles_full_payload()
                })
                game.handle_verdict(verdict)
                game.current_turn_number += 1
                game._check_game_conditions()

                if game.is_game_over:
                    await updater.update_status(TaskState.working, new_agent_text_message(f"Game ended: {game.game_over_reason}"))

                    # Submit result immediately when game ends (not turn update)
                    if hasattr(req, '_battle_id') and hasattr(req, '_backend_url'):
                        winner = None
                        max_wealth = 0
                        for uid, p in game.players.items():
                            if p.values.money > max_wealth and p.values.health > 0:
                                max_wealth, winner = p.values.money, uid

                        winner_agent_id = "draw"
                        if winner and hasattr(req, '_role_to_agent_id'):
                            winner_agent_id = req._role_to_agent_id.get(winner, "draw")

                        # Convert role-based keys to agent_id-based keys for frontend
                        role_to_agent = req._role_to_agent_id if hasattr(req, '_role_to_agent_id') else {}
                        
                        # Map final wealth with agent_ids as keys
                        final_wealth = {}
                        for role, p in game.players.items():
                            agent_id = role_to_agent.get(role, role)
                            final_wealth[agent_id] = p.values.money
                        
                        # Map final health with agent_ids as keys
                        final_health = {}
                        for role, p in game.players.items():
                            agent_id = role_to_agent.get(role, role)
                            final_health[agent_id] = p.values.health
                        
                        # Map final actions with agent_ids as keys
                        final_actions = {}
                        for role, action in actions.items():
                            agent_id = role_to_agent.get(role, role)
                            final_actions[agent_id] = action
                        
                        # Add agent metadata with fallback values to prevent undefined errors
                        agent_metadata = {}
                        for role, agent_id in role_to_agent.items():
                            agent_metadata[agent_id] = {
                                "identifier": agent_id,
                                "name": f"Player {role.split('_')[1]}",
                                "avatar_url": None,
                                "description": "Roguelike player agent"
                            }

                        battle_result = {
                            "is_result": True,
                            "winner": winner_agent_id,
                            "reported_by": "green_agent",
                            "message": f"Battle completed - Winner: {winner_agent_id if winner_agent_id != 'draw' else 'Draw'}",
                            "detail": {
                                "final_wealth": final_wealth,
                                "final_health": final_health,
                                "turns_played": game.current_turn_number,
                                "turn": turn + 1,
                                "final_actions": final_actions
                            },
                            "agent_metadata": agent_metadata,
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }

                        try:
                            logger.info(f"Submitting battle result with agent_ids: {json.dumps(battle_result, indent=2)}")
                            async with httpx.AsyncClient(timeout=5.0) as client:
                                resp = await client.post(f"{req._backend_url}/battles/{req._battle_id}", json=battle_result)
                                logger.info(f"Result submitted: {resp.status_code}")
                                if resp.status_code != 204:
                                    logger.error(f"Result failed: {resp.text}")
                                else:
                                    # Mark battle as processed to ignore duplicate notifications
                                    self._processed_battles.add(req._battle_id)
                                    logger.info(f"Battle {req._battle_id} marked as processed")
                        except Exception as e:
                            logger.error(f"Failed to submit result: {e}")

                    break

                # Send turn update for non-final turns only
                if hasattr(req, '_battle_id') and hasattr(req, '_backend_url'):
                    try:
                        # Convert role-based keys to agent_id-based keys for frontend
                        role_to_agent = req._role_to_agent_id if hasattr(req, '_role_to_agent_id') else {}
                        
                        # Map actions with agent_ids as keys
                        actions_by_agent = {}
                        for role, action in actions.items():
                            agent_id = role_to_agent.get(role, role)
                            actions_by_agent[agent_id] = action
                        
                        # Map player stats with agent_ids as keys
                        stats_by_agent = {}
                        for role, p in game.players.items():
                            agent_id = role_to_agent.get(role, role)
                            stats_by_agent[agent_id] = {"money": p.values.money, "health": p.values.health}
                        
                        # Add agent metadata with fallback values
                        agent_metadata = {}
                        for role, agent_id in role_to_agent.items():
                            agent_metadata[agent_id] = {
                                "identifier": agent_id,
                                "name": f"Player {role.split('_')[1]}",
                                "avatar_url": None,
                                "description": "Roguelike player agent"
                            }
                        
                        turn_event = {
                            "is_result": False,
                            "turn": turn + 1,
                            "reported_by": "green_agent",
                            "message": f"Turn {turn + 1} completed",
                            "actions": actions_by_agent,
                            "player_stats": stats_by_agent,
                            "agent_metadata": agent_metadata,
                            "timestamp": datetime.utcnow().isoformat() + "Z"
                        }
                        async with httpx.AsyncClient(timeout=5.0) as client:
                            await client.post(f"{req._backend_url}/battles/{req._battle_id}", json=turn_event)
                    except Exception as e:
                        logger.warning(f"Failed to send turn update: {e}")

            # Score
            winner = None
            max_wealth = 0
            for uid, p in game.players.items():
                if p.values.money > max_wealth and p.values.health > 0:
                    max_wealth, winner = p.values.money, uid

            result = EvalResult(winner=winner or "none", detail={
                "final_wealth": {uid: p.values.money for uid, p in game.players.items()},
                "final_health": {uid: p.values.health for uid, p in game.players.items()},
                "turns_played": game.current_turn_number
            })

            # Add artifact
            await updater.add_artifact(
                parts=[Part(root=TextPart(text=result.model_dump_json()))],
                name="Result"
            )
        finally:
            self._tool_provider.reset()


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9009)
    parser.add_argument("--card-url", type=str, help="Public URL for agent card (e.g., cloudflared tunnel URL)")
    args = parser.parse_args()

    agent = RoguelikeJudge()
    executor = GreenExecutor(agent)

    # Use public URL if provided, otherwise use host:port
    if args.card_url:
        base_url = args.card_url.rstrip('/')
        logger.info(f"Using public URL from --card-url: {base_url}")
    else:
        base_url = f"http://{args.host}:{args.port}"
        logger.warning(f"Using local URL (no --card-url provided): {base_url}")

    agent_url = os.getenv("AGENT_URL")

    agent_card = AgentCard(
        name="RoguelikeJudge",
        description="Roguelike economy game judge",
        url=agent_url,
        version="1.0.0",
        default_input_modes=["text"],
        default_output_modes=["text"],
        capabilities=AgentCapabilities(streaming=True),
        skills=[{
            "id": "host_roguelike_game",
            "name": "Roguelike Game Hosting",
            "description": "Host a roguelike economy game to assess agent decision making.",
            "examples": [
                "Your task is to host a roguelike game to test the agents.\n"
                "You should use the following env configuration:\n"
                "<env_config>\n"
                "{\n"
                "  \"max_turns\": 10,\n"
                "  \"world_size\": 10\n"
                "}\n"
                "</env_config>"
            ],
            "tags": [
                "green agent",
                "roguelike",
                "hosting"
            ]
        }]
    )
    logger.info(f"Agent card URL: {agent_url}")

    request_handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )

    server = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    # Add status and reset endpoints
    app = server.build()

    async def status(request):
        return JSONResponse({"status": "server up, with agent running"})

    async def reset(request):
        try:
            body = await request.body()
            payload = json.loads(body) if body else {}
            logger.info(f"Reset request received: {payload}")

            agent._tool_provider.reset()
            logger.info("Agent reset successful")

            # Signal ready to backend
            agent_id = payload.get("agent_id")
            backend_url = payload.get("backend_url")
            if agent_id and backend_url:
                # Replace localhost with agentbeats.org for production
                if "localhost" in backend_url:
                    backend_url = "https://agentbeats.org/api"
                try:
                    ready_url = f"{backend_url}/agents/{agent_id}"
                    logger.info(f"Marking agent ready at: {ready_url}")
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.put(ready_url, json={"ready": True})
                        logger.info(f"Ready response: {resp.status_code}")
                except Exception as e:
                    logger.error(f"Failed to mark agent as ready: {e}\n{traceback.format_exc()}")

            return JSONResponse({"success": True, "message": "Agent reset successfully"}, status_code=200)
        except Exception as e:
            logger.error(f"Reset error: {e}")
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    async def notify(request):
        """Handle battle notifications from AgentBeats"""
        try:
            body = await request.body()
            payload = json.loads(body) if body else {}
            logger.info(f"Notify request received: {payload}")
            
            # Extract battle info from AgentBeats notification
            battle_id = payload.get("battle_id")
            backend_url = payload.get("backend_url", "https://agentbeats.org/api")
            
            if "localhost" in backend_url:
                backend_url = "https://agentbeats.org/api"
            
            logger.info(f"Battle notification - ID: {battle_id}, Backend: {backend_url}")
            
            # Create an A2A message to trigger the executor
            battle_message = {
                "type": "battle_start",
                "battle_id": battle_id,
                "backend_url": backend_url
            }
            
            # Use the A2A client to send message to ourselves
            # This will trigger the green_executor.execute() method
            try:
                from agentbeats_lib.client import send_message
                
                # Send the battle notification as an A2A message
                result = await send_message(
                    message=json.dumps(battle_message),
                    base_url=base_url,
                    streaming=False
                )
                
                logger.info(f"Battle notification forwarded successfully: {result}")
                return JSONResponse({
                    "success": True, 
                    "message": "Battle notification received and processing started",
                    "battle_id": battle_id
                }, status_code=200)
                
            except Exception as e:
                logger.error(f"Error forwarding battle notification: {e}\n{traceback.format_exc()}")
                return JSONResponse({
                    "success": False, 
                    "error": f"Internal error: {str(e)}"
                }, status_code=500)
                
        except Exception as e:
            logger.error(f"Notify error: {e}\n{traceback.format_exc()}")
            return JSONResponse({"success": False, "error": str(e)}, status_code=500)

    app.routes.append(Route("/", 
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

    ))
    app.routes.append(Route("/status", status))
    app.routes.append(Route("/reset", reset, methods=["POST"]))
    app.routes.append(Route("/notify", notify, methods=["POST"]))

    uvicorn_config = uvicorn.Config(app, host=args.host, port=args.port)
    uvicorn_server = uvicorn.Server(uvicorn_config)
    await uvicorn_server.serve()


if __name__ == "__main__":
    asyncio.run(main())
