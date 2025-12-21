#!/usr/bin/env python3
"""
Test script to run the game and check for issues.
"""

import pygame
import sys
import time
from main import GameEngine

def test_game_startup():
    """Test if the game can start up properly."""
    print("Testing game startup...")
    
    try:
        # Initialize pygame
        pygame.init()
        print("✓ Pygame initialized")
        
        # Create game engine
        game = GameEngine()
        print("✓ Game engine created")
        
        # Test a few game loop iterations
        print("Testing game loop...")
        for i in range(10):
            # Simulate some events
            events = pygame.event.get()
            
            # Update game state
            game.update()
            
            # Test rendering (but don't display)
            game.render()
            
            print(f"  Frame {i+1}: OK")
            time.sleep(0.1)
        
        print("✓ Game loop test completed")
        
        # Clean shutdown
        pygame.quit()
        print("✓ Clean shutdown")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_interactive_mode():
    """Test the game in interactive mode for a few seconds."""
    print("\nTesting interactive mode...")
    print("Game will run for 5 seconds, then auto-close...")
    
    try:
        game = GameEngine()
        
        start_time = time.time()
        while time.time() - start_time < 5.0:  # Run for 5 seconds
            game.handle_events()
            game.update()
            game.render()
            game.clock.tick(60)
            
            # Check if user closed window
            if not game.running:
                break
        
        pygame.quit()
        print("✓ Interactive test completed")
        return True
        
    except Exception as e:
        print(f"✗ Interactive test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Pacman Smash - Game Test Suite")
    print("=" * 40)
    
    # Test 1: Basic startup
    if not test_game_startup():
        print("Basic startup test failed!")
        sys.exit(1)
    
    # Test 2: Interactive mode
    if not test_interactive_mode():
        print("Interactive test failed!")
        sys.exit(1)
    
    print("\n" + "=" * 40)
    print("All tests passed! The game should work correctly.")
    print("Run 'python main.py' to start the full game.")