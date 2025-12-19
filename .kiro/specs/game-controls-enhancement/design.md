# Game Controls Enhancement Design Document

## Overview

This design document outlines the implementation of enhanced game controls and alphabet progression for the HTML5 Canvas game. The enhancements focus on providing predictable alphabet changes every 5 points and standardized keyboard controls for game state management including pause, stop, restart, and new game functionality.

## Architecture

The enhancement will extend the existing game architecture by:

1. **Enhanced Game State Management**: Extending the current game state to include pause functionality
2. **Alphabet Progression System**: Implementing sequential alphabet changes with visual feedback
3. **Keyboard Control Handler**: Centralizing all game control inputs with clear state-based routing
4. **Visual Feedback System**: Adding overlays and transitions for state changes

## Components and Interfaces

### Game State Manager
```javascript
gameState: {
  mode: 'menu' | 'playing' | 'paused' | 'stopped' | 'gameover',
  previousMode: string,
  pauseTime: number,
  controlsVisible: boolean
}
```

### Alphabet Progression Controller
```javascript
alphabetController: {
  currentIndex: number,
  letters: string[],
  lastChangeScore: number,
  changeThreshold: 5,
  transitionActive: boolean,
  transitionTimer: number
}
```

### Control Input Handler
```javascript
controlHandler: {
  keyMappings: Map<string, function>,
  stateBasedControls: Map<string, string[]>,
  handleKeyPress: function,
  updateControlDisplay: function
}
```

## Data Models

### Enhanced Game Object
The existing game object will be extended with:

```javascript
game: {
  // Existing properties...
  state: {
    mode: 'playing',
    previousMode: null,
    pauseStartTime: 0,
    totalPauseTime: 0
  },
  alphabet: {
    currentIndex: 0,
    letters: ['A', 'B', 'C', ..., 'Z'],
    lastChangeScore: 0,
    changeThreshold: 5,
    transition: {
      active: false,
      timer: 0,
      duration: 60, // frames
      newLetter: null
    }
  },
  controls: {
    instructions: {
      playing: "S: Pause | ESC: New Game",
      paused: "S: Stop | R: Restart | ESC: New Game",
      stopped: "R: Restart | ESC: New Game"
    },
    visible: true,
    fadeTimer: 0
  }
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After reviewing the prework analysis, several properties can be consolidated:
- Properties 1.5 and 3.2 both test visual feedback for alphabet changes - these will be combined
- Properties 2.5 and 3.5 both test UI updates for state changes - these will be combined
- Property 3.3 can be merged with the consolidated UI update property

### Core Properties

**Property 1: Alphabet progression follows score thresholds**
*For any* score that is a multiple of 5, the alphabet should advance to the next letter in sequence, wrapping from Z back to A
**Validates: Requirements 1.1, 1.4**

**Property 2: Alphabet display updates correctly**
*For any* alphabet change, the display should show the new letter prominently in the center with visual feedback effects
**Validates: Requirements 1.2, 1.5, 3.2**

**Property 3: Pause control behavior**
*For any* game in playing state, pressing 'S' should transition to paused state and display pause controls
**Validates: Requirements 2.1**

**Property 4: Stop control behavior**
*For any* game in paused state, pressing 'S' should transition to stopped state and return to main menu
**Validates: Requirements 2.2**

**Property 5: Restart control behavior**
*For any* game in paused or stopped state, pressing 'R' should restart the game session with reset state
**Validates: Requirements 2.3**

**Property 6: New game control behavior**
*For any* game state, pressing 'ESC' should start a completely new game session
**Validates: Requirements 2.4**

**Property 7: UI state consistency**
*For any* game state change, all UI elements should update to reflect the current state with appropriate instructions and formatting
**Validates: Requirements 2.5, 3.3, 3.5**

**Property 8: Control input feedback**
*For any* valid control input, the system should provide immediate visual confirmation of the action
**Validates: Requirements 3.4**

## Error Handling

### Input Validation
- **Invalid Key Presses**: Ignore unrecognized keyboard inputs during gameplay
- **Rapid Key Presses**: Implement debouncing to prevent state thrashing from rapid inputs
- **State Conflicts**: Ensure state transitions are atomic and cannot be interrupted

### State Management
- **Invalid State Transitions**: Log and recover from impossible state combinations
- **Timer Overflow**: Handle long pause durations without breaking game timing
- **Memory Leaks**: Properly clean up event listeners and timers during state changes

### Visual Rendering
- **Canvas Context Loss**: Gracefully handle canvas rendering failures
- **Animation Interruption**: Ensure visual transitions can be safely interrupted
- **Display Scaling**: Handle different screen sizes and zoom levels

## Testing Strategy

### Unit Testing Approach
The implementation will use Jest for unit testing with the following focus areas:

**State Management Tests:**
- Test individual state transitions (playing → paused, paused → stopped, etc.)
- Test state validation and error recovery
- Test timer management during pause/resume cycles

**Alphabet Progression Tests:**
- Test score threshold detection (multiples of 5)
- Test alphabet sequence advancement and wraparound
- Test visual transition timing and effects

**Control Input Tests:**
- Test keyboard event handling for each control key
- Test state-dependent control behavior
- Test input debouncing and validation

### Property-Based Testing Approach
The implementation will use fast-check for property-based testing with a minimum of 100 iterations per test:

**Property Test Configuration:**
- Each property-based test will run 100+ iterations with randomized inputs
- Tests will use smart generators that create valid game states and score values
- Each test will be tagged with comments referencing the design document properties

**Test Generators:**
- `gameStateGenerator`: Creates valid game state objects
- `scoreGenerator`: Creates score values including multiples of 5
- `keyInputGenerator`: Creates valid keyboard input events
- `alphabetIndexGenerator`: Creates valid alphabet indices with wraparound

**Property Test Implementation:**
- Each correctness property will be implemented as a single property-based test
- Tests will be tagged with format: `**Feature: game-controls-enhancement, Property {number}: {property_text}**`
- Tests will validate universal behaviors across all valid inputs rather than specific examples

### Integration Testing
- **End-to-End Game Flow**: Test complete game sessions with state changes
- **Canvas Rendering**: Test visual output for different states and transitions
- **Performance**: Ensure smooth 60fps gameplay during state transitions

The dual testing approach ensures comprehensive coverage: unit tests catch specific bugs and edge cases, while property tests verify that universal rules hold across all possible inputs and game states.