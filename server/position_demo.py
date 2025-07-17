#!/usr/bin/env python3
"""
Position Tracking System Demo

This script demonstrates the position tracking system functionality
in a realistic scenario.
"""

import sys
import time
from unittest.mock import Mock

# Add the server directory to the path
sys.path.insert(0, '.')

from position_tracker import (
    start_position_logging, stop_position_logging, 
    save_pre_mission_position, restore_pre_mission_position,
    update_player_position, display_player_position
)


def create_demo_session():
    """Create a demo session."""
    session = Mock()
    session.user_id = "demo_player"
    session.current_character = "DemoHero"
    session.current_level = "BridgeTown"
    session.running = True
    session.clientEntID = 99999
    
    # Mock entities
    session.entities = {
        99999: {
            'id': 99999,
            'x': 360.0,
            'y': 1458.99,
            'z': 0.0,
            'name': "DemoHero",
            'is_player': True
        }
    }
    
    # Mock character data
    session.current_char_dict = {
        'name': "DemoHero",
        'CurrentLevel': "BridgeTown",
        'positionTracking': {
            'lastWorldPosition': {'x': None, 'y': None, 'z': None, 'level': None, 'timestamp': None},
            'currentPosition': {'x': None, 'y': None, 'z': None, 'level': None, 'timestamp': None},
            'missionEntryPosition': {'x': None, 'y': None, 'z': None, 'level': None, 'timestamp': None, 'missionEntered': None},
            'positionLoggingEnabled': True
        }
    }
    
    session.char_list = [session.current_char_dict]
    
    return session


def simulate_player_movement(session, x, y, z, description):
    """Simulate player movement."""
    print(f"\n📍 {description}")
    update_player_position(session, x, y, z)
    display_player_position(session)


def simulate_level_change(session, new_level):
    """Simulate changing levels."""
    print(f"\n🚪 Player moving to level: {new_level}")
    session.current_level = new_level
    session.current_char_dict['CurrentLevel'] = new_level


def main():
    """Run the position tracking demo."""
    print("🎮 Dungeon Blitz Position Tracking System Demo")
    print("=" * 60)
    
    # Create demo session
    session = create_demo_session()
    
    print("\n1. Starting position tracking for player...")
    start_position_logging(session)
    
    print("\n2. Player spawns in BridgeTown at default position")
    display_player_position(session)
    
    print("\n3. Player explores BridgeTown...")
    simulate_player_movement(session, 500.0, 200.0, 0.0, "Player moves to the market area")
    time.sleep(1)
    
    simulate_player_movement(session, 750.0, 350.0, 5.0, "Player climbs to the bridge overlook")
    time.sleep(1)
    
    simulate_player_movement(session, 1000.0, 600.0, 0.0, "Player reaches the mission portal")
    time.sleep(1)
    
    print("\n4. Player enters a mission...")
    print("💾 Saving current position before mission entry")
    save_pre_mission_position(session, "BT_Mission1")
    
    simulate_level_change(session, "BT_Mission1")
    simulate_player_movement(session, 100.0, 100.0, 0.0, "Player spawns in mission")
    
    print("\n5. Player progresses through the mission...")
    simulate_player_movement(session, 300.0, 250.0, 10.0, "Player fights through enemies")
    time.sleep(1)
    
    simulate_player_movement(session, 600.0, 400.0, 20.0, "Player reaches the boss room")
    time.sleep(1)
    
    print("\n6. Mission completed! Player exits mission...")
    print("🔄 Restoring pre-mission position")
    
    # Simulate mission exit
    simulate_level_change(session, "BridgeTown")
    restored_position = restore_pre_mission_position(session)
    
    if restored_position:
        x, y, z, level = restored_position
        print(f"✅ Position restored successfully!")
        update_player_position(session, x, y, z)
        display_player_position(session)
    else:
        print("❌ Failed to restore position")
    
    print("\n7. Player continues exploring...")
    simulate_player_movement(session, 1200.0, 800.0, 0.0, "Player explores new areas")
    
    print("\n8. Stopping position tracking...")
    stop_position_logging(session)
    
    print("\n🎉 Demo completed!")
    print("\nKey Features Demonstrated:")
    print("✓ Real-time position tracking and logging")
    print("✓ Automatic position saving before mission entry")
    print("✓ Position restoration after mission completion")
    print("✓ Mission vs. world level detection")
    print("✓ Persistent position data storage")
    
    print("\n📋 Integration Points in Server:")
    print("• Position logging starts when player enters world (packet 0x18)")
    print("• Position saving triggers on door usage to missions (packet 0x2D)")
    print("• Position restoration happens during level transfers (packet 0x1D)")
    print("• Position logging stops when session ends (cleanup)")
    
    print("\n🔧 Usage in Game:")
    print("• Players can explore freely without losing progress")
    print("• Mission entry/exit is seamless with position preservation")
    print("• Console shows position updates every 5 seconds for debugging")
    print("• Position data persists across server restarts")


if __name__ == "__main__":
    main()
