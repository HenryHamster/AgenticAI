# src/services/aiServices/mock.py
from __future__ import annotations
from typing import Optional, Type, Any, Dict, List
import uuid
from pydantic import BaseModel
from ..AiServicesBase import AiServicesBase

class MockAiService(AiServicesBase):
    """
    Deterministic mock AI service.
    - Text replies: constant, short.
    - Structured replies: fixed, minimal GameResponse-shaped payload.
    """

    def __init__(
        self,
        chat_id: str = None,
        history: List[dict] | None = None,
        model: str = "mock",
        temperature: float = 0.0,
        system_prompt: str = ""
    ):
        super().__init__(chat_id or str(uuid.uuid4()), history or [], system_prompt)
        self.model = model
        self.temperature = temperature

    def ask_ai_response(self, message: str) -> Optional[str]:
        reply = "[MOCK] ok."
        self._append_history(message, reply)
        return reply

    def ask_isolated_ai_response(self, message: str) -> Optional[str]:
        reply = "[MOCK] ok."
        self._append_history(message, reply)
        return reply

    def ask_ai_response_with_structured_output(
        self,
        message: str,
        structured_output_class: Type[BaseModel]
    ) -> Optional[BaseModel | Dict[str, Any]]:
        # Get the class name to determine which mock payload to use
        class_name = structured_output_class.__name__

        # Different payloads for different structured output types
        if class_name == "TileModel":
            payload: Dict[str, Any] = {
                "position": [0, 0],
                "description": "[MOCK] A generic tile with nothing special.",
                "terrainType": "plains",
                "terrainEmoji": "🌾",
                "secrets": []
            }
        elif class_name == "PlayerAction":
            payload: Dict[str, Any] = {
                "action": "[MOCK] wait",
                "target": None,
                "reasoning": "[MOCK] Waiting to see what happens."
            }
        else:
            # Default: GameResponse-shaped payload
            payload: Dict[str, Any] = {
                "character_state_change": [
                    {"uid": "player0", "position_change": [1, 0], "money_change": 2, "health_change": -2},
                    {"uid": "player1", "position_change": [0, -1], "money_change": 5, "health_change": 1},
                ],
                "world_state_change": {"tiles": []},
                "narrative_result": "[MOCK] This is a mock narrative."
            }

        try:
            if hasattr(structured_output_class, "model_validate"):  # pydantic v2
                inst = structured_output_class.model_validate(payload)
            else:  # pydantic v1
                inst = structured_output_class(**payload)
            self._append_history(message, "[MOCK structured]")
            return inst
        except Exception:
            self._append_history(message, "[MOCK structured-dict]")
            return payload
    def reset_history(self):
        self.history = []

    def get_history(self) -> List[dict]:
        return self.history.copy()

    def _append_history(self, user: str, assistant: str):
        self.history.append({"role": "user", "content": user})
        self.history.append({"role": "assistant", "content": assistant})
