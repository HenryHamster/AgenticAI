"""
Comprehensive tests for the DnD character progression system
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from schema.characterModel import (
    CharacterTemplate, load_character_template, CharacterAttributes,
    CharacterState as CharState, SkillData, RacialTrait
)
from src.app.Player import Player
from api.apiDtoModel import CharacterState


def test_character_template_loading():
    """Test 1: Character templates load correctly from JSON files"""
    print("\n=== Test 1: Template Loading ===")

    for class_name in ['Warrior', 'Mage', 'Rogue']:
        try:
            template = load_character_template(class_name)
            print(f"✓ Loaded {class_name} template")
            print(f"  - Race: {template.race}")
            print(f"  - Class: {template.character_class}")
            print(f"  - Skills: {len(template.skills)}")
            print(f"  - Racial Traits: {len(template.racial_traits)}")
            assert len(template.skills) >= 15, f"{class_name} should have at least 15 skills"
            assert template.resource_pools, f"{class_name} should have resource pools"
        except Exception as e:
            print(f"✗ Failed to load {class_name}: {e}")
            raise

    print("✓ All templates loaded successfully\n")


def test_skill_unlock_logic():
    """Test 2: Skills unlock correctly at appropriate levels"""
    print("=== Test 2: Skill Unlock Logic ===")

    template = load_character_template('Warrior')
    attrs = template.base_attributes

    level_1_skills = template.get_available_skills(1, [], attrs)
    print(f"Level 1 available skills: {len(level_1_skills)}")
    assert len(level_1_skills) >= 3, "Should have at least 3 skills at level 1"

    current_abilities = [skill.name for skill in level_1_skills]

    level_3_skills = template.get_available_skills(3, current_abilities, attrs)
    print(f"Level 3 available skills: {len(level_3_skills)}")

    level_5_skills = template.get_available_skills(5, current_abilities + [s.name for s in level_3_skills], attrs)
    print(f"Level 5 available skills: {len(level_5_skills)}")

    print("✓ Skill unlock progression works correctly\n")


def test_action_validation():
    """Test 3: Skill validation checks capabilities, resources, and cooldowns"""
    print("=== Test 3: Action Validation ===")

    template = load_character_template('Mage')
    current_abilities = template.get_level_1_abilities()
    resources = template.resource_pools.copy()
    cooldowns = {}

    valid, msg = template.can_use_skill('Magic Missile', current_abilities, resources, cooldowns)
    print(f"Magic Missile (valid, has resources): {valid} - {msg}")
    assert valid, "Should be able to use level 1 skill with resources"

    valid, msg = template.can_use_skill('Fireball', current_abilities, resources, cooldowns)
    print(f"Fireball (not unlocked): {valid} - {msg}")
    assert not valid, "Should not be able to use locked skill"

    resources['spell_slots_1'] = 0
    valid, msg = template.can_use_skill('Magic Missile', current_abilities, resources, cooldowns)
    print(f"Magic Missile (no resources): {valid} - {msg}")
    assert not valid, "Should not be able to use skill without resources"

    resources['spell_slots_1'] = 2
    cooldowns['Magic Missile'] = 2
    valid, msg = template.can_use_skill('Magic Missile', current_abilities, resources, cooldowns)
    print(f"Magic Missile (on cooldown): {valid} - {msg}")
    assert not valid, "Should not be able to use skill on cooldown"

    print("✓ Action validation works correctly\n")


def test_xp_and_level_up():
    """Test 4: XP thresholds trigger level-ups correctly"""
    print("=== Test 4: XP and Level-Up ===")

    player = Player("TestMage", position=(0, 0), character_template_name="Mage")

    print(f"Starting level: {player.level}, XP: {player.experience}")
    assert player.level == 1, "Should start at level 1"

    player.experience = 300
    new_skills = player.check_level_up()
    print(f"After 300 XP: Level {player.level}, new skills: {new_skills}")
    assert player.level == 2, "Should level up at 300 XP"

    player.experience = 900
    new_skills = player.check_level_up()
    print(f"After 900 XP: Level {player.level}, new skills: {new_skills}")
    assert player.level == 3, "Should level up at 900 XP"

    player.experience = 2700
    new_skills = player.check_level_up()
    print(f"After 2700 XP: Level {player.level}")
    assert player.level == 4, "Should level up at 2700 XP"

    print("✓ XP and level-up calculations work correctly\n")


def test_resource_management():
    """Test 5: Resources deplete and regenerate correctly"""
    print("=== Test 5: Resource Management ===")

    player = Player("TestWarrior", position=(0, 0), character_template_name="Warrior")

    initial_stamina = player.resource_pools['stamina']
    print(f"Initial stamina: {initial_stamina}")

    player.update_resources({'stamina': -20})
    print(f"After using 20 stamina: {player.resource_pools['stamina']}")
    assert player.resource_pools['stamina'] == initial_stamina - 20

    player.update_resources({'stamina': 10})
    print(f"After recovering 10 stamina: {player.resource_pools['stamina']}")

    player.update_resources({'stamina': -1000})
    print(f"After massive depletion: {player.resource_pools['stamina']}")
    assert player.resource_pools['stamina'] == 0, "Resources should not go negative"

    print("✓ Resource management works correctly\n")


def test_cooldown_tracking():
    """Test 6: Skill cooldowns track and decrement correctly"""
    print("=== Test 6: Cooldown Tracking ===")

    player = Player("TestRogue", position=(0, 0), character_template_name="Rogue")

    player.set_cooldown('Stealth', 3)
    print(f"Set Stealth cooldown to 3 turns")
    assert player.skill_cooldowns['Stealth'] == 3

    player.update_cooldowns(turn_delta=1)
    print(f"After 1 turn: {player.skill_cooldowns.get('Stealth', 0)}")
    assert player.skill_cooldowns.get('Stealth', 0) == 2

    player.update_cooldowns(turn_delta=1)
    print(f"After 2 turns: {player.skill_cooldowns.get('Stealth', 0)}")

    player.update_cooldowns(turn_delta=1)
    print(f"After 3 turns: {player.skill_cooldowns.get('Stealth', 0)}")
    assert 'Stealth' not in player.skill_cooldowns, "Cooldown should be removed when it reaches 0"

    print("✓ Cooldown tracking works correctly\n")


def test_player_save_load():
    """Test 7: Player state saves and loads with all character data"""
    print("=== Test 7: Player Save/Load ===")

    player1 = Player("TestSaveLoad", position=(5, 5), character_template_name="Warrior")
    player1.experience = 500
    player1.check_level_up()
    player1.update_resources({'stamina': -30})
    player1.set_cooldown('Heavy Strike', 2)
    player1.inventory.append("Magic Sword")

    saved_data = player1.save()
    print(f"Saved player data (length: {len(saved_data)} chars)")

    player2 = Player("TestSaveLoad")
    player2.load(saved_data)

    print(f"Loaded player:")
    print(f"  - Level: {player2.level}")
    print(f"  - XP: {player2.experience}")
    print(f"  - Position: {player2.position}")
    print(f"  - Abilities: {len(player2.current_abilities)}")
    print(f"  - Resources: {player2.resource_pools}")
    print(f"  - Cooldowns: {player2.skill_cooldowns}")
    print(f"  - Inventory: {player2.inventory}")

    assert player2.level == player1.level
    assert player2.experience == player1.experience
    assert player2.position == player1.position
    assert len(player2.current_abilities) == len(player1.current_abilities)
    assert "Magic Sword" in player2.inventory

    print("✓ Player save/load preserves character data\n")


def test_attribute_modifiers():
    """Test 8: Attribute modifiers calculate correctly"""
    print("=== Test 8: Attribute Modifiers ===")

    attrs = CharacterAttributes(STR=8, DEX=14, INT=18, WIS=10, CON=12, CHA=16)

    tests = [
        ('STR', 8, -1),
        ('DEX', 14, 2),
        ('INT', 18, 4),
        ('WIS', 10, 0),
        ('CON', 12, 1),
        ('CHA', 16, 3)
    ]

    for attr, value, expected_mod in tests:
        mod = attrs.get_modifier(attr)
        print(f"{attr}: {value} → modifier: {mod} (expected: {expected_mod})")
        assert mod == expected_mod, f"{attr} modifier calculation incorrect"

    print("✓ Attribute modifiers calculate correctly\n")


def test_skill_prerequisites():
    """Test 9: Skills with prerequisites only unlock when requirements met"""
    print("=== Test 9: Skill Prerequisites ===")

    template = load_character_template('Warrior')
    attrs = template.base_attributes

    cleaving_strike = next(s for s in template.skills if s.name == "Cleaving Strike")
    print(f"Cleaving Strike requires: {cleaving_strike.prerequisites}")

    without_prereq = template.get_available_skills(3, [], attrs)
    cleaving_available = any(s.name == "Cleaving Strike" for s in without_prereq)
    print(f"Available at level 3 without Heavy Strike: {cleaving_available}")
    assert not cleaving_available, "Cleaving Strike should not be available without prerequisites"

    with_prereq = template.get_available_skills(3, ["Heavy Strike"], attrs)
    cleaving_available = any(s.name == "Cleaving Strike" for s in with_prereq)
    print(f"Available at level 3 with Heavy Strike: {cleaving_available}")
    assert cleaving_available, "Cleaving Strike should be available with prerequisites met"

    print("✓ Prerequisite checking works correctly\n")


def test_inventory_management():
    """Test 10: Inventory additions and removals work correctly"""
    print("=== Test 10: Inventory Management ===")

    player = Player("TestInventory", position=(0, 0), character_template_name="Rogue")

    starting_items = len(player.inventory)
    print(f"Starting inventory: {player.inventory}")

    player.inventory.append("Healing Potion")
    player.inventory.append("Lockpick Set")
    print(f"After adding items: {player.inventory}")
    assert len(player.inventory) == starting_items + 2

    player.inventory.remove("Lockpick Set")
    print(f"After removing Lockpick Set: {player.inventory}")
    assert "Lockpick Set" not in player.inventory
    assert "Healing Potion" in player.inventory

    print("✓ Inventory management works correctly\n")


def test_prompt_injection():
    """Test 11: Player context gets enriched with character data correctly"""
    print("=== Test 11: Prompt Injection ===")

    player = Player("TestPrompt", position=(0, 0), character_template_name="Mage")

    base_context = {
        "tiles": [],
        "verdict": "Previous verdict"
    }

    enriched = player._enrich_context_with_character_data(base_context)

    print("Enriched context keys:")
    for key in enriched.keys():
        if key not in base_context:
            print(f"  - {key}: {enriched[key]}")

    assert 'character_name' in enriched
    assert 'race' in enriched
    assert 'character_class' in enriched
    assert 'current_level' in enriched
    assert 'STR' in enriched
    assert 'STR_mod' in enriched
    assert 'resource_status' in enriched

    print("✓ Prompt injection includes all required character data\n")


def test_multi_level_progression():
    """Test 12: Multiple level-ups handle skill unlocks correctly"""
    print("=== Test 12: Multi-Level Progression ===")

    player = Player("TestProgression", position=(0, 0), character_template_name="Warrior")

    levels_and_xp = [(1, 0), (2, 300), (3, 900), (4, 2700), (5, 6500)]

    for target_level, xp in levels_and_xp:
        player.experience = xp
        while player.check_level_up():
            pass
        print(f"XP {xp} → Level {player.level}, Abilities: {len(player.current_abilities)}")
        assert player.level == target_level, f"Should be level {target_level} at {xp} XP"

    print("✓ Multi-level progression works correctly\n")


def run_all_tests():
    """Run all character system tests"""
    print("\n" + "="*60)
    print("CHARACTER SYSTEM COMPREHENSIVE TEST SUITE")
    print("="*60)

    tests = [
        test_character_template_loading,
        test_skill_unlock_logic,
        test_action_validation,
        test_xp_and_level_up,
        test_resource_management,
        test_cooldown_tracking,
        test_player_save_load,
        test_attribute_modifiers,
        test_skill_prerequisites,
        test_inventory_management,
        test_prompt_injection,
        test_multi_level_progression
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ {test.__name__} FAILED: {e}\n")

    print("="*60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("="*60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
