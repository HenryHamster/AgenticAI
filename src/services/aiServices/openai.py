# implements the AiServicesBase class for OpenAI

import openai
from typing import Optional
from ..AiServicesBase import AiServicesBase
from ...core.settings import ai_config

class OpenAiService(AiServicesBase):
    def __init__(self, chat_id: str, history: list[dict], constraints: list = None):
        super().__init__(chat_id, history, constraints or [])
        self.client = openai.OpenAI(api_key=ai_config.openai_api_key)

    def ask_ai_response(self, message: str) -> Optional[str]:
        """Get AI response from OpenAI API"""
        try:
            # Prepare messages with system prompt
            messages = [
                {"role": "system", "content": ai_config.system_prompt}
            ]
            
            # Add history
            messages.extend(self.history)
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Apply constraints to the message
            for constraint in self.constraints:
                if constraint.is_active:
                    message = constraint.modify_input_message(message)
            
            # Make API call
            response = self.client.chat.completions.create(
                model=ai_config.openai_model,
                messages=messages,
                max_tokens=ai_config.max_tokens,
                temperature=ai_config.openai_temperature
            )
            
            ai_response = response.choices[0].message.content
            
            # Apply constraints to the response
            for constraint in self.constraints:
                if constraint.is_active:
                    ai_response = constraint.modify_response(ai_response)
            
            # Add to history
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": ai_response})
            
            return ai_response
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def delete_chat(self):
        """Clear chat history"""
        self.history = []

    def reset_history(self):
        """Reset chat history"""
        self.history = []

    def get_history(self) -> list[dict]:
        """Get chat history"""
        return self.history.copy()
    