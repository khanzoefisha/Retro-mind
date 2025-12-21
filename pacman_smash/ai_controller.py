"""
AI Controller for Pacman Smash.
Manages performance tracking, difficulty balancing, and chaos events.
"""

import time
import random
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum

class BalancingAction(Enum):
    """Types of balancing actions the AI can take."""
    INCREASE_GHOST_AGGRESSION = "increase_ghost_aggression"
    SPAWN_POWERUP = "spawn_powerup"
    TRIGGER_CHAOS = "trigger_chaos"
    REDUCE_GHOST_SPEED = "reduce_ghost_speed"

@dataclass
class PerformanceMetrics:
    """Tracks performance metrics for a player."""
    player_id: int
    avg_speed: float = 0.0
    pellet_collection_rate: float = 0.0
    death_frequency: float = 0.0
    score_trend: List[int] = field(default_factory=list)
    last_updated: float = 0.0
    
    def update_score_trend(self, current_score: int) -> None:
        """Update the score trend history."""
        self.score_trend.append(current_score)
        # Keep only last 10 scores
        if len(self.score_trend) > 10:
            self.score_trend.pop(0)
    
    def get_score_velocity(self) -> float:
        """Calculate the rate of score change."""
        if len(self.score_trend) < 2:
            return 0.0
        
        recent_scores = self.score_trend[-5:]  # Last 5 scores
        if len(recent_scores) < 2:
            return 0.0
        
        return (recent_scores[-1] - recent_scores[0]) / len(recent_scores)

@dataclass
class ChaosEvent:
    """Represents a chaos event that can be triggered."""
    name: str
    description: str
    duration: float
    cooldown: float
    last_triggered: float = 0.0
    
    def can_trigger(self) -> bool:
        """Check if enough time has passed since last trigger."""
        return time.time() - self.last_triggered >= self.cooldown
    
    def trigger(self) -> None:
        """Mark the event as triggered."""
        self.last_triggered = time.time()

