# Custom evaluation service implementation for local models and custom evaluation logic

import json
import uuid
from typing import Optional, Dict, Any, List, Callable
from .EvalServicesBase import EvalServicesBase


class CustomEvalService(EvalServicesBase):
    """Custom evaluation service for local models and custom evaluation logic"""
    
    def __init__(self, 
                 eval_id: str = None, 
                 config: Dict[str, Any] = None, 
                 results_history: List[Dict[str, Any]] = None,
                 evaluation_function: Optional[Callable] = None,
                 model_client: Optional[Any] = None):
        """
        Initialize the custom evaluation service
        
        Args:
            eval_id: Unique identifier for this evaluation session
            config: Configuration dictionary
            results_history: Previous evaluation results
            evaluation_function: Custom function for evaluation
            model_client: Client for local model (e.g., transformers, llama-cpp-python)
        """
        super().__init__(eval_id or str(uuid.uuid4()), config, results_history)
        self.evaluation_function = evaluation_function
        self.model_client = model_client
    
    def evaluate_interaction(self, 
                           environment_state: Any, 
                           user_action: Any,
                           system_prompt: str = "") -> Dict[str, Any]:
        """
        Evaluate user-environment interaction using custom evaluation function or model
        
        Args:
            environment_state: Current state of the environment
            user_action: Action taken by the user
            system_prompt: System prompt defining the environment and user behavior
            
        Returns:
            Dictionary containing evaluation results
        """
        try:
            if self.evaluation_function:
                # Use custom evaluation function
                result = self.evaluation_function(
                    environment_state=environment_state,
                    user_action=user_action,
                    system_prompt=system_prompt,
                    config=self.config
                )
            elif self.model_client:
                # Use local model for evaluation
                result = self._evaluate_with_model(
                    environment_state=environment_state,
                    user_action=user_action,
                    system_prompt=system_prompt
                )
            else:
                # Fallback to simple heuristic evaluation
                result = self._heuristic_evaluation(
                    environment_state=environment_state,
                    user_action=user_action,
                    system_prompt=system_prompt
                )
            
            # Ensure result has required fields
            if not isinstance(result, dict):
                result = {"score": 0.0, "reasoning": "Invalid result format", "passed": False}
            
            # Add default fields if missing
            result.setdefault("score", 0.0)
            result.setdefault("reasoning", "Custom evaluation completed")
            result.setdefault("passed", result.get("score", 0.0) >= self.config.get("threshold", 0.7))
            result.setdefault("details", {})
            
            # Add custom service info
            result["details"]["custom_service"] = True
            result["details"]["has_eval_function"] = self.evaluation_function is not None
            result["details"]["has_model_client"] = self.model_client is not None
            
            self._append_result(result)
            return result
            
        except Exception as e:
            error_result = {
                "score": 0.0,
                "reasoning": f"Custom evaluation error: {str(e)}",
                "passed": False,
                "details": {
                    "error": "custom_evaluation_error",
                    "exception": str(e),
                    "custom_service": True
                }
            }
            self._append_result(error_result)
            return error_result
    
    def _evaluate_with_model(self, 
                           environment_state: Any, 
                           user_action: Any,
                           system_prompt: str = "") -> Dict[str, Any]:
        """Evaluate using local model"""
        try:
            # Create evaluation prompt
            prompt = self._create_evaluation_prompt(environment_state, user_action, system_prompt)
            
            # Generate response from model
            if hasattr(self.model_client, 'generate'):
                response = self.model_client.generate(prompt)
            elif hasattr(self.model_client, 'predict'):
                response = self.model_client.predict(prompt)
            elif callable(self.model_client):
                response = self.model_client(prompt)
            else:
                raise ValueError("Model client does not support generation")
            
            # Parse response
            result = self._parse_model_response(response)
            return result
            
        except Exception as e:
            return {
                "score": 0.0,
                "reasoning": f"Model evaluation error: {str(e)}",
                "passed": False,
                "details": {"error": "model_evaluation_error", "exception": str(e)}
            }
    
    def _heuristic_evaluation(self, 
                            environment_state: Any, 
                            user_action: Any,
                            system_prompt: str = "") -> Dict[str, Any]:
        """Fallback heuristic evaluation"""
        score = 0.5  # Base score
        
        # Adjust score based on environment complexity
        if isinstance(environment_state, dict):
            env_complexity = len(environment_state) / 10
            score += min(env_complexity * 0.1, 0.2)
        
        # Adjust score based on user action appropriateness
        if isinstance(user_action, str):
            if len(user_action) > 3:
                score += 0.1
            if any(word in user_action.lower() for word in ['help', 'please', 'good', 'yes', 'no']):
                score += 0.1
        
        # Check for logical consistency
        if isinstance(environment_state, dict) and isinstance(user_action, dict):
            env_keys = set(str(k).lower() for k in environment_state.keys())
            action_keys = set(str(k).lower() for k in user_action.keys())
            if env_keys.intersection(action_keys):
                score += 0.15
        
        score = min(1.0, score)
        
        return {
            "score": score,
            "reasoning": f"Heuristic evaluation based on environment-action interaction. Score: {score:.2f}",
            "passed": score >= self.config.get("threshold", 0.7),
            "details": {"evaluation_type": "heuristic"}
        }
    
    def _create_evaluation_prompt(self, 
                                environment_state: Any, 
                                user_action: Any,
                                system_prompt: str = "") -> str:
        """Create evaluation prompt for model"""
        prompt = f"""
Evaluate how well the user interacts with the environment.

System Prompt (Environment Definition): {system_prompt}

Environment State: {environment_state}
User Action: {user_action}

Please provide an evaluation in the following JSON format:
{{
    "score": <float between 0 and 1>,
    "reasoning": "<explanation of the evaluation>",
    "passed": <boolean>
}}

Score should reflect how appropriate and effective the user action is given the environment state and system prompt.
"""
        
        return prompt
    
    def _parse_model_response(self, response: str) -> Dict[str, Any]:
        """Parse model response into evaluation result"""
        try:
            # Try to extract JSON from response
            if isinstance(response, str):
                # Look for JSON in the response
                start_idx = response.find('{')
                end_idx = response.rfind('}') + 1
                
                if start_idx != -1 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    result = json.loads(json_str)
                    return result
            
            # Fallback: treat response as reasoning
            return {
                "score": 0.5,
                "reasoning": str(response),
                "passed": False,
                "details": {"parsing": "fallback"}
            }
            
        except Exception as e:
            return {
                "score": 0.0,
                "reasoning": f"Failed to parse model response: {str(e)}",
                "passed": False,
                "details": {"error": "parsing_error", "exception": str(e)}
            }
    
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
        results = []
        
        for i, interaction in enumerate(interaction_pairs):
            environment_state = interaction.get("environment_state")
            user_action = interaction.get("user_action")
            
            if environment_state is None or user_action is None:
                result = {
                    "score": 0.0,
                    "reasoning": "Missing environment state or user action",
                    "passed": False,
                    "details": {
                        "error": "missing_data",
                        "batch_index": i,
                        "custom_service": True
                    }
                }
            else:
                result = self.evaluate_interaction(environment_state, user_action, system_prompt)
                result["details"]["batch_index"] = i
            
            results.append(result)
        
        return results
    
    def get_evaluation_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics from evaluation history"""
        if not self.results_history:
            return {
                "total_evaluations": 0,
                "average_score": 0.0,
                "pass_rate": 0.0,
                "custom_service": True
            }
        
        scores = [result.get("score", 0.0) for result in self.results_history]
        passed_count = sum(1 for result in self.results_history if result.get("passed", False))
        
        return {
            "total_evaluations": len(self.results_history),
            "average_score": sum(scores) / len(scores) if scores else 0.0,
            "pass_rate": passed_count / len(self.results_history) if self.results_history else 0.0,
            "min_score": min(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0.0,
            "custom_service": True,
            "has_eval_function": self.evaluation_function is not None,
            "has_model_client": self.model_client is not None
        }
    
    def reset_history(self):
        """Reset evaluation history"""
        self.results_history = []
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get evaluation history"""
        return self.results_history.copy()
    
    def set_evaluation_function(self, evaluation_function: Callable):
        """Set custom evaluation function"""
        self.evaluation_function = evaluation_function
    
    def set_model_client(self, model_client: Any):
        """Set model client"""
        self.model_client = model_client