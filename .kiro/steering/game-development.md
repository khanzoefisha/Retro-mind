# Game Development Guidelines

## Project Context
This is a static web game built with vanilla HTML5 Canvas and JavaScript. The project follows a zero-config approach for maximum deployment simplicity.

## Development Standards
- **No External Dependencies**: Keep everything self-contained
- **Single File Build**: Maintain `game-standalone.html` as production build
- **Canvas-Based**: Use HTML5 Canvas for all rendering
- **ES6+ JavaScript**: Modern JavaScript features are acceptable
- **Responsive Design**: Consider different screen sizes

## File Management
- **Development Files**: `index.html` + `game.js` for modular development
- **Production Build**: `game-standalone.html` with everything inlined
- **Assets**: Embed all assets (CSS, JS) inline for portability
- **No Build Tools**: Avoid webpack, rollup, or other bundlers

## Deployment Requirements
- **Static Hosting**: Must work on any static file hosting
- **Zero Config**: No server configuration required
- **Offline Capable**: Should work without internet connection
- **Cross-Browser**: Support modern browsers (Chrome, Firefox, Safari, Edge)

## Code Quality
- **Clean Code**: Readable, well-commented JavaScript
- **Error Handling**: Graceful handling of edge cases
- **Performance**: Optimize for smooth 60fps gameplay
- **Accessibility**: Basic keyboard navigation support

## Testing Approach
- **Local Testing**: Use Python HTTP server on port 7080
- **Browser Testing**: Test in multiple browsers
- **Mobile Testing**: Verify basic mobile compatibility
- **Production Testing**: Always test the standalone build before deployment