class AIController:
    """Central AI system that manages game balance and chaos."""
    
    def __init__(self):
        """Initialize the AI controller."""
        # Performance tracking
        self.player_metrics: Dict[int, PerformanceMetrics] = {}
        self.tracking_interval = 2.0  # Update metrics every 2 seconds
        self.last_tracking_update = 0.0
        
        # Difficulty balancing
        self.score_difference_threshold = 0.2  # 20% difference triggers balancing
        self.balancing_cooldown = 5.0  # Minimum time between balancing actions
        self.last_balancing_action = 0.0
        
        # Chaos management
        self.chaos_events = self._initialize_chaos_events()
        self.chaos_interval_min = 30.0  # Minimum 30 seconds between chaos
        self.chaos_interval_max = 45.0  # Maximum 45 seconds between chaos
        self.next_chaos_time = time.time() + random.uniform(self.chaos_interval_min, 
                                                           self.chaos_interval_max)
        
        # State tracking
        self.game_start_time = time.time()
        self.total_balancing_actions = 0
        self.total_chaos_events = 0
        
        # AI personality settings
        self.aggression_level = 1.0  # How aggressive the AI is (0.5 - 2.0)
        self.chaos_preference = 1.0  # How much the AI likes chaos (0.5 - 2.0)
        self.fairness_factor = 0.8   # How much the AI tries to be fair (0.0 - 1.0)
    
    def _initialize_chaos_events(self) -> List[ChaosEvent]:
        """Initialize the available chaos events."""
        return [
            ChaosEvent("Wall Removal", "Temporarily removes random walls", 10.0, 20.0),
            ChaosEvent("Ghost Speed Boost", "Increases all ghost speeds", 8.0, 25.0),
            ChaosEvent("Pellet Shower", "Spawns extra pellets", 0.0, 30.0),
            ChaosEvent("Confusion Storm", "Makes all ghosts confused", 6.0, 15.0),
            ChaosEvent("Speed Reversal", "Swaps player speeds temporarily", 5.0, 35.0)
        ]
    
    def register_player(self, player_id: int) -> None:
        """Register a player for performance tracking."""
        self.player_metrics[player_id] = PerformanceMetrics(player_id)
    
    def update_player_metrics(self, players: List) -> None:
        """Update performance metrics for all players."""
        current_time = time.time()
        
        if current_time - self.last_tracking_update < self.tracking_interval:
            return
        
        for player in players:
            if player.player_id not in self.player_metrics:
                self.register_player(player.player_id)
            
            metrics = self.player_metrics[player.player_id]
            
            # Update metrics
            metrics.avg_speed = player.get_average_speed()
            metrics.pellet_collection_rate = player.get_pellet_collection_rate()
            
            # Calculate death frequency (deaths per minute)
            game_duration = max(1.0, current_time - self.game_start_time)
            metrics.death_frequency = (player.death_count / game_duration) * 60.0
            
            # Update score trend
            metrics.update_score_trend(player.score)
            metrics.last_updated = current_time
        
        self.last_tracking_update = current_time
    
    def analyze_performance_imbalance(self, players: List) -> Optional[Tuple[int, int, float]]:
        """
        Analyze if there's a performance imbalance between players.
        
        Returns:
            Tuple of (winning_player_id, losing_player_id, imbalance_ratio) or None
        """
        if len(players) < 2:
            return None
        
        # Sort players by score
        sorted_players = sorted(players, key=lambda p: p.score, reverse=True)
        winner = sorted_players[0]
        loser = sorted_players[-1]
        
        # Calculate imbalance ratio
        if loser.score == 0:
            imbalance_ratio = float('inf') if winner.score > 0 else 0.0
        else:
            imbalance_ratio = winner.score / loser.score
        
        # Check if imbalance exceeds threshold
        if imbalance_ratio > (1.0 + self.score_difference_threshold):
            return winner.player_id, loser.player_id, imbalance_ratio
        
        return None
    
    def determine_balancing_actions(self, winner_id: int, loser_id: int, 
                                  imbalance_ratio: float) -> List[BalancingAction]:
        """Determine what balancing actions to take."""
        actions = []
        
        # More severe imbalance = more actions
        severity = min(3, int(imbalance_ratio - 1.0))
        
        if severity >= 1:
            # Always increase ghost aggression toward winner
            actions.append(BalancingAction.INCREASE_GHOST_AGGRESSION)
        
        if severity >= 2:
            # Spawn power-up near loser
            actions.append(BalancingAction.SPAWN_POWERUP)
        
        if severity >= 3:
            # Trigger chaos event
            actions.append(BalancingAction.TRIGGER_CHAOS)
        
        return actions
    
    def apply_balancing_actions(self, actions: List[BalancingAction], 
                              winner_id: int, loser_id: int,
                              ghost_manager, maze, players: List) -> List[str]:
        """
        Apply the determined balancing actions.
        
        Returns:
            List of messages describing actions taken
        """
        messages = []
        current_time = time.time()
        
        if current_time - self.last_balancing_action < self.balancing_cooldown:
            return messages
        
        for action in actions:
            if action == BalancingAction.INCREASE_GHOST_AGGRESSION:
                # Make ghosts target the winning player more aggressively
                ghost_manager.set_target_priorities([(winner_id, 2.0), (loser_id, 0.5)])
                messages.append(f"Ghosts are now hunting Player {winner_id} more aggressively!")
            
            elif action == BalancingAction.SPAWN_POWERUP:
                # Find losing player and spawn power-up nearby
                loser_player = next((p for p in players if p.player_id == loser_id), None)
                if loser_player:
                    nearby_positions = maze.find_empty_positions_near(loser_player.position, 3)
                    if nearby_positions:
                        spawn_pos = random.choice(nearby_positions)
                        if maze.place_powerup(spawn_pos[0], spawn_pos[1]):
                            messages.append(f"A power-up appeared near Player {loser_id}!")
            
            elif action == BalancingAction.TRIGGER_CHAOS:
                # Trigger a random chaos event
                available_events = [e for e in self.chaos_events if e.can_trigger()]
                if available_events:
                    event = random.choice(available_events)
                    self._trigger_chaos_event(event, maze, ghost_manager)
                    messages.append(f"CHAOS: {event.description}!")
            
            elif action == BalancingAction.REDUCE_GHOST_SPEED:
                # Reduce ghost speed targeting the loser
                for ghost in ghost_manager.ghosts:
                    if ghost.target_player == loser_id:
                        ghost.set_speed_multiplier(0.7)
                messages.append(f"Ghosts chasing Player {loser_id} have slowed down!")
        
        if messages:
            self.last_balancing_action = current_time
            self.total_balancing_actions += len(actions)
        
        return messages
    
    def _trigger_chaos_event(self, event: ChaosEvent, maze, ghost_manager) -> None:
        """Trigger a specific chaos event."""
        event.trigger()
        
        if event.name == "Wall Removal":
            maze.apply_chaos_mode(event.duration, random.randint(3, 7))
        
        elif event.name == "Ghost Speed Boost":
            for ghost in ghost_manager.ghosts:
                ghost.set_speed_multiplier(ghost.speed_multiplier * 1.5)
            # Schedule speed restoration (would need a timer system)
        
        elif event.name == "Pellet Shower":
            # Add extra pellets to random empty positions
            empty_positions = maze.find_path_positions()
            for _ in range(random.randint(5, 10)):
                if empty_positions:
                    pos = random.choice(empty_positions)
                    maze.place_powerup(pos[0], pos[1])
        
        elif event.name == "Confusion Storm":
            ghost_manager.set_all_confused(event.duration)
        
        elif event.name == "Speed Reversal":
            # This would need to be implemented in the game loop
            pass
    
    def check_chaos_timing(self) -> bool:
        """Check if it's time for a chaos event."""
        current_time = time.time()
        return current_time >= self.next_chaos_time
    
    def trigger_random_chaos(self, maze, ghost_manager) -> Optional[str]:
        """Trigger a random chaos event if it's time."""
        if not self.check_chaos_timing():
            return None
        
        available_events = [e for e in self.chaos_events if e.can_trigger()]
        if not available_events:
            return None
        
        # Weight events by chaos preference
        event = random.choice(available_events)
        self._trigger_chaos_event(event, maze, ghost_manager)
        
        # Schedule next chaos event
        self.next_chaos_time = time.time() + random.uniform(
            self.chaos_interval_min / self.chaos_preference,
            self.chaos_interval_max / self.chaos_preference
        )
        
        self.total_chaos_events += 1
        return f"CHAOS EVENT: {event.description}!"
    
    def update(self, players: List, ghost_manager, maze) -> List[str]:
        """
        Main update method for the AI controller.
        
        Returns:
            List of messages about AI actions taken
        """
        messages = []
        
        # Update player metrics
        self.update_player_metrics(players)
        
        # Check for performance imbalance and apply balancing
        imbalance = self.analyze_performance_imbalance(players)
        if imbalance:
            winner_id, loser_id, ratio = imbalance
            actions = self.determine_balancing_actions(winner_id, loser_id, ratio)
            balance_messages = self.apply_balancing_actions(
                actions, winner_id, loser_id, ghost_manager, maze, players
            )
            messages.extend(balance_messages)
        
        # Check for chaos events
        chaos_message = self.trigger_random_chaos(maze, ghost_manager)
        if chaos_message:
            messages.append(chaos_message)
        
        return messages
    
    def get_performance_summary(self) -> Dict[int, Dict[str, float]]:
        """Get a summary of all player performance metrics."""
        summary = {}
        for player_id, metrics in self.player_metrics.items():
            summary[player_id] = {
                'avg_speed': metrics.avg_speed,
                'collection_rate': metrics.pellet_collection_rate,
                'death_frequency': metrics.death_frequency,
                'score_velocity': metrics.get_score_velocity()
            }
        return summary
    
    def get_ai_stats(self) -> Dict[str, int]:
        """Get statistics about AI activity."""
        return {
            'total_balancing_actions': self.total_balancing_actions,
            'total_chaos_events': self.total_chaos_events,
            'game_duration': int(time.time() - self.game_start_time)
        }
    
    def adjust_personality(self, aggression: float = None, 
                          chaos: float = None, fairness: float = None) -> None:
        """Adjust AI personality parameters."""
        if aggression is not None:
            self.aggression_level = max(0.5, min(2.0, aggression))
        if chaos is not None:
            self.chaos_preference = max(0.5, min(2.0, chaos))
        if fairness is not None:
            self.fairness_factor = max(0.0, min(1.0, fairness))