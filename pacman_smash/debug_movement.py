#!/usr/bin/env python3
"""
Debug script to test player movement.
"""

import pygame
import time
from main import GameEngine

def test_movement():
    """Test player movement with debug output."""
    pygame.init()
    
    game = GameEngine()
    
    print("=== Movement Debug Test ===")
    print(f"Player 1 starting position: {game.players[0].position}")
    print(f"Player 2 starting position: {game.players[1].position}")
    print(f"Player 1 move cooldown: {game.players[0].move_cooldown}")
    print(f"Player 2 move cooldown: {game.players[1].move_cooldown}")
    
    # Test if players can move initially
    print(f"Player 1 can move: {game.players[0].is_movement_allowed()}")
    print(f"Player 2 can move: {game.players[1].is_movement_allowed()}")
    
    # Test manual movement
    print("\n=== Testing Manual Movement ===")
    
    # Try to move player 1 right
    old_pos = game.players[0].position
    new_pos = (old_pos[0] + 1, old_pos[1])
    
    print(f"Trying to move Player 1 from {old_pos} to {new_pos}")
    print(f"Is valid position: {game.maze.is_valid_position(new_pos[0], new_pos[1])}")
    
    if game.maze.is_valid_position(new_pos[0], new_pos[1]):
        game.players[0].move(new_pos)
        print(f"Player 1 new position: {game.players[0].position}")
        print(f"Movement successful: {game.players[0].position != old_pos}")
    else:
        print("Position is not valid (wall or out of bounds)")
    
    # Test key simulation
    print("\n=== Testing Key Input Simulation ===")
    
    # Simulate key press
    keys = pygame.key.get_pressed()
    print(f"Current keys pressed: {sum(keys)}")
    
    # Create a fake key state
    fake_keys = [False] * 512
    fake_keys[pygame.K_d] = True  # Simulate 'D' key press
    
    print("Simulating 'D' key press...")
    
    # Test the input handling logic manually
    player1 = game.players[0]
    if player1.is_movement_allowed():
        new_pos = None
        if fake_keys[pygame.K_d]:  # Right
            new_pos = (player1.position[0] + 1, player1.position[1])
            print(f"D key detected, new position would be: {new_pos}")
        
        if new_pos and game.maze.is_valid_position(new_pos[0], new_pos[1]):
            old_pos = player1.position
            player1.move(new_pos)
            print(f"Moved from {old_pos} to {player1.position}")
        else:
            print("Cannot move to that position")
    else:
        print("Player movement not allowed (cooldown or frozen)")
    
    # Test maze validity around starting positions
    print("\n=== Testing Maze Validity ===")
    for player_id, player in enumerate(game.players, 1):
        x, y = player.position
        print(f"Player {player_id} at ({x}, {y}):")
        print(f"  Up ({x}, {y-1}): {game.maze.is_valid_position(x, y-1)}")
        print(f"  Down ({x}, {y+1}): {game.maze.is_valid_position(x, y+1)}")
        print(f"  Left ({x-1}, {y}): {game.maze.is_valid_position(x-1, y)}")
        print(f"  Right ({x+1}, {y}): {game.maze.is_valid_position(x+1, y)}")
    
    pygame.quit()

if __name__ == "__main__":
    test_movement()