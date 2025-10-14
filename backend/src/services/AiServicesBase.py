# dataclass for Ai Services. This will be used to create a base class for all Ai Services. Having the base methods
# will allow for easy extension and reuse of the Ai Services.
# possibly add create with the history of another AiService

from dataclasses import dataclass
from abc import abstractmethod
from pydantic import BaseModel, create_model, Field
from typing import Optional, Dict, Any, Type, Union, List
import json

@dataclass
class AiServicesBase:
    chat_id: str
    history: list[dict]
    system_prompt: str

    def __init__(self, chat_id: str, history: list[dict] = [], system_prompt: str = ""):
        self.chat_id = chat_id
        self.history = history
        self.system_prompt = system_prompt

    @abstractmethod
    def ask_ai_response(self, message: str):
        raise NotImplementedError("ask_ai_response method not implemented")

    @abstractmethod
    def ask_ai_response_with_structured_output(self, message: str, structured_output_class: BaseModel):
        """
        Ask the AI service to respond with a structured output. Example:
        class Joke(BaseModel):

            setup: str = Field(description="The setup of the joke")
            punchline: str = Field(description="The punchline to the joke")
            rating: Optional[int] = Field(
                description="How funny the joke is, from 1 to 10"
    )
        """
        raise NotImplementedError("ask_ai_response_with_structured_output method not implemented")

    @abstractmethod
    def ask_isolated_ai_response(self, message: str):
        raise NotImplementedError("ask_isolated_ai_response method not implemented")

    @abstractmethod
    def reset_history(self):
        raise NotImplementedError("reset_history method not implemented")

    @abstractmethod
    def get_history(self):
        raise NotImplementedError("get_history method not implemented")

    # Static method to create a new chat_id (for example, using uuid4)
    @staticmethod
    def generate_structured_output_class_from_dict(data_dict: dict, class_name: str = "DynamicModel") -> Type[BaseModel]:
        """
        Generate a Pydantic model class from a dictionary structure.
        
        Args:
            data_dict: A dictionary representing the data structure
            class_name: Name for the generated Pydantic model class
            
        Returns:
            A Pydantic model class that can be instantiated with the dictionary data
            
        Example:
            data = {
                "name": "John",
                "age": 30,
                "email": "john@example.com",
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown"
                }
            }
            UserModel = AiServicesBase.generate_structured_output_class_from_dict(data, "User")
            user = UserModel(**data)
        """
        def _infer_type(value: Any) -> Type:
            """Infer Python type from a value"""
            if isinstance(value, bool):
                return bool
            elif isinstance(value, int):
                return int
            elif isinstance(value, float):
                return float
            elif isinstance(value, str):
                return str
            elif isinstance(value, list):
                if not value:  # Empty list
                    return List[str]  # Default to list of strings
                # Infer type from first element
                element_type = _infer_type(value[0])
                return List[element_type]
            elif isinstance(value, dict):
                # For nested dictionaries, create a nested model
                nested_class_name = f"{class_name}Nested"
                nested_model = AiServicesBase.generate_structured_output_class_from_dict(value, nested_class_name)
                return nested_model
            else:
                return str  # Default fallback
        
        # Build field definitions for the model
        field_definitions = {}
        
        for key, value in data_dict.items():
            # Convert key to valid Python identifier
            field_name = key.replace(" ", "_").replace("-", "_")
            
            # Infer type
            field_type = _infer_type(value)
            
            # Make field optional if value is None
            if value is None:
                field_type = Optional[field_type]
            
            # Create field with description
            field_definitions[field_name] = (field_type, Field(description=f"Field {key}"))
        
        # Create the dynamic model
        dynamic_model = create_model(class_name, **field_definitions)
        
        return dynamic_model
    
    @staticmethod
    def create_pydantic_model_from_dict(data_dict: dict, class_name: str = "DynamicModel") -> Type[BaseModel]:
        """
        Alternative method name for creating Pydantic models from dictionaries.
        This is the recommended method name.
        """
        return AiServicesBase.generate_structured_output_class_from_dict(data_dict, class_name)
    
    @staticmethod
    def validate_dict_with_model(data_dict: dict, model_class: Type[BaseModel]) -> BaseModel:
        """
        Validate a dictionary against a Pydantic model and return the validated instance.
        
        Args:
            data_dict: Dictionary to validate
            model_class: Pydantic model class to validate against
            
        Returns:
            Validated Pydantic model instance
            
        Raises:
            ValidationError: If the dictionary doesn't match the model schema
        """
        return model_class(**data_dict)

