import json
import re
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass
from .schema import DnDCharacterSchema, WorldStateSchema

@dataclass
class ParsedResponse:
    """Container for parsed LLM response data"""
    character_state: Dict[str, Any]
    world_state: Dict[str, Any]
    narrative: str
    raw_response: str
    parse_errors: list[str]

class DnDResponseParser:
    """Parses LLM responses and extracts structured D&D game data"""

    def __init__(self):
        self.character_schema = DnDCharacterSchema()
        self.world_schema = WorldStateSchema()

    def parse_response(self, response: str) -> ParsedResponse:
        """Parse LLM response and extract structured data"""
        errors = []

        # Extract JSON from response
        json_data = self._extract_json(response)
        if not json_data:
            errors.append("No valid JSON found in response")
            return self._create_default_response(response, errors)

        # Parse character state
        character_state = self._parse_character_state(
            json_data.get("character_state", {}), errors
        )

        # Parse world state
        world_state = self._parse_world_state(
            json_data.get("world_state", {}), errors
        )

        # Extract narrative
        narrative = json_data.get("narrative", response)

        return ParsedResponse(
            character_state=character_state,
            world_state=world_state,
            narrative=narrative,
            raw_response=response,
            parse_errors=errors
        )

    def _extract_json(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from response text"""
        json_pattern = r'\{.*\}'

        matches = re.findall(json_pattern, response, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue

        # Try parsing entire response as JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return None

    def _parse_character_state(self, data: Dict[str, Any], errors: list[str]) -> Dict[str, Any]:
        """Parse and validate character state data"""
        result = self.character_schema.DEFAULTS.copy()

        if not data:
            errors.append("Missing character_state in response")
            return result

        # Parse basic fields
        for field in ["money", "skill_level", "health", "experience"]:
            if field in data:
                try:
                    result[field] = int(data[field])
                except (ValueError, TypeError):
                    errors.append(f"Invalid {field}: {data[field]}")

        # Parse attributes
        if "attributes" in data and isinstance(data["attributes"], dict):
            for attr in result["attributes"]:
                if attr in data["attributes"]:
                    try:
                        value = int(data["attributes"][attr])
                        result["attributes"][attr] = max(1, min(20, value))
                    except (ValueError, TypeError):
                        errors.append(f"Invalid attribute {attr}: {data['attributes'][attr]}")

        # Parse position
        if "position" in data:
            try:
                pos = data["position"]
                if isinstance(pos, list) and len(pos) >= 2:
                    result["position"] = [int(pos[0]), int(pos[1])]
                else:
                    errors.append(f"Invalid position format: {pos}")
            except (ValueError, TypeError):
                errors.append(f"Invalid position: {data['position']}")

        # Parse string fields
        for field in ["current_action"]:
            if field in data:
                result[field] = str(data[field])

        # Parse inventory
        if "inventory" in data:
            try:
                if isinstance(data["inventory"], list):
                    result["inventory"] = [str(item) for item in data["inventory"]]
                else:
                    errors.append(f"Inventory must be a list: {data['inventory']}")
            except Exception:
                errors.append(f"Invalid inventory: {data['inventory']}")

        return result

    def _parse_world_state(self, data: Dict[str, Any], errors: list[str]) -> Dict[str, Any]:
        """Parse and validate world state data"""
        result = self.world_schema.DEFAULTS.copy()

        if not data:
            errors.append("Missing world_state in response")
            return result

        # Parse string fields
        for field in ["environment_type", "description"]:
            if field in data:
                result[field] = str(data[field])

        # Parse list fields
        for field in ["available_actions", "npcs", "treasures", "hazards"]:
            if field in data:
                try:
                    if isinstance(data[field], list):
                        result[field] = [str(item) for item in data[field]]
                    else:
                        errors.append(f"{field} must be a list: {data[field]}")
                except Exception:
                    errors.append(f"Invalid {field}: {data[field]}")

        return result

    def _create_default_response(self, response: str, errors: list[str]) -> ParsedResponse:
        """Create response with default values when parsing fails"""
        return ParsedResponse(
            character_state=self.character_schema.DEFAULTS.copy(),
            world_state=self.world_schema.DEFAULTS.copy(),
            narrative=response,
            raw_response=response,
            parse_errors=errors
        )

    def get_schema_prompt(self) -> str:
        """Get the schema instruction for system prompts"""
        from .schema import get_system_prompt_schema_instruction
        return get_system_prompt_schema_instruction()

    def validate_response_format(self, response: str) -> bool:
        """Quick validation to check if response follows expected format"""
        try:
            json_data = self._extract_json(response)
            return json_data is not None and "character_state" in json_data
        except Exception:
            return False