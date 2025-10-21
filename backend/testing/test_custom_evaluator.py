# Test Custom AI Evaluation Service

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from eval import EvalWrapper, CustomEvalService, quick_evaluate


def test_custom_evaluation():
    """Test custom AI evaluation service"""
    
    print("=== Testing Custom AI Evaluation Service ===\n")
    
    # Test data
    environment = "You are a customer service agent. A customer is complaining about a delayed order and is very upset."
    user_response = "I sincerely apologize for the inconvenience. Let me immediately check your order status and provide you with an updated timeline. I understand your frustration and want to resolve this quickly."
    
    print(f"Environment: {environment}")
    print(f"User Response: {user_response}")
    print()
    
    # Test EvalWrapper with custom service
    print("EVALWRAPPER WITH CUSTOM SERVICE:")
    try:
        result = EvalWrapper.evaluate(environment, user_response, service_type="custom")
        print(f"  Score: {result['score']:.2f}")
        print(f"  Reasoning: {result['reasoning']}")
        if 'relevance' in result:
            print(f"  Relevance: {result['relevance']:.2f}")
            print(f"  Appropriateness: {result['appropriateness']:.2f}")
            print(f"  Completeness: {result['completeness']:.2f}")
            print(f"  Clarity: {result['clarity']:.2f}")
        print(f"  Details: {result.get('details', {})}")
    except Exception as e:
        print(f"  Error: {e}")
    print()
    
    # Test quick_evaluate with custom service
    print("QUICK_EVALUATE WITH CUSTOM SERVICE:")
    try:
        result = quick_evaluate(environment, user_response, service_type="custom")
        print(f"  Score: {result['score']:.2f}")
        print(f"  Reasoning: {result['reasoning']}")
        if 'relevance' in result:
            print(f"  Relevance: {result['relevance']:.2f}")
            print(f"  Appropriateness: {result['appropriateness']:.2f}")
            print(f"  Completeness: {result['completeness']:.2f}")
            print(f"  Clarity: {result['clarity']:.2f}")
    except Exception as e:
        print(f"  Error: {e}")
    print()


def test_custom_service_directly():
    """Test CustomEvalService directly"""
    
    print("=== Testing CustomEvalService Directly ===\n")
    
    # Create custom service instance
    custom_service = CustomEvalService(
        eval_id="test-custom-001",
        ai_model="gpt-4.1-nano"
    )
    
    # Test scenarios
    scenarios = [
        {
            "name": "Excellent Response",
            "env": "You are a teacher. A student asks for help understanding calculus derivatives.",
            "response": "I'd be happy to help you understand derivatives! Let me break this down step by step. A derivative represents the rate of change of a function at any given point. We can think of it as the slope of the tangent line to the curve at that point."
        },
        {
            "name": "Good Response",
            "env": "You are a teacher. A student asks for help understanding calculus derivatives.",
            "response": "Derivatives show how fast something is changing. I can help you work through some examples."
        },
        {
            "name": "Poor Response",
            "env": "You are a teacher. A student asks for help understanding calculus derivatives.",
            "response": "Just memorize the formulas."
        },
        {
            "name": "Irrelevant Response",
            "env": "You are a teacher. A student asks for help understanding calculus derivatives.",
            "response": "I love pizza and the weather is nice today."
        }
    ]
    
    for scenario in scenarios:
        print(f"SCENARIO: {scenario['name']}")
        print(f"Environment: {scenario['env']}")
        print(f"Response: {scenario['response']}")
        
        try:
            result = custom_service.evaluate(
                scenario['env'], 
                scenario['response'], 
                None, 
                None
            )
            print(f"  Score: {result['score']:.2f}")
            print(f"  Reasoning: {result['reasoning']}")
            if 'relevance' in result:
                print(f"  Relevance: {result['relevance']:.2f}")
                print(f"  Appropriateness: {result['appropriateness']:.2f}")
                print(f"  Completeness: {result['completeness']:.2f}")
                print(f"  Clarity: {result['clarity']:.2f}")
        except Exception as e:
            print(f"  Error: {e}")
        print()


