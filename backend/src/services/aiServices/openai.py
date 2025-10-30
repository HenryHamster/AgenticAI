# implements the AiServicesBase class for OpenAI

import openai
from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel
from ..AiServicesBase import AiServicesBase
from core.settings import ai_config
import uuid
import inspect

class OpenAiService(AiServicesBase):

    llm: ChatOpenAI
    chat_prompt: ChatPromptTemplate

    def __init__(self, chat_id: str = uuid.uuid4(), history: list[dict] = [], model: str = "gpt-4.1-mini", temperature: float = 0.7, system_prompt: str = ai_config.system_prompt):
        """
        Initialize the OpenAI service.
        Args:
            chat_id: The ID of the chat.
            history: The history of the chat.
            model: The model to use. be careful the model supports structured output.
            system_prompt: The system prompt to use.
        """
        super().__init__(chat_id, history, system_prompt)

        self.llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=ai_config.openai_max_tokens,
            timeout=ai_config.openai_timeout,
            api_key=ai_config.openai_api_key,
            max_retries=2,
        )
        
        # Create ChatPromptTemplate with system message and chat history placeholder
        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])

    def _convert_history_to_messages(self) -> list:
        """Convert history dict format to LangChain message format"""
        messages = []
        for entry in self.history:
            if entry["role"] == "user":
                messages.append(HumanMessage(content=entry["content"]))
            elif entry["role"] == "assistant":
                messages.append(AIMessage(content=entry["content"]))
        return messages

    def ask_ai_response(self, message: str) -> Optional[str]:
        """Get AI response from OpenAI API with system prompt and chat history"""
        try:
            # Convert history to LangChain message format
            chat_history = self._convert_history_to_messages()
            
            # Create the chain with prompt template and LLM
            chain = self.chat_prompt | self.llm
            
            # Prepare input data with message and chat history
            input_data = {
                "input": message,
                "chat_history": chat_history
            }
            
            # Generate response using the chain
            ai_response = chain.invoke(input_data)
            
            # Update history
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": ai_response.content})
            
            return ai_response.content
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def ask_isolated_ai_response(self, message: str) -> Optional[str]:
        """Get AI response from OpenAI API without chat history (isolated)"""
        try:
            # Create a simple prompt template without chat history for isolated responses
            isolated_prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{input}")
            ])
            
            # Create the chain with prompt template and LLM
            chain = isolated_prompt | self.llm
            
            # Prepare input data
            input_data = {"input": message}
            
            # Generate response using the chain
            ai_response = chain.invoke(input_data)
            
            # Update history
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": ai_response.content})

            return ai_response.content

        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def ask_ai_response_with_structured_output(self, message: str, structured_output_class: BaseModel) -> Optional[str]:
        """Get AI response from OpenAI API with structured output, system prompt and chat history"""

        if not (inspect.isclass(structured_output_class) and issubclass(structured_output_class, BaseModel)):
            raise TypeError("structured_output_class must be a subclass of pydantic.BaseModel")

        try:
            # Convert history to LangChain message format
            chat_history = self._convert_history_to_messages()
            
            # Create the chain with prompt template and LLM with structured output
            chain = self.chat_prompt | self.llm.with_structured_output(structured_output_class, method="function_calling")
            
            # Prepare input data with message and chat history
            input_data = {
                "input": message,
                "chat_history": chat_history
            }
            
            # Generate response using the chain
            ai_response = chain.invoke(input_data)
            
            # Update history
            self.history.append({"role": "user", "content": message})
            self.history.append({"role": "assistant", "content": str(ai_response)})

            return ai_response
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return None

    def reset_history(self):
        """Reset chat history"""
        self.history = []

    def get_history(self) -> list[dict]:
        """Get chat history"""
        return self.history.copy()
    