"""
Ghost AI system for Pacman Smash.
Handles ghost behavior, pathfinding, and adaptive targeting.
"""

import pygame
import random
import time
from typing import List, Tuple, Optional, Set
from enum import Enum
from dataclasses import dataclass

class GhostBehavior(Enum):
    """Different behavior states for ghosts."""
    CHASE = "chase"
    RANDOM = "random" 
    CONFUSED = "confused"
    NEUTRAL = "neutral"

@dataclass
class GhostTarget:
    """Represents a ghost's current target."""
    player_id: Optional[int]  # None for no specific target
    priority: float  # Higher values = higher priority
    
class Ghost:
    """AI-controlled ghost entity."""
    
    def __init__(self, ghost_id: int, start_position: Tuple[int, int], 
                 color: Tuple[int, int, int]):
        """
        Initialize a ghost.
        
        Args:
            ghost_id: Unique identifier
            start_position: Starting (x, y) grid position
            color: RGB color tuple for rendering
        """
        self.ghost_id = ghost_id
        self.position = start_position
        self.start_position = start_position
        self.color = color
        
        # Movement and behavior
        self.speed_multiplier = 1.0
        self.behavior_state = GhostBehavior.NEUTRAL
        self.target_player: Optional[int] = None
        
        # Pathfinding and movement history
        self.path_history: List[Tuple[int, int]] = []
        self.last_move_time = 0.0
        self.move_cooldown = 0.5  # Seconds between moves
        
        # Confusion state
        self.confusion_end_time = 0.0
        
        # Coordination to prevent clustering
        self.preferred_distance_from_others = 3
        
    def set_behavior(self, behavior: GhostBehavior, duration: Optional[float] = None) -> None:
        """Set the ghost's behavior state."""
        self.behavior_state = behavior
        
        if behavior == GhostBehavior.CONFUSED and duration:
            self.confusion_end_time = time.time() + duration
    
    def set_target_player(self, player_id: Optional[int], priority: float = 1.0) -> None:
        """Set which player this ghost should target."""
        self.target_player = player_id
    
    def set_speed_multiplier(self, multiplier: float) -> None:
        """Adjust the ghost's movement speed."""
        self.speed_multiplier = max(0.1, min(3.0, multiplier))  # Clamp between 0.1 and 3.0
    
    def can_move(self) -> bool:
        """Check if enough time has passed since last move."""
        current_time = time.time()
        time_since_move = current_time - self.last_move_time
        move_interval = self.move_cooldown / self.speed_multiplier
        return time_since_move >= move_interval
    
    def is_confused(self) -> bool:
        """Check if the ghost is currently confused."""
        return (self.behavior_state == GhostBehavior.CONFUSED and 
                time.time() < self.confusion_end_time)
    
    def get_valid_moves(self, maze_grid: List[List[int]]) -> List[Tuple[int, int]]:
        """Get all valid adjacent positions the ghost can move to."""
        x, y = self.position
        valid_moves = []
        
        # Check all four directions
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            
            # Check bounds
            if (0 <= new_x < len(maze_grid[0]) and 
                0 <= new_y < len(maze_grid)):
                
                # Check if position is not a wall (assuming 1 = wall)
                if maze_grid[new_y][new_x] != 1:
                    valid_moves.append((new_x, new_y))
        
        return valid_moves
    
    def calculate_distance(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
        """Calculate Manhattan distance between two positions."""
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])
    
    def choose_chase_move(self, valid_moves: List[Tuple[int, int]], 
                         target_position: Tuple[int, int]) -> Tuple[int, int]:
        """Choose the best move when chasing a target."""
        if not valid_moves:
            return self.position
        
        # Find the move that gets closest to target
        best_move = valid_moves[0]
        best_distance = self.calculate_distance(best_move, target_position)
        
        for move in valid_moves[1:]:
            distance = self.calculate_distance(move, target_position)
            if distance < best_distance:
                best_distance = distance
                best_move = move
        
        return best_move
    
    def choose_random_move(self, valid_moves: List[Tuple[int, int]]) -> Tuple[int, int]:
        """Choose a random valid move."""
        if not valid_moves:
            return self.position
        return random.choice(valid_moves)
    
    def avoid_clustering(self, valid_moves: List[Tuple[int, int]], 
                        other_ghosts: List['Ghost']) -> List[Tuple[int, int]]:
        """Filter moves to avoid clustering with other ghosts."""
        if not other_ghosts:
            return valid_moves
        
        filtered_moves = []
        
        for move in valid_moves:
            too_close = False
            for other_ghost in other_ghosts:
                if other_ghost.ghost_id != self.ghost_id:
                    distance = self.calculate_distance(move, other_ghost.position)
                    if distance < self.preferred_distance_from_others:
                        too_close = True
                        break
            
            if not too_close:
                filtered_moves.append(move)
        
        # If all moves would cause clustering, return original moves
        return filtered_moves if filtered_moves else valid_moves
    
    def update(self, maze_grid: List[List[int]], players: List, 
               other_ghosts: List['Ghost']) -> None:
        """Update ghost AI and movement."""
        if not self.can_move():
            return
        
        # Update confusion state
        if self.is_confused():
            self.behavior_state = GhostBehavior.CONFUSED
        elif self.behavior_state == GhostBehavior.CONFUSED and time.time() >= self.confusion_end_time:
            self.behavior_state = GhostBehavior.NEUTRAL
        
        valid_moves = self.get_valid_moves(maze_grid)
        if not valid_moves:
            return
        
        # Apply clustering avoidance
        valid_moves = self.avoid_clustering(valid_moves, other_ghosts)
        
        # Choose move based on behavior
        new_position = self.position
        
        if self.behavior_state == GhostBehavior.CONFUSED:
            new_position = self.choose_random_move(valid_moves)
        
        elif self.behavior_state == GhostBehavior.CHASE and self.target_player is not None:
            # Find target player
            target_position = None
            for player in players:
                if player.player_id == self.target_player:
                    target_position = player.position
                    break
            
            if target_position:
                new_position = self.choose_chase_move(valid_moves, target_position)
            else:
                new_position = self.choose_random_move(valid_moves)
        
        elif self.behavior_state == GhostBehavior.RANDOM:
            new_position = self.choose_random_move(valid_moves)
        
        else:  # NEUTRAL behavior
            # Simple patrol behavior - prefer continuing in same direction
            if self.path_history:
                last_pos = self.path_history[-1]
                current_direction = (self.position[0] - last_pos[0], 
                                   self.position[1] - last_pos[1])
                
                # Try to continue in same direction
                preferred_pos = (self.position[0] + current_direction[0],
                               self.position[1] + current_direction[1])
                
                if preferred_pos in valid_moves:
                    new_position = preferred_pos
                else:
                    new_position = self.choose_random_move(valid_moves)
            else:
                new_position = self.choose_random_move(valid_moves)
        
        # Update position and history
        if new_position != self.position:
            self.path_history.append(self.position)
            self.position = new_position
            self.last_move_time = time.time()
            
            # Limit history size
            if len(self.path_history) > 10:
                self.path_history.pop(0)
    
    def check_collision_with_player(self, player) -> bool:
        """Check if ghost collides with a player."""
        return self.position == player.position
    
    def render(self, screen: pygame.Surface, cell_size: int, 
               offset_x: int = 0, offset_y: int = 0) -> None:
        """Render the ghost on the screen."""
        pixel_x = self.position[0] * cell_size + offset_x + cell_size // 4
        pixel_y = self.position[1] * cell_size + offset_y + cell_size // 4
        radius = cell_size // 3
        
        # Modify color based on behavior
        render_color = self.color
        if self.is_confused():
            # Flash between original color and white when confused
            if int(time.time() * 4) % 2:
                render_color = (255, 255, 255)
        
        # Draw ghost as a circle
        pygame.draw.circle(screen, render_color, (pixel_x, pixel_y), radius)
        
        # Draw behavior indicator
        if self.behavior_state == GhostBehavior.CHASE:
            # Small red dot for chase mode
            pygame.draw.circle(screen, (255, 0, 0), (pixel_x, pixel_y - radius - 5), 2)

