# Main evaluation module - entry point for evaluation infrastructure

from .wrapper import EvalWrapper, quick_evaluate_interaction, quick_batch_evaluate_interactions

# Export main functionality
__all__ = [
    "EvalWrapper",
    "quick_evaluate_interaction",
    "quick_batch_evaluate_interactions"
]

# Convenience aliases
evaluate_interaction = quick_evaluate_interaction
batch_evaluate_interactions = quick_batch_evaluate_interactions
