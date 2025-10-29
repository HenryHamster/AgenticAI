import argparse
import contextlib
import uvicorn
import asyncio
import logging
from dotenv import load_dotenv
from typing import Any, Dict

load_dotenv()

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    TaskState,
    Part,
    TextPart,
)
from a2a.utils import (
    new_agent_text_message
)

from agentbeats.src.green_executor import GreenAgent, GreenExecutor
from agentbeats.src.models import EvalRequest, EvalResult
from agentbeats.src.tool_provider import ToolProvider
from eval.wrapper import EvalWrapper

from agentbeats.dnd.dnd_master_common import dnd_master_agent_card


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dnd_master")


class DnDMaster(GreenAgent):
    def __init__(self):
        self._required_roles = ["player0", "player1"]
        self._required_config_keys = ["scenario", "num_turns"]
        self._tool_provider = ToolProvider()

    def validate_request(self, request: EvalRequest) -> tuple[bool, str]:
        missing_roles = set(self._required_roles) - set(request.participants.keys())
        if missing_roles:
            return False, f"Missing roles: {missing_roles}"
        missing_config_keys = set(self._required_config_keys) - set(request.config.keys())
        if missing_config_keys:
            return False, f"Missing config keys: {missing_config_keys}"
        try:
            int(request.config["num_turns"])
        except Exception as e:
            return False, f"Can't parse num_turns: {e}"
        return True, "ok"

    async def run_eval(self, req: EvalRequest, updater: TaskUpdater) -> None:
        logger.info(f"Starting D&D game orchestration: {req}")

        try:
            game = await self.orchestrate_game(req.participants,
                                                req.config["scenario"],
                                                req.config["num_turns"],
                                                updater)

            game_log = ""
            for i, turns in enumerate(game["turns"], start=1):
                game_log += f"Turn {i}:\n"
                for player_name, action in turns.items():
                    game_log += f"  {player_name}: {action}\n"

            await updater.update_status(TaskState.working, new_agent_text_message(f"Game finished. Starting evaluation."))
            logger.info("Game finished. Evaluating game.")


            # TODO: implement a evaluate_game function that will be rutnrend
            # game_eval: Dict[str, Any] = await EvalWrapper.evaluate_game(environment_text=req.config["scenario"], user_response_text=game_log, service_type="custom")
            game_eval = {
                "winner": "player0",
                "scores": {
                    "player0": 0.8,
                    "player1": 0.2
                }
            }
            logger.info(f"Game Evaluation:\n{game_eval}")

            result = EvalResult(winner=game_eval["winner"], detail=game_eval)
            await updater.add_artifact(
                parts=[
                    Part(root=TextPart(text=game_eval)),
                    Part(root=TextPart(text=result.model_dump_json())),
                ],
                name="Result",
            )
        finally:
            self._tool_provider.reset()

    async def orchestrate_game(
        self,
        participants: dict[str, str],
        scenario: str,
        num_turns: int,
        updater: TaskUpdater,
    ) -> dict[str, list[str]]:
        scenario_context: dict[str, list[str]] = {"player0": [], "player1": []}

        async def turn(role: str, prompt: str) -> str:
            response = await self._tool_provider.talk_to_agent(prompt, str(participants[role]), new_conversation=False)
            logger.info(f"{role}: {response}")
            scenario_context[role].append(response)
            await updater.update_status(TaskState.working, new_agent_text_message(f"{role}: {response}"))
            return response

        # Opening turns
        response = await turn("player0", f"Scenario: {scenario_context}. Present your opening action.")
        response = await turn("player1", f"Scenario: {scenario_context}. Present your opening action. Your opponent opened with: {response}")

        # Remaining rounds
        for _ in range(num_turns - 1):
            response = await turn("player0", f"Your opponent said: {response}. Present your next action.")
            response = await turn("player1", f"Your opponent said: {response}. Present your next action.")

        return scenario_context

    async def judge_game(self, scenario_context: dict[str, list[str]]) -> Dict[str, Any]:

        evaluated: Dict[str, Any] = await EvalWrapper.evaluate_game(environment_text=scenario_context, user_response_text=game_log, service_type="custom")
        return evaluated


async def main():
    parser = argparse.ArgumentParser(description="Run the A2A debate judge.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server")
    parser.add_argument("--port", type=int, default=9019, help="Port to bind the server")
    parser.add_argument("--card-url", type=str, help="External URL to provide in the agent card")
    parser.add_argument("--cloudflare-quick-tunnel", action="store_true", help="Use a Cloudflare quick tunnel. Requires cloudflared. This will override --card-url")
    args = parser.parse_args()

    if args.cloudflare_quick_tunnel:
        from agentbeats.cloudflare import quick_tunnel
        agent_url_cm = quick_tunnel(f"http://{args.host}:{args.port}")
    else:
        agent_url_cm = contextlib.nullcontext(args.card_url or f"http://{args.host}:{args.port}/")

    async with agent_url_cm as agent_url:
        agent = DnDMaster()
        executor = GreenExecutor(agent)
        agent_card = dnd_master_agent_card("DnDMaster", agent_url)

        request_handler = DefaultRequestHandler(
            agent_executor=executor,
            task_store=InMemoryTaskStore(),
        )

        server = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler,
        )

        uvicorn_config = uvicorn.Config(server.build(), host=args.host, port=args.port)
        uvicorn_server = uvicorn.Server(uvicorn_config)
        await uvicorn_server.serve()

if __name__ == '__main__':
    asyncio.run(main())
