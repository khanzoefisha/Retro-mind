# Reset Logic & Edge Case Handling Specification

## Overview
This document defines the exact behavior of the circle touch system, including reset logic, debouncing, and edge case handling.

## Core Rules

### 1. Touch Detection Logic
**What Counts as a Touch:**
- Player must transition from `outside` → `inside` or `boundary`
- Only the moment of entry counts, not staying inside
- Each entry increments the counter by exactly 1

**What Does NOT Count:**
- Staying inside the circle (no continuous counting)
- Moving from `inside` → `boundary` or vice versa
- Any movement that doesn't cross the outside boundary

### 2. Reset Logic Decisions

#### Q: Does leaving the circle reset anything?
**Answer: NO**
- Leaving the circle does NOT reset the touch counter
- Leaving the circle does NOT reset any game state
- The counter is persistent and cumulative
- **Rationale**: Encourages exploration and doesn't punish leaving

#### Q: Does re-entering count again?
**Answer: YES (with debouncing)**
- Every legitimate re-entry counts as a new touch
- Must fully exit (`outside`) before re-entry counts
- Subject to debounce timer to prevent exploitation
- **Rationale**: Rewards deliberate, controlled movement

#### Q: Should rapid re-entries be debounced?
**Answer: YES**
- Debounce period: 30 frames (0.5 seconds at 60fps)
- Prevents rapid oscillation at boundary from inflating counter
- Encourages deliberate, controlled entries
- **Rationale**: Maintains integrity of skill measurement

## Implementation Details

### Debounce System
```javascript
// Debounce configuration
touchDebounceDelay: 30, // frames (0.5 seconds at 60fps)
lastTouchTime: 0,       // frame number of last valid touch

// Debounce check
const timeSinceLastTouch = frameCount - game.lastTouchTime;
const canRegisterTouch = timeSinceLastTouch >= game.touchDebounceDelay;
```

### State Transitions That Count
- `outside` → `inside` ✅ (Valid touch)
- `outside` → `boundary` ✅ (Valid touch)
- `inside` → `outside` → `inside` ✅ (Valid re-entry after debounce)
- `boundary` → `outside` → `boundary` ✅ (Valid re-entry after debounce)

### State Transitions That Don't Count
- `inside` → `boundary` ❌ (Internal movement)
- `boundary` → `inside` ❌ (Internal movement)
- `outside` → `inside` (within debounce period) ❌ (Too rapid)

## Edge Cases Handled

### 1. Rapid Oscillation
**Scenario**: Player rapidly moves in/out at circle boundary
**Handling**: Debounce timer prevents counting until 0.5 seconds elapsed
**Result**: Only deliberate entries count

### 2. Boundary Dancing
**Scenario**: Player stays on boundary line, flickering between states
**Handling**: Only `outside` → `inside/boundary` transitions count
**Result**: Internal boundary movement doesn't inflate counter

### 3. Accidental Exits
**Scenario**: Player accidentally leaves circle briefly
**Handling**: No reset occurs, re-entry counts normally (after debounce)
**Result**: Forgiving system that doesn't punish mistakes

### 4. Intentional Gaming
**Scenario**: Player tries to rapidly exit/enter to boost counter
**Handling**: Debounce timer prevents exploitation
**Result**: System maintains integrity while allowing legitimate play

## Logging & Debugging

### Console Messages
- `🎯 CIRCLE TOUCH EVENT! Count: X (Debounced: Y frames)` - Valid touch
- `⏱️ TOUCH DEBOUNCED: Too rapid (X/30 frames)` - Blocked by debounce
- `Zone Status: outside → inside` - State transition logging

### Visual Feedback
- Touch counter updates immediately on valid touch
- Visual ring expansion effect on successful entry
- "🎯 CIRCLE TOUCHED!" message appears briefly

## Design Philosophy

### Encouraging Exploration
- No penalties for leaving the safe zone
- Counter never decreases
- Mistakes don't reset progress

### Skill Development
- Rewards controlled, deliberate movement
- Prevents exploitation through rapid movement
- Encourages spatial awareness and precision

### User Experience
- Clear, immediate feedback on valid touches
- Forgiving system that doesn't frustrate
- Progressive difficulty through natural skill development

## Testing Scenarios

### Valid Touch Patterns
1. Enter circle → Exit → Wait 0.5s → Re-enter ✅
2. Enter circle → Stay inside → Exit → Re-enter ✅
3. Multiple deliberate entries with proper timing ✅

### Invalid/Debounced Patterns
1. Rapid in/out oscillation at boundary ❌
2. Quick exit/re-entry within 0.5 seconds ❌
3. Boundary line dancing without full exit ❌

## Future Considerations

### Potential Enhancements
- Adjustable debounce timing based on skill level
- Streak bonuses for consecutive clean entries
- Different scoring for different entry speeds
- Advanced patterns recognition

### Metrics to Track
- Average time between touches
- Success rate of entry attempts
- Spatial accuracy of entries
- Learning curve progression

This specification ensures consistent, fair, and engaging touch detection that promotes skill development while preventing exploitation.