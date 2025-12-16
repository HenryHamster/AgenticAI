from abc import abstractmethod
from pydantic import ValidationError

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InvalidParamsError,
    Task,
    TaskState,
    UnsupportedOperationError,
    InternalError,
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError

from agentbeats_lib.models import EvalRequest

import re
from typing import Dict


def parse_tags(str_with_tags: str) -> Dict[str, str]:
    """the target str contains tags in the format of <tag_name> ... </tag_name>, parse them out and return a dict"""

    tags = re.findall(r"<(.*?)>(.*?)</\1>", str_with_tags, re.DOTALL)
    return {tag: content.strip() for tag, content in tags}


class GreenAgent:

    @abstractmethod
    async def run_eval(self, request: EvalRequest, updater: TaskUpdater) -> None:
        pass

    @abstractmethod
    def validate_request(self, request: EvalRequest) -> tuple[bool, str]:
        pass

import json
import logging

class GreenExecutor(AgentExecutor):

    def __init__(self, green_agent: GreenAgent):
        self.agent = green_agent

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        logger = logging.getLogger("green_executor")
        logger.info(f"context.message type: {type(context.message)}")
        logger.info(f"context.message: {context.message}")
        request_text = context.get_user_input()
        logger.info(f"request_text (len={len(request_text)}): '{request_text[:200] if request_text else 'EMPTY'}'")

        try:
            # Try parsing as JSON first
            msg_data = None
            try:
                msg_data = json.loads(request_text)
            except json.JSONDecodeError:
                pass

            if msg_data and msg_data.get("type") in ["battle_start", "battle_info"]:
                # Battle notification format
                logger.info("Converting AgentBeats battle notification to EvalRequest")
                battle_id = msg_data.get("battle_id")
                backend_url = msg_data.get("backend_url", "https://agentbeats.org/api")
                if "localhost" in backend_url:
                    backend_url = "https://agentbeats.org/api"

                import httpx
                participants = {}
                config = {"max_turns": 5, "world_size": 1, "starting_wealth": 100, "negotiation_rounds": 1}
                opponents = []

                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.get(f"{backend_url}/battles/{battle_id}")
                        battle_data = resp.json()
                        logger.info(f"Fetched battle data: {json.dumps(battle_data, indent=2)}")
                        opponents = battle_data.get("opponents", [])
                        for idx, opp in enumerate(opponents):
                            role = f"player_{idx + 1}"
                            agent_id = opp.get("agent_id", "")
                            agent_resp = await client.get(f"{backend_url}/agents/{agent_id}")
                            agent_data = agent_resp.json()
                            participants[role] = agent_data.get("register_info", {}).get("agent_url", "")
                        if battle_data.get("task_config"):
                            config = json.loads(battle_data["task_config"])
                except Exception as e:
                    logger.error(f"Failed to fetch battle info: {e}")

                req = EvalRequest(participants=participants, config=config)
                req._battle_id = battle_id
                req._backend_url = backend_url
                req._role_to_agent_id = {f"player_{idx + 1}": opp.get("agent_id", "") for idx, opp in enumerate(opponents)}
                logger.info(f"Converted to EvalRequest: {req.model_dump_json()}")

            elif msg_data and "participants" in msg_data:
                # Direct JSON EvalRequest format
                req = EvalRequest.model_validate_json(request_text)

            else:
                # Tag-based format from AgentBeats platform
                logger.info("Parsing tag-based format from AgentBeats")

                # Extract all white_agent_url tags
                white_agent_urls = re.findall(r"<white_agent_url>\s*(.*?)\s*</white_agent_url>", request_text, re.DOTALL)
                logger.info(f"Found {len(white_agent_urls)} white_agent_urls: {white_agent_urls}")

                # Extract env_config if present (optional)
                env_config_match = re.search(r"<env_config>\s*(.*?)\s*</env_config>", request_text, re.DOTALL)
                if env_config_match:
                    config = json.loads(env_config_match.group(1))
                else:
                    # Default config
                    config = {"max_turns": 5, "world_size": 1, "starting_wealth": 100, "negotiation_rounds": 1}

                # Build participants from white_agent_urls
                participants = {}
                for idx, url in enumerate(white_agent_urls):
                    role = f"player_{idx + 1}"
                    participants[role] = url.strip()

                logger.info(f"Parsed participants: {participants}, config: {config}")
                req = EvalRequest(participants=participants, config=config)

            ok, msg = self.agent.validate_request(req)
            if not ok:
                raise ServerError(error=InvalidParamsError(message=msg))
        except ValidationError as e:
            raise ServerError(error=InvalidParamsError(message=e.json()))

        msg = context.message
        if msg:
            task = new_task(msg)
            await event_queue.enqueue_event(task)
        else:
            raise ServerError(error=InvalidParamsError(message="Missing message."))

        updater = TaskUpdater(event_queue, task.id, task.context_id)
        await updater.update_status(
            TaskState.working,
            new_agent_text_message(f"Starting assessment.\n{req.model_dump_json()}", context_id=context.context_id)
        )

        try:
            await self.agent.run_eval(req, updater)
            await updater.complete()
        except Exception as e:
            print(f"Agent error: {e}")
            await updater.failed(new_agent_text_message(f"Agent error: {e}", context_id=context.context_id))
            raise ServerError(error=InternalError(message=str(e)))

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())
