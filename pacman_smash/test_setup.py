"""
Basic setup tests to verify the project structure is working.
"""

import pytest
import pygame
from player import Player, PLAYER_1_CONTROLS, PLAYER_1_COLOR
from maze import Maze, CellType
from ghost_ai import Ghost, GhostManager
from ai_controller import AIController

def test_pygame_import():
    """Test that pygame can be imported and initialized."""
    pygame.init()
    assert pygame.get_init()
    pygame.quit()

def test_player_creation():
    """Test that players can be created with basic properties."""
    player = Player(1, (1, 1), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    assert player.player_id == 1
    assert player.position == (1, 1)
    assert player.score == 0
    assert player.speed == 1.0

def test_maze_creation():
    """Test that maze can be created and has basic properties."""
    maze = Maze(25, 19)
    assert maze.width == 25
    assert maze.height == 19
    assert len(maze.grid) == 19
    assert len(maze.grid[0]) == 25
    assert maze.total_pellets > 0

def test_ghost_creation():
    """Test that ghosts can be created."""
    ghost = Ghost(0, (10, 10), (255, 0, 0))
    assert ghost.ghost_id == 0
    assert ghost.position == (10, 10)
    assert ghost.speed_multiplier == 1.0

def test_ai_controller_creation():
    """Test that AI controller can be created."""
    ai = AIController()
    assert ai.tracking_interval == 2.0
    assert len(ai.chaos_events) > 0

def test_ghost_manager_creation():
    """Test that ghost manager can be created and manage ghosts."""
    manager = GhostManager()
    manager.create_default_ghosts(25, 19)
    assert len(manager.ghosts) == 4

if __name__ == "__main__":
    pytest.main([__file__])