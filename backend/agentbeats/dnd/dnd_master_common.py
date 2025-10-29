from pydantic import BaseModel
from typing import Literal

from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)



def dnd_master_agent_card(agent_name: str, card_url: str) -> AgentCard:
    skill = AgentSkill(
        id='orchestrate_and_judge_dnd_game',
        name='Orchestrates and judges a D&D game',
        description='Orchestrate and judge a D&D game between two players.',
        tags=['dnd'],
        examples=["""
{
  "participants": {
    "player0": "https://player0.example.com:443",
    "player1": "https://player1.example.org:8443"
  },
  "config": {
    "scenario": "A dragon threatens the village of Eldreth. The players must work together to defeat it.",
    "num_turns": 5
  }
}
"""]
    )
    agent_card = AgentCard(
        name=agent_name,
        description='Orchestrate and judge a D&D game between two players.',
        url=card_url,
        version='1.0.0',
        default_input_modes=['text'],
        default_output_modes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[skill],
    )
    return agent_card
  