# Dungeon Blitz Position Tracking System

## Overview

This document describes the comprehensive player position tracking system implemented for the Dungeon Blitz Flash game server. The system provides seamless position management for players entering and exiting missions, ensuring they don't lose their exploration progress.

## Features

### 1. **Position Tracking Function**
- Real-time retrieval and display of player position (X, Y, Z coordinates)
- Current level/world information
- Player identification and session management

### 2. **Console Logging**
- Automatic position logging every 5 seconds while the game is running
- Formatted output with timestamp, player name, and coordinates
- Thread-safe implementation with proper cleanup

### 3. **Mission Entry Position Saving**
- Automatically detects when a player enters a mission/dungeon
- Saves the exact position on the main map before mission entry
- Stores position data both in memory and persistent storage
- Supports character-specific position data

### 4. **Mission Exit Respawn**
- Restores players to their exact pre-mission position when exiting
- Seamless transition back to the main world
- Handles position restoration through the server's transfer system
- Clears saved position data after successful restoration

### 5. **Persistent Storage**
- Position data survives server restarts
- Character-specific position tracking in save files
- Backup position storage in separate JSON file
- Automatic data cleanup and management

## Implementation

### Core Files

#### `position_tracker.py`
The main position tracking module containing:
- `PositionTracker` class with all core functionality
- Convenience functions for easy integration
- Thread-safe position logging system
- Mission level detection logic
- Persistent data management

#### `server.py` (Modified)
Integration points added:
- Position tracking initialization on player world entry
- Mission entry detection in door handling (packet 0x2D)
- Position restoration in level transfers (packet 0x1D)
- Session cleanup with position tracking termination

#### `Character.py` (Modified)
Extended character data structure:
- `positionTracking` field added to character dictionary
- Stores last world position, current position, and mission entry position
- Includes timestamps and mission tracking information

### Key Functions

```python
# Basic position operations
get_player_position(session) -> Tuple[float, float, float, str]
display_player_position(session)
update_player_position(session, x, y, z)

# Position logging
start_position_logging(session)
stop_position_logging(session)

# Mission position management
save_pre_mission_position(session, target_level)
restore_pre_mission_position(session) -> Optional[Tuple[float, float, float, str]]

# Utility functions
is_mission_level(level_name) -> bool
clear_saved_position(session)
```

## Mission Level Detection

The system intelligently detects mission levels using:

1. **Explicit World Level Exclusions**: Known world/town levels are explicitly excluded
2. **Keyword Detection**: Levels containing mission-related keywords (Mission, Dungeon, Arena, etc.)
3. **Level Configuration**: Uses the instanced flag from `level_config.py`
4. **Special Cases**: Handles tutorial levels and other edge cases

### World Levels (Non-Mission)
- CraftTown, CraftTownTutorial
- BridgeTown, BridgeTownHard
- NewbieRoad, NewbieRoadHard
- CemeteryHill, CemeteryHillHard
- Castle, CastleHard
- LavaLands, LavaLandsHard

### Mission Levels (Tracked)
- Any level with "Mission", "Dungeon", "Arena", "Boss" in the name
- Tutorial levels (except CraftTownTutorial)
- Instanced levels not in the world level list

## Data Structure

### Character Position Tracking Data
```json
{
  "positionTracking": {
    "lastWorldPosition": {
      "x": 360.0,
      "y": 1458.99,
      "z": 0.0,
      "level": "BridgeTown",
      "timestamp": "2024-01-01T12:00:00"
    },
    "currentPosition": {
      "x": 500.0,
      "y": 300.0,
      "z": 5.0,
      "level": "BridgeTown",
      "timestamp": "2024-01-01T12:05:00"
    },
    "missionEntryPosition": {
      "x": 500.0,
      "y": 300.0,
      "z": 5.0,
      "level": "BridgeTown",
      "timestamp": "2024-01-01T12:05:00",
      "missionEntered": "BT_Mission1"
    },
    "positionLoggingEnabled": true
  }
}
```

## Integration Points

### Server Packet Handling

1. **Player World Entry (Packet 0x18)**
   - Starts position tracking when player enters world
   - Initializes position logging thread

2. **Door Usage (Packet 0x2D)**
   - Detects mission entry attempts
   - Saves current position before mission entry
   - Handles CraftTown special case

3. **Level Transfer (Packet 0x1D)**
   - Restores position when exiting missions
   - Updates spawn coordinates in transfer packet
   - Clears saved position data after use

4. **Session Cleanup**
   - Stops position logging threads
   - Saves final position data
   - Cleans up resources

## Testing

### Test Suite (`test_position_tracker.py`)
Comprehensive tests covering:
- Position retrieval and display
- Mission level detection
- Position saving and restoration
- Position updates and character data integration

### Demo Script (`position_demo.py`)
Interactive demonstration showing:
- Real-world usage scenario
- Mission entry/exit flow
- Position preservation across level changes

## Usage Examples

### Starting Position Tracking
```python
from position_tracker import start_position_logging
start_position_logging(session)
```

### Mission Entry Handling
```python
from position_tracker import save_pre_mission_position, is_mission_level

if is_mission_level(target_level) and not is_mission_level(current_level):
    save_pre_mission_position(session, target_level)
```

### Mission Exit Handling
```python
from position_tracker import restore_pre_mission_position

if not is_mission_level(target_level) and is_mission_level(current_level):
    restored_position = restore_pre_mission_position(session)
    if restored_position:
        x, y, z, level = restored_position
        # Use coordinates in transfer packet
```

## Benefits

1. **Seamless Player Experience**: Players don't lose exploration progress when entering missions
2. **Debug Information**: Console logging helps with server debugging and monitoring
3. **Data Persistence**: Position data survives server restarts and reconnections
4. **Flexible Integration**: Easy to integrate with existing server architecture
5. **Comprehensive Testing**: Well-tested system with automated test suite

## Future Enhancements

- Position history tracking for advanced debugging
- Multiple saved position slots per player
- Position-based achievements or statistics
- Integration with anti-cheat systems for position validation
- Web-based position monitoring dashboard

## Files Created/Modified

### New Files
- `server/position_tracker.py` - Main position tracking module
- `server/test_position_tracker.py` - Test suite
- `server/position_demo.py` - Demonstration script
- `server/POSITION_TRACKING_README.md` - This documentation

### Modified Files
- `server/server.py` - Added position tracking integration
- `server/Character.py` - Extended character data structure

The position tracking system is now fully implemented and ready for use in the Dungeon Blitz Flash game server!
