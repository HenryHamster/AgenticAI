# Unified interface for all evaluation services

from typing import Optional, Dict, Any, List, Callable
from evalServices.EvalServicesBase import EvalServicesBase, EvaluationResult, EvaluationConfig
from evalServices.geval import GEvalService
from evalServices.mock import MockEvalService
from evalServices.custom import CustomEvalService
import uuid
import sys
import traceback


class EvalWrapper:
    """Unified interface for all evaluation services"""
    
    _services: Dict[str, EvalServicesBase] = {}
    
    @classmethod
    def evaluate_interaction(cls,
                           environment_state: Any,
                           user_action: Any,
                           system_prompt: str = "",
                           service_type: str = "mock",
                           eval_id: Optional[str] = None,
                           config: Optional[Dict[str, Any]] = None,
                           verbose: bool = True) -> Optional[Dict[str, Any]]:
        """
        Evaluate how well a user interacts with an environment
        
        Args:
            environment_state: Current state of the environment
            user_action: Action taken by the user
            system_prompt: System prompt defining the environment and user behavior
            service_type: Type of evaluation service ("geval", "mock", "custom")
            eval_id: Evaluation session ID (creates new if None)
            config: Configuration for the evaluation service
            verbose: Whether to print verbose output
            
        Returns:
            Evaluation result dictionary with score (0-1)
        """
        try:
            if verbose:
                print("\n[EVAL] === New interaction evaluation ===")
                print(f"[EVAL] Service: {service_type}")
                print(f"[EVAL] Environment type: {type(environment_state).__name__}")
                print(f"[EVAL] Action type: {type(user_action).__name__}")
                print(f"[EVAL] System prompt length: {len(system_prompt)}")
            
            eval_id = eval_id or str(uuid.uuid4())
            if verbose:
                print(f"[EVAL] Using evaluation session: {eval_id}")
            
            service = cls._get_service(service_type, eval_id, config)
            if verbose:
                print("[EVAL] Service ready.")
            
            result = service.evaluate_interaction(environment_state, user_action, system_prompt)
            
            if verbose:
                print(f"[EVAL] Score: {result.get('score', 0.0):.2f}")
                print(f"[EVAL] Passed: {result.get('passed', False)}")
                print(f"[EVAL] Reasoning: {result.get('reasoning', 'No reasoning provided')[:100]}...")
            
            return result
            
        except Exception as e:
            print("\n[EvalWrapper.evaluate_interaction] crashed:", repr(e), file=sys.stderr)
            traceback.print_exc()
            raise
    
    @classmethod
    def batch_evaluate_interactions(cls,
                                  interaction_pairs: List[Dict[str, Any]],
                                  system_prompt: str = "",
                                  service_type: str = "mock",
                                  eval_id: Optional[str] = None,
                                  config: Optional[Dict[str, Any]] = None,
                                  verbose: bool = True) -> List[Dict[str, Any]]:
        """
        Evaluate multiple user-environment interactions in batch
        
        Args:
            interaction_pairs: List of dicts with 'environment_state' and 'user_action' keys
            system_prompt: System prompt defining the environment and user behavior
            service_type: Type of evaluation service
            eval_id: Evaluation session ID
            config: Configuration for the evaluation service
            verbose: Whether to print verbose output
            
        Returns:
            List of evaluation result dictionaries
        """
        try:
            if verbose:
                print("\n[EVAL] === Batch interaction evaluation ===")
                print(f"[EVAL] Service: {service_type}")
                print(f"[EVAL] Interaction count: {len(interaction_pairs)}")
                print(f"[EVAL] System prompt length: {len(system_prompt)}")
            
            eval_id = eval_id or str(uuid.uuid4())
            if verbose:
                print(f"[EVAL] Using evaluation session: {eval_id}")
            
            service = cls._get_service(service_type, eval_id, config)
            if verbose:
                print("[EVAL] Service ready.")
            
            results = service.batch_evaluate_interactions(interaction_pairs, system_prompt)
            
            if verbose:
                passed_count = sum(1 for r in results if r.get('passed', False))
                avg_score = sum(r.get('score', 0.0) for r in results) / len(results) if results else 0.0
                print(f"[EVAL] Batch completed: {passed_count}/{len(results)} passed")
                print(f"[EVAL] Average score: {avg_score:.2f}")
            
            return results
            
        except Exception as e:
            print("\n[EvalWrapper.batch_evaluate_interactions] crashed:", repr(e), file=sys.stderr)
            traceback.print_exc()
            raise
    
    @classmethod
    def get_metrics(cls, eval_id: str) -> Optional[Dict[str, Any]]:
        """
        Get aggregated metrics for an evaluation session
        
        Args:
            eval_id: Evaluation session ID
            
        Returns:
            Dictionary containing aggregated metrics
        """
        if eval_id in cls._services:
            return cls._services[eval_id].get_evaluation_metrics()
        return None
    
    @classmethod
    def get_history(cls, eval_id: str) -> List[Dict[str, Any]]:
        """
        Get evaluation history for a session
        
        Args:
            eval_id: Evaluation session ID
            
        Returns:
            List of evaluation results
        """
        if eval_id in cls._services:
            return cls._services[eval_id].get_history()
        return []
    
    @classmethod
    def reset_session(cls, eval_id: str):
        """
        Reset evaluation history for a session
        
        Args:
            eval_id: Evaluation session ID
        """
        if eval_id in cls._services:
            cls._services[eval_id].reset_history()
    
    @classmethod
    def save_results(cls, eval_id: str, filepath: str):
        """
        Save evaluation results to file
        
        Args:
            eval_id: Evaluation session ID
            filepath: Path to save results
        """
        if eval_id in cls._services:
            cls._services[eval_id].save_results(filepath)
    
    @classmethod
    def load_results(cls, eval_id: str, filepath: str):
        """
        Load evaluation results from file
        
        Args:
            eval_id: Evaluation session ID
            filepath: Path to load results from
        """
        if eval_id in cls._services:
            cls._services[eval_id].load_results(filepath)
    
    @classmethod
    def create_custom_service(cls,
                             eval_id: str,
                             evaluation_function: Optional[Callable] = None,
                             model_client: Optional[Any] = None,
                             config: Optional[Dict[str, Any]] = None) -> str:
        """
        Create a custom evaluation service
        
        Args:
            eval_id: Evaluation session ID
            evaluation_function: Custom evaluation function
            model_client: Model client for local evaluation
            config: Configuration dictionary
            
        Returns:
            Evaluation session ID
        """
        service = CustomEvalService(
            eval_id=eval_id,
            config=config,
            evaluation_function=evaluation_function,
            model_client=model_client
        )
        cls._services[eval_id] = service
        return eval_id
    
    @classmethod
    def test_service(cls, service_type: str, config: Optional[Dict[str, Any]] = None) -> bool:
        """
        Test if a service is working properly
        
        Args:
            service_type: Type of service to test
            config: Configuration for the service
            
        Returns:
            True if service is working, False otherwise
        """
        try:
            test_eval_id = str(uuid.uuid4())
            service = cls._get_service(service_type, test_eval_id, config)
            
            # Test with simple interaction
            result = service.evaluate_interaction(
                environment_state={"test": "environment"},
                user_action={"test": "action"},
                system_prompt="Test environment"
            )
            
            # Check if result has required fields
            required_fields = ["score", "reasoning", "passed"]
            return all(field in result for field in required_fields)
            
        except Exception:
            return False
    
    @classmethod
    def _get_service(cls, service_type: str, eval_id: str, config: Optional[Dict[str, Any]]) -> EvalServicesBase:
        """Get or create evaluation service instance"""
        if eval_id not in cls._services:
            config = config or {}
            
            if service_type.lower() == "geval":
                cls._services[eval_id] = GEvalService(
                    eval_id=eval_id,
                    config=config,
                    api_key=config.get("api_key")
                )
            elif service_type.lower() == "mock":
                cls._services[eval_id] = MockEvalService(
                    eval_id=eval_id,
                    config=config,
                    deterministic=config.get("deterministic", False)
                )
            elif service_type.lower() == "custom":
                cls._services[eval_id] = CustomEvalService(
                    eval_id=eval_id,
                    config=config,
                    evaluation_function=config.get("evaluation_function"),
                    model_client=config.get("model_client")
                )
            else:
                raise ValueError(f"Unknown service type: {service_type}")
        
        return cls._services[eval_id]
    
    @classmethod
    def list_services(cls) -> List[str]:
        """List all active evaluation services"""
        return list(cls._services.keys())
    
    @classmethod
    def clear_services(cls):
        """Clear all evaluation services"""
        cls._services.clear()


