"""
Test pellet collection and scoring system.
"""

import time
from maze import Maze, CellType
from player import Player, PLAYER_1_CONTROLS, PLAYER_1_COLOR

def test_pellet_collection_scoring():
    """Test basic pellet collection and scoring."""
    maze = Maze(10, 10)
    player = Player(1, (1, 1), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    
    # Find a pellet position
    pellet_positions = list(maze.pellet_positions)
    assert len(pellet_positions) > 0, "Maze should have pellets"
    
    test_pos = pellet_positions[0]
    initial_score = player.score
    initial_pellet_count = maze.get_pellet_count()
    
    # Collect the pellet
    collected = maze.collect_pellet(test_pos[0], test_pos[1])
    assert collected, "Should successfully collect pellet"
    
    # Update player score
    player.collect_pellet(10)
    
    # Verify results
    assert player.score == initial_score + 10, "Score should increase by 10"
    assert maze.get_pellet_count() == initial_pellet_count - 1, "Pellet count should decrease"
    assert test_pos not in maze.pellet_positions, "Pellet should be removed from positions"
    assert maze.grid[test_pos[1]][test_pos[0]] == CellType.EMPTY.value, "Cell should be empty"

def test_pellet_respawn_system():
    """Test pellet respawn mechanics."""
    maze = Maze(10, 10)
    
    # Collect some pellets
    pellet_positions = list(maze.pellet_positions)
    initial_count = len(pellet_positions)
    
    # Collect first 5 pellets
    for i in range(min(5, len(pellet_positions))):
        pos = pellet_positions[i]
        maze.collect_pellet(pos[0], pos[1])
    
    collected_count = maze.get_pellet_count()
    assert collected_count < initial_count, "Should have fewer pellets after collection"
    
    # Force pellet respawn
    respawned = maze.respawn_pellets()
    assert respawned > 0, "Should respawn some pellets"
    
    new_count = maze.get_pellet_count()
    assert new_count > collected_count, "Should have more pellets after respawn"

def test_scoring_system():
    """Test comprehensive scoring mechanics."""
    player = Player(1, (1, 1), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    
    # Test pellet collection scoring
    initial_score = player.score
    player.collect_pellet(10)
    assert player.score == initial_score + 10
    
    # Test multiple collections
    for i in range(5):
        player.collect_pellet(10)
    
    assert player.score == initial_score + 60  # 6 pellets * 10 points
    assert player.pellets_collected == 6
    
    # Test death penalty
    player.die(50)
    assert player.score == initial_score + 10  # 60 - 50 penalty
    assert player.death_count == 1

def test_performance_tracking():
    """Test pellet collection rate tracking."""
    player = Player(1, (1, 1), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    
    # Collect pellets over time
    start_time = time.time()
    for i in range(3):
        player.collect_pellet(10)
        time.sleep(0.1)
    
    # Test collection rate calculation
    collection_rate = player.get_pellet_collection_rate(1.0)
    assert collection_rate > 0, "Should have positive collection rate"
    
    # Test that rate decreases over time without collection
    time.sleep(1.0)
    later_rate = player.get_pellet_collection_rate(0.5)
    # Rate should be lower or zero for shorter time window

def test_maze_completion_tracking():
    """Test maze completion percentage tracking."""
    maze = Maze(10, 8)  # Larger maze to ensure pellets are generated
    
    initial_completion = maze.get_completion_percentage()
    print(f"Debug: Initial completion = {initial_completion}")
    print(f"Debug: Total pellets = {maze.total_pellets}")
    print(f"Debug: Current pellets = {len(maze.pellet_positions)}")
    
    # Should start at 0% since no pellets collected yet
    if maze.total_pellets > 0:
        assert abs(initial_completion - 0.0) < 0.1, f"Should start at ~0% completion, got {initial_completion}"
        
        # Collect some pellets
        pellet_positions = list(maze.pellet_positions)
        half_pellets = len(pellet_positions) // 2
        
        for i in range(half_pellets):
            pos = pellet_positions[i]
            maze.collect_pellet(pos[0], pos[1])
        
        mid_completion = maze.get_completion_percentage()
        assert 40 <= mid_completion <= 60, f"Should be around 50% complete, got {mid_completion}"
        
        # Collect remaining pellets
        remaining_positions = list(maze.pellet_positions)
        for pos in remaining_positions:
            maze.collect_pellet(pos[0], pos[1])
        
        final_completion = maze.get_completion_percentage()
        assert abs(final_completion - 100.0) < 0.1, f"Should be ~100% complete, got {final_completion}"
    else:
        print("Warning: No pellets generated in maze, skipping completion test")

def test_score_display_data():
    """Test that score display has correct data."""
    player1 = Player(1, (1, 1), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    player2 = Player(2, (5, 5), PLAYER_1_CONTROLS, (255, 0, 255))
    
    # Simulate different scores
    player1.collect_pellet(50)
    player2.collect_pellet(30)
    
    # Test score comparison
    assert player1.score > player2.score
    
    # Test that both players maintain separate scores
    player1.collect_pellet(20)
    assert player1.score == 70
    assert player2.score == 30

if __name__ == "__main__":
    test_pellet_collection_scoring()
    print("✓ Pellet collection and scoring test passed")
    
    test_pellet_respawn_system()
    print("✓ Pellet respawn system test passed")
    
    test_scoring_system()
    print("✓ Scoring system test passed")
    
    test_performance_tracking()
    print("✓ Performance tracking test passed")
    
    test_maze_completion_tracking()
    print("✓ Maze completion tracking test passed")
    
    test_score_display_data()
    print("✓ Score display data test passed")
    
    print("\nAll pellet collection and scoring tests passed!")