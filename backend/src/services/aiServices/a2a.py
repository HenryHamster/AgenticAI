# A2A (Agent-to-Agent) Service - allows using external A2A agents as AI service

import asyncio
import json
from typing import Optional, List, Dict, Type
from pydantic import BaseModel
from ..AiServicesBase import AiServicesBase
import uuid

DEFAULT_TIMEOUT = 300

# Lazy imports for A2A - only loaded when actually used
_a2a_imported = False
A2ACardResolver = None
ClientConfig = None
ClientFactory = None
Message = None
Part = None
Role = None
TextPart = None
DataPart = None


def _ensure_a2a_imports():
    """Lazy import A2A dependencies only when needed"""
    global _a2a_imported, A2ACardResolver, ClientConfig, ClientFactory
    global Message, Part, Role, TextPart, DataPart

    if _a2a_imported:
        return

    try:
        import httpx  # noqa: F401
        from a2a.client import A2ACardResolver as _A2ACardResolver
        from a2a.client import ClientConfig as _ClientConfig
        from a2a.client import ClientFactory as _ClientFactory
        from a2a.types import Message as _Message
        from a2a.types import Part as _Part
        from a2a.types import Role as _Role
        from a2a.types import TextPart as _TextPart
        from a2a.types import DataPart as _DataPart

        A2ACardResolver = _A2ACardResolver
        ClientConfig = _ClientConfig
        ClientFactory = _ClientFactory
        Message = _Message
        Part = _Part
        Role = _Role
        TextPart = _TextPart
        DataPart = _DataPart
        _a2a_imported = True
    except ImportError as e:
        raise ImportError(
            f"A2A dependencies not installed. Install with: pip install a2a-sdk httpx\n"
            f"Original error: {e}"
        )


def create_message(*, text: str, context_id: str | None = None):
    _ensure_a2a_imports()
    return Message(
        kind="message",
        role=Role.user,
        parts=[Part(TextPart(kind="text", text=text))],
        message_id=uuid.uuid4().hex,
        context_id=context_id
    )


def merge_parts(parts: list) -> str:
    _ensure_a2a_imports()
    chunks = []
    for part in parts:
        if isinstance(part.root, TextPart):
            chunks.append(part.root.text)
        elif isinstance(part.root, DataPart):
            chunks.append(part.root.data)
    return "\n".join(chunks)


async def _send_a2a_message(message: str, base_url: str, context_id: str | None = None) -> dict:
    """Send message to A2A agent and return response with context_id"""
    _ensure_a2a_imports()
    import httpx
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as httpx_client:
        resolver = A2ACardResolver(httpx_client=httpx_client, base_url=base_url)
        agent_card = await resolver.get_agent_card()
        config = ClientConfig(
            httpx_client=httpx_client,
            streaming=False,
        )
        factory = ClientFactory(config)
        client = factory.create(agent_card)

        outbound_msg = create_message(text=message, context_id=context_id)
        last_event = None
        outputs = {
            "response": "",
            "context_id": None
        }

        async for event in client.send_message(outbound_msg):
            last_event = event

        match last_event:
            case Message() as msg:
                outputs["context_id"] = msg.context_id
                outputs["response"] += merge_parts(msg.parts)

            case (task, update):
                outputs["context_id"] = task.context_id
                outputs["status"] = task.status.state.value
                msg = task.status.message
                if msg:
                    outputs["response"] += merge_parts(msg.parts)
                if task.artifacts:
                    for artifact in task.artifacts:
                        outputs["response"] += merge_parts(artifact.parts)

            case _:
                pass

        return outputs


