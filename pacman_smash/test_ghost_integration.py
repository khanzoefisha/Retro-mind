"""
Test ghost AI integration with the main game.
"""

import pygame
import time
from main import GameEngine

def test_ghost_game_integration():
    """Test that ghosts work properly in the game context."""
    pygame.init()
    
    # Create game engine
    game = GameEngine()
    
    # Verify ghosts are created
    assert len(game.ghost_manager.ghosts) == 4, "Should have 4 ghosts"
    
    # Verify ghosts are positioned in valid locations
    for ghost in game.ghost_manager.ghosts:
        x, y = ghost.position
        assert game.maze.is_valid_position(x, y), f"Ghost at {ghost.position} should be in valid position"
    
    # Test ghost updates
    initial_positions = [ghost.position for ghost in game.ghost_manager.ghosts]
    
    # Run a few update cycles
    for _ in range(10):
        game.ghost_manager.update_all(game.maze.grid, game.players)
        time.sleep(0.1)
    
    # Check that at least some ghosts have moved (they might not all move due to cooldowns)
    current_positions = [ghost.position for ghost in game.ghost_manager.ghosts]
    moved_ghosts = sum(1 for i, pos in enumerate(current_positions) 
                      if pos != initial_positions[i])
    
    print(f"Ghosts that moved: {moved_ghosts}/4")
    
    # Test collision detection
    # Move a player to a ghost position to test collision
    if game.ghost_manager.ghosts:
        ghost_pos = game.ghost_manager.ghosts[0].position
        game.players[0].position = ghost_pos
        
        collisions = game.ghost_manager.check_collisions(game.players)
        assert len(collisions) > 0, "Should detect collision when player is at ghost position"
    
    # Test AI controller integration
    # The AI controller should be able to modify ghost behavior
    game.ai_controller.register_player(1)
    game.ai_controller.register_player(2)
    
    # Simulate performance imbalance
    game.players[0].score = 100
    game.players[1].score = 10
    
    # Update AI controller
    ai_messages = game.ai_controller.update(game.players, game.ghost_manager, game.maze)
    
    print(f"AI messages: {ai_messages}")
    
    pygame.quit()
    print("Ghost integration test completed successfully!")

if __name__ == "__main__":
    test_ghost_game_integration()