# Mock evaluation service implementation for testing and development

import random
import uuid
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from .EvalServicesBase import EvalServicesBase


class MockEvalService(EvalServicesBase):
    """Mock evaluation service for testing and development"""
    
    def __init__(self, 
                 eval_id: str = None, 
                 config: Dict[str, Any] = None, 
                 results_history: List[Dict[str, Any]] = None,
                 deterministic: bool = False):
        """
        Initialize the mock evaluation service
        
        Args:
            eval_id: Unique identifier for this evaluation session
            config: Configuration dictionary
            results_history: Previous evaluation results
            deterministic: If True, use deterministic scoring
        """
        super().__init__(eval_id or str(uuid.uuid4()), "", results_history)
        self.config = config or {}
        self.deterministic = deterministic
        self.seed = 42 if deterministic else None
        
        if self.seed:
            random.seed(self.seed)
    
    def evaluate(self, 
                 environment: str, 
                 user_response: str,
                 expected_output: Optional[str],
                 evaluation_criteria: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Mock evaluation that returns simulated results
        
        Args:
            environment: The environment description
            user_response: The user's response
            expected_output: Expected response (optional)
            evaluation_criteria: Custom criteria for evaluation
            
        Returns:
            Dictionary containing mock evaluation results
        """
        # Generate mock score based on input characteristics
        combined_text = environment + " " + user_response
        if len(combined_text) > 0:
            # Simple heuristic: longer inputs tend to score higher
            base_score = min(0.3 + (len(combined_text) / 1000) * 0.4, 0.9)
        else:
            base_score = random.uniform(0.4, 0.8)
        
        # Add some randomness unless deterministic
        if not self.deterministic:
            score = base_score + random.uniform(-0.1, 0.1)
        else:
            score = base_score
        
        score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
        
        # Generate mock metrics
        metrics = {
            "accuracy": score + random.uniform(-0.05, 0.05) if not self.deterministic else score,
            "relevance": score + random.uniform(-0.1, 0.1) if not self.deterministic else score,
            "coherence": score + random.uniform(-0.08, 0.08) if not self.deterministic else score,
            "completeness": score + random.uniform(-0.06, 0.06) if not self.deterministic else score
        }
        
        # Clamp metrics to [0, 1]
        for key in metrics:
            metrics[key] = max(0.0, min(1.0, metrics[key]))
        
        # Determine if passed
        threshold = self.config.get("threshold", 0.7)
        passed = score >= threshold
        
        # Generate mock reasoning
        reasoning_templates = [
            f"The input demonstrates {'good' if score > 0.7 else 'adequate' if score > 0.5 else 'poor'} quality with a score of {score:.2f}.",
            f"Evaluation shows {'strong' if score > 0.8 else 'moderate' if score > 0.6 else 'weak'} performance across all metrics.",
            f"Results indicate {'excellent' if score > 0.8 else 'satisfactory' if score > 0.6 else 'needs improvement'} based on the evaluation criteria."
        ]
        
        reasoning = random.choice(reasoning_templates) if not self.deterministic else reasoning_templates[0]
        
        result = {
            "score": score,
            "metrics": metrics,
            "reasoning": reasoning,
            "passed": passed,
            "details": {
                "environment_length": len(environment),
                "response_length": len(user_response),
                "has_expected_output": expected_output is not None,
                "criteria_count": len(evaluation_criteria) if evaluation_criteria else 0,
                "mock_evaluation": True
            }
        }
        
        return result    