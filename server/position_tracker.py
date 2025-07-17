"""
Position Tracking System for Dungeon Blitz Flash Game Server

This module provides comprehensive player position tracking functionality including:
1. Real-time position retrieval and display
2. Automatic console logging every 5 seconds
3. Mission entry position saving
4. Mission exit position restoration
5. Persistent position storage across sessions

Author: Dungeon Blitz Server Team
"""

import time
import threading
import json
import os
from typing import Dict, Tuple, Optional, Any
from datetime import datetime


class PositionTracker:
    """
    Handles all player position tracking functionality for the Dungeon Blitz server.
    """
    
    def __init__(self):
        self.position_log_interval = 5.0  # Log position every 5 seconds
        self.position_loggers = {}  # Dict to store position logging threads per session
        self.mission_positions = {}  # Store positions before entering missions
        self.active_sessions = {}  # Track active sessions for position logging
        self.position_save_file = "saves/position_data.json"
        self.load_position_data()
    
    def load_position_data(self):
        """Load persistent position data from file."""
        try:
            if os.path.exists(self.position_save_file):
                with open(self.position_save_file, 'r') as f:
                    data = json.load(f)
                    self.mission_positions = data.get('mission_positions', {})
                    print(f"[POSITION_TRACKER] Loaded position data for {len(self.mission_positions)} users")
            else:
                self.mission_positions = {}
                print("[POSITION_TRACKER] No existing position data found, starting fresh")
        except Exception as e:
            print(f"[POSITION_TRACKER] Error loading position data: {e}")
            self.mission_positions = {}
    
    def save_position_data(self):
        """Save persistent position data to file."""
        try:
            os.makedirs(os.path.dirname(self.position_save_file), exist_ok=True)
            data = {
                'mission_positions': self.mission_positions,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.position_save_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[POSITION_TRACKER] Saved position data for {len(self.mission_positions)} users")
        except Exception as e:
            print(f"[POSITION_TRACKER] Error saving position data: {e}")
    
    def get_player_position(self, session) -> Tuple[float, float, float, str]:
        """
        Retrieve the current player's position and level.
        
        Args:
            session: The player session object
            
        Returns:
            Tuple of (x, y, z, level_name)
        """
        try:
            if hasattr(session, 'entities') and session.clientEntID in session.entities:
                entity = session.entities[session.clientEntID]
                x = entity.get('x', 0.0)
                y = entity.get('y', 0.0)
                z = entity.get('z', 0.0)
                level = getattr(session, 'current_level', 'Unknown')
                return x, y, z, level
            else:
                # Fallback to default position if entity not found
                level = getattr(session, 'current_level', 'Unknown')
                return 360.0, 1458.99, 0.0, level
        except Exception as e:
            print(f"[POSITION_TRACKER] Error getting player position: {e}")
            return 360.0, 1458.99, 0.0, "Unknown"
    
    def display_player_position(self, session):
        """
        Display the current player's position in a formatted way.
        
        Args:
            session: The player session object
        """
        x, y, z, level = self.get_player_position(session)
        player_name = getattr(session, 'current_character', 'Unknown Player')
        user_id = getattr(session, 'user_id', 'Unknown ID')
        
        print(f"[POSITION_TRACKER] Player: {player_name} (ID: {user_id})")
        print(f"[POSITION_TRACKER] Level: {level}")
        print(f"[POSITION_TRACKER] Position: X={x:.2f}, Y={y:.2f}, Z={z:.2f}")
        print(f"[POSITION_TRACKER] Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
    
    def start_position_logging(self, session):
        """
        Start automatic position logging for a session.
        
        Args:
            session: The player session object
        """
        user_id = getattr(session, 'user_id', None)
        if not user_id:
            print("[POSITION_TRACKER] Cannot start logging: No user ID found")
            return
        
        # Stop existing logger if running
        self.stop_position_logging(session)
        
        # Create and start new logging thread
        def position_logger():
            while user_id in self.active_sessions:
                try:
                    if hasattr(session, 'running') and session.running:
                        self.display_player_position(session)
                    time.sleep(self.position_log_interval)
                except Exception as e:
                    print(f"[POSITION_TRACKER] Error in position logger: {e}")
                    break
        
        self.active_sessions[user_id] = session
        logger_thread = threading.Thread(target=position_logger, daemon=True)
        logger_thread.start()
        self.position_loggers[user_id] = logger_thread
        
        print(f"[POSITION_TRACKER] Started position logging for user {user_id}")
    
    def stop_position_logging(self, session):
        """
        Stop automatic position logging for a session.
        
        Args:
            session: The player session object
        """
        user_id = getattr(session, 'user_id', None)
        if not user_id:
            return
        
        # Remove from active sessions to stop the logging loop
        if user_id in self.active_sessions:
            del self.active_sessions[user_id]
        
        # Clean up the logger thread reference
        if user_id in self.position_loggers:
            del self.position_loggers[user_id]
        
        print(f"[POSITION_TRACKER] Stopped position logging for user {user_id}")

    def is_mission_level(self, level_name: str) -> bool:
        """
        Check if a level is a mission/dungeon level.

        Args:
            level_name: The name of the level to check

        Returns:
            True if it's a mission level, False otherwise
        """
        # Explicitly exclude main world/town levels
        world_levels = [
            'CraftTown', 'CraftTownTutorial', 'BridgeTown', 'BridgeTownHard',
            'NewbieRoad', 'NewbieRoadHard', 'CemeteryHill', 'CemeteryHillHard',
            'Castle', 'CastleHard', 'LavaLands', 'LavaLandsHard'
        ]

        if level_name in world_levels:
            return False

        mission_keywords = [
            'Mission', 'Dungeon', 'Arena', 'Boss',
            'Elite', 'Challenge', 'Raid', 'Instance'
        ]

        # Check if level name contains mission keywords
        for keyword in mission_keywords:
            if keyword in level_name:
                return True

        # Special case for Tutorial levels (but not CraftTownTutorial)
        if 'Tutorial' in level_name and level_name != 'CraftTownTutorial':
            return True

        # Check if level has "true" instanced flag in level config
        try:
            from level_config import LEVEL_CONFIG
            if level_name in LEVEL_CONFIG:
                _, _, _, is_instanced = LEVEL_CONFIG[level_name]
                # Only consider it a mission if it's instanced AND not a main world level
                return is_instanced and level_name not in world_levels
        except ImportError:
            pass

        return False

    def save_pre_mission_position(self, session, target_level: str):
        """
        Save the player's current position before entering a mission.

        Args:
            session: The player session object
            target_level: The mission level the player is entering
        """
        user_id = getattr(session, 'user_id', None)
        if not user_id:
            print("[POSITION_TRACKER] Cannot save position: No user ID found")
            return

        # Only save if entering a mission from a non-mission level
        current_level = getattr(session, 'current_level', '')
        if self.is_mission_level(current_level):
            print(f"[POSITION_TRACKER] Not saving position: Already in mission level {current_level}")
            return

        if not self.is_mission_level(target_level):
            print(f"[POSITION_TRACKER] Not saving position: Target level {target_level} is not a mission")
            return

        # Get current position
        x, y, z, level = self.get_player_position(session)

        # Save position data in global tracker
        if user_id not in self.mission_positions:
            self.mission_positions[user_id] = {}

        self.mission_positions[user_id] = {
            'x': x,
            'y': y,
            'z': z,
            'level': current_level,
            'saved_at': datetime.now().isoformat(),
            'mission_entered': target_level
        }

        # Also save in character data if available
        if hasattr(session, 'current_char_dict') and session.current_char_dict:
            char_dict = session.current_char_dict
            if 'positionTracking' not in char_dict:
                char_dict['positionTracking'] = {
                    'lastWorldPosition': {'x': None, 'y': None, 'z': None, 'level': None, 'timestamp': None},
                    'currentPosition': {'x': None, 'y': None, 'z': None, 'level': None, 'timestamp': None},
                    'missionEntryPosition': {'x': None, 'y': None, 'z': None, 'level': None, 'timestamp': None, 'missionEntered': None},
                    'positionLoggingEnabled': True
                }

            char_dict['positionTracking']['missionEntryPosition'] = {
                'x': x,
                'y': y,
                'z': z,
                'level': current_level,
                'timestamp': datetime.now().isoformat(),
                'missionEntered': target_level
            }

            # Save character data to file
            self._save_character_data(session)

        # Persist to file
        self.save_position_data()

        print(f"[POSITION_TRACKER] Saved pre-mission position for {user_id}:")
        print(f"[POSITION_TRACKER] Position: X={x:.2f}, Y={y:.2f}, Z={z:.2f}")
        print(f"[POSITION_TRACKER] Level: {current_level} -> {target_level}")

    def _save_character_data(self, session):
        """Save character data to file."""
        try:
            if hasattr(session, 'user_id') and session.user_id and hasattr(session, 'char_list'):
                from Character import save_characters
                save_characters(session.user_id, session.char_list)
                print(f"[POSITION_TRACKER] Saved character data for user {session.user_id}")
        except Exception as e:
            print(f"[POSITION_TRACKER] Error saving character data: {e}")

    def restore_pre_mission_position(self, session) -> Optional[Tuple[float, float, float, str]]:
        """
        Restore the player's position from before entering a mission.

        Args:
            session: The player session object

        Returns:
            Tuple of (x, y, z, level_name) if position was restored, None otherwise
        """
        user_id = getattr(session, 'user_id', None)
        if not user_id:
            print("[POSITION_TRACKER] Cannot restore position: No user ID found")
            return None

        # First try to get position from character data
        if hasattr(session, 'current_char_dict') and session.current_char_dict:
            char_dict = session.current_char_dict
            if 'positionTracking' in char_dict and 'missionEntryPosition' in char_dict['positionTracking']:
                mission_pos = char_dict['positionTracking']['missionEntryPosition']
                if mission_pos.get('x') is not None:
                    x = mission_pos.get('x', 360.0)
                    y = mission_pos.get('y', 1458.99)
                    z = mission_pos.get('z', 0.0)
                    level = mission_pos.get('level', 'BridgeTown')

                    print(f"[POSITION_TRACKER] Restoring pre-mission position from character data for {user_id}:")
                    print(f"[POSITION_TRACKER] Position: X={x:.2f}, Y={y:.2f}, Z={z:.2f}")
                    print(f"[POSITION_TRACKER] Level: {level}")

                    # Clear the mission entry position after use
                    mission_pos.update({'x': None, 'y': None, 'z': None, 'level': None, 'timestamp': None, 'missionEntered': None})
                    self._save_character_data(session)

                    return x, y, z, level

        # Fallback to global position data
        if user_id not in self.mission_positions:
            print(f"[POSITION_TRACKER] No saved position found for user {user_id}")
            return None

        position_data = self.mission_positions[user_id]
        x = position_data.get('x', 360.0)
        y = position_data.get('y', 1458.99)
        z = position_data.get('z', 0.0)
        level = position_data.get('level', 'BridgeTown')

        print(f"[POSITION_TRACKER] Restoring pre-mission position from global data for {user_id}:")
        print(f"[POSITION_TRACKER] Position: X={x:.2f}, Y={y:.2f}, Z={z:.2f}")
        print(f"[POSITION_TRACKER] Level: {level}")

        return x, y, z, level

    def clear_saved_position(self, session):
        """
        Clear the saved position data for a user.

        Args:
            session: The player session object
        """
        user_id = getattr(session, 'user_id', None)
        if not user_id:
            return

        if user_id in self.mission_positions:
            del self.mission_positions[user_id]
            self.save_position_data()
            print(f"[POSITION_TRACKER] Cleared saved position for user {user_id}")

    def update_player_position(self, session, x: float, y: float, z: float):
        """
        Update the player's position in the entity system and character data.

        Args:
            session: The player session object
            x, y, z: New position coordinates
        """
        try:
            # Update entity position
            if hasattr(session, 'entities') and session.clientEntID in session.entities:
                entity = session.entities[session.clientEntID]
                entity['x'] = x
                entity['y'] = y
                entity['z'] = z
                print(f"[POSITION_TRACKER] Updated player position to X={x:.2f}, Y={y:.2f}, Z={z:.2f}")
            else:
                print("[POSITION_TRACKER] Warning: Could not update position - entity not found")

            # Update character data position
            if hasattr(session, 'current_char_dict') and session.current_char_dict:
                char_dict = session.current_char_dict
                if 'positionTracking' not in char_dict:
                    char_dict['positionTracking'] = {
                        'lastWorldPosition': {'x': None, 'y': None, 'z': None, 'level': None, 'timestamp': None},
                        'currentPosition': {'x': None, 'y': None, 'z': None, 'level': None, 'timestamp': None},
                        'missionEntryPosition': {'x': None, 'y': None, 'z': None, 'level': None, 'timestamp': None, 'missionEntered': None},
                        'positionLoggingEnabled': True
                    }

                current_level = getattr(session, 'current_level', 'Unknown')
                char_dict['positionTracking']['currentPosition'] = {
                    'x': x,
                    'y': y,
                    'z': z,
                    'level': current_level,
                    'timestamp': datetime.now().isoformat()
                }

                # If not in a mission, also update last world position
                if not self.is_mission_level(current_level):
                    char_dict['positionTracking']['lastWorldPosition'] = {
                        'x': x,
                        'y': y,
                        'z': z,
                        'level': current_level,
                        'timestamp': datetime.now().isoformat()
                    }

        except Exception as e:
            print(f"[POSITION_TRACKER] Error updating player position: {e}")


# Global position tracker instance
position_tracker = PositionTracker()


def get_player_position(session) -> Tuple[float, float, float, str]:
    """
    Convenience function to get player position.
    
    Args:
        session: The player session object
        
    Returns:
        Tuple of (x, y, z, level_name)
    """
    return position_tracker.get_player_position(session)


def display_player_position(session):
    """
    Convenience function to display player position.
    
    Args:
        session: The player session object
    """
    position_tracker.display_player_position(session)


def start_position_logging(session):
    """
    Convenience function to start position logging.
    
    Args:
        session: The player session object
    """
    position_tracker.start_position_logging(session)


def stop_position_logging(session):
    """
    Convenience function to stop position logging.

    Args:
        session: The player session object
    """
    position_tracker.stop_position_logging(session)


def save_pre_mission_position(session, target_level: str):
    """
    Convenience function to save pre-mission position.

    Args:
        session: The player session object
        target_level: The mission level the player is entering
    """
    position_tracker.save_pre_mission_position(session, target_level)


def restore_pre_mission_position(session) -> Optional[Tuple[float, float, float, str]]:
    """
    Convenience function to restore pre-mission position.

    Args:
        session: The player session object

    Returns:
        Tuple of (x, y, z, level_name) if position was restored, None otherwise
    """
    return position_tracker.restore_pre_mission_position(session)


def clear_saved_position(session):
    """
    Convenience function to clear saved position.

    Args:
        session: The player session object
    """
    position_tracker.clear_saved_position(session)


def update_player_position(session, x: float, y: float, z: float):
    """
    Convenience function to update player position.

    Args:
        session: The player session object
        x, y, z: New position coordinates
    """
    position_tracker.update_player_position(session, x, y, z)


def is_mission_level(level_name: str) -> bool:
    """
    Convenience function to check if a level is a mission.

    Args:
        level_name: The name of the level to check

    Returns:
        True if it's a mission level, False otherwise
    """
    return position_tracker.is_mission_level(level_name)
