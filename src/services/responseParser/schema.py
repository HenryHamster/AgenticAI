from dataclasses import dataclass
from typing import Dict, Any, List, Tuple, Optional
import json

@dataclass
class DnDCharacterSchema:
    """Schema definition for D&D character state variables"""

    SCHEMA = {
        "type": "object",
        "properties": {
            "money": {"type": "integer", "minimum": 0},
            "skill_level": {"type": "integer", "minimum": 1},
            "attributes": {
                "type": "object",
                "properties": {
                    "strength": {"type": "integer", "minimum": 1, "maximum": 20},
                    "dexterity": {"type": "integer", "minimum": 1, "maximum": 20},
                    "intelligence": {"type": "integer", "minimum": 1, "maximum": 20},
                    "wisdom": {"type": "integer", "minimum": 1, "maximum": 20},
                    "constitution": {"type": "integer", "minimum": 1, "maximum": 20},
                    "charisma": {"type": "integer", "minimum": 1, "maximum": 20}
                },
                "required": ["strength", "dexterity", "intelligence", "wisdom", "constitution", "charisma"]
            },
            "position": {
                "type": "array",
                "items": {"type": "integer"},
                "minItems": 2,
                "maxItems": 2
            },
            "current_action": {"type": "string"},
            "inventory": {
                "type": "array",
                "items": {"type": "string"}
            },
            "health": {"type": "integer", "minimum": 0},
            "experience": {"type": "integer", "minimum": 0}
        },
        "required": ["money", "skill_level", "attributes", "position", "current_action", "health"]
    }

    DEFAULTS = {
        "money": 100,
        "skill_level": 1,
        "attributes": {
            "strength": 10,
            "dexterity": 10,
            "intelligence": 10,
            "wisdom": 10,
            "constitution": 10,
            "charisma": 10
        },
        "position": [0, 0],
        "current_action": "",
        "inventory": [],
        "health": 100,
        "experience": 0
    }

@dataclass
class WorldStateSchema:
    """Schema for world/environment state"""

    SCHEMA = {
        "type": "object",
        "properties": {
            "environment_type": {"type": "string"},
            "description": {"type": "string"},
            "available_actions": {
                "type": "array",
                "items": {"type": "string"}
            },
            "npcs": {
                "type": "array",
                "items": {"type": "string"}
            },
            "treasures": {
                "type": "array",
                "items": {"type": "string"}
            },
            "hazards": {
                "type": "array",
                "items": {"type": "string"}
            }
        },
        "required": ["environment_type", "description"]
    }

    DEFAULTS = {
        "environment_type": "plains",
        "description": "An open field with grass and scattered trees",
        "available_actions": [],
        "npcs": [],
        "treasures": [],
        "hazards": []
    }

