"""
Configuration settings for the AgenticAI game
"""
import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class GameConfig:
    """Game configuration settings"""
    # Game mechanics
    max_turns: int = 100
    world_size: tuple = (10, 10)  # (width, height)
    starting_wealth: int = 100
    starting_health: int = 100
    
    # AI settings
    max_ai_retries: int = 3
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
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.7
    
    # Claude settings
    claude_api_key: str = os.getenv("CLAUDE_API_KEY", "")
    claude_model: str = "claude-3-sonnet-20240229"
    claude_temperature: float = 0.7
    
    # General AI settings
    max_tokens: int = 1000
    system_prompt: str = "You are an AI agent in a text-based RPG. Make strategic decisions to maximize your wealth."

# Global configuration instances
game_config = GameConfig()
ai_config = AIConfig()

def get_config() -> Dict[str, Any]:
    """Get all configuration as a dictionary"""
    return {
        "game": game_config,
        "ai": ai_config
    }
