"""
Test ghost AI system functionality.
"""

import time
from ghost_ai import Ghost, GhostManager, GhostBehavior
from player import Player, PLAYER_1_CONTROLS, PLAYER_1_COLOR
from maze import Maze

def test_ghost_creation():
    """Test basic ghost creation and properties."""
    ghost = Ghost(0, (10, 10), (255, 0, 0))
    
    assert ghost.ghost_id == 0
    assert ghost.position == (10, 10)
    assert ghost.color == (255, 0, 0)
    assert ghost.speed_multiplier == 1.0
    assert ghost.behavior_state == GhostBehavior.NEUTRAL
    assert ghost.target_player is None

def test_ghost_movement():
    """Test ghost movement mechanics."""
    maze = Maze(10, 10)
    ghost = Ghost(0, (5, 5), (255, 0, 0))
    
    # Test valid moves calculation
    valid_moves = ghost.get_valid_moves(maze.grid)
    assert len(valid_moves) > 0, "Should have valid moves in open area"
    
    # All valid moves should be adjacent
    for move in valid_moves:
        distance = abs(move[0] - ghost.position[0]) + abs(move[1] - ghost.position[1])
        assert distance == 1, "Valid moves should be adjacent positions"
    
    # Test movement timing
    assert ghost.can_move(), "Should be able to move initially"
    
    # Simulate movement
    if valid_moves:
        new_pos = valid_moves[0]
        ghost.position = new_pos
        ghost.last_move_time = time.time()
        
        # Should be on cooldown now
        assert not ghost.can_move(), "Should be on cooldown after move"

