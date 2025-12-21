"""
Player management system for Pacman Smash.
Handles player state, movement, controls, and interactions.
"""

import pygame
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
import time

class PowerUpType(Enum):
    """Types of power-ups available in the game."""
    SPEED_BOOST = "speed_boost"
    FREEZE_OPPONENT = "freeze_opponent"
    GHOST_CONFUSION = "ghost_confusion"

@dataclass
class PowerUp:
    """Represents an active power-up effect."""
    type: PowerUpType
    duration: float
    start_time: float
    
    def is_expired(self) -> bool:
        """Check if the power-up has expired."""
        return time.time() - self.start_time >= self.duration

class Player:
    """Represents a player in the game with position, state, and controls."""
    
    def __init__(self, player_id: int, start_position: Tuple[int, int], 
                 controls: Dict[str, int], color: Tuple[int, int, int]):
        """
        Initialize a player.
        
        Args:
            player_id: Unique identifier (1 or 2)
            start_position: Starting (x, y) grid position
            controls: Dictionary mapping direction to pygame key constants
            color: RGB color tuple for rendering
        """
        self.player_id = player_id
        self.position = start_position
        self.start_position = start_position
        self.score = 0
        self.speed = 1.0  # Base movement speed
        self.death_count = 0
        self.controls = controls
        self.color = color
        
        # Power-up management
        self.active_powerups: List[PowerUp] = []
        
        # Performance tracking
        self.movement_history: List[Tuple[int, int, float]] = []
        self.pellets_collected = 0
        self.last_pellet_time = 0.0
        
        # Movement state
        self.last_move_time = 0.0
        self.move_cooldown = 0.15  # Minimum time between moves (seconds)
        self.is_frozen = False
        self.freeze_end_time = 0.0
    
    def get_current_speed(self) -> float:
        """Get the current movement speed including power-up modifiers."""
        base_speed = self.speed
        
        # Apply speed boost if active
        for powerup in self.active_powerups:
            if powerup.type == PowerUpType.SPEED_BOOST and not powerup.is_expired():
                base_speed *= 1.5
        
        return base_speed
    
    def is_movement_allowed(self) -> bool:
        """Check if the player can currently move."""
        current_time = time.time()
        
        # Check if frozen
        if self.is_frozen and current_time < self.freeze_end_time:
            return False
        
        # Check movement cooldown (affected by speed)
        time_since_move = current_time - self.last_move_time
        required_cooldown = self.move_cooldown / self.get_current_speed()
        
        return time_since_move >= required_cooldown
    
    def add_powerup(self, powerup_type: PowerUpType, duration: float = 5.0) -> None:
        """Add a power-up effect to the player."""
        powerup = PowerUp(powerup_type, duration, time.time())
        self.active_powerups.append(powerup)
    
    def freeze(self, duration: float = 3.0) -> None:
        """Freeze the player for the specified duration."""
        self.is_frozen = True
        self.freeze_end_time = time.time() + duration
    
    def update_powerups(self) -> None:
        """Remove expired power-ups."""
        self.active_powerups = [p for p in self.active_powerups if not p.is_expired()]
        
        # Update freeze state
        if self.is_frozen and time.time() >= self.freeze_end_time:
            self.is_frozen = False
    
    def move(self, new_position: Tuple[int, int]) -> None:
        """Move the player to a new position."""
        if not self.is_movement_allowed():
            return
            
        current_time = time.time()
        self.movement_history.append((self.position[0], self.position[1], current_time))
        self.position = new_position
        self.last_move_time = current_time
    
    def collect_pellet(self, points: int = 10) -> None:
        """Handle pellet collection."""
        self.score += points
        self.pellets_collected += 1
        self.last_pellet_time = time.time()
    
    def die(self, score_penalty: int = 50) -> None:
        """Handle player death (collision with ghost)."""
        self.score = max(0, self.score - score_penalty)
        self.death_count += 1
        self.position = self.start_position
    
    def get_pellet_collection_rate(self, time_window: float = 10.0) -> float:
        """Calculate pellets collected per second over the time window."""
        current_time = time.time()
        if current_time - self.last_pellet_time > time_window:
            return 0.0
        
        # Simple rate calculation - can be enhanced with more sophisticated tracking
        return self.pellets_collected / max(1.0, current_time - (current_time - time_window))
    
    def get_average_speed(self, time_window: float = 10.0) -> float:
        """Calculate average movement speed over the time window."""
        current_time = time.time()
        recent_moves = [
            move for move in self.movement_history 
            if current_time - move[2] <= time_window
        ]
        
        if len(recent_moves) < 2:
            return 0.0
        
        total_distance = 0.0
        total_time = 0.0
        
        for i in range(1, len(recent_moves)):
            prev_x, prev_y, prev_time = recent_moves[i-1]
            curr_x, curr_y, curr_time = recent_moves[i]
            
            distance = abs(curr_x - prev_x) + abs(curr_y - prev_y)  # Manhattan distance
            time_diff = curr_time - prev_time
            
            total_distance += distance
            total_time += time_diff
        
        return total_distance / max(0.001, total_time)
    
    def render(self, screen: pygame.Surface, cell_size: int, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render the player on the screen."""
        pixel_x = self.position[0] * cell_size + offset_x + cell_size // 4
        pixel_y = self.position[1] * cell_size + offset_y + cell_size // 4
        radius = cell_size // 3
        
        # Draw player as a circle
        pygame.draw.circle(screen, self.color, (pixel_x, pixel_y), radius)
        
        # Draw power-up indicators
        if self.active_powerups:
            indicator_y = pixel_y - radius - 10
            for i, powerup in enumerate(self.active_powerups):
                if not powerup.is_expired():
                    indicator_color = (255, 255, 0)  # Yellow for active power-ups
                    pygame.draw.circle(screen, indicator_color, 
                                     (pixel_x + i * 8 - 8, indicator_y), 3)

# Player control configurations
PLAYER_1_CONTROLS = {
    'up': pygame.K_w,
    'down': pygame.K_s,
    'left': pygame.K_a,
    'right': pygame.K_d
}

PLAYER_2_CONTROLS = {
    'up': pygame.K_UP,
    'down': pygame.K_DOWN,
    'left': pygame.K_LEFT,
    'right': pygame.K_RIGHT
}

# Player colors
PLAYER_1_COLOR = (255, 255, 0)  # Yellow
PLAYER_2_COLOR = (255, 0, 255)  # Magenta