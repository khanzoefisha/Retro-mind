"""
Test maze rendering without running the full game loop.
"""

import pygame
import sys
from maze import Maze

def test_maze_rendering():
    """Test that maze renders correctly."""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Maze Rendering Test")
    
    # Create maze
    maze = Maze(25, 19)
    
    # Calculate offset to center maze
    maze_pixel_width = maze.width * maze.cell_size
    maze_pixel_height = maze.height * maze.cell_size
    offset_x = (800 - maze_pixel_width) // 2
    offset_y = (600 - maze_pixel_height) // 2
    
    # Render once and save screenshot
    screen.fill((0, 0, 0))
    maze.render(screen, offset_x, offset_y)
    pygame.display.flip()
    
    print(f"Maze created with {maze.width}x{maze.height} cells")
    print(f"Total pellets: {maze.total_pellets}")
    print(f"Current pellets: {maze.get_pellet_count()}")
    print(f"Completion: {maze.get_completion_percentage():.1f}%")
    
    # Test some maze functions
    assert maze.is_valid_position(1, 1), "Starting position should be valid"
    assert maze.is_wall(0, 0), "Border should be wall"
    
    # Test pellet collection
    pellet_positions = list(maze.pellet_positions)
    if pellet_positions:
        test_pos = pellet_positions[0]
        initial_count = maze.get_pellet_count()
        collected = maze.collect_pellet(test_pos[0], test_pos[1])
        assert collected, "Should be able to collect pellet"
        assert maze.get_pellet_count() == initial_count - 1, "Pellet count should decrease"
    
    pygame.quit()
    print("Maze rendering test passed!")

if __name__ == "__main__":
    test_maze_rendering()