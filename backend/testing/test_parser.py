#!/usr/bin/env python3
"""
Test script for the D&D response parser
"""

from src.services.responseParser.parser import DnDResponseParser

def test_parser():
    parser = DnDResponseParser()

    # Test case 1: Complete valid response
    valid_response = """
    I approach the merchant to negotiate a better price for the sword.

    {
        "character_state": {
            "money": 150,
            "skill_level": 2,
            "attributes": {
                "strength": 14,
                "dexterity": 12,
                "intelligence": 10,
                "wisdom": 13,
                "constitution": 11,
                "charisma": 16
            },
            "position": [3, 4],
            "current_action": "negotiating with merchant",
            "inventory": ["iron sword", "health potion"],
            "health": 85,
            "experience": 250
        },
        "world_state": {
            "environment_type": "marketplace",
            "description": "A bustling marketplace with various merchants and goods",
            "available_actions": ["buy", "sell", "negotiate", "leave"],
            "npcs": ["weapon merchant", "potion seller"],
            "treasures": [],
            "hazards": ["pickpockets"]
        },
        "narrative": "The merchant eyes you suspiciously but seems willing to negotiate."
    }
    """

    result = parser.parse_response(valid_response)
    print("=== Test 1: Valid Response ===")
    print(f"Character money: {result.character_state['money']}")
    print(f"Position: {result.character_state['position']}")
    print(f"Environment: {result.world_state['environment_type']}")
    print(f"Parse errors: {result.parse_errors}")
    print()

    # Test case 2: Malformed JSON
    malformed_response = """
    I cast a fireball at the dragon!

    {
        "character_state": {
            "money": "not_a_number",
            "position": [5],
            "invalid_field": true
        }
        // missing closing brace and world_state
    """

    result2 = parser.parse_response(malformed_response)
    print("=== Test 2: Malformed Response ===")
    print(f"Character money (default): {result2.character_state['money']}")
    print(f"Position (default): {result2.character_state['position']}")
    print(f"Parse errors: {result2.parse_errors}")
    print()

    # Test case 3: No JSON at all
    no_json_response = "I search for treasure in the ancient ruins."

    result3 = parser.parse_response(no_json_response)
    print("=== Test 3: No JSON ===")
    print(f"Narrative: {result3.narrative}")
    print(f"Using defaults - Money: {result3.character_state['money']}")
    print(f"Parse errors: {result3.parse_errors}")
    print()

    # Test schema prompt
    print("=== Schema Prompt ===")
    print(parser.get_schema_prompt())

if __name__ == "__main__":
    test_parser()