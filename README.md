# Pacman Smash 🎮

A competitive two-player Pacman game with AI-driven dynamic elements built with Python and Pygame.

## 🎯 Game Overview

Pacman Smash is an innovative twist on the classic Pacman game featuring:
- **Two-player competitive gameplay** - Race against your friend to collect the most pellets
- **Intelligent AI system** - Dynamic difficulty balancing that keeps games exciting
- **Power-ups and chaos** - Special abilities and random maze modifications
- **Real-time performance tracking** - AI monitors player performance and adjusts accordingly

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/khanzoefisha/Retro-mind.git
   cd Retro-mind
   ```

2. **Install dependencies:**
   ```bash
   cd pacman_smash
   pip install -r requirements.txt
   ```

3. **Run the game:**
   ```bash
   python main.py
   ```

## 🕹️ How to Play

### Controls
- **Player 1 (Blue):** W/A/S/D keys
- **Player 2 (Red):** Arrow keys (↑/←/↓/→)
- **ESC:** Quit game

### Objective
Collect more pellets than your opponent while avoiding AI-controlled ghosts!

### Game Elements
- **🟡 Pellets:** Collect for +10 points each
- **🎁 Power-ups:** Special abilities (speed boost, freeze opponent, ghost confusion)
- **👻 Ghosts:** AI enemies that reduce your score and respawn you if they catch you
- **🧱 Maze:** Dynamic environment that can change during gameplay

## 🤖 AI Features

### Dynamic Difficulty Balancing
- Ghosts target the winning player more aggressively
- Power-ups spawn more frequently near losing players
- Keeps games competitive and engaging

### Chaos Mode
- Random wall removal and maze modifications
- Temporary environmental changes
- Creates new strategic opportunities

## 🏗️ Project Structure

```
pacman_smash/
├── main.py              # Main game engine and entry point
├── player.py            # Player mechanics and controls
├── ghost_ai.py          # Ghost AI behavior system
├── maze.py              # Maze generation and management
├── ai_controller.py     # Dynamic difficulty AI controller
├── requirements.txt     # Python dependencies
└── test_*.py           # Test suite files
```

## 🧪 Testing

Run the test suite to verify everything works:

```bash
cd pacman_smash
python -m pytest . -v
```

Test game functionality:
```bash
python test_game_run.py
```

## 📋 Features

### ✅ Implemented
- Two-player competitive gameplay
- Player movement and controls (WASD + Arrow keys)
- Ghost AI with multiple behavior patterns
- Pellet collection and scoring system
- Power-up system (speed boost, freeze, ghost confusion)
- Dynamic maze generation
- Performance tracking and metrics
- Real-time UI with scores and game messages
- Comprehensive test suite (29 tests)

### 🚧 Planned Features
- Chaos mode with dynamic maze modifications
- Advanced AI controller with performance balancing
- Enhanced power-up system
- Audio system integration
- Match timer and end-game conditions

## 🎮 Game Mechanics

### Movement System
- Movement cooldown prevents spam (0.15 seconds between moves)
- Speed can be modified by power-ups
- Wall collision detection
- Smooth, responsive controls

### AI System
- Ghosts use pathfinding to navigate the maze
- Multiple behavior states (chase, random, confused)
- Anti-clustering coordination between ghosts
- Adaptive targeting based on player performance

### Scoring System
- Pellets: +10 points each
- Ghost collision: -50 points and respawn
- Performance metrics tracked for AI balancing

## 🛠️ Development

### Built With
- **Python 3.13** - Core language
- **Pygame 2.6** - Graphics and game engine
- **Pytest** - Testing framework
- **Hypothesis** - Property-based testing (planned)

### Architecture
The game follows a component-based architecture with clear separation of concerns:
- Game Engine coordinates all systems
- Player management handles input and state
- Ghost AI manages enemy behavior
- Maze system handles environment and collisions
- AI Controller provides dynamic balancing

## 📖 Specification Documents

This project was built using a formal specification-driven development process:
- **Requirements:** `.kiro/specs/pacman-smash/requirements.md`
- **Design:** `.kiro/specs/pacman-smash/design.md`
- **Tasks:** `.kiro/specs/pacman-smash/tasks.md`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🎉 Acknowledgments

- Built with the Kiro AI development environment
- Inspired by classic Pacman gameplay
- Uses modern AI techniques for dynamic difficulty balancing

---

**Ready to play?** Run `python main.py` and start competing! 🎮