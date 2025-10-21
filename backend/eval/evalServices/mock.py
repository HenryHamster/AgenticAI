# Mock evaluation service implementation for testing and development

import random
import uuid
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from .EvalServicesBase import EvalServicesBase, EvaluationResult, EvaluationConfig


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
        super().__init__(eval_id or str(uuid.uuid4()), config, results_history)
        self.deterministic = deterministic
        self.seed = 42 if deterministic else None
        
        if self.seed:
            random.seed(self.seed)
    
    def evaluate(self, 
                 input_data: Any, 
                 expected_output: Optional[Any] = None,
                 evaluation_criteria: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Mock evaluation that returns simulated results
        
        Args:
            input_data: The data to evaluate
            expected_output: Expected output for comparison
            evaluation_criteria: Custom criteria for evaluation
            
        Returns:
            Dictionary containing mock evaluation results
        """
        # Generate mock score based on input characteristics
        if isinstance(input_data, str):
            # Simple heuristic: longer inputs tend to score higher
            base_score = min(0.3 + (len(input_data) / 1000) * 0.4, 0.9)
        elif isinstance(input_data, (list, dict)):
            # Complex data structures get higher scores
            base_score = 0.6 + random.uniform(0.0, 0.3)
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
                "input_type": type(input_data).__name__,
                "input_length": len(str(input_data)) if hasattr(input_data, '__len__') else 0,
                "has_expected_output": expected_output is not None,
                "criteria_count": len(evaluation_criteria) if evaluation_criteria else 0,
                "mock_evaluation": True
            }
        }
        
        self._append_result(result)
        return result
    
    def batch_evaluate(self, 
                      input_data_list: List[Any], 
                      expected_outputs: Optional[List[Any]] = None,
                      evaluation_criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Mock batch evaluation
        
        Args:
            input_data_list: List of data to evaluate
            expected_outputs: List of expected outputs
            evaluation_criteria: Custom criteria for evaluation
            
        Returns:
            List of mock evaluation result dictionaries
        """
        results = []
        
        for i, input_data in enumerate(input_data_list):
            expected_output = expected_outputs[i] if expected_outputs and i < len(expected_outputs) else None
            
            result = self.evaluate(input_data, expected_output, evaluation_criteria)
            result["details"]["batch_index"] = i
            results.append(result)
        
        return results
    
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
                "metrics_summary": {},
                "mock_service": True
            }
        
        scores = [result.get("score", 0.0) for result in self.results_history]
        passed_count = sum(1 for result in self.results_history if result.get("passed", False))
        
        # Aggregate metrics
        all_metrics = {}
        for result in self.results_history:
            metrics = result.get("metrics", {})
            for key, value in metrics.items():
                if key not in all_metrics:
                    all_metrics[key] = []
                all_metrics[key].append(value)
        
        # Calculate averages
        metrics_summary = {}
        for key, values in all_metrics.items():
            metrics_summary[key] = sum(values) / len(values) if values else 0.0
        
        return {
            "total_evaluations": len(self.results_history),
            "average_score": sum(scores) / len(scores) if scores else 0.0,
            "pass_rate": passed_count / len(self.results_history) if self.results_history else 0.0,
            "metrics_summary": metrics_summary,
            "min_score": min(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0.0,
            "mock_service": True,
            "deterministic": self.deterministic
        }
    
    def reset_history(self):
        """Reset evaluation history"""
        self.results_history = []
        if self.seed:
            random.seed(self.seed)  # Reset random seed for deterministic behavior
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get evaluation history"""
        return self.results_history.copy()
    
    def set_deterministic(self, deterministic: bool):
        """Set deterministic mode"""
        self.deterministic = deterministic
        if deterministic:
            self.seed = 42
            random.seed(self.seed)
        else:
            self.seed = None
