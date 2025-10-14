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
            "health": {"type": "integer", "minimum": 0},
            "position": {
                "type": "array",
                "items": {"type": "integer"},
                "minItems": 2,
                "maxItems": 2
            },
            "current_action": {"type": "string"},
            # "skill_level": {"type": "integer", "minimum": 1},
            # "attributes": {
            #     "type": "object",
            #     "properties": {
            #         "strength": {"type": "integer", "minimum": 1, "maximum": 20},
            #         "dexterity": {"type": "integer", "minimum": 1, "maximum": 20},
            #         "intelligence": {"type": "integer", "minimum": 1, "maximum": 20},
            #         "wisdom": {"type": "integer", "minimum": 1, "maximum": 20},
            #         "constitution": {"type": "integer", "minimum": 1, "maximum": 20},
            #         "charisma": {"type": "integer", "minimum": 1, "maximum": 20}
            #     },
            #     "required": ["strength", "dexterity", "intelligence", "wisdom", "constitution", "charisma"]
            # },
            # "inventory": {
            #     "type": "array",
            #     "items": {"type": "string"}
            # },
            # "experience": {"type": "integer", "minimum": 0}
        },
        "required": ["money", "health", "position", "current_action"] #, "skill_level", "attributes",
    }

    DEFAULTS = {
        "money": 100,
        "health": 100,
        "position": [0,0],
        "current_action": ""
        # "skill_level": 1,
        # "attributes": {
        #     "strength": 10,
        #     "dexterity": 10,
        #     "intelligence": 10,
        #     "wisdom": 10,
        #     "constitution": 10,
        #     "charisma": 10
        # },
        # "inventory": [],
        # "experience": 0
    }

@dataclass
class WorldStateSchema:
    """Schema for world/environment state"""

    SCHEMA = {
        "type": "object",
        "properties": {
            "tiles": {
                "type": "array",
                "description": "List of tiles, each mapping a coordinate [x,y] to a string value",
                "items": {
                    "type": "object",
                    "properties": {
                        "coord": {
                            "type": "array",
                            "items": {"type": "integer"},
                            "minItems": 2,
                            "maxItems": 2,
                            "description": "Coordinate [x,y]"
                        },
                        "value": {
                            "type": "string",
                            "description": "Tile description or type"
                        }
                    },
                    "required": ["coord", "value"],
                    "additionalProperties": False
                }
            }
        },
        "required": ["tiles"]
    }

    DEFAULTS = {
        "tiles": []
    }


