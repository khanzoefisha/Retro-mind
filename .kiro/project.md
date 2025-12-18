# Kiro Project Configuration

## Project Overview
- **Type**: Static Web Game
- **Framework**: Vanilla HTML5/CSS/JavaScript
- **Build System**: None (zero-config)
- **Deployment**: Static hosting ready

## File Structure for Kiro
```
├── index.html              # Development entry point
├── game.js                 # Game logic (development)
├── game-standalone.html    # Production build (DEPLOY THIS)
├── .kiro/
│   ├── deployment.md       # Deployment documentation
│   └── project.md          # This configuration file
└── README.md               # Public documentation
```

## Development Workflow
1. **Edit**: Modify `game.js` for game logic changes
2. **Test**: Open `index.html` in browser or use local server
3. **Build**: Update `game-standalone.html` with changes
4. **Deploy**: Upload standalone file to hosting platform

## Kiro Integration Notes
- **No Build Process**: Direct file editing workflow
- **Live Server**: Use Python HTTP server on port 7080
- **Version Control**: All files tracked in git (including .kiro/)
- **Deployment**: Single-file output for maximum compatibility

## Quick Commands
- **Start Local Server**: `python -m http.server 7080`
- **Test Game**: Open http://localhost:7080/index.html
- **Deploy Build**: Upload `game-standalone.html` as `index.html`