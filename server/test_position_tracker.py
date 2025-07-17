#!/usr/bin/env python3
"""
Test script for the Position Tracking System

This script tests the core functionality of the position tracking system
including position retrieval, mission entry/exit handling, and logging.
"""

import sys
import time
import json
from unittest.mock import Mock

# Add the server directory to the path
sys.path.insert(0, '.')

from position_tracker import (
    PositionTracker, get_player_position, display_player_position,
    save_pre_mission_position, restore_pre_mission_position,
    is_mission_level, update_player_position
)


def create_mock_session(user_id="test_user", character_name="TestChar", level="BridgeTown"):
    """Create a mock session for testing."""
    session = Mock()
    session.user_id = user_id
    session.current_character = character_name
    session.current_level = level
    session.running = True
    session.clientEntID = 12345
    
    # Mock entities
    session.entities = {
        12345: {
            'id': 12345,
            'x': 360.0,
            'y': 1458.99,
            'z': 0.0,
            'name': character_name,
            'is_player': True
        }
    }
    
    # Mock character data
    session.current_char_dict = {
        'name': character_name,
        'CurrentLevel': level,
        'positionTracking': {
            'lastWorldPosition': {'x': None, 'y': None, 'z': None, 'level': None, 'timestamp': None},
            'currentPosition': {'x': None, 'y': None, 'z': None, 'level': None, 'timestamp': None},
            'missionEntryPosition': {'x': None, 'y': None, 'z': None, 'level': None, 'timestamp': None, 'missionEntered': None},
            'positionLoggingEnabled': True
        }
    }
    
    session.char_list = [session.current_char_dict]
    
    return session


def test_position_retrieval():
    """Test basic position retrieval functionality."""
    print("=" * 60)
    print("Testing Position Retrieval")
    print("=" * 60)
    
    session = create_mock_session()
    
    # Test getting position
    x, y, z, level = get_player_position(session)
    print(f"Retrieved position: X={x}, Y={y}, Z={z}, Level={level}")
    
    # Test displaying position
    display_player_position(session)
    
    assert x == 360.0, f"Expected X=360.0, got {x}"
    assert y == 1458.99, f"Expected Y=1458.99, got {y}"
    assert z == 0.0, f"Expected Z=0.0, got {z}"
    assert level == "BridgeTown", f"Expected level=BridgeTown, got {level}"
    
    print("✓ Position retrieval test passed!")
    return True


def test_mission_level_detection():
    """Test mission level detection."""
    print("=" * 60)
    print("Testing Mission Level Detection")
    print("=" * 60)
    
    # Test various level names
    test_cases = [
        ("BridgeTown", False),
        ("CraftTown", False),
        ("NewbieRoad", False),
        ("TutorialDungeon", True),
        ("GoblinRiverDungeon", True),
        ("BT_Mission1", True),
        ("AC_Mission2Hard", True),
        ("LDArena1", True),
        ("CemeteryHill", False),
    ]
    
    for level_name, expected in test_cases:
        result = is_mission_level(level_name)
        print(f"Level '{level_name}': {'Mission' if result else 'World'} (Expected: {'Mission' if expected else 'World'})")
        assert result == expected, f"Mission detection failed for {level_name}"
    
    print("✓ Mission level detection test passed!")
    return True


def test_mission_position_saving():
    """Test mission entry position saving."""
    print("=" * 60)
    print("Testing Mission Position Saving")
    print("=" * 60)
    
    session = create_mock_session()
    
    # Move player to a different position
    session.entities[12345]['x'] = 500.0
    session.entities[12345]['y'] = 300.0
    session.entities[12345]['z'] = 10.0
    
    # Test saving position before entering mission
    save_pre_mission_position(session, "TutorialDungeon")
    
    # Check if position was saved in character data
    mission_pos = session.current_char_dict['positionTracking']['missionEntryPosition']
    assert mission_pos['x'] == 500.0, f"Expected saved X=500.0, got {mission_pos['x']}"
    assert mission_pos['y'] == 300.0, f"Expected saved Y=300.0, got {mission_pos['y']}"
    assert mission_pos['level'] == "BridgeTown", f"Expected saved level=BridgeTown, got {mission_pos['level']}"
    assert mission_pos['missionEntered'] == "TutorialDungeon", f"Expected mission=TutorialDungeon, got {mission_pos['missionEntered']}"
    
    print("✓ Mission position saving test passed!")
    return True


def test_mission_position_restoration():
    """Test mission exit position restoration."""
    print("=" * 60)
    print("Testing Mission Position Restoration")
    print("=" * 60)
    
    session = create_mock_session(level="TutorialDungeon")
    
    # Set up saved mission entry position
    session.current_char_dict['positionTracking']['missionEntryPosition'] = {
        'x': 750.0,
        'y': 250.0,
        'z': 5.0,
        'level': 'BridgeTown',
        'timestamp': '2024-01-01T12:00:00',
        'missionEntered': 'TutorialDungeon'
    }
    
    # Test restoring position
    restored = restore_pre_mission_position(session)
    
    assert restored is not None, "Position restoration returned None"
    x, y, z, level = restored
    assert x == 750.0, f"Expected restored X=750.0, got {x}"
    assert y == 250.0, f"Expected restored Y=250.0, got {y}"
    assert z == 5.0, f"Expected restored Z=5.0, got {z}"
    assert level == "BridgeTown", f"Expected restored level=BridgeTown, got {level}"
    
    # Check that mission entry position was cleared
    mission_pos = session.current_char_dict['positionTracking']['missionEntryPosition']
    assert mission_pos['x'] is None, "Mission entry position was not cleared"
    
    print("✓ Mission position restoration test passed!")
    return True


def test_position_update():
    """Test position update functionality."""
    print("=" * 60)
    print("Testing Position Update")
    print("=" * 60)
    
    session = create_mock_session()
    
    # Test updating position
    new_x, new_y, new_z = 1000.0, 500.0, 20.0
    update_player_position(session, new_x, new_y, new_z)
    
    # Check entity position was updated
    entity = session.entities[12345]
    assert entity['x'] == new_x, f"Expected entity X={new_x}, got {entity['x']}"
    assert entity['y'] == new_y, f"Expected entity Y={new_y}, got {entity['y']}"
    assert entity['z'] == new_z, f"Expected entity Z={new_z}, got {entity['z']}"
    
    # Check character data was updated
    current_pos = session.current_char_dict['positionTracking']['currentPosition']
    assert current_pos['x'] == new_x, f"Expected char data X={new_x}, got {current_pos['x']}"
    assert current_pos['y'] == new_y, f"Expected char data Y={new_y}, got {current_pos['y']}"
    assert current_pos['z'] == new_z, f"Expected char data Z={new_z}, got {current_pos['z']}"
    
    print("✓ Position update test passed!")
    return True


def run_all_tests():
    """Run all position tracking tests."""
    print("Starting Position Tracking System Tests")
    print("=" * 60)
    
    tests = [
        test_position_retrieval,
        test_mission_level_detection,
        test_mission_position_saving,
        test_mission_position_restoration,
        test_position_update,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with error: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("🎉 All tests passed! Position tracking system is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
