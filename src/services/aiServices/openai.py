# implements the AiServicesBase class for OpenAI

import openai
from typing import Optional
from ..AiServicesBase import AiServicesBase
from ...core.settings import ai_config

class OpenAiService(AiServicesBase):
    def __init__(self, chat_id: str, history: list[dict] = None, system_prompt: str = ""):
        super().__init__(chat_id, history, system_prompt)
        self.client = openai.OpenAI(api_key=ai_config.openai_api_key)

    def ask_ai_response(self, message: str) -> Optional[str]:
        try:
            messages = [{"role": "system", "content": self.system_prompt}]
            messages.extend(self.history)
            messages.append({"role": "user", "content": message})

            response = self.client.chat.completions.create(
                model=ai_config.openai_model,
                messages=messages,
                max_tokens=ai_config.max_tokens,
                temperature=ai_config.openai_temperature
            )

            ai_response = response.choices[0].message.content

            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": ai_response})

            return ai_response
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def delete_chat(self):
        self.history = []

    def reset_history(self):
        self.history = []

    def get_history(self) -> list[dict]:
        return self.history.copy()