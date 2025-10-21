# Evaluation services package

from .evalServices.EvalServicesBase import EvalServicesBase, EvaluationResult, EvaluationConfig
from .evalServices.geval import GEvalService
from .evalServices.mock import MockEvalService
from .evalServices.custom import CustomEvalService
from .wrapper import EvalWrapper, quick_evaluate_interaction, quick_batch_evaluate_interactions

__all__ = [
    "EvalServicesBase",
    "EvaluationResult", 
    "EvaluationConfig",
    "GEvalService",
    "MockEvalService", 
    "CustomEvalService",
    "EvalWrapper",
    "quick_evaluate_interaction",
    "quick_batch_evaluate_interactions"
]

# Convenience aliases
evaluate_interaction = quick_evaluate_interaction
batch_evaluate_interactions = quick_batch_evaluate_interactions