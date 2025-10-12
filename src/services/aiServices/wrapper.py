from typing import Optional, Type
from pydantic import BaseModel
from ..AiServicesBase import AiServicesBase
from .openai import OpenAiService
from .mock import MockAiService
from .claude import ClaudeService
from ...core.settings import ai_config
import uuid
import inspect
import sys, traceback


class AIWrapper:
    """Unified interface for all AI services"""

    _services: dict[str, AiServicesBase] = {}

    @classmethod
    def ask(cls,
            message: str,
            model: str = "gpt-4.1-nano",
            chat_id: Optional[str] = None,
            system_prompt: Optional[str] = None,
            structured_output: Optional[Type[BaseModel]] = None,
            isolated: bool = False, verbose: bool = True) -> Optional[str | BaseModel]:
        """
        Send message to AI service and get response

        Args:
            message: The message to send
            model: Model identifier (e.g., "gpt-4.1-nano", "claude-3-sonnet")
            chat_id: Chat session ID (creates new if None)
            system_prompt: Override default system prompt
            structured_output: Pydantic model for structured responses
            isolated: If True, don't use chat history

        Returns:
            Response string or Pydantic model instance
        """
        try:
            if verbose:
                print("\n[AI] === New request ===")
                print(f"[AI] Model: {model}")
                print(f"[AI] Message: {message[:250]}{'...' if len(message) > 250 else ''}")
            if structured_output is not None:
                assert inspect.isclass(structured_output), "structured_output must be a class, not an instance"
                assert issubclass(structured_output, BaseModel), "GameResponse must subclass pydantic.BaseModel"
                assert structured_output is not BaseModel, "You are passing BaseModel itself!"
            chat_id = chat_id or str(uuid.uuid4())
            if verbose:
                print(f"[AI] Using chat session: {chat_id}")
                print(f"[AI] Initializing backend for model '{model}'...")
                print(f"[AI] Model supports structured output: {'yes' if structured_output else 'no'}")
        
            service = cls._get_service(model, chat_id, system_prompt)
            if verbose:
                print("[AI] Service ready.")
            result = None
            if structured_output:
                result = service.ask_ai_response_with_structured_output(message, structured_output)
            elif isolated:
                result = service.ask_isolated_ai_response(message)
            else:
                result = service.ask_ai_response(message)
            if verbose:
                if isinstance(result, str):
                    print(f"[AI] Output: {result[:200]}{'...' if len(result) > 200 else ''}")
                else:
                    print(f"[AI] Parsed structured output: {result}")

            return result
        except Exception as e:
            print("\n[AIWrapper.ask] crashed:", repr(e), file=sys.stderr)
            traceback.print_exc()          # full stack with line numbers
            raise             

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
            elif "mock" in model.lower():
                cls._services[chat_id] = MockAiService(
                    chat_id=chat_id,
                    model=model,
                    system_prompt=prompt
                )
            else:
                raise ValueError(f"Unknown model: {model}")

        return cls._services[chat_id]
