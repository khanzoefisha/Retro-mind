#!/usr/bin/env python3
"""
Interactive movement test - shows player positions as you press keys.
"""

import pygame
import sys
from main import GameEngine

def test_interactive_movement():
    """Test movement with real key presses."""
    pygame.init()
    
    game = GameEngine()
    
    print("=== Interactive Movement Test ===")
    print("Controls:")
    print("Player 1 (Blue): WASD")
    print("Player 2 (Red): Arrow Keys")
    print("ESC: Quit")
    print("This test will show position changes when you press keys.")
    print("Press keys to test movement...")
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # Store old positions
        old_p1_pos = game.players[0].position
        old_p2_pos = game.players[1].position
        
        # Handle input
        keys = pygame.key.get_pressed()
        game.handle_player_input(keys)
        
        # Check for position changes
        new_p1_pos = game.players[0].position
        new_p2_pos = game.players[1].position
        
        if old_p1_pos != new_p1_pos:
            print(f"Player 1 moved: {old_p1_pos} -> {new_p1_pos}")
        
        if old_p2_pos != new_p2_pos:
            print(f"Player 2 moved: {old_p2_pos} -> {new_p2_pos}")
        
        # Update game
        game.update()
        game.render()
        
        clock.tick(60)
    
    pygame.quit()
    print("Test completed!")

if __name__ == "__main__":
    test_interactive_movement()