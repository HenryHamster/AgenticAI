import argparse
import contextlib
import uvicorn
import asyncio
import logging
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Literal

load_dotenv()

from openai import OpenAI
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

# Import local modules
import sys
import os

# Ensure we import from the local directory

from green_executor import GreenAgent, GreenExecutor
from models import EvalRequest, EvalResult
from tool_provider import ToolProvider

from dnd_common import DnDEval, dnd_master_agent_card


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dnd_master")


class DnDGameMaster(GreenAgent):
    def __init__(self):
        self._required_roles = ["player0", "player1"]
        self._required_config_keys = ["scenario", "num_turns"]
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY environment variable")
        self._client = OpenAI(api_key=api_key)
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
            game_eval: DnDEval = await self.judge_game(req.config["scenario"], game_log)
            logger.info(f"Game Evaluation:\n{game_eval.model_dump_json()}")

            result = EvalResult(winner=game_eval.winner, detail=game_eval.model_dump())
            await updater.add_artifact(
                parts=[
                    Part(root=TextPart(text=game_eval.reason)),
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
        turns: list[dict[str, str]] = []

        async def turn(player_role: str, prompt: str) -> str:
            response = await self._tool_provider.talk_to_agent(prompt, str(participants[player_role]), new_conversation=False)
            logger.info(f"{player_role}: {response}")
            await updater.update_status(TaskState.working, new_agent_text_message(f"{player_role}: {response}"))
            return response

        # Game loop
        scenario_context = scenario
        for turn_num in range(num_turns):
            turn_actions = {}
            
            # Get actions from all players
            for player_name in participants.keys():
                prompt = f"Scenario: {scenario_context}\nIt's turn {turn_num + 1}. What do you do?"
                action = await turn(player_name, prompt)
                turn_actions[player_name] = action
            
            turns.append(turn_actions)
            
            # Update scenario context based on player actions
            scenario_context = f"{scenario_context}\nTurn {turn_num + 1}: {' '.join(turn_actions.values())}"

        return {"turns": turns}

    async def judge_game(self, scenario: str, game_log: str) -> DnDEval:
        system_prompt = """
        You are an experienced Dungeon Master tasked with evaluating a D&D game session. Evaluate the player's actions based on: strategy, role-playing, cooperation, and effectiveness.

        Scoring Criteria:
        1. Strategy: How well did the players plan and execute their actions?
        2. Role-playing: How well did the players stay in character and contribute to the narrative?
        3. Cooperation: How well did the players work together?
        4. Effectiveness: How effective were their actions in addressing the scenario?

        Please output the result in JSON format with scores for each player.
        """

        user_prompt = f"""
        Evaluate the D&D game session.
        Original scenario: {scenario}
        
        Game log:
        {game_log}
        
        Provide a JSON formatted response with scores and comments.
        """

        response = self._client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=DnDEval,
        )
        return response.choices[0].message.parsed


async def main():
    parser = argparse.ArgumentParser(description="Run the A2A D&D Game Master.")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host to bind the server")
    parser.add_argument("--port", type=int, default=9009, help="Port to bind the server")
    parser.add_argument("--card-url", type=str, help="External URL to provide in the agent card")
    parser.add_argument("--cloudflare-quick-tunnel", action="store_true", help="Use a Cloudflare quick tunnel. Requires cloudflared. This will override --card-url")
    parser.add_argument("--local-only", action="store_true", default=True, help="Use localhost URL (for local development)")
    args = parser.parse_args()

    # For local development, just use localhost
    if args.local_only:
        agent_url = f"http://127.0.0.1:{args.port}/"
        agent_url_cm = contextlib.nullcontext(agent_url)
    elif args.cloudflare_quick_tunnel:
        from cloudflare import quick_tunnel
        agent_url_cm = quick_tunnel(f"http://{args.host}:{args.port}")
    else:
        agent_url_cm = contextlib.nullcontext(args.card_url or f"http://{args.host}:{args.port}/")

    async with agent_url_cm as agent_url:
        agent = DnDGameMaster()
        executor = GreenExecutor(agent)
        agent_card = dnd_master_agent_card("DnDGameMaster", agent_url)

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
