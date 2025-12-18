// Landing Experience Controller
const landingScreen = document.getElementById('landingScreen');
const gameContainer = document.getElementById('gameContainer');
const startButton = document.getElementById('startButton');
const backButton = document.getElementById('backButton');
const aiToggle = document.getElementById('aiToggle');

// Game elements
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// Error handling for canvas context
if (!ctx) {
    console.error('Canvas 2D context not supported');
    if (landingScreen) {
        landingScreen.innerHTML = '<p style="color: white; text-align: center;">Canvas not supported in this browser</p>';
    }
}

// Game state
const game = {
    running: false,
    aiEnabled: true,
    player: {
        x: canvas.width / 2,
        y: canvas.height / 2,
        size: 20,
        color: '#00ff00'
    }
};

// Landing screen controls
if (startButton) startButton.addEventListener('click', startGame);
if (backButton) backButton.addEventListener('click', showLanding);
if (aiToggle) aiToggle.addEventListener('change', toggleAI);

function startGame() {
    if (landingScreen) landingScreen.style.display = 'none';
    if (gameContainer) gameContainer.style.display = 'block';
    initGame();
}

function showLanding() {
    if (gameContainer) gameContainer.style.display = 'none';
    if (landingScreen) landingScreen.style.display = 'block';
    game.running = false;
}

function toggleAI() {
    game.aiEnabled = aiToggle.checked;
    console.log('AI Features:', game.aiEnabled ? 'Enabled' : 'Disabled');
}

// Initialize game
function initGame() {
    try {
        game.running = true;
        gameLoop();
        console.log('Game initialized successfully');
        if (game.aiEnabled) {
            console.log('AI features are active');
        }
    } catch (error) {
        console.error('Game initialization failed:', error);
    }
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
    if (game.aiEnabled) {
        // AI-enhanced features could go here
    }
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
    
    // AI indicator
    if (game.aiEnabled) {
        ctx.fillStyle = '#00ff00';
        ctx.font = '16px Arial';
        ctx.fillText('AI: ON', 10, 25);
    }
}