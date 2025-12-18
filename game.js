// Game source file
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Game state
const game = {
    running: false,
    player: {
        x: canvas.width / 2,
        y: canvas.height / 2,
        size: 20,
        color: '#00ff00'
    }
};

// Initialize game
function init() {
    game.running = true;
    gameLoop();
}

// Main game loop
function gameLoop() {
    if (!game.running) return;
    
    update();
    render();
    
    requestAnimationFrame(gameLoop);
}

// Update game logic
function update() {
    // Game logic goes here
}

// Render game
function render() {
    // Clear canvas
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw player
    ctx.fillStyle = game.player.color;
    ctx.fillRect(
        game.player.x - game.player.size / 2,
        game.player.y - game.player.size / 2,
        game.player.size,
        game.player.size
    );
}

// Start the game
init();