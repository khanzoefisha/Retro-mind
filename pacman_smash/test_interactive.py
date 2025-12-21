"""
Interactive test to verify player controls work in the game.
Run this and use WASD and arrow keys to test movement.
Press ESC to quit.
"""

import pygame
import sys
from main import GameEngine

def main():
    """Run interactive test."""
    print("Interactive Player Control Test")
    print("===============================")
    print("Player 1: Use WASD keys to move")
    print("Player 2: Use Arrow keys to move")
    print("Press ESC to quit")
    print("Watch the console for pellet collection messages")
    print()
    
    # Create and run game for a short test
    game = GameEngine()
    
    # Add some test messages
    game.add_message("Welcome to Pacman Smash!")
    game.add_message("Move around to collect pellets")
    
    # Run for a limited time or until ESC
    start_time = pygame.time.get_ticks()
    test_duration = 30000  # 30 seconds
    
    while game.running:
        current_time = pygame.time.get_ticks()
        
        # Auto-quit after test duration
        if current_time - start_time > test_duration:
            print(f"\nTest completed after {test_duration/1000} seconds")
            break
        
        game.handle_events()
        game.update()
        game.render()
        game.clock.tick(60)
        
        # Print score updates
        if current_time % 5000 < 100:  # Every 5 seconds
            print(f"Scores - Player 1: {game.players[0].score}, Player 2: {game.players[1].score}")
    
    # Print final stats
    print("\nFinal Results:")
    for player in game.players:
        print(f"Player {player.player_id}:")
        print(f"  Score: {player.score}")
        print(f"  Pellets collected: {player.pellets_collected}")
        print(f"  Deaths: {player.death_count}")
        print(f"  Position: {player.position}")
    
    pygame.quit()

if __name__ == "__main__":
    main()