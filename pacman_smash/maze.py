"""
Maze system for Pacman Smash.
Handles maze generation, rendering, and dynamic modifications.
"""

import pygame
import random
import time
from typing import List, Tuple, Set, Dict, Optional
from dataclasses import dataclass
from enum import Enum

class CellType(Enum):
    """Types of cells in the maze grid."""
    PATH = 0
    WALL = 1
    PELLET = 2
    POWER_UP = 3
    EMPTY = 4  # Path with no pellet

@dataclass
class TemporaryModification:
    """Represents a temporary change to the maze."""
    position: Tuple[int, int]
    original_value: int
    new_value: int
    end_time: float

class Maze:
    """Manages the game maze, including dynamic modifications."""
    
    def __init__(self, width: int = 25, height: int = 19):
        """
        Initialize the maze.
        
        Args:
            width: Maze width in grid cells
            height: Maze height in grid cells
        """
        self.width = width
        self.height = height
        
        # Grid representation
        self.grid: List[List[int]] = []
        self.original_grid: List[List[int]] = []
        
        # Pellet tracking
        self.pellet_positions: Set[Tuple[int, int]] = set()
        self.total_pellets = 0
        self.pellet_respawn_timer = 0.0
        self.pellet_respawn_interval = 15.0  # Respawn pellets every 15 seconds
        self.max_pellets_per_respawn = 10
        
        # Dynamic modifications
        self.temporary_modifications: Dict[Tuple[int, int], TemporaryModification] = {}
        
        # Visual properties
        self.cell_size = 25
        self.wall_color = (0, 0, 255)  # Blue
        self.path_color = (0, 0, 0)    # Black
        self.pellet_color = (255, 255, 255)  # White
        self.powerup_color = (255, 255, 0)   # Yellow
        
        # Generate initial maze
        self.generate_maze()
    
    def generate_maze(self) -> None:
        """Generate a basic maze layout."""
        # Create a simple maze pattern
        self.grid = [[CellType.WALL.value for _ in range(self.width)] 
                     for _ in range(self.height)]
        
        # Create paths and add pellets
        self._create_basic_layout()
        self._add_pellets()
        
        # Store original for restoration
        self.original_grid = [row[:] for row in self.grid]
    
    def _create_basic_layout(self) -> None:
        """Create a basic Pacman-style maze layout."""
        # Create outer walls and inner paths
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # Create corridors
                if (x % 2 == 1 and y % 2 == 1) or \
                   (x % 4 == 0 and y % 2 == 1) or \
                   (y % 4 == 0 and x % 2 == 1):
                    self.grid[y][x] = CellType.PATH.value
        
        # Create center area for ghosts
        center_x = self.width // 2
        center_y = self.height // 2
        
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if (0 <= center_x + dx < self.width and 
                    0 <= center_y + dy < self.height):
                    self.grid[center_y + dy][center_x + dx] = CellType.PATH.value
        
        # Ensure player starting positions are clear AND connected
        # Player 1 starting area (top-left)
        self.grid[1][1] = CellType.PATH.value  # Player 1 start
        self.grid[1][2] = CellType.PATH.value  # Right of start
        self.grid[2][1] = CellType.PATH.value  # Below start
        self.grid[1][3] = CellType.PATH.value  # More right
        self.grid[3][1] = CellType.PATH.value  # More below
        
        # Player 2 starting area (bottom-right)
        p2_x, p2_y = self.width - 2, self.height - 2
        self.grid[p2_y][p2_x] = CellType.PATH.value  # Player 2 start
        self.grid[p2_y][p2_x - 1] = CellType.PATH.value  # Left of start
        self.grid[p2_y - 1][p2_x] = CellType.PATH.value  # Above start
        self.grid[p2_y][p2_x - 2] = CellType.PATH.value  # More left
        self.grid[p2_y - 2][p2_x] = CellType.PATH.value  # More above
        
        # Add some strategic openings for better connectivity
        for y in range(self.height):
            if y % 6 == 0:
                for x in range(1, self.width - 1):
                    if x % 3 == 0:
                        self.grid[y][x] = CellType.PATH.value
        
        # Create horizontal corridors
        for y in range(1, self.height - 1, 4):
            for x in range(1, self.width - 1):
                self.grid[y][x] = CellType.PATH.value
        
        # Create vertical corridors
        for x in range(1, self.width - 1, 4):
            for y in range(1, self.height - 1):
                self.grid[y][x] = CellType.PATH.value
    
    def _add_pellets(self) -> None:
        """Add pellets to path cells."""
        self.pellet_positions.clear()
        
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == CellType.PATH.value:
                    # Don't place pellets at player starting positions
                    if (x, y) not in [(1, 1), (self.width - 2, self.height - 2)]:
                        # Don't place pellets in center ghost area
                        center_x = self.width // 2
                        center_y = self.height // 2
                        if not (abs(x - center_x) <= 2 and abs(y - center_y) <= 2):
                            self.grid[y][x] = CellType.PELLET.value
                            self.pellet_positions.add((x, y))
        
        self.total_pellets = len(self.pellet_positions)
    
    def is_valid_position(self, x: int, y: int) -> bool:
        """Check if a position is within bounds and not a wall."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return False
        return self.grid[y][x] != CellType.WALL.value
    
    def is_wall(self, x: int, y: int) -> bool:
        """Check if a position is a wall."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return True
        return self.grid[y][x] == CellType.WALL.value
    
    def get_cell_type(self, x: int, y: int) -> Optional[CellType]:
        """Get the type of cell at the given position."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return None
        return CellType(self.grid[y][x])
    
    def collect_pellet(self, x: int, y: int) -> bool:
        """
        Collect a pellet at the given position.
        
        Returns:
            True if a pellet was collected, False otherwise
        """
        if (x, y) in self.pellet_positions:
            self.pellet_positions.remove((x, y))
            self.grid[y][x] = CellType.EMPTY.value
            return True
        return False
    
    def place_powerup(self, x: int, y: int) -> bool:
        """
        Place a power-up at the given position.
        
        Returns:
            True if power-up was placed, False otherwise
        """
        if self.is_valid_position(x, y) and self.grid[y][x] != CellType.WALL.value:
            self.grid[y][x] = CellType.POWER_UP.value
            return True
        return False
    
    def collect_powerup(self, x: int, y: int) -> bool:
        """
        Collect a power-up at the given position.
        
        Returns:
            True if a power-up was collected, False otherwise
        """
        if (0 <= x < self.width and 0 <= y < self.height and 
            self.grid[y][x] == CellType.POWER_UP.value):
            self.grid[y][x] = CellType.EMPTY.value
            return True
        return False
    
    def get_valid_adjacent_positions(self, x: int, y: int) -> List[Tuple[int, int]]:
        """Get all valid adjacent positions."""
        positions = []
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]  # up, down, left, right
        
        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if self.is_valid_position(new_x, new_y):
                positions.append((new_x, new_y))
        
        return positions
    
    def find_path_positions(self) -> List[Tuple[int, int]]:
        """Find all positions that are not walls."""
        positions = []
        for y in range(self.height):
            for x in range(self.width):
                if not self.is_wall(x, y):
                    positions.append((x, y))
        return positions
    
    def is_area_accessible(self, start_pos: Tuple[int, int], 
                          target_positions: List[Tuple[int, int]]) -> bool:
        """
        Check if all target positions are accessible from start position.
        Uses simple flood fill algorithm.
        """
        if not target_positions:
            return True
        
        visited = set()
        queue = [start_pos]
        visited.add(start_pos)
        
        while queue:
            x, y = queue.pop(0)
            
            # Check if we've reached all targets
            if all(pos in visited for pos in target_positions):
                return True
            
            # Add valid adjacent positions
            for adj_x, adj_y in self.get_valid_adjacent_positions(x, y):
                if (adj_x, adj_y) not in visited:
                    visited.add((adj_x, adj_y))
                    queue.append((adj_x, adj_y))
        
        # Check if all targets were reached
        return all(pos in visited for pos in target_positions)
    
    def apply_chaos_mode(self, duration: float = 10.0, num_walls_to_remove: int = 5) -> None:
        """
        Apply chaos mode by temporarily removing random walls.
        
        Args:
            duration: How long the chaos lasts in seconds
            num_walls_to_remove: Number of walls to remove
        """
        current_time = time.time()
        end_time = current_time + duration
        
        # Find wall positions that can be safely removed
        wall_positions = []
        for y in range(1, self.height - 1):  # Don't remove border walls
            for x in range(1, self.width - 1):
                if self.grid[y][x] == CellType.WALL.value:
                    wall_positions.append((x, y))
        
        # Randomly select walls to remove
        walls_to_remove = random.sample(wall_positions, 
                                       min(num_walls_to_remove, len(wall_positions)))
        
        for x, y in walls_to_remove:
            # Create temporary modification
            mod = TemporaryModification((x, y), CellType.WALL.value, 
                                      CellType.PATH.value, end_time)
            self.temporary_modifications[(x, y)] = mod
            
            # Apply the change
            self.grid[y][x] = CellType.PATH.value
    
    def update_temporary_modifications(self) -> int:
        """Update and remove expired temporary modifications.
        
        Returns:
            Number of pellets respawned
        """
        current_time = time.time()
        expired_mods = []
        
        for pos, mod in self.temporary_modifications.items():
            if current_time >= mod.end_time:
                # Restore original value
                x, y = pos
                self.grid[y][x] = mod.original_value
                expired_mods.append(pos)
        
        # Remove expired modifications
        for pos in expired_mods:
            del self.temporary_modifications[pos]
        
        # Handle pellet respawning
        return self.update_pellet_respawn()
    
    def update_pellet_respawn(self) -> int:
        """
        Update pellet respawn system.
        
        Returns:
            Number of pellets respawned
        """
        current_time = time.time()
        
        if current_time - self.pellet_respawn_timer >= self.pellet_respawn_interval:
            self.pellet_respawn_timer = current_time
            return self.respawn_pellets()
        
        return 0
    
    def respawn_pellets(self) -> int:
        """
        Respawn pellets in empty path positions.
        
        Returns:
            Number of pellets respawned
        """
        # Find empty path positions where pellets can be respawned
        empty_positions = []
        
        for y in range(self.height):
            for x in range(self.width):
                if (self.grid[y][x] == CellType.EMPTY.value and 
                    (x, y) not in self.pellet_positions):
                    # Don't respawn near player starting positions
                    if not ((x, y) in [(1, 1), (self.width - 2, self.height - 2)]):
                        # Don't respawn in center ghost area
                        center_x = self.width // 2
                        center_y = self.height // 2
                        if not (abs(x - center_x) <= 2 and abs(y - center_y) <= 2):
                            empty_positions.append((x, y))
        
        # Randomly select positions to respawn pellets
        import random
        num_to_respawn = min(self.max_pellets_per_respawn, len(empty_positions))
        
        if num_to_respawn > 0:
            respawn_positions = random.sample(empty_positions, num_to_respawn)
            
            for x, y in respawn_positions:
                self.grid[y][x] = CellType.PELLET.value
                self.pellet_positions.add((x, y))
        
        return num_to_respawn
    
    def restore_original_maze(self) -> None:
        """Restore the maze to its original state."""
        self.grid = [row[:] for row in self.original_grid]
        self.temporary_modifications.clear()
        
        # Restore pellet positions (but keep collected ones removed)
        for y in range(self.height):
            for x in range(self.width):
                if (self.original_grid[y][x] == CellType.PELLET.value and 
                    (x, y) not in self.pellet_positions):
                    self.grid[y][x] = CellType.EMPTY.value
    
    def get_pellet_count(self) -> int:
        """Get the current number of pellets remaining."""
        return len(self.pellet_positions)
    
    def get_completion_percentage(self) -> float:
        """Get the percentage of pellets collected."""
        if self.total_pellets == 0:
            return 100.0
        collected_pellets = self.total_pellets - len(self.pellet_positions)
        return (collected_pellets / self.total_pellets) * 100.0
    
    def render(self, screen: pygame.Surface, offset_x: int = 0, offset_y: int = 0) -> None:
        """Render the maze on the screen."""
        for y in range(self.height):
            for x in range(self.width):
                pixel_x = x * self.cell_size + offset_x
                pixel_y = y * self.cell_size + offset_y
                
                cell_type = CellType(self.grid[y][x])
                
                if cell_type == CellType.WALL:
                    # Draw wall
                    pygame.draw.rect(screen, self.wall_color,
                                   (pixel_x, pixel_y, self.cell_size, self.cell_size))
                
                elif cell_type == CellType.PELLET:
                    # Draw path background then pellet
                    pygame.draw.rect(screen, self.path_color,
                                   (pixel_x, pixel_y, self.cell_size, self.cell_size))
                    pellet_x = pixel_x + self.cell_size // 2
                    pellet_y = pixel_y + self.cell_size // 2
                    pygame.draw.circle(screen, self.pellet_color, 
                                     (pellet_x, pellet_y), 2)
                
                elif cell_type == CellType.POWER_UP:
                    # Draw path background then power-up
                    pygame.draw.rect(screen, self.path_color,
                                   (pixel_x, pixel_y, self.cell_size, self.cell_size))
                    powerup_x = pixel_x + self.cell_size // 2
                    powerup_y = pixel_y + self.cell_size // 2
                    pygame.draw.circle(screen, self.powerup_color, 
                                     (powerup_x, powerup_y), 6)
                
                else:  # PATH or EMPTY
                    # Draw path
                    pygame.draw.rect(screen, self.path_color,
                                   (pixel_x, pixel_y, self.cell_size, self.cell_size))
                
                # Highlight temporary modifications
                if (x, y) in self.temporary_modifications:
                    # Draw a flashing border to indicate temporary change
                    if int(time.time() * 4) % 2:  # Flash every 0.25 seconds
                        pygame.draw.rect(screen, (255, 0, 0),
                                       (pixel_x, pixel_y, self.cell_size, self.cell_size), 2)
    
    def get_player_starting_positions(self) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """Get the starting positions for both players."""
        return (1, 1), (self.width - 2, self.height - 2)
    
    def find_empty_positions_near(self, center: Tuple[int, int], 
                                 radius: int = 3) -> List[Tuple[int, int]]:
        """Find empty positions near a center point."""
        x, y = center
        positions = []
        
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                new_x, new_y = x + dx, y + dy
                if (self.is_valid_position(new_x, new_y) and 
                    self.grid[new_y][new_x] in [CellType.PATH.value, CellType.EMPTY.value]):
                    positions.append((new_x, new_y))
        
        return positions