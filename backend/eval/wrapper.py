# Simplified unified interface for evaluation services

from typing import Optional, Dict, Any, List
from .evalServices.EvalServicesBase import EvalServicesBase
from .evalServices.mock import MockEvalService
from .evalServices.custom import CustomEvalService
import uuid
import sys
import traceback


class EvalWrapper:
    """Simplified unified interface for evaluation services"""
    
    @classmethod
    def evaluate(cls,
                 environment_text: str,
                 user_response_text: str,
                 evaluation_criteria: Optional[Dict[str, Any]] = None,
                 service_type: str = "mock",
                 ai_model: str = "gpt-4o-mini",
                 eval_id: Optional[str] = None,
                 verbose: bool = True) -> Optional[Dict[str, Any]]:
        """
        Evaluate user response to environment using specified evaluation service
        
        Args:
            environment_text: The environment description
            user_response_text: The user's response
            evaluation_criteria: Custom criteria for evaluation
            service_type: Type of evaluation service ("mock", "custom")
            ai_model: AI model to use for evaluation
            eval_id: Evaluation session ID (creates new if None)
            verbose: Whether to print verbose output
            
        Returns:
            Evaluation result dictionary with score (0-1)
        """
        try:
            if verbose:
                print("\n[EVAL] === New evaluation ===")
                print(f"[EVAL] Service: {service_type}")
            
            eval_id = eval_id or str(uuid.uuid4())
            if verbose:
                print(f"[EVAL] Using evaluation session: {eval_id}")
            
            service = cls._get_service(service_type, eval_id, ai_model)
            if verbose:
                print("[EVAL] Service ready.")
            
            result = service.evaluate(environment_text, user_response_text, None, evaluation_criteria)
            
            if verbose:
                print(f"[EVAL] Score: {result.get('score', 0.0):.2f}")
                print(f"[EVAL] Reasoning: {result.get('reasoning', 'No reasoning provided')[:100]}...")
            
            return result
            
        except Exception as e:
            print("\n[EvalWrapper.evaluate] crashed:", repr(e), file=sys.stderr)
            traceback.print_exc()
            raise

    @classmethod
    def _get_service(cls, service_type: str, eval_id: str, ai_model: str):
        """Get evaluation service instance"""
        if service_type == "mock":
            return MockEvalService(eval_id=eval_id)
        elif service_type == "custom":
            return CustomEvalService(eval_id=eval_id, ai_model=ai_model)
        else:
            raise ValueError(f"Unknown service type: {service_type}")


# Convenience functions for quick evaluation
def quick_evaluate(environment_text: str,
                 user_response_text: str,
                 evaluation_criteria: Optional[Dict[str, Any]] = None,
                 service_type: str = "mock",
                 **kwargs) -> Dict[str, Any]:
    """
    Quick evaluation function for simple use cases
    
    Args:
        environment_text: The environment description
        user_response_text: The user's response
        evaluation_criteria: Custom criteria for evaluation
        service_type: Type of evaluation service ("mock", "custom")
        **kwargs: Additional arguments passed to EvalWrapper.evaluate
        
    Returns:
        Evaluation result dictionary
    """
    return EvalWrapper.evaluate(
        environment_text=environment_text,
        user_response_text=user_response_text,
        evaluation_criteria=evaluation_criteria,
        service_type=service_type,
        **kwargs
    )