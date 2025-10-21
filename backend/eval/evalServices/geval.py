# G-Eval service implementation for evaluation services

import requests
import json
from typing import Optional, Dict, Any, List
from .EvalServicesBase import EvalServicesBase
import uuid
import time


class GEvalService(EvalServicesBase):
    """G-Eval service implementation for evaluation"""
    
    def __init__(self, 
                 eval_id: str = None, 
                 config: Dict[str, Any] = None, 
                 results_history: List[Dict[str, Any]] = None,
                 api_key: str = None,
                 base_url: str = "https://api.geval.ai/v1"):
        """
        Initialize the G-Eval service
        
        Args:
            eval_id: Unique identifier for this evaluation session
            config: Configuration dictionary
            results_history: Previous evaluation results
            api_key: G-Eval API key
            base_url: Base URL for G-Eval API
        """
        super().__init__(eval_id or str(uuid.uuid4()), config, results_history)
        self.api_key = api_key
        self.base_url = base_url
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
    
    def evaluate_interaction(self, 
                           environment_state: Any, 
                           user_action: Any,
                           system_prompt: str = "") -> Dict[str, Any]:
        """
        Evaluate user-environment interaction using G-Eval API
        
        Args:
            environment_state: Current state of the environment
            user_action: Action taken by the user
            system_prompt: System prompt defining the environment and user behavior
            
        Returns:
            Dictionary containing evaluation results
        """
        try:
            # Prepare evaluation request
            eval_request = {
                "environment_state": environment_state,
                "user_action": user_action,
                "system_prompt": system_prompt,
                "evaluation_type": "interaction_quality",
                "criteria": self.config.get("criteria", {}),
                "threshold": self.config.get("threshold", 0.7)
            }
            
            # Make API request
            response = self.session.post(
                f"{self.base_url}/evaluate_interaction",
                json=eval_request,
                timeout=self.config.get("timeout", 30)
            )
            
            if response.status_code == 200:
                result = response.json()
                self._append_result(result)
                return result
            else:
                error_result = {
                    "score": 0.0,
                    "reasoning": f"API error: {response.status_code} - {response.text}",
                    "passed": False,
                    "details": {"error": "api_error", "status_code": response.status_code}
                }
                self._append_result(error_result)
                return error_result
                
        except Exception as e:
            error_result = {
                "score": 0.0,
                "reasoning": f"Evaluation error: {str(e)}",
                "passed": False,
                "details": {"error": "evaluation_error", "exception": str(e)}
            }
            self._append_result(error_result)
            return error_result
    
    def batch_evaluate_interactions(self, 
                                  interaction_pairs: List[Dict[str, Any]],
                                  system_prompt: str = "") -> List[Dict[str, Any]]:
        """
        Evaluate multiple user-environment interactions in batch using G-Eval API
        
        Args:
            interaction_pairs: List of dicts with 'environment_state' and 'user_action' keys
            system_prompt: System prompt defining the environment and user behavior
            
        Returns:
            List of evaluation result dictionaries
        """
        try:
            # Prepare batch evaluation request
            batch_request = {
                "interactions": interaction_pairs,
                "system_prompt": system_prompt,
                "evaluation_type": "interaction_quality",
                "criteria": self.config.get("criteria", {}),
                "threshold": self.config.get("threshold", 0.7)
            }
            
            # Make API request
            response = self.session.post(
                f"{self.base_url}/batch_evaluate_interactions",
                json=batch_request,
                timeout=self.config.get("timeout", 60)
            )
            
            if response.status_code == 200:
                results = response.json().get("results", [])
                for result in results:
                    self._append_result(result)
                return results
            else:
                # Return error results for all interactions
                error_results = []
                for i in range(len(interaction_pairs)):
                    error_result = {
                        "score": 0.0,
                        "reasoning": f"Batch API error: {response.status_code} - {response.text}",
                        "passed": False,
                        "details": {"error": "batch_api_error", "status_code": response.status_code, "interaction_index": i}
                    }
                    error_results.append(error_result)
                    self._append_result(error_result)
                return error_results
                
        except Exception as e:
            # Return error results for all interactions
            error_results = []
            for i in range(len(interaction_pairs)):
                error_result = {
                    "score": 0.0,
                    "reasoning": f"Batch evaluation error: {str(e)}",
                    "passed": False,
                    "details": {"error": "batch_evaluation_error", "exception": str(e), "interaction_index": i}
                }
                error_results.append(error_result)
                self._append_result(error_result)
            return error_results
    
    def get_evaluation_metrics(self) -> Dict[str, Any]:
        """
        Get aggregated metrics from evaluation history
        
        Returns:
            Dictionary containing aggregated metrics
        """
        if not self.results_history:
            return {
                "total_evaluations": 0,
                "average_score": 0.0,
                "pass_rate": 0.0,
                "geval_service": True
            }
        
        scores = [result.get("score", 0.0) for result in self.results_history]
        passed_count = sum(1 for result in self.results_history if result.get("passed", False))
        
        return {
            "total_evaluations": len(self.results_history),
            "average_score": sum(scores) / len(scores) if scores else 0.0,
            "pass_rate": passed_count / len(self.results_history) if self.results_history else 0.0,
            "min_score": min(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0.0,
            "geval_service": True
        }
    
    def reset_history(self):
        """Reset evaluation history"""
        self.results_history = []
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get evaluation history"""
        return self.results_history.copy()
    
    def set_api_key(self, api_key: str):
        """Set or update the API key"""
        self.api_key = api_key
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
    
    def test_connection(self) -> bool:
        """Test connection to G-Eval API"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            return response.status_code == 200
        except Exception:
            return False