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


class GreenAgent:

    @abstractmethod
    async def run_eval(self, request: EvalRequest, updater: TaskUpdater) -> None:
        pass

    @abstractmethod
    def validate_request(self, request: EvalRequest) -> tuple[bool, str]:
        pass


class GreenExecutor(AgentExecutor):

    def __init__(self, green_agent: GreenAgent):
        self.agent = green_agent

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        request_text = context.get_user_input()
        import json
        import logging
        logger = logging.getLogger("green_executor")

        try:
            # Parse incoming message
            msg_data = json.loads(request_text)
            logger.info(f"Received message: {json.dumps(msg_data, indent=2)}")

            # Check if this is AgentBeats battle notification format
            if msg_data.get("type") in ["battle_start", "battle_info"]:
                # Convert AgentBeats format to EvalRequest format
                logger.info("Converting AgentBeats battle notification to EvalRequest")

                # Fetch battle info from backend
                battle_id = msg_data.get("battle_id")
                backend_url = msg_data.get("backend_url", "https://agentbeats.org/api")
                if "localhost" in backend_url:
                    backend_url = "https://agentbeats.org/api"

                import httpx
                participants = {}
                config = {"max_turns": 3, "world_size": 1, "starting_wealth": 100}
                opponents = []

                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        resp = await client.get(f"{backend_url}/battles/{battle_id}")
                        battle_data = resp.json()
                        logger.info(f"Fetched battle data: {json.dumps(battle_data, indent=2)}")

                        # Extract opponents
                        opponents = battle_data.get("opponents", [])
                        for idx, opp in enumerate(opponents):
                            role = f"player_{idx + 1}"
                            agent_id = opp.get("agent_id", "")
                            # Fetch agent info to get URL
                            agent_resp = await client.get(f"{backend_url}/agents/{agent_id}")
                            agent_data = agent_resp.json()
                            participants[role] = agent_data.get("register_info", {}).get("agent_url", "")

                        # Extract config if available
                        if battle_data.get("task_config"):
                            config = json.loads(battle_data["task_config"])
                except Exception as e:
                    logger.error(f"Failed to fetch battle info: {e}")
                    # Use defaults

                req = EvalRequest(participants=participants, config=config)
                # Attach battle context for result submission
                req._battle_id = battle_id
                req._backend_url = backend_url
                # Map role to agent_id for winner reporting
                req._role_to_agent_id = {}
                for idx, opp in enumerate(opponents):
                    role = f"player_{idx + 1}"
                    req._role_to_agent_id[role] = opp.get("agent_id", "")
                logger.info(f"Converted to EvalRequest: {req.model_dump_json()}")
                logger.info(f"Role to agent_id mapping: {req._role_to_agent_id}")
            else:
                # Standard EvalRequest format
                req = EvalRequest.model_validate_json(request_text)

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
