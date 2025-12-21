# Pacman Smash Design Document

## Overview

Pacman Smash is a competitive two-player arcade game built with Python and Pygame that combines classic Pacman mechanics with intelligent AI systems. The game features real-time performance monitoring, adaptive difficulty balancing, and dynamic maze modifications to create engaging, chaotic gameplay experiences.

The system architecture emphasizes modularity with separate components for player management, AI control, maze handling, and game state management. The AI innovation centers on three core systems: adaptive ghost behavior, performance-based difficulty balancing, and dynamic environmental changes.

## Architecture

The game follows a component-based architecture with clear separation of concerns:

```
Game Engine (main.py)
├── Player Management (player.py)
├── AI Controller (ai_controller.py)
│   ├── Performance Tracker
│   ├── Difficulty Balancer
│   └── Chaos Manager
├── Ghost AI (ghost_ai.py)
├── Maze System (maze.py)
├── Power-up Manager
└── Rendering Engine
```

The main game loop operates at 60 FPS, processing input, updating game state, running AI systems, and rendering graphics in sequence. The AI Controller acts as the central intelligence hub, coordinating between different AI subsystems based on real-time performance metrics.

## Components and Interfaces

### Player Component
- **Position Management**: Handles 2D coordinates and movement validation
- **Input Processing**: Maps WASD (Player 1) and Arrow Keys (Player 2) to movement commands
- **State Tracking**: Maintains score, speed modifiers, active power-ups, and death count
- **Collision Interface**: Provides methods for pellet collection and ghost collision detection

### AI Controller
- **Performance Tracker**: Monitors player speed, pellet collection rate, death frequency every 2 seconds
- **Difficulty Balancer**: Compares player scores and triggers balancing mechanisms when score differential exceeds 20%
- **Chaos Manager**: Triggers random events every 30-45 seconds including wall removal and speed changes
- **Event Dispatcher**: Coordinates AI decisions across ghost behavior, power-up spawning, and maze modifications

### Ghost AI System
- **Base Movement**: Implements pathfinding using simple direction-based algorithms
- **Adaptive Targeting**: Adjusts chase behavior based on AI Controller performance analysis
- **Speed Modulation**: Dynamically changes movement speed based on target player performance
- **Collision Detection**: Handles player interactions and respawn mechanics

### Maze System
- **Grid Management**: Maintains 2D array representation (1=wall, 0=path, 2=pellet, 3=power-up)
- **Dynamic Modification**: Supports temporary wall removal and restoration for chaos events
- **Pathfinding Support**: Provides valid movement queries for both players and ghosts
- **Rendering Interface**: Converts grid data to visual representation

## Data Models

### Player Model
```python
class Player:
    position: (int, int)
    score: int
    speed: float
    active_powerups: List[PowerUp]
    death_count: int
    movement_history: List[(int, int, timestamp)]
    controls: Dict[str, str]  # Key mappings
```

### Performance Metrics Model
```python
class PerformanceMetrics:
    player_id: int
    avg_speed: float
    pellet_collection_rate: float  # pellets per second
    death_frequency: float  # deaths per minute
    score_trend: List[int]  # score history for trend analysis
    last_updated: timestamp
```

### Ghost Model
```python
class Ghost:
    position: (int, int)
    target_player: int  # 1 or 2, or None for neutral
    speed_multiplier: float
    behavior_state: str  # "chase", "random", "confused"
    path_history: List[(int, int)]
```

