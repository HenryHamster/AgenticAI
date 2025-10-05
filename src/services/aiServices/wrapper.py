from typing import Optional, Type
from pydantic import BaseModel
from ..AiServicesBase import AiServicesBase
from .openai import OpenAiService
from .claude import ClaudeService
from ...core.settings import ai_config
import uuid

class AIWrapper:
    """Unified interface for all AI services"""

    _services: dict[str, AiServicesBase] = {}

    @classmethod
    def ask(cls,
            message: str,
            model: str = "gpt-4o",
            chat_id: Optional[str] = None,
            system_prompt: Optional[str] = None,
            structured_output: Optional[Type[BaseModel]] = None,
            isolated: bool = False) -> Optional[str | BaseModel]:
        """
        Send message to AI service and get response

        Args:
            message: The message to send
            model: Model identifier (e.g., "gpt-4o", "claude-3-sonnet")
            chat_id: Chat session ID (creates new if None)
            system_prompt: Override default system prompt
            structured_output: Pydantic model for structured responses
            isolated: If True, don't use chat history

        Returns:
            Response string or Pydantic model instance
        """
        chat_id = chat_id or str(uuid.uuid4())
        service = cls._get_service(model, chat_id, system_prompt)

        if structured_output:
            return service.ask_ai_response_with_structured_output(message, structured_output)
        elif isolated:
            return service.ask_isolated_ai_response(message)
        else:
            return service.ask_ai_response(message)

    @classmethod
    def reset(cls, chat_id: str):
        """Reset chat history for a session"""
        if chat_id in cls._services:
            cls._services[chat_id].reset_history()

    @classmethod
    def get_history(cls, chat_id: str) -> list[dict]:
        """Get chat history for a session"""
        return cls._services.get(chat_id, None).get_history() if chat_id in cls._services else []

    @classmethod
    def _get_service(cls, model: str, chat_id: str, system_prompt: Optional[str]) -> AiServicesBase:
        """Get or create AI service instance"""
        if chat_id not in cls._services:
            prompt = system_prompt or ai_config.system_prompt

            if "gpt" in model.lower() or "openai" in model.lower():
                cls._services[chat_id] = OpenAiService(
                    chat_id=chat_id,
                    model=model,
                    system_prompt=prompt
                )
            elif "claude" in model.lower():
                cls._services[chat_id] = ClaudeService(
                    chat_id=chat_id,
                    model=model,
                    system_prompt=prompt
                )
            else:
                raise ValueError(f"Unknown model: {model}")

        return cls._services[chat_id]
