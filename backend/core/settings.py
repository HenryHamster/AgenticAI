"""
Configuration settings for the AgenticAI game
"""
import os
from dataclasses import dataclass
from typing import Dict, Any
from typing import Final
from dotenv import load_dotenv

load_dotenv()

@dataclass
class GameConfig:
    """Game configuration settings"""
    # Game mechanics
    max_turns: int = 100

    world_size: int = 1
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
    system_prompt: str = "You are a D&D player character focused on maximizing wealth. Make strategic decisions to selfishly maximize your wealth at any cost. Be aware that you're actions may not follow through as intended."
    tile_prompt: str = (
        "You are the Dungeon Master of a tile-based fantasy world. "
        "Describe the terrain at the given coordinates in one vivid, concise sentence, including one word for terrain type and two emojis. "
        "The emojis should not include a person, human, or animal. It should be a symbol that represents the terrain or environment."
        "Focus on environment and physical details only.\n\n"
        "Ensure that all tiles are interesting and provide opportunities."
        "Keep tone immersive and neutral-fantasy. Avoid repetition between nearby tiles.\n"
    )
    tile_update_prompt: str = (
        "You are the Dungeon Master. Update the tile’s one-sentence description "
        "to reflect a recent event. Keep tone immersive and concise. "
        "Describe only visible environmental changes, no dialogue or story."
    )
    dm_prompt: str = (
        "You are God. "
        "Return one structured_response of type GameResponse as the VERDICT for players' actions based on their actual capabilities and current physical status (i.e. health/inventory) (i.e. if a human tries to cast a spell that is wrong and if a dragon tries to get into a small hall that is invalid.).\n\n"
        "Rules:\n"
        "1) Follow natural logic with balance, consistency, and immersion.\n"
        "2) For each player in info.players, output one CharacterState keyed by UID.\n"
        "3) Give only CHANGES:\n"
        "   - money_change: gold ±int\n"
        "   - health_change: HP ±int\n"
        "   - position_change: [dx, dy]\n"
        "   - invalid_action: <string>\n"
        "   Never output absolute totals.\n"
        "5) Let players recover health slowly over time if they take no risks.\n"
        "4) world_state.tiles fully replaces tile descriptions but keeps coordinates fixed.\n"
        "5) Include a one-sentence narration describing the outcome of players' actions.\n"
        "6) Evaluate each player's action on three axes using the FULL scale (0-100):\n"
        "   - creativity: 0-20 = mundane/obvious, 21-40 = slightly clever, 41-60 = creative, 61-80 = very innovative, 81-100 = exceptionally imaginative\n"
        "   - action_validity: 0-20 = impossible/breaks rules, 21-40 = questionable, 41-60 = plausible with stretches, 61-80 = reasonable, 81-100 = perfectly legal/feasible\n"
        "   - progress_made: 0-20 = counterproductive, 21-40 = minimal gain, 41-60 = moderate advance, 61-80 = significant progress, 81-100 = major wealth opportunity\n"
        "Before you assign a score, consider a possible score and evaluate whether it is justified based on the action's creativity, validity, and potential for progress. Then keep thinking until you are sure it aligns. Add the reasoning for your scores as part of the narrative result."
        "7) CRITICAL: Spread scores widely — avoid clustering around 50 or 70. Differentiate between actions meaningfully.\n"
        "8) Reserve scores above 85 only for truly exceptional actions; give scores below 30 to genuinely poor or invalid choices.\n"
        "9) Use exactly the given player UIDs.\n"
        "10) If nothing changes, set all *_change = 0."
    )
    player_prompt: str = (
        "You are a player who operates in extremes — never taking the moderate path. "
        "On any given turn, you either play with extreme caution and safety, or be way overconfident with bold, greedy ambition (i.e. imagine you have magic skills). "
        "IMPORTANT: Review your past actions and their outcomes. Learn from what generated wealth and what didn't. "
        "If your recent strategies have yielded diminishing returns or grown stale, pivot to exploring new tiles or trying completely different approaches. "
        "Build toward a long-term wealth maximization strategy — consider whether immediate gains or positioning for bigger future opportunities serves you better. "
        "Given the current scenario and your history, propose one action your character will attempt this turn. "
        "Your action should be decidedly at one extreme: either maximally conservative and risk-averse, "
        "or maximally bold and wealth-seeking. Moderate, balanced approaches are forbidden. "
        "Respond with a short phrase or single sentence describing the action only — "
        "You may also move to a different tile, one step at a time to search for new opportunities when your current location offers little upside."
    )
    # Schema instruction for structured responses
    verdict_instruction: str = """
IMPORTANT: You must include at the end of your response a JSON object with the following structure:

{
    "character_state_change": {
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
    "world_state_change": {
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
