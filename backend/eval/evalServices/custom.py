# Custom Environment Response Evaluator using AI Wrapper with Structured Output

import json
import uuid
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from .EvalServicesBase import EvalServicesBase
from src.services.aiServices.wrapper import AIWrapper


class EvaluationResult(BaseModel):
    """Structured evaluation result using Pydantic"""
    score: float = Field(ge=0.0, le=1.0, description="Overall evaluation score from 0.0 to 1.0")
    reasoning: str = Field(description="Brief explanation of the evaluation")
    appropriateness: float = Field(ge=0.0, le=1.0, description="How appropriate the response is for the context")
    completeness: float = Field(ge=0.0, le=1.0, description="How complete the response addresses the environment")
    clarity: float = Field(ge=0.0, le=1.0, description="How clear and understandable the response is")
    creativity: float = Field(ge=0.0, le=1.0, description="How creative the response is")
    action_validity: float = Field(ge=0.0, le=1.0, description="How valid the response is for the context")



class CustomEvalService(EvalServicesBase):
    """Custom evaluator using AI wrapper with structured Pydantic output"""

    def __init__(self, 
                 eval_id: str = None, 
                 system_prompt: str = "",
                 results_history: List[Dict[str, Any]] = None,
                 ai_model: str = "gpt-4.1-nano"):
        super().__init__(eval_id or str(uuid.uuid4()), system_prompt, results_history)
        self.ai_model = ai_model
    
    def evaluate(self, 
                      environment: str, 
                      user_response: str,
                      expected_output: Optional[str],
                      evaluation_criteria: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """AI evaluation using structured Pydantic output"""
        

            # Simple message for AI evaluation
        message = f"""Evaluate this user response to an environment.

Environment: {environment}

User Response: {user_response}

Provide a comprehensive evaluation with scores from 0.0 to 1.0 for each metric."""
            
            # Use AI wrapper with structured output
        result: EvaluationResult = AIWrapper.ask(
                message=message,
                model=self.ai_model,
                structured_output=EvaluationResult,
                isolated=True,
                verbose=1
            )
            
        return result.model_dump()
    
