# Simplified Evaluation Infrastructure

A simple evaluation infrastructure focused on environment-user interaction scoring, similar to the AI services structure but without external model dependencies.

## Overview

This evaluation infrastructure provides a unified interface for evaluating how well users interact with environments. It uses a system prompt to define the environment and expected user behavior, then scores interactions from 0-1 based on appropriateness and quality.

## Key Features

- **No External Dependencies**: No Pydantic or other heavy dependencies required
- **Simple Scoring**: 0-1 score based on environment-user interaction quality
- **System Prompt Driven**: Uses system prompts to define environment and user behavior
- **Multiple Services**: Mock, G-Eval, and Custom evaluation services
- **Batch Evaluation**: Support for evaluating multiple interactions at once

## Quick Start

### Basic Interaction Evaluation

```python
from eval import EvalWrapper

# Define environment and user action
environment_state = {
    "weather": "sunny",
    "temperature": 75,
    "location": "park"
}

user_action = {
    "action": "go_for_walk",
    "reasoning": "Perfect weather for a walk"
}

system_prompt = """
You are evaluating how well a user interacts with their environment.
Users should make appropriate decisions based on current conditions.
Good interactions show logical reasoning and appropriate responses.
"""

# Evaluate the interaction
result = EvalWrapper.evaluate_interaction(
    environment_state=environment_state,
    user_action=user_action,
    system_prompt=system_prompt,
    service_type="mock"
)

print(f"Score: {result['score']:.2f}")  # 0.0 to 1.0
print(f"Passed: {result['passed']}")    # True/False
print(f"Reasoning: {result['reasoning']}")
```

### Batch Evaluation

```python
interactions = [
    {
        "environment_state": {"weather": "rainy", "temperature": 45},
        "user_action": {"action": "stay_inside", "reasoning": "It's raining"}
    },
    {
        "environment_state": {"weather": "sunny", "temperature": 80},
        "user_action": {"action": "go_swimming", "reasoning": "Perfect beach weather"}
    }
]

results = EvalWrapper.batch_evaluate_interactions(
    interaction_pairs=interactions,
    system_prompt="Evaluate weather-appropriate actions",
    service_type="mock"
)

for i, result in enumerate(results):
    print(f"Interaction {i+1}: Score {result['score']:.2f}")
```

### Quick Functions

```python
from eval import quick_evaluate_interaction, quick_batch_evaluate_interactions

# Quick single evaluation
result = quick_evaluate_interaction(
    environment_state={"weather": "sunny"},
    user_action={"action": "go_outside"},
    system_prompt="Evaluate weather-appropriate actions"
)

# Quick batch evaluation
results = quick_batch_evaluate_interactions(
    interaction_pairs=interactions,
    system_prompt="Evaluate weather-appropriate actions"
)
```

## Service Types

### Mock Service (`mock`)
- **Purpose**: Testing and development
- **Features**: Deterministic or random scoring
- **Use Case**: When you need consistent results for testing

```python
result = EvalWrapper.evaluate_interaction(
    environment_state=env_state,
    user_action=user_action,
    system_prompt=system_prompt,
    service_type="mock",
    config={"deterministic": True, "threshold": 0.7}
)
```

### G-Eval Service (`geval`)
- **Purpose**: Production evaluation using G-Eval API
- **Features**: Real evaluation metrics, API integration
- **Use Case**: When you need professional evaluation services

```python
result = EvalWrapper.evaluate_interaction(
    environment_state=env_state,
    user_action=user_action,
    system_prompt=system_prompt,
    service_type="geval",
    config={"api_key": "your-api-key"}
)
```

### Custom Service (`custom`)
- **Purpose**: Custom evaluation logic or local models
- **Features**: Custom evaluation functions, local model integration
- **Use Case**: When you have specific evaluation requirements

```python
def my_eval_function(environment_state, user_action, system_prompt="", config=None):
    # Your custom evaluation logic
    score = 0.8  # Calculate based on your criteria
    return {
        "score": score,
        "reasoning": "Custom evaluation completed",
        "passed": score >= 0.7
    }

eval_id = EvalWrapper.create_custom_service(
    eval_id="my_custom_eval",
    evaluation_function=my_eval_function
)

result = EvalWrapper.evaluate_interaction(
    environment_state=env_state,
    user_action=user_action,
    eval_id=eval_id
)
```

## Evaluation Structure

### Input Format

