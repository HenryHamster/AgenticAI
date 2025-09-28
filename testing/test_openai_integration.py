#!/usr/bin/env python3

from src.services.aiServices.openai import OpenAiService
from src.core.settings import ai_config

def test_openai_integration():
    """Test OpenAI service with structured response parsing"""

    service = OpenAiService("test_chat", [])

    # Test message simulating a D&D action
    test_message = "I enter the tavern and approach the barkeeper to ask about local treasures and job opportunities."

    print("=== System Prompt with Schema ===")
    schema_prompt = service.parser.get_schema_prompt()
    full_prompt = ai_config.system_prompt + schema_prompt
    print(full_prompt[:500] + "..." if len(full_prompt) > 500 else full_prompt)
    print()

    print("=== Testing Structured Response ===")
    print(f"User message: {test_message}")
    print()

    # Get structured response
    try:
        parsed_result = service.ask_ai_response_structured(test_message)

        if parsed_result:
            print("✓ Received structured response")
            print(f"Character money: {parsed_result.character_state['money']}")
            print(f"Position: {parsed_result.character_state['position']}")
            print(f"Current action: {parsed_result.character_state['current_action']}")
            print(f"Environment: {parsed_result.world_state['environment_type']}")
            print(f"Available actions: {parsed_result.world_state['available_actions']}")
            print(f"NPCs: {parsed_result.world_state['npcs']}")
            print()

            if parsed_result.parse_errors:
                print(f"⚠ Parse errors: {parsed_result.parse_errors}")
            else:
                print("✓ No parse errors")
            print()

            print("=== Raw Response ===")
            print(parsed_result.raw_response)
            print()

        else:
            print("✗ Failed to get response from OpenAI")

    except Exception as e:
        print(f"✗ Error during API call: {e}")

    print("=== Testing Regular Response (for comparison) ===")
    try:
        regular_response = service.ask_ai_response("What do you see in the tavern?")
        if regular_response:
            print("Regular response:", regular_response[:200] + "..." if len(regular_response) > 200 else regular_response)
        else:
            print("✗ Failed to get regular response")
    except Exception as e:
        print(f"✗ Error during regular API call: {e}")

def test_parser_validation():
    """Test parser with sample OpenAI-style responses"""

    from src.services.responseParser.parser import DnDResponseParser

    parser = DnDResponseParser()

    # Simulate realistic OpenAI response
    sample_response = """I greet the barkeeper with a friendly smile and order an ale. "Good evening! I'm new to these parts. I've heard rumors of ancient ruins nearby - any truth to those tales? Also, are there any merchants or adventurers looking for skilled help?"

{
    "character_state": {
        "money": 95,
        "skill_level": 1,
        "attributes": {
            "strength": 12,
            "dexterity": 14,
            "intelligence": 13,
            "wisdom": 11,
            "constitution": 10,
            "charisma": 15
        },
        "position": [2, 3],
        "current_action": "talking to barkeeper in tavern",
        "inventory": ["traveler's clothes", "coin purse", "walking stick"],
        "health": 100,
        "experience": 0
    },
    "world_state": {
        "environment_type": "tavern",
        "description": "A cozy tavern with wooden tables, a stone fireplace, and the smell of roasted meat",
        "available_actions": ["order drink", "ask about rumors", "talk to patrons", "rent room", "leave"],
        "npcs": ["barkeeper", "old merchant", "local farmer"],
        "treasures": [],
        "hazards": []
    },
    "narrative": "The barkeeper nods knowingly and leans in closer, lowering his voice."
}"""

    print("=== Testing Parser with Realistic Response ===")
    result = parser.parse_response(sample_response)

    print(f"✓ Character money: {result.character_state['money']}")
    print(f"✓ Charisma: {result.character_state['attributes']['charisma']}")
    print(f"✓ Inventory: {result.character_state['inventory']}")
    print(f"✓ Environment: {result.world_state['environment_type']}")
    print(f"✓ NPCs: {result.world_state['npcs']}")
    print(f"✓ Narrative: {result.narrative}")

    if result.parse_errors:
        print(f"⚠ Parse errors: {result.parse_errors}")
    else:
        print("✓ No parse errors - perfect parsing!")

if __name__ == "__main__":
    print("Testing D&D Response Parser with OpenAI Integration")
    print("=" * 60)

    # Test parser validation first
    test_parser_validation()
    print("\n" + "=" * 60 + "\n")

    # Test actual OpenAI integration (requires API key)
    if ai_config.openai_api_key:
        test_openai_integration()
    else:
        print("OpenAI API key not found - skipping live API test")
        print("Set OPENAI_API_KEY environment variable to test live integration")