def test_custom_with_criteria():
    """Test custom evaluation with specific criteria"""
    
    print("=== Testing Custom Evaluation with Criteria ===\n")
    
    environment = "You are a software engineer. A colleague asks you to review their code for a critical bug fix."
    user_response = "I'll review your code carefully. Let me examine the logic, check for edge cases, and ensure the fix addresses the root cause without introducing new issues."
    
    # Define evaluation criteria
    criteria = {
        "focus_areas": ["technical_accuracy", "communication_clarity", "thoroughness"],
        "minimum_score": 0.6,
        "weighted_metrics": {
            "relevance": 0.3,
            "appropriateness": 0.3,
            "completeness": 0.2,
            "clarity": 0.2
        }
    }
    
    print(f"Environment: {environment}")
    print(f"User Response: {user_response}")
    print(f"Criteria: {criteria}")
    print()
    
    try:
        result = quick_evaluate(
            environment, 
            user_response, 
            evaluation_criteria=criteria,
            service_type="custom"
        )
        print(f"Score: {result['score']:.2f}")
        print(f"Reasoning: {result['reasoning']}")
        if 'relevance' in result:
            print(f"Relevance: {result['relevance']:.2f}")
            print(f"Appropriateness: {result['appropriateness']:.2f}")
            print(f"Completeness: {result['completeness']:.2f}")
            print(f"Clarity: {result['clarity']:.2f}")
    except Exception as e:
        print(f"Error: {e}")
    print()


def test_custom_service_history():
    """Test custom service evaluation history"""
    
    print("=== Testing Custom Service History ===\n")
    
    custom_service = CustomEvalService(
        eval_id="test-history-001",
        threshold=0.6
    )
    
    # Run multiple evaluations
    test_cases = [
        ("You are a chef. A customer asks about gluten-free options.", "We have several gluten-free dishes available. Let me show you our menu and explain the ingredients."),
        ("You are a chef. A customer asks about gluten-free options.", "No."),
        ("You are a chef. A customer asks about gluten-free options.", "I love cooking pasta and bread.")
    ]
    
    print("Running multiple evaluations...")
    for i, (env, response) in enumerate(test_cases):
        try:
            result = custom_service.evaluate(env, response, None, None)
            print(f"  Evaluation {i+1}: Score={result['score']:.2f}")
        except Exception as e:
            print(f"  Evaluation {i+1}: Error - {e}")
    
    print(f"\nTotal evaluations in history: {len(custom_service.results_history)}")
    print("History details:")
    for i, result in enumerate(custom_service.results_history):
        print(f"  {i+1}. Score: {result.get('score', 0):.2f}, Timestamp: {result.get('timestamp', 'N/A')}")


def show_custom_service_features():
    """Show custom service features and capabilities"""
    
    print("=== Custom Service Features ===\n")
    
    print("The CustomEvalService provides:")
    print("1. AI-powered evaluation using structured Pydantic models")
    print("2. Multiple evaluation metrics:")
    print("   - Overall score (0.0-1.0)")
    print("   - Relevance score")
    print("   - Appropriateness score") 
    print("   - Completeness score")
    print("   - Clarity score")
    print("3. Detailed reasoning for each evaluation")
    print("4. Configurable threshold for pass/fail")
    print("5. Support for custom evaluation criteria")
    print("6. Evaluation history tracking")
    print("7. Integration with AI wrapper system")
    print()
    print("Usage examples:")
    print("  # Basic usage")
    print("  result = quick_evaluate(env, response, service_type='custom')")
    print()
    print("  # With custom AI model")
    print("  result = quick_evaluate(env, response, service_type='custom', ai_model='gpt-4')")
    print()
    print("  # With evaluation criteria")
    print("  criteria = {'focus_areas': ['technical_accuracy', 'clarity']}")
    print("  result = quick_evaluate(env, response, service_type='custom', evaluation_criteria=criteria)")


if __name__ == "__main__":
    test_custom_evaluation()
    test_custom_service_directly()
    test_custom_with_criteria()
    show_custom_service_features()
