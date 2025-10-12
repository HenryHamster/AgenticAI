"""
Configuration settings for the AgenticAI game
"""
import os
from dataclasses import dataclass
from typing import Dict, Any
from typing import Final

@dataclass
class GameConfig:
    """Game configuration settings"""
    # Game mechanics
    max_turns: int = 100
    world_size: int = 0
    starting_wealth: int = 100
    starting_health: int = 100
    player_vision: int = 0 #Measured in tiles away from player position
    # AI settings
    num_responses: int = 1 #Number of verdicts per action
    max_ai_retries: int = 0
    ai_timeout: int = 30  # seconds
    
    # File paths
    save_dir: str = "saves"
    data_dir: str = "data"
    
    def __post_init__(self):
        """Ensure directories exist"""
        os.makedirs(self.save_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)

@dataclass
class AIConfig:
    """AI service configuration"""
    # OpenAI settings
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_timeout: int = 30
    openai_max_tokens: int = 1000
    openai_model: str = "gpt-4.1-nano"
    openai_temperature: float = 0.7

    # Claude settings
    claude_api_key: str = os.getenv("CLAUDE_API_KEY", "")
    claude_model: str = "claude-3-sonnet-20240229"
    claude_temperature: float = 0.7

    # General AI settings
    system_prompt: str = "You are a D&D player character focused on maximizing wealth. Make strategic decisions following D&D rules."
    tile_prompt: str = (
        "You are the Dungeon Master of a tile-based fantasy world. "
        "Describe the terrain at the given coordinates in one vivid, concise sentence. "
        "Focus on environment and physical details only — no story, characters, or dialogue.\n\n"
        "Keep tone immersive and neutral-fantasy. Avoid repetition between nearby tiles.\n"
        "Examples:\n"
        "• 'A moss-covered stone path winding through damp roots.'\n"
        "• 'A cracked obsidian floor glowing faintly with runes.'\n"
        "• 'A dry grass plain littered with pottery shards.'"
    )
    tile_update_prompt: str = (
        "You are the Dungeon Master. Update the tile’s one-sentence description "
        "to reflect a recent event. Keep tone immersive and concise. "
        "Describe only visible environmental changes, no dialogue or story."
    )
    dm_prompt: str = (
        "You are the Dungeon Master for a Dungeons & Dragons campaign. "
        "Return one structured_response of type GameResponse as the VERDICT for players’ actions.\n\n"
        "Rules:\n"
        "1) Follow D&D logic with balance, consistency, and immersion.\n"
        "2) For each player in info.players, output one CharacterState keyed by UID.\n"
        "3) Give only CHANGES:\n"
        "   - money_change: gold ±int\n"
        "   - health_change: HP ±int\n"
        "   - position_change: [dx, dy]\n"
        "   Never output absolute totals.\n"
        "4) world_state.tiles fully replaces tile descriptions but keeps coordinates fixed.\n"
        "5) Include a one-sentence narration and boolean success.\n"
        "6) Use exactly the given player UIDs.\n"
        "7) If nothing changes, set all *_change = 0."
    )
    player_prompt:str = (
        "You are a Dungeons & Dragons player. "
        "Given the current situation, propose one short action your character will attempt this turn. "
        "You may act creatively, even bending or breaking typical D&D rules, "
        "but remember: impossible, reckless, or unethical actions may fail or backfire. "
        "Keep the response concise (a short phrase or single sentence) and focused on the action itself — "
        "do not narrate outcomes or include dialogue."
    )
    # Schema instruction for structured responses
    verdict_instruction: str = """
IMPORTANT: You must include at the end of your response a JSON object with the following structure:

{
    "character_state": {
        "money": <integer>,
        "skill_level": <integer>,
        "attributes": {
            "strength": <1-20>,
            "dexterity": <1-20>,
            "intelligence": <1-20>,
            "wisdom": <1-20>,
            "constitution": <1-20>,
            "charisma": <1-20>
        },
        "position": [x, y],
        "current_action": "<string>",
        "inventory": ["<item1>", "<item2>"],
        "health": <integer>,
        "experience": <integer>
    },
    "world_state": {
        "environment_type": "<string>",
        "description": "<string>",
        "available_actions": ["<action1>", "<action2>"],
        "npcs": ["<npc1>", "<npc2>"],
        "treasures": ["<treasure1>"],
        "hazards": ["<hazard1>"]
    },
    "narrative": "<your response text>"
}
"""

# Global configuration instances
game_config = GameConfig()
ai_config = AIConfig()

def get_config() -> Dict[str, Any]:
    """Get all configuration as a dictionary"""
    return {
        "game": game_config,
        "ai": ai_config
    }
