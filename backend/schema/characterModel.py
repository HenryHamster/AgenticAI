"""
DnD-style character progression system with race, class, skills, and leveling
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, ClassVar
import json
import os


class SkillData(BaseModel):
    name: str
    description: str
    unlock_level: int = Field(ge=1, le=20)
    prerequisites: List[str] = Field(default_factory=list)
    attribute_requirements: Dict[str, int] = Field(default_factory=dict)
    resource_cost: Dict[str, int] = Field(default_factory=dict)
    cooldown_turns: int = Field(ge=0, default=0)
    effect_description: str
    damage_formula: Optional[str] = None

    @field_validator('attribute_requirements')
    @classmethod
    def validate_attributes(cls, v):
        valid_attrs = {'STR', 'DEX', 'INT', 'WIS', 'CON', 'CHA'}
        for attr in v.keys():
            if attr not in valid_attrs:
                raise ValueError(f"Invalid attribute: {attr}")
        return v


class RacialTrait(BaseModel):
    name: str
    description: str
    mechanical_effect: str


class CharacterAttributes(BaseModel):
    STR: int = Field(ge=1, le=20, default=10)
    DEX: int = Field(ge=1, le=20, default=10)
    INT: int = Field(ge=1, le=20, default=10)
    WIS: int = Field(ge=1, le=20, default=10)
    CON: int = Field(ge=1, le=20, default=10)
    CHA: int = Field(ge=1, le=20, default=10)

    def get_modifier(self, attr: str) -> int:
        """Calculate DnD 5e modifier: (attribute - 10) // 2"""
        value = getattr(self, attr)
        return (value - 10) // 2

    def to_dict(self) -> Dict[str, int]:
        return {
            'STR': self.STR,
            'DEX': self.DEX,
            'INT': self.INT,
            'WIS': self.WIS,
            'CON': self.CON,
            'CHA': self.CHA
        }


class CharacterTemplate(BaseModel):
    race: str
    character_class: str
    racial_traits: List[RacialTrait]
    base_attributes: CharacterAttributes
    primary_attributes: List[str]
    skills: List[SkillData]
    proficiencies: List[str]
    starting_equipment: List[str]
    resource_pools: Dict[str, int]
    hit_die: str

    def get_available_skills(self, level: int, current_abilities: List[str],
                            attributes: CharacterAttributes) -> List[SkillData]:
        """Get skills that can be unlocked at current level"""
        available = []
        for skill in self.skills:
            if skill.name in current_abilities:
                continue
            if skill.unlock_level > level:
                continue
            if not all(prereq in current_abilities for prereq in skill.prerequisites):
                continue
            if not all(attributes.to_dict().get(attr, 0) >= val
                      for attr, val in skill.attribute_requirements.items()):
                continue
            available.append(skill)
        return available

    def can_use_skill(self, skill_name: str, current_abilities: List[str],
                     resources: Dict[str, int], cooldowns: Dict[str, int]) -> tuple[bool, str]:
        """Check if skill can be used given current state"""
        skill = next((s for s in self.skills if s.name == skill_name), None)
        if not skill:
            return False, f"Skill '{skill_name}' does not exist for this class"

        if skill_name not in current_abilities:
            return False, f"Skill '{skill_name}' is not unlocked yet"

        for resource, cost in skill.resource_cost.items():
            if resources.get(resource, 0) < cost:
                return False, f"Insufficient {resource} (need {cost}, have {resources.get(resource, 0)})"

        if cooldowns.get(skill_name, 0) > 0:
            return False, f"Skill on cooldown for {cooldowns[skill_name]} more turns"

        return True, "Valid"

    def calculate_skill_effect(self, skill_name: str, attributes: CharacterAttributes) -> Dict:
        """Calculate skill effect including damage if applicable"""
        skill = next((s for s in self.skills if s.name == skill_name), None)
        if not skill:
            return {}

        result = {
            'description': skill.effect_description,
            'resource_cost': skill.resource_cost,
            'cooldown': skill.cooldown_turns
        }

        if skill.damage_formula:
            result['damage_formula'] = skill.damage_formula

            for attr in ['STR', 'DEX', 'INT', 'WIS', 'CON', 'CHA']:
                modifier_key = f'{attr}_modifier'
                if modifier_key in skill.damage_formula or attr in skill.damage_formula:
                    result[modifier_key] = attributes.get_modifier(attr)

        return result

    @staticmethod
    def load_from_file(filepath: str) -> 'CharacterTemplate':
        """Load character template from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return CharacterTemplate(**data)

    def get_level_1_abilities(self) -> List[str]:
        """Get all abilities available at level 1"""
        return [skill.name for skill in self.skills if skill.unlock_level == 1]


class CharacterState(BaseModel):
    """Full character state including progression"""
    character_template_name: str
    race: str
    character_class: str
    level: int = Field(ge=1, le=20, default=1)
    experience: int = Field(ge=0, default=0)
    core_attributes: CharacterAttributes
    current_abilities: List[str]
    resource_pools: Dict[str, int]
    skill_cooldowns: Dict[str, int] = Field(default_factory=dict)
    inventory: List[str] = Field(default_factory=list)

    XP_THRESHOLDS: ClassVar[List[int]] = [
        0, 300, 900, 2700, 6500, 14000, 23000, 34000, 48000, 64000,
        85000, 100000, 120000, 140000, 165000, 195000, 225000, 265000, 305000, 355000
    ]

    def check_level_up(self) -> Optional[int]:
        """Check if XP threshold reached, return new level if applicable"""
        if self.level >= 20:
            return None

        next_threshold = self.XP_THRESHOLDS[self.level]
        if self.experience >= next_threshold:
            return self.level + 1
        return None

    def get_ability_modifiers(self) -> Dict[str, int]:
        """Get all attribute modifiers"""
        return {
            f'{attr}_modifier': self.core_attributes.get_modifier(attr)
            for attr in ['STR', 'DEX', 'INT', 'WIS', 'CON', 'CHA']
        }


class LevelUpResult(BaseModel):
    """Result of leveling up"""
    new_level: int
    newly_unlocked_skills: List[str]
    attribute_increase_available: bool
    message: str


def get_character_template_path(class_name: str) -> str:
    """Get path to character template file"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'data', 'character_templates', f'{class_name.lower()}.json')


def load_character_template(class_name: str) -> CharacterTemplate:
    """Load character template by class name"""
    filepath = get_character_template_path(class_name)
    return CharacterTemplate.load_from_file(filepath)
