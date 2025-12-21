"""
Test player mechanics and controls.
"""

import pygame
import time
from player import Player, PLAYER_1_CONTROLS, PLAYER_1_COLOR, PowerUpType
from maze import Maze

def test_player_movement():
    """Test basic player movement mechanics."""
    player = Player(1, (5, 5), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    
    # Test initial state
    assert player.position == (5, 5)
    assert player.score == 0
    assert player.is_movement_allowed()
    
    # Test movement
    player.move((6, 5))
    assert player.position == (6, 5)
    assert len(player.movement_history) == 1
    
    # Test movement cooldown
    assert not player.is_movement_allowed()  # Should be on cooldown
    
    # Wait for cooldown
    time.sleep(0.2)
    assert player.is_movement_allowed()  # Should be able to move again

def test_pellet_collection():
    """Test pellet collection mechanics."""
    player = Player(1, (1, 1), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    
    initial_score = player.score
    player.collect_pellet(10)
    
    assert player.score == initial_score + 10
    assert player.pellets_collected == 1

def test_power_ups():
    """Test power-up mechanics."""
    player = Player(1, (1, 1), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    
    # Test adding power-up
    player.add_powerup(PowerUpType.SPEED_BOOST, 2.0)
    assert len(player.active_powerups) == 1
    
    # Test speed boost effect
    base_speed = 1.0
    boosted_speed = player.get_current_speed()
    assert boosted_speed > base_speed
    
    # Test freeze
    player.freeze(1.0)
    assert player.is_frozen
    assert not player.is_movement_allowed()

def test_player_death():
    """Test player death mechanics."""
    player = Player(1, (5, 5), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    player.score = 100
    
    initial_deaths = player.death_count
    player.die(50)
    
    assert player.death_count == initial_deaths + 1
    assert player.score == 50  # 100 - 50 penalty
    assert player.position == player.start_position

def test_performance_metrics():
    """Test performance tracking."""
    player = Player(1, (1, 1), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    
    # Simulate some movement
    for i in range(5):
        player.move((i + 2, 1))
        time.sleep(0.01)
    
    # Test metrics calculation
    avg_speed = player.get_average_speed(1.0)
    assert avg_speed >= 0.0
    
    collection_rate = player.get_pellet_collection_rate(1.0)
    assert collection_rate >= 0.0

def test_maze_integration():
    """Test player interaction with maze."""
    maze = Maze(10, 10)
    player = Player(1, (1, 1), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    
    # Test valid position
    assert maze.is_valid_position(1, 1)
    assert not maze.is_wall(1, 1)
    
    # Test wall collision prevention
    assert maze.is_wall(0, 0)  # Border should be wall
    
    # Test pellet collection
    pellet_positions = list(maze.pellet_positions)
    if pellet_positions:
        test_pos = pellet_positions[0]
        initial_count = maze.get_pellet_count()
        collected = maze.collect_pellet(test_pos[0], test_pos[1])
        assert collected
        assert maze.get_pellet_count() == initial_count - 1

if __name__ == "__main__":
    pygame.init()  # Initialize pygame for time functions
    
    test_player_movement()
    print("✓ Player movement test passed")
    
    test_pellet_collection()
    print("✓ Pellet collection test passed")
    
    test_power_ups()
    print("✓ Power-up test passed")
    
    test_player_death()
    print("✓ Player death test passed")
    
    test_performance_metrics()
    print("✓ Performance metrics test passed")
    
    test_maze_integration()
    print("✓ Maze integration test passed")
    
    pygame.quit()
    print("\nAll player mechanics tests passed!")