# Convenience functions for quick evaluation
def quick_evaluate_interaction(environment_state: Any, 
                             user_action: Any,
                             system_prompt: str = "",
                             service_type: str = "mock",
                             **kwargs) -> Dict[str, Any]:
    """
    Quick interaction evaluation function for simple use cases
    
    Args:
        environment_state: Current state of the environment
        user_action: Action taken by the user
        system_prompt: System prompt defining the environment and user behavior
        service_type: Type of evaluation service ("mock", "geval", "custom")
        **kwargs: Additional arguments passed to EvalWrapper.evaluate_interaction
        
    Returns:
        Evaluation result dictionary
    """
    return EvalWrapper.evaluate_interaction(
        environment_state=environment_state,
        user_action=user_action,
        system_prompt=system_prompt,
        service_type=service_type,
        **kwargs
    )


def quick_batch_evaluate_interactions(interaction_pairs: List[Dict[str, Any]],
                                    system_prompt: str = "",
                                    service_type: str = "mock",
                                    **kwargs) -> List[Dict[str, Any]]:
    """
    Quick batch interaction evaluation function for simple use cases
    
    Args:
        interaction_pairs: List of dicts with 'environment_state' and 'user_action' keys
        system_prompt: System prompt defining the environment and user behavior
        service_type: Type of evaluation service
        **kwargs: Additional arguments passed to EvalWrapper.batch_evaluate_interactions
        
    Returns:
        List of evaluation result dictionaries
    """
    return EvalWrapper.batch_evaluate_interactions(
        interaction_pairs=interaction_pairs,
        system_prompt=system_prompt,
        service_type=service_type,
        **kwargs
    )