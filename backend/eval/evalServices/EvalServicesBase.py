# Base class for Evaluation Services. This will be used to create a base class for all Evaluation Services.
# Having the base methods will allow for easy extension and reuse of the Evaluation Services.

from dataclasses import dataclass
from abc import abstractmethod
from typing import Optional, Dict, Any, List, Union
import json
from datetime import datetime


@dataclass
class EvalServicesBase:
    """Base class for all evaluation services"""
    
    eval_id: str
    config: Dict[str, Any]
    results_history: List[Dict[str, Any]]
    
    def __init__(self, eval_id: str, config: Dict[str, Any] = None, results_history: List[Dict[str, Any]] = None):
        self.eval_id = eval_id
        self.config = config or {}
        self.results_history = results_history or []
    
    @abstractmethod
    def evaluate_interaction(self, 
                           environment_state: Any, 
                           user_action: Any,
                           system_prompt: str = "") -> Dict[str, Any]:
        """
        Evaluate how well a user interacts with an environment
        
        Args:
            environment_state: Current state of the environment
            user_action: Action taken by the user
            system_prompt: System prompt defining the environment and user behavior
            
        Returns:
            Dictionary containing evaluation results with score (0-1)
        """
        raise NotImplementedError("evaluate_interaction method not implemented")
    
    @abstractmethod
    def batch_evaluate_interactions(self, 
                                  interaction_pairs: List[Dict[str, Any]],
                                  system_prompt: str = "") -> List[Dict[str, Any]]:
        """
        Evaluate multiple user-environment interactions in batch
        
        Args:
            interaction_pairs: List of dicts with 'environment_state' and 'user_action' keys
            system_prompt: System prompt defining the environment and user behavior
            
        Returns:
            List of evaluation result dictionaries
        """
        raise NotImplementedError("batch_evaluate_interactions method not implemented")
    
    @abstractmethod
    def get_evaluation_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated metrics from evaluation history
        
        Returns:
            Dictionary containing aggregated metrics
        """
        raise NotImplementedError("get_evaluation_metrics method not implemented")
    
    @abstractmethod
    def reset_history(self):
        """Reset evaluation history"""
        raise NotImplementedError("reset_history method not implemented")
    
    @abstractmethod
    def get_history(self) -> List[Dict[str, Any]]:
        """Get evaluation history"""
        raise NotImplementedError("get_history method not implemented")
    
    def _append_result(self, result: Dict[str, Any]):
        """Helper method to append result to history"""
        result["timestamp"] = datetime.now().isoformat()
        result["eval_id"] = self.eval_id
        self.results_history.append(result)
    
    def save_results(self, filepath: str):
        """Save evaluation results to file"""
        with open(filepath, 'w') as f:
            json.dump({
                "eval_id": self.eval_id,
                "config": self.config,
                "results": self.results_history,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2)
    
    def load_results(self, filepath: str):
        """Load evaluation results from file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
            self.eval_id = data.get("eval_id", self.eval_id)
            self.config = data.get("config", self.config)
            self.results_history = data.get("results", self.results_history)


# Simple data classes for evaluation results (no Pydantic dependency)
class EvaluationResult:
    """Simple evaluation result class"""
    
    def __init__(self, score: float, reasoning: str, passed: bool = None, details: Dict[str, Any] = None):
        self.score = max(0.0, min(1.0, score))  # Clamp to 0-1
        self.reasoning = reasoning
        self.passed = passed if passed is not None else (score >= 0.7)
        self.details = details or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "score": self.score,
            "reasoning": self.reasoning,
            "passed": self.passed,
            "details": self.details
        }


class EvaluationConfig:
    """Simple configuration class"""
    
    def __init__(self, 
                 system_prompt: str = "",
                 threshold: float = 0.7,
                 max_retries: int = 3,
                 timeout: int = 30,
                 **kwargs):
        self.system_prompt = system_prompt
        self.threshold = threshold
        self.max_retries = max_retries
        self.timeout = timeout
        self.extra_config = kwargs
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "system_prompt": self.system_prompt,
            "threshold": self.threshold,
            "max_retries": self.max_retries,
            "timeout": self.timeout,
            **self.extra_config
        }