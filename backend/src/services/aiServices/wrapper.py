from typing import Optional, Type
from pydantic import BaseModel
from ..AiServicesBase import AiServicesBase
from .openai import OpenAiService
from .mock import MockAiService
from .claude import ClaudeService
from core.settings import ai_config
import uuid
import inspect
import sys, traceback


class AIWrapper:
    """Unified interface for all AI services"""

    _services: dict[str, AiServicesBase] = {}

    @classmethod
    def ask(cls,
            message: str,
            model: str = "gpt-4.1-mini",
            chat_id: Optional[str] = None,
            system_prompt: Optional[str] = None,
            structured_output: Optional[Type[BaseModel]] = None,
            isolated: bool = False, verbose: bool = True) -> Optional[str | BaseModel]:
        """
        Send message to AI service and get response

        Args:
            message: The message to send
            model: Model identifier (e.g., "gpt-4.1-mini", "claude-3-sonnet")
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
                print(f"[AI] Current history length: {len(service.history)} messages")
                cls._debug_prompt_lengths(message)
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

    @classmethod
    def _debug_prompt_lengths(cls, message: str) -> None:
        """Log rough lengths of the prompt components."""
        try:
            # Split sections based on our formatting convention
            system_part, context_part, schema_part = cls._split_prompt_sections(message)

            def _section_info(label: str, text: str) -> None:
                tokens = text.count(" ") + 1 if text else 0
                print(f"[AI] Section '{label}' length: chars={len(text)}, approx_tokens={tokens}")

            _section_info("system+preface", system_part)
            _section_info("context", context_part)
            _section_info("schema", schema_part)

            cls._print_context_subsections(context_part)
        except Exception as exc:
            print(f"[AI] Prompt length debug failed: {exc}")

    @staticmethod
    def _split_prompt_sections(message: str) -> tuple[str, str, str]:
        """Split formatted prompt into system, context, schema parts."""
        system_part = message
        context_part = ""
        schema_part = ""
        context_marker = "\n\nContext:\n"
        schema_marker = "\n\nSchema:\n"

        if context_marker in message:
            system_part, rest = message.split(context_marker, 1)
            if schema_marker in rest:
                context_part, schema_part = rest.split(schema_marker, 1)
            else:
                context_part = rest
        return system_part, context_part, schema_part

    @classmethod
    def _print_context_subsections(cls, context_text: str) -> None:
        """Attempt to parse context JSON and report per-key sizes."""
        if not context_text:
            return
        import json
        try:
            context_obj = json.loads(context_text)
            if isinstance(context_obj, dict):
                print("[AI] Context breakdown:")
                for key, value in context_obj.items():
                    text = json.dumps(value)
                    tokens = text.count(" ") + 1 if text else 0
                    print(f"  - {key}: chars={len(text)}, approx_tokens={tokens}")
        except json.JSONDecodeError:
            print("[AI] Context is not valid JSON; skipping breakdown.")
