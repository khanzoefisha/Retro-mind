# Kiro Project Documentation Index

## Project Overview
This HTML5 Canvas game demonstrates user-controlled movement with AI coaching, designed to teach reaction time, precision, and spatial awareness skills.

## Documentation Files

### 📚 Educational Design
- **[educational-summary.md](./educational-summary.md)** - Quick overview of learning objectives
- **[game-design-documentation.md](./game-design-documentation.md)** - Comprehensive educational framework

### 🔧 Technical Specifications
- **[reset-logic-specification.md](./reset-logic-specification.md)** - Touch detection and edge case handling
- **[project.md](./project.md)** - Kiro project configuration
- **[deployment.md](./deployment.md)** - Complete deployment guide

### 🚀 Deployment & Testing
- **[deployment-links.md](./deployment-links.md)** - Live URLs and repository links
- **[validation-checklist.md](./validation-checklist.md)** - Post-deployment testing guide
- **[recording-guide.md](./recording-guide.md)** - Screen recording instructions

### 🎯 Development Guidelines
- **[steering/game-development.md](./steering/game-development.md)** - Active development guidelines

## Quick Reference

### Game Mechanics
- **Control**: WASD or Arrow Keys move the neon square
- **Objective**: Enter the green circle to increment touch counter
- **AI Coach**: Provides real-time guidance and warnings
- **Danger Zones**: Visual warnings when approaching risky areas

### Educational Goals
- **Reaction Skills**: Quick response to visual danger warnings
- **Precision Skills**: Accurate positioning and controlled movement
- **Cognitive Skills**: Pattern recognition and strategic planning
- **Spatial Awareness**: Boundary recognition and risk assessment

### Technical Features
- **Zero Dependencies**: Pure HTML5/CSS/JavaScript
- **Cross-Platform**: Works on desktop and mobile browsers
- **60fps Performance**: Smooth, responsive gameplay
- **Debounced Touch Detection**: Prevents exploitation while maintaining fairness

## Development Workflow
1. **Edit**: Modify `game.js` for game logic changes
2. **Test**: Use `python -m http.server 8000` for local testing
3. **Build**: Update `game-standalone.html` with changes
4. **Deploy**: Upload to GitHub Pages or static hosting

## Live Demo
- **Repository**: https://github.com/khanzoefisha/Retro-mind
- **Live Game**: https://khanzoefisha.github.io/Retro-mind

This project follows zero-config deployment principles and serves as a complete example of educational game development with AI coaching integration.