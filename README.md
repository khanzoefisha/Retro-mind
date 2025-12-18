# Game Project

A simple web-based game built with HTML5 Canvas and JavaScript.

## Getting Started

### Quick Play (One-Click Experience)
1. Open `game-standalone.html` in your web browser
2. The game runs immediately - no dependencies, no setup

### Development Mode
1. Open `index.html` in your web browser
2. The game will start automatically

## Project Structure

```
├── index.html           # Development entry point
├── game.js              # Game source code
├── game-standalone.html # Single-file build output (DEPLOY THIS)
├── README.md            # This file
├── .kiro/               # Kiro configuration directory
└── .gitignore           # Git ignore rules
```

## Build Output

✅ **Single Build Ready**: `game-standalone.html`
- Zero dependencies
- All assets bundled inline
- One-click play experience
- Works offline
- Ready for any static hosting

## Development

This is a basic game template. You can extend it by:
- Adding player controls
- Implementing game mechanics
- Adding sprites and animations
- Creating levels or stages

## Deployment

This project is ready for zero-config deployment on static hosting platforms:

### Option 1: GitHub Pages (Recommended)
1. Push this repository to GitHub
2. Go to repository Settings → Pages
3. Select "Deploy from a branch" → main branch → / (root)
4. Your game will be live at `https://[username].github.io/[repository-name]`

### Option 2: Netlify
1. Visit [netlify.com](https://netlify.com)
2. Drag and drop your project folder to deploy instantly
3. Or connect your GitHub repository for automatic deployments

### Option 3: Vercel
1. Visit [vercel.com](https://vercel.com)
2. Import your GitHub repository
3. Vercel auto-detects this as a static frontend project
4. Deploy with zero configuration

## Files

- `index.html` - Development entry point with canvas setup
- `game.js` - Game source code (development)
- `game-standalone.html` - **Production build** - single file with everything bundled