def test_ghost_behaviors():
    """Test different ghost behavior states."""
    maze = Maze(10, 10)
    ghost = Ghost(0, (5, 5), (255, 0, 0))
    player = Player(1, (7, 7), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    
    # Test chase behavior
    ghost.set_behavior(GhostBehavior.CHASE)
    ghost.set_target_player(1)
    
    assert ghost.behavior_state == GhostBehavior.CHASE
    assert ghost.target_player == 1
    
    # Test chase move selection
    valid_moves = ghost.get_valid_moves(maze.grid)
    if valid_moves:
        chase_move = ghost.choose_chase_move(valid_moves, player.position)
        
        # Chase move should be closer to player than current position
        current_distance = ghost.calculate_distance(ghost.position, player.position)
        chase_distance = ghost.calculate_distance(chase_move, player.position)
        assert chase_distance <= current_distance, "Chase move should get closer to player"
    
    # Test confusion behavior
    ghost.set_behavior(GhostBehavior.CONFUSED, 2.0)
    assert ghost.behavior_state == GhostBehavior.CONFUSED
    assert ghost.is_confused()
    
    # Test random behavior
    ghost.set_behavior(GhostBehavior.RANDOM)
    if valid_moves:
        random_move = ghost.choose_random_move(valid_moves)
        assert random_move in valid_moves, "Random move should be valid"

def test_ghost_collision():
    """Test ghost-player collision detection."""
    ghost = Ghost(0, (5, 5), (255, 0, 0))
    player = Player(1, (5, 5), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    
    # Same position should be collision
    assert ghost.check_collision_with_player(player), "Same position should be collision"
    
    # Different positions should not be collision
    player.position = (6, 6)
    assert not ghost.check_collision_with_player(player), "Different positions should not collide"

def test_ghost_manager():
    """Test ghost manager functionality."""
    manager = GhostManager()
    
    # Test adding ghosts
    ghost1 = Ghost(0, (5, 5), (255, 0, 0))
    ghost2 = Ghost(1, (6, 6), (0, 255, 0))
    
    manager.add_ghost(ghost1)
    manager.add_ghost(ghost2)
    
    assert len(manager.ghosts) == 2
    
    # Test default ghost creation
    manager2 = GhostManager()
    manager2.create_default_ghosts(25, 19)
    assert len(manager2.ghosts) == 4, "Should create 4 default ghosts"
    
    # Test collision checking
    player = Player(1, (5, 5), PLAYER_1_CONTROLS, PLAYER_1_COLOR)
    players = [player]
    
    collisions = manager.check_collisions(players)
    assert len(collisions) == 1, "Should detect collision with ghost1"
    assert collisions[0][0] == ghost1, "Should be collision with ghost1"
    assert collisions[0][1] == player, "Should be collision with player"

def test_ghost_coordination():
    """Test ghost anti-clustering behavior."""
    maze = Maze(15, 15)
    
    # Create ghosts close together
    ghost1 = Ghost(0, (7, 7), (255, 0, 0))
    ghost2 = Ghost(1, (8, 7), (0, 255, 0))
    ghost3 = Ghost(2, (7, 8), (0, 0, 255))
    
    other_ghosts = [ghost2, ghost3]
    
    # Test clustering avoidance
    valid_moves = ghost1.get_valid_moves(maze.grid)
    filtered_moves = ghost1.avoid_clustering(valid_moves, other_ghosts)
    
    # Should prefer moves that maintain distance from other ghosts
    for move in filtered_moves:
        for other_ghost in other_ghosts:
            distance = ghost1.calculate_distance(move, other_ghost.position)
            # Should maintain some minimum distance when possible
            if len(filtered_moves) < len(valid_moves):
                assert distance >= ghost1.preferred_distance_from_others

def test_ghost_speed_modification():
    """Test ghost speed adjustment."""
    ghost = Ghost(0, (5, 5), (255, 0, 0))
    
    # Test speed multiplier
    ghost.set_speed_multiplier(2.0)
    assert ghost.speed_multiplier == 2.0
    
    # Test speed limits
    ghost.set_speed_multiplier(5.0)  # Too high
    assert ghost.speed_multiplier <= 3.0, "Speed should be clamped to maximum"
    
    ghost.set_speed_multiplier(0.05)  # Too low
    assert ghost.speed_multiplier >= 0.1, "Speed should be clamped to minimum"

def test_ghost_targeting():
    """Test ghost targeting system."""
    manager = GhostManager()
    manager.create_default_ghosts(15, 15)
    
    # Test setting target priorities
    player_priorities = [(1, 2.0), (2, 0.5)]  # Player 1 high priority, Player 2 low
    manager.set_target_priorities(player_priorities)
    
    # Check that ghosts have been assigned targets
    targeted_ghosts = [g for g in manager.ghosts if g.target_player is not None]
    assert len(targeted_ghosts) > 0, "Some ghosts should have targets"
    
    # Check that high priority player gets more attention
    player1_hunters = [g for g in manager.ghosts if g.target_player == 1]
    player2_hunters = [g for g in manager.ghosts if g.target_player == 2]
    
    # Should have more ghosts targeting high priority player
    assert len(player1_hunters) >= len(player2_hunters), "High priority player should have more hunters"

def test_ghost_confusion_effect():
    """Test ghost confusion power-up effect."""
    manager = GhostManager()
    manager.create_default_ghosts(10, 10)
    
    # Make all ghosts confused
    manager.set_all_confused(3.0)
    
    # All ghosts should be confused
    for ghost in manager.ghosts:
        assert ghost.behavior_state == GhostBehavior.CONFUSED
        assert ghost.is_confused()
    
    # Test that confusion expires
    time.sleep(0.1)  # Small delay
    # Confusion should still be active
    for ghost in manager.ghosts:
        assert ghost.is_confused()

if __name__ == "__main__":
    test_ghost_creation()
    print("✓ Ghost creation test passed")
    
    test_ghost_movement()
    print("✓ Ghost movement test passed")
    
    test_ghost_behaviors()
    print("✓ Ghost behaviors test passed")
    
    test_ghost_collision()
    print("✓ Ghost collision test passed")
    
    test_ghost_manager()
    print("✓ Ghost manager test passed")
    
    test_ghost_coordination()
    print("✓ Ghost coordination test passed")
    
    test_ghost_speed_modification()
    print("✓ Ghost speed modification test passed")
    
    test_ghost_targeting()
    print("✓ Ghost targeting test passed")
    
    test_ghost_confusion_effect()
    print("✓ Ghost confusion effect test passed")
    
    print("\nAll ghost AI tests passed!")