### Maze Model
```python
class Maze:
    grid: List[List[int]]
    original_grid: List[List[int]]  # For restoration after chaos
    width: int
    height: int
    pellet_positions: Set[(int, int)]
    temporary_modifications: Dict[(int, int), (int, timestamp)]
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

**Property 1: Player Input Handling**
*For any* valid player input (WASD for Player 1, arrows for Player 2), the corresponding player should move in the correct direction unless blocked by a wall
**Validates: Requirements 1.1, 1.2, 1.4**

**Property 2: Pellet Collection Mechanics**
*For any* pellet position and player position, when a player moves over a pellet, both the pellet removal and score increase should occur atomically
**Validates: Requirements 2.1, 2.2**

**Property 3: Ghost Pathfinding Validity**
*For any* maze configuration and ghost position, ghosts should never occupy wall positions during movement
**Validates: Requirements 3.1**

**Property 4: Ghost-Player Collision Effects**
*For any* ghost-player collision, the player's score should decrease and the player should respawn at the starting position
**Validates: Requirements 3.2**

**Property 5: Performance Metrics Accuracy**
*For any* sequence of player actions, the calculated performance metrics (speed, collection rate, death frequency) should accurately reflect the actual player behavior
**Validates: Requirements 4.1**

**Property 6: Dynamic Difficulty Balancing**
*For any* game state where one player significantly outperforms another, the AI should adjust ghost targeting to favor the losing player
**Validates: Requirements 4.2, 4.3, 4.4**

**Property 7: Power-up Effect Lifecycle**
*For any* power-up collection, the effect should activate immediately, persist for the specified duration, and restore normal mechanics upon expiration
**Validates: Requirements 5.1, 5.2, 5.3, 5.5**

**Property 8: Maze Chaos Round-trip**
*For any* maze configuration, applying chaos mode (wall removal) followed by restoration should return the maze to its original state
**Validates: Requirements 6.1, 6.3**

**Property 9: Maze Connectivity Preservation**
*For any* maze modification, all previously accessible areas should remain reachable after the modification
**Validates: Requirements 6.2**

**Property 10: UI State Consistency**
*For any* game state, the displayed scores, timer, and power-up indicators should accurately reflect the actual game state
**Validates: Requirements 7.1, 7.3, 7.4**

**Property 11: Collision Processing Atomicity**
*For any* game frame with multiple collisions, all collision effects should be processed together without partial state inconsistencies
**Validates: Requirements 8.2**

## Error Handling

The system implements comprehensive error handling across all major components:

**Input Validation**
- Invalid key presses are ignored without affecting game state
- Out-of-bounds movement attempts are prevented with position validation
- Malformed configuration data triggers graceful fallbacks to default values

**AI System Resilience**
- Performance calculation errors default to neutral AI behavior
- Ghost pathfinding failures trigger random movement as fallback
- Chaos mode failures are logged but don't interrupt core gameplay

**Resource Management**
- Audio file loading failures are handled silently with visual-only feedback
- Texture loading errors display colored rectangles as placeholders
- Memory allocation failures for large data structures trigger cleanup routines

**Game State Recovery**
- Corrupted player positions are reset to valid starting locations
- Invalid maze states trigger restoration from backup configuration
- Timer synchronization issues are resolved by resetting to last known good state

## Testing Strategy

The testing approach combines unit testing and property-based testing to ensure comprehensive coverage:

**Unit Testing Framework**: pytest for Python-based testing
- Specific example verification for edge cases and integration points
- Mock-based testing for Pygame components to enable headless testing
- Component isolation testing for AI systems, maze management, and player mechanics

**Property-Based Testing Framework**: Hypothesis for Python
- Each property-based test configured to run minimum 100 iterations
- Smart generators for game states, player positions, and maze configurations
- Each test tagged with format: **Feature: pacman-smash, Property {number}: {property_text}**

**Test Coverage Requirements**:
- Unit tests verify specific examples, edge cases, and component integration
- Property tests verify universal correctness across all valid inputs
- Both approaches are complementary: unit tests catch concrete bugs, property tests verify general correctness
- All correctness properties must be implemented as property-based tests
- Each correctness property implemented by exactly one property-based test

**Testing Infrastructure**:
- Headless rendering mode for automated testing without display requirements
- Deterministic random number generation for reproducible test results
- Performance benchmarking for AI systems to ensure real-time operation
- Integration test suite for full gameplay scenarios