class GhostManager:
    """Manages multiple ghosts and their coordination."""
    
    def __init__(self):
        """Initialize the ghost manager."""
        self.ghosts: List[Ghost] = []
        
    def add_ghost(self, ghost: Ghost) -> None:
        """Add a ghost to the manager."""
        self.ghosts.append(ghost)
    
    def create_default_ghosts(self, maze_width: int, maze_height: int) -> None:
        """Create a default set of ghosts."""
        # Ghost colors (classic Pac-Man inspired)
        ghost_colors = [
            (255, 0, 0),    # Red
            (255, 192, 203), # Pink
            (0, 255, 255),   # Cyan
            (255, 165, 0)    # Orange
        ]
        
        # Place ghosts in center area
        center_x = maze_width // 2
        center_y = maze_height // 2
        
        positions = [
            (center_x - 1, center_y),
            (center_x + 1, center_y),
            (center_x, center_y - 1),
            (center_x, center_y + 1)
        ]
        
        for i, (pos, color) in enumerate(zip(positions, ghost_colors)):
            ghost = Ghost(i, pos, color)
            self.add_ghost(ghost)
    
    def update_all(self, maze_grid: List[List[int]], players: List) -> None:
        """Update all ghosts."""
        for ghost in self.ghosts:
            ghost.update(maze_grid, players, self.ghosts)
    
    def check_collisions(self, players: List) -> List[Tuple[Ghost, any]]:
        """Check for collisions between ghosts and players."""
        collisions = []
        for ghost in self.ghosts:
            for player in players:
                if ghost.check_collision_with_player(player):
                    collisions.append((ghost, player))
        return collisions
    
    def set_all_confused(self, duration: float = 5.0) -> None:
        """Make all ghosts confused for the specified duration."""
        for ghost in self.ghosts:
            ghost.set_behavior(GhostBehavior.CONFUSED, duration)
    
    def set_target_priorities(self, player_priorities: List[Tuple[int, float]]) -> None:
        """Set targeting priorities for ghosts based on player performance."""
        # Distribute ghosts to target players based on priorities
        for i, ghost in enumerate(self.ghosts):
            if player_priorities:
                # Assign ghosts to players with higher priority
                target_player, priority = player_priorities[i % len(player_priorities)]
                ghost.set_target_player(target_player)
                ghost.set_behavior(GhostBehavior.CHASE)
                
                # Adjust speed based on priority
                ghost.set_speed_multiplier(1.0 + priority * 0.5)
    
    def render_all(self, screen: pygame.Surface, cell_size: int, 
                   offset_x: int = 0, offset_y: int = 0) -> None:
        """Render all ghosts."""
        for ghost in self.ghosts:
            ghost.render(screen, cell_size, offset_x, offset_y)