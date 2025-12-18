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

// AI reasoning variables
let aiThoughts = [];
let frameCount = 0;

// Update game logic
function update() {
    frameCount++;
    
    if (game.aiEnabled) {
        // AI reasoning: Analyze player position
        if (frameCount % 60 === 0) { // Every second
            const centerDistance = Math.sqrt(
                Math.pow(game.player.x - canvas.width/2, 2) + 
                Math.pow(game.player.y - canvas.height/2, 2)
            );
            
            if (centerDistance < 50) {
                aiThoughts.push("Player is centered - optimal position");
            } else {
                aiThoughts.push("Player off-center - suggesting movement");
            }
            
            // Keep only last 3 thoughts
            if (aiThoughts.length > 3) {
                aiThoughts.shift();
            }
            
            console.log('AI Analysis:', aiThoughts[aiThoughts.length - 1]);
        }
        
        // AI-enhanced player movement (subtle animation)
        game.player.x += Math.sin(frameCount * 0.02) * 0.5;
        game.player.y += Math.cos(frameCount * 0.03) * 0.3;
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
    
    // AI indicator and reasoning display
    if (game.aiEnabled) {
        ctx.fillStyle = '#00ff00';
        ctx.font = '16px Arial';
        ctx.fillText('AI: ON', 10, 25);
        
        // Display AI thoughts
        ctx.font = '12px Arial';
        ctx.fillStyle = '#88ff88';
        aiThoughts.forEach((thought, index) => {
            ctx.fillText(`AI: ${thought}`, 10, 50 + (index * 15));
        });
        
        // AI analysis visualization
        ctx.strokeStyle = '#00ff00';
        ctx.setLineDash([5, 5]);
        ctx.beginPath();
        ctx.arc(canvas.width/2, canvas.height/2, 50, 0, 2 * Math.PI);
        ctx.stroke();
        ctx.setLineDash([]);
        
        ctx.fillStyle = '#00ff00';
        ctx.font = '10px Arial';
        ctx.fillText('AI Optimal Zone', canvas.width/2 - 40, canvas.height/2 + 65);
    }
}