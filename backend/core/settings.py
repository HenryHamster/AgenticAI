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
    num_responses: int = 3 #Number of verdicts per action
    num_negotiation_rounds: int = 2 #Number of negotiation rounds before final action
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
    openai_model: str = "gpt-4.1-mini"
    openai_temperature: float = 0.7

    # Claude settings
    claude_api_key: str = os.getenv("CLAUDE_API_KEY", "")
    claude_model: str = "claude-3-sonnet-20240229"
    claude_temperature: float = 0.7

    # General AI settings
    system_prompt: str = "You are a D&D player character focused on maximizing wealth. Make strategic decisions to selfishly maximize your wealth at any cost. Be aware that you're actions may not follow through as intended."
    tile_prompt: str = (
        "You are the Dungeon Master of a tile-based fantasy world. Determine how resource-rich the tile is based on its terrain and context.\n"
        "Describe the terrain at the given coordinates in one vivid, concise sentence, including one word for terrain type and two emojis. "
        "The emojis should not include a person, human, or animal. They should be symbols that represent the terrain or environment. "
        "Focus on environment and physical details only.\n\n"
        "CRITICAL: The description must cover only visible terrain and environment. Do NOT mention or hint at hidden treasures, caches, artifacts, or any secret objects in the description. "
        "Players must discover secrets through their actions, not by reading the description. The description should be about what they can see, not what might be hidden.\n\n"
        "Secret generation rules:\n"
        "- Resource-rich tiles (ruins, markets, enchanted groves, fertile valleys, arcane laboratories, bustling ports, etc.) should include 3-5 secrets with clearly distinct themes (coin stash, rare material, lore clue, hidden tool, dormant hazard, favor, rumor, etc.).\n"
        "- Average tiles (farmlands, mixed forests, villages, crossroads) should include 2-3 varied secrets.\n"
        "- Sparse or harsh tiles (deserts, salt flats, barren tundra, blasted wastelands) should include 0-2 secrets and may legitimately total 0 value by leaning on flavor, hazards, or depleted discoveries instead of treasure.\n"
        "- Keep total secret value low overall: barren tiles should usually be 0; harsh tiles 0-10; average tiles around 20 ±10; rich tiles 30-40; only truly exceptional sites may reach 50, and even then rarely.\n"
        "- Split value so that no single secret holds more than half of its tile's total value, and use small integer values that reflect the terrain's plausibility.\n"
        "- Provide each secret as a key/value pair suited for TileModel.secrets, and favor variety (currencies, resources, information, hazards, favors, tools, social leverage) rather than repeating the same type.\n\n"
        "Ensure that all tiles are interesting and provide opportunities even if value is low. "
        "Keep tone immersive and neutral-fantasy. Avoid repetition between nearby tiles.\n"
    )
    tile_update_prompt: str = (
        "You are the Dungeon Master. Update the tile’s one-sentence description "
        "to reflect a recent event. Keep tone immersive and concise. "
        "Whenever value is given to a player, remove an equal amount from the relevant secret. Secret value cannot go below 0."
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
        "   Never output absolute totals.\n"
        "4) world_state.tiles fully replaces tile descriptions but keeps coordinates fixed.\n"
        "5) Let players recover health slowly over time if they take no risks.\n"
        "6) Include a one-sentence narration describing the outcome of players' actions. Write narrative that describes what happened naturally without explicitly revealing secret details. Describe outcomes and consequences from the player's perspective, not the underlying secret mechanics. For example, say 'you discover something valuable' or 'your search reveals hidden treasure' rather than stating exact secret values or keys.\n"
        "7) Evaluate each player's action on three axes using the FULL scale (0-100):\n"
        "   - creativity: 0-20 = mundane/obvious, 21-40 = slightly clever, 41-60 = creative, 61-80 = very innovative, 81-100 = exceptionally imaginative\n"
        "   - action_validity: 0-20 = impossible/breaks rules, 21-40 = questionable, 41-60 = plausible with stretches, 61-80 = reasonable, 81-100 = perfectly legal/feasible\n"
        "   - progress_made: 0-20 = counterproductive, 21-40 = minimal gain, 41-60 = moderate advance, 61-80 = significant progress, 81-100 = major wealth opportunity\n"
        "Before you assign a score, consider a possible score and evaluate whether it is justified based on the action's creativity, validity, and potential for progress. Then keep thinking until you are sure it aligns. Add the reasoning for your scores as part of the narrative result."
        "8) CRITICAL: Spread scores widely — avoid clustering around 50 or 70. Differentiate between actions meaningfully.\n"
        "9) Reserve scores above 85 only for truly exceptional actions; give scores below 30 to genuinely poor or invalid choices.\n"
        "10) Use exactly the given player UIDs.\n"
        "11) If nothing changes, set all *_change = 0.\n"
        "12) Ensure that all rewards are taken from the relevant secret, and the secret's value updated accordingly. (Value should not be hallucinated)"
    )
    negotiation_prompt: str = (
        "You are a thoughtful adventurer focused on long-term wealth creation. "
        "This is a PLANNING PHASE where you can discuss and negotiate with other players before committing to your final action. "
        "You can propose strategies, coordinate moves, make deals, or express concerns about other players' plans. "
        "Both collaboration and competition are valid: coordinate openly with other players, pursue solo gains, or mix the two when it helps you. "
        "CRITICAL: Do NOT assume that specific valuable items, treasures, or resources exist based purely on terrain descriptions. "
        "Tile descriptions cover only visible features; hidden opportunities must be discovered through your actions. "
        "Review the negotiation history (`negotiation_history`) to see what other players have said in previous rounds of this planning phase. "
        "Respond with a brief message (1-3 sentences) directed at other players. This is discussion only, not your final action. "
        "You can propose ideas, ask questions, make offers, or express your intentions. Be strategic and consider how others might respond."
    )
    player_prompt: str = (
        "You are a thoughtful adventurer focused on long-term wealth creation. "
        "Each turn, choose the action that best advances your interests given the current situation. "
        "Review your past actions and outcomes; adapt if prior approaches stalled. "
        "Both collaboration and competition are valid: you can coordinate openly with other players, pursue solo gains, or mix the two when it helps you. "
        "CRITICAL: Do NOT assume that specific valuable items, treasures, or resources exist based purely on terrain descriptions. "
        "Tile descriptions cover only visible features; hidden opportunities must be discovered through your actions. "
        "Review the `negotiation_history` to see what was discussed during the planning phase with other players. "
        "This context should inform your final decision, but remember: only your final action (this response) will be executed. "
        "Given the current scenario, negotiation history, and your history, propose the single action your character will attempt this turn. "
        "Respond with a short phrase or single sentence describing the action only — "
        "You may also move to a different tile, one step at a time, to search for new opportunities when your current location offers little upside."
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