**Environment State**: Any data structure representing the current environment
```python
environment_state = {
    "weather": "sunny",
    "temperature": 75,
    "location": "park",
    "time": "afternoon"
}
```

**User Action**: Any data structure representing the user's action
```python
user_action = {
    "action": "go_for_walk",
    "reasoning": "Perfect weather for outdoor activity",
    "details": {"duration": "30_minutes"}
}
```

**System Prompt**: String defining the environment and expected user behavior
```python
system_prompt = """
You are evaluating user-environment interactions.
The environment includes weather, temperature, location, and time.
Users should make appropriate decisions based on current conditions.
Good interactions show logical reasoning and appropriate responses.
"""
```

### Output Format

**Evaluation Result**: Dictionary with score and reasoning
```python
{
    "score": 0.85,           # Float between 0.0 and 1.0
    "reasoning": "Excellent interaction! The user action shows good understanding...",
    "passed": True,          # Boolean based on threshold
    "details": {             # Additional evaluation details
        "environment_type": "dict",
        "action_type": "dict",
        "mock_evaluation": True
    }
}
```

## Advanced Usage

### Evaluation Sessions

```python
# Create a persistent evaluation session
eval_id = "my_evaluation_session"

# Run multiple evaluations in the same session
EvalWrapper.evaluate_interaction(env1, action1, system_prompt, eval_id=eval_id)
EvalWrapper.evaluate_interaction(env2, action2, system_prompt, eval_id=eval_id)

# Get aggregated metrics
metrics = EvalWrapper.get_metrics(eval_id)
print(f"Average score: {metrics['average_score']:.2f}")
print(f"Pass rate: {metrics['pass_rate']:.2f}")
```

### Saving and Loading Results

```python
# Save evaluation results
EvalWrapper.save_results(eval_id, "results.json")

# Load evaluation results
EvalWrapper.load_results(eval_id, "results.json")
```

### Service Testing

```python
# Test if a service is working
if EvalWrapper.test_service("mock"):
    print("Mock service is available")
else:
    print("Mock service is not available")
```

## Game-Specific Evaluation

The infrastructure works well for game evaluation:

```python
def game_eval_function(environment_state, user_action, system_prompt="", config=None):
    score = 0.5
    
    # Check if action is appropriate for game state
    if "position" in environment_state and "move" in user_action:
        score += 0.2
    
    # Check for strategic thinking
    reasoning = user_action.get("reasoning", "")
    if "strategy" in reasoning.lower():
        score += 0.3
    
    return {
        "score": min(1.0, score),
        "reasoning": f"Game interaction evaluation. Score: {score:.2f}",
        "passed": score >= 0.6
    }

# Create game evaluation service
eval_id = EvalWrapper.create_custom_service(
    eval_id="game_eval",
    evaluation_function=game_eval_function
)

# Evaluate game interaction
game_state = {"player_position": [5, 3], "enemies": [{"pos": [7, 3]}]}
player_action = {"action": "move_towards_enemy", "reasoning": "Strategic engagement"}

result = EvalWrapper.evaluate_interaction(game_state, player_action, eval_id=eval_id)
```

## Configuration

### Service Configuration

```python
config = {
    "threshold": 0.7,        # Pass/fail threshold
    "timeout": 30,           # Timeout in seconds
    "max_retries": 3,        # Maximum retries
    "deterministic": True,   # For mock service
    "api_key": "key"         # For G-Eval service
}

result = EvalWrapper.evaluate_interaction(
    environment_state=env_state,
    user_action=user_action,
    system_prompt=system_prompt,
    service_type="mock",
    config=config
)
```

## Examples

See `examples.py` for comprehensive examples including:
- Basic interaction evaluation
- Batch evaluation
- Custom evaluation functions
- Game-specific evaluation
- Metrics and reporting

## Error Handling

The infrastructure includes comprehensive error handling:

```python
try:
    result = EvalWrapper.evaluate_interaction(
        environment_state=env_state,
        user_action=user_action,
        service_type="geval",
        config={"api_key": "invalid-key"}
    )
except Exception as e:
    print(f"Evaluation failed: {e}")
    # Fallback to mock service
    result = EvalWrapper.evaluate_interaction(
        environment_state=env_state,
        user_action=user_action,
        service_type="mock"
    )
```

This simplified evaluation infrastructure provides a clean, dependency-free way to evaluate user-environment interactions with scores from 0-1, perfect for game evaluation and other interaction-based assessments.