class A2AService(AiServicesBase):
    """AI service that routes requests to an external A2A agent"""

    base_url: str
    context_id: Optional[str]

    def __init__(self, chat_id: str = None, history: Optional[List[Dict]] = None,
                 model: str = "a2a://localhost:9018", system_prompt: str = ""):
        """
        Initialize the A2A service.

        Args:
            chat_id: The ID of the chat session
            history: The history of the chat (not used for A2A, but kept for interface compatibility)
            model: The A2A agent URL in format "a2a://host:port" or just the URL
            system_prompt: System prompt (sent as prefix to first message if needed)
        """
        super().__init__(chat_id or str(uuid.uuid4()), history, system_prompt)

        # Parse the model string to get the URL
        self.base_url = self._parse_model_url(model)
        self.context_id = None  # Will be set after first message

        print(f"[A2AService] Initialized for agent at {self.base_url}")

    def _parse_model_url(self, model: str) -> str:
        """Parse model string to extract the A2A agent URL"""
        # Handle formats: "a2a://localhost:9018", "a2a:localhost:9018", "http://localhost:9018"
        if model.startswith("a2a://"):
            url = model[6:]  # Remove "a2a://"
            # Add http:// if not present
            if not url.startswith("http"):
                url = f"http://{url}"
            return url
        elif model.startswith("a2a:"):
            url = model[4:]  # Remove "a2a:"
            if not url.startswith("http"):
                url = f"http://{url}"
            return url
        elif model.startswith("http"):
            return model
        else:
            # Assume it's just host:port
            return f"http://{model}"

    def _run_async(self, coro):
        """Run async coroutine in sync context"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a new thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, coro)
                    return future.result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(coro)

    def ask_ai_response(self, message: str) -> Optional[str]:
        """Get response from A2A agent with conversation context"""
        try:
            # Send message to A2A agent
            result = self._run_async(_send_a2a_message(
                message=message,
                base_url=self.base_url,
                context_id=self.context_id
            ))

            response = result.get("response", "")
            self.context_id = result.get("context_id")

            # Update history for compatibility
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": response})

            return response
        except Exception as e:
            print(f"[A2AService] Error communicating with agent: {e}")
            return None

    def ask_isolated_ai_response(self, message: str) -> Optional[str]:
        """Get response from A2A agent without conversation context (new context_id)"""
        try:
            # Send message without context_id to start fresh conversation
            result = self._run_async(_send_a2a_message(
                message=message,
                base_url=self.base_url,
                context_id=None  # Force new conversation
            ))

            response = result.get("response", "")
            # Don't update self.context_id to keep isolated

            # Update history for compatibility
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": response})

            return response
        except Exception as e:
            print(f"[A2AService] Error communicating with agent: {e}")
            return None

    def ask_ai_response_with_structured_output(self, message: str, structured_output_class: Type[BaseModel]) -> Optional[BaseModel]:
        """
        Get structured response from A2A agent.

        Note: A2A agents don't natively support structured output, so we:
        1. Add instructions to return JSON
        2. Parse the response as JSON
        3. Validate against the Pydantic model
        """
        try:
            # Add JSON instruction to message
            schema_json = json.dumps(structured_output_class.model_json_schema(), indent=2)
            enhanced_message = f"""{message}

IMPORTANT: You must respond with valid JSON that matches this schema:
{schema_json}

Respond ONLY with the JSON object, no additional text."""

            # Get response
            result = self._run_async(_send_a2a_message(
                message=enhanced_message,
                base_url=self.base_url,
                context_id=self.context_id
            ))

            response = result.get("response", "")
            self.context_id = result.get("context_id")

            # Update history
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": response})

            # Try to parse JSON from response
            # Handle cases where response might have markdown code blocks
            json_str = response.strip()
            if json_str.startswith("```json"):
                json_str = json_str[7:]
            if json_str.startswith("```"):
                json_str = json_str[3:]
            if json_str.endswith("```"):
                json_str = json_str[:-3]
            json_str = json_str.strip()

            # Parse and validate
            data = json.loads(json_str)
            return structured_output_class(**data)

        except json.JSONDecodeError as e:
            print(f"[A2AService] Failed to parse JSON response: {e}")
            print(f"[A2AService] Raw response: {response[:500]}")
            return None
        except Exception as e:
            print(f"[A2AService] Error: {e}")
            return None

    def reset_history(self):
        """Reset chat history and context"""
        self.history = []
        self.context_id = None

    def get_history(self) -> list[dict]:
        """Get chat history"""
        return self.history.copy()
