"""
Pacman Smash - Main Game Entry Point
A competitive two-player Pacman game with AI-driven dynamic elements.
"""

import pygame
import sys
from typing import Optional, List
from maze import Maze
from player import Player, PLAYER_1_CONTROLS, PLAYER_2_CONTROLS, PLAYER_1_COLOR, PLAYER_2_COLOR
from ghost_ai import GhostManager
from ai_controller import AIController

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
BACKGROUND_COLOR = (0, 0, 0)  # Black

class GameEngine:
    """Main game engine that manages the game loop and coordinates all systems."""
    
    def __init__(self):
        """Initialize the game engine."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Pacman Smash")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Initialize game systems
        self.maze = Maze(25, 19)
        self.ghost_manager = GhostManager()
        self.ai_controller = AIController()
        
        # Calculate maze rendering offset to center it
        maze_pixel_width = self.maze.width * self.maze.cell_size
        maze_pixel_height = self.maze.height * self.maze.cell_size
        self.maze_offset_x = (SCREEN_WIDTH - maze_pixel_width) // 2
        self.maze_offset_y = (SCREEN_HEIGHT - maze_pixel_height) // 2
        
        # Initialize players
        player_starts = self.maze.get_player_starting_positions()
        self.players = [
            Player(1, player_starts[0], PLAYER_1_CONTROLS, PLAYER_1_COLOR),
            Player(2, player_starts[1], PLAYER_2_CONTROLS, PLAYER_2_COLOR)
        ]
        
        # Register players with AI controller
        for player in self.players:
            self.ai_controller.register_player(player.player_id)
        
        # Initialize ghosts
        self.ghost_manager.create_default_ghosts(self.maze.width, self.maze.height)
        
        # Game state
        self.game_messages: List[str] = []
        self.message_display_time = 3.0  # seconds
        self.message_timestamps: List[float] = []
        
        # Initialize font for UI
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
    def handle_events(self) -> None:
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
        
        # Handle continuous key presses for player movement
        keys = pygame.key.get_pressed()
        self.handle_player_input(keys)
    
    def handle_player_input(self, keys) -> None:
        """Handle player input for movement."""
        # Player 1 controls (WASD)
        player1 = self.players[0]
        if player1.is_movement_allowed():
            new_pos = None
            if keys[pygame.K_w]:  # Up
                new_pos = (player1.position[0], player1.position[1] - 1)
            elif keys[pygame.K_s]:  # Down
                new_pos = (player1.position[0], player1.position[1] + 1)
            elif keys[pygame.K_a]:  # Left
                new_pos = (player1.position[0] - 1, player1.position[1])
            elif keys[pygame.K_d]:  # Right
                new_pos = (player1.position[0] + 1, player1.position[1])
            
            if new_pos and self.maze.is_valid_position(new_pos[0], new_pos[1]):
                player1.move(new_pos)
                self.handle_player_maze_interactions(player1)
        
        # Player 2 controls (Arrow keys)
        player2 = self.players[1]
        if player2.is_movement_allowed():
            new_pos = None
            if keys[pygame.K_UP]:  # Up
                new_pos = (player2.position[0], player2.position[1] - 1)
            elif keys[pygame.K_DOWN]:  # Down
                new_pos = (player2.position[0], player2.position[1] + 1)
            elif keys[pygame.K_LEFT]:  # Left
                new_pos = (player2.position[0] - 1, player2.position[1])
            elif keys[pygame.K_RIGHT]:  # Right
                new_pos = (player2.position[0] + 1, player2.position[1])
            
            if new_pos and self.maze.is_valid_position(new_pos[0], new_pos[1]):
                player2.move(new_pos)
                self.handle_player_maze_interactions(player2)
    
    def handle_player_maze_interactions(self, player) -> None:
        """Handle player interactions with maze elements."""
        x, y = player.position
        
        # Check for pellet collection
        if self.maze.collect_pellet(x, y):
            points = 10
            player.collect_pellet(points)
            self.add_message(f"Player {player.player_id} collected a pellet! (+{points} points)")
        
        # Check for power-up collection
        if self.maze.collect_powerup(x, y):
            # Randomly assign a power-up type
            import random
            from player import PowerUpType
            
            powerup_types = list(PowerUpType)
            powerup_type = random.choice(powerup_types)
            player.add_powerup(powerup_type, 5.0)
            
            # Apply power-up effects
            if powerup_type == PowerUpType.FREEZE_OPPONENT:
                # Freeze the other player
                other_player = self.players[1] if player.player_id == 1 else self.players[0]
                other_player.freeze(3.0)
                self.add_message(f"Player {other_player.player_id} is frozen!")
            
            elif powerup_type == PowerUpType.GHOST_CONFUSION:
                # Confuse all ghosts
                self.ghost_manager.set_all_confused(5.0)
                self.add_message("All ghosts are confused!")
            
            elif powerup_type == PowerUpType.SPEED_BOOST:
                self.add_message(f"Player {player.player_id} got a speed boost!")
            
            self.add_message(f"Player {player.player_id} collected a power-up!")
    
    def update(self) -> None:
        """Update all game systems."""
        # Update maze (handle temporary modifications and pellet respawning)
        respawned_pellets = self.maze.update_temporary_modifications()
        if respawned_pellets > 0:
            self.add_message(f"{respawned_pellets} pellets respawned!")
        
        # Update players (power-ups, etc.)
        for player in self.players:
            player.update_powerups()
        
        # Update ghosts
        self.ghost_manager.update_all(self.maze.grid, self.players)
        
        # Check ghost-player collisions
        collisions = self.ghost_manager.check_collisions(self.players)
        for ghost, player in collisions:
            player.die()
            self.add_message(f"Player {player.player_id} was caught by a ghost!")
        
        # Update AI controller
        ai_messages = self.ai_controller.update(self.players, self.ghost_manager, self.maze)
        for message in ai_messages:
            self.add_message(message)
        
        # Clean up old messages
        self.cleanup_old_messages()
    
    def add_message(self, message: str) -> None:
        """Add a message to display on screen."""
        import time
        self.game_messages.append(message)
        self.message_timestamps.append(time.time())
        
        # Limit number of messages
        if len(self.game_messages) > 5:
            self.game_messages.pop(0)
            self.message_timestamps.pop(0)
    
    def cleanup_old_messages(self) -> None:
        """Remove messages that have been displayed too long."""
        import time
        current_time = time.time()
        
        while (self.message_timestamps and 
               current_time - self.message_timestamps[0] > self.message_display_time):
            self.game_messages.pop(0)
            self.message_timestamps.pop(0)
    
    def render_ui(self) -> None:
        """Render the user interface."""
        # Render player scores
        score_y = 10
        for i, player in enumerate(self.players):
            score_text = f"Player {player.player_id}: {player.score}"
            color = player.color
            text_surface = self.font.render(score_text, True, color)
            self.screen.blit(text_surface, (10 + i * 200, score_y))
            
            # Show active power-ups
            if player.active_powerups:
                powerup_text = f"Power-ups: {len(player.active_powerups)}"
                powerup_surface = self.small_font.render(powerup_text, True, color)
                self.screen.blit(powerup_surface, (10 + i * 200, score_y + 30))
        
        # Render game messages
        message_y = SCREEN_HEIGHT - 150
        for message in self.game_messages[-3:]:  # Show last 3 messages
            message_surface = self.small_font.render(message, True, (255, 255, 255))
            self.screen.blit(message_surface, (10, message_y))
            message_y += 25
        
        # Render pellet count
        pellet_text = f"Pellets: {self.maze.get_pellet_count()}"
        pellet_surface = self.small_font.render(pellet_text, True, (255, 255, 255))
        self.screen.blit(pellet_surface, (SCREEN_WIDTH - 150, 10))
        
        # Render completion percentage
        completion = self.maze.get_completion_percentage()
        completion_text = f"Complete: {completion:.1f}%"
        completion_surface = self.small_font.render(completion_text, True, (255, 255, 255))
        self.screen.blit(completion_surface, (SCREEN_WIDTH - 150, 35))
    
    def render(self) -> None:
        """Render all game elements."""
        self.screen.fill(BACKGROUND_COLOR)
        
        # Render maze
        self.maze.render(self.screen, self.maze_offset_x, self.maze_offset_y)
        
        # Render players
        for player in self.players:
            player.render(self.screen, self.maze.cell_size, 
                         self.maze_offset_x, self.maze_offset_y)
        
        # Render ghosts
        self.ghost_manager.render_all(self.screen, self.maze.cell_size,
                                     self.maze_offset_x, self.maze_offset_y)
        
        # Render UI
        self.render_ui()
        
        pygame.display.flip()
    
    def run(self) -> None:
        """Main game loop."""
        print("Starting Pacman Smash!")
        print("Controls:")
        print("Player 1: WASD keys")
        print("Player 2: Arrow keys")
        print("Press ESC to quit")
        
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

def main():
    """Entry point for the game."""
    game = GameEngine()
    game.run()

if __name__ == "__main__":
    main()