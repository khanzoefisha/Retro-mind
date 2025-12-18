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
    score: 0,
    player: {
        x: canvas.width / 2,
        y: canvas.height / 2,
        size: 20,
        color: '#00ff00',
        speed: 5
    },
    target: {
        x: Math.random() * (canvas.width - 40) + 20,
        y: Math.random() * (canvas.height - 40) + 20,
        size: 15,
        color: '#00ff00'
    },
    safeZone: {
        x: canvas.width / 2,
        y: canvas.height / 2,
        radius: 100,
        color: 'rgba(0, 255, 0, 0.2)',
        borderColor: '#00ff00'
    },
    zoneStatus: 'outside', // 'inside', 'outside', 'boundary'
    previousZoneStatus: 'outside', // Track previous state for entry detection
    dangerZone: {
        active: false,
        flashTimer: 0,
        flashDuration: 120, // frames (2 seconds at 60fps)
        warningText: '',
        distanceThreshold: 150 // pixels from safe zone center
    },
    touchCounter: 0, // Count circle touches
    keys: {
        up: false,
        down: false,
        left: false,
        right: false
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
        setupControls();
        gameLoop();
        console.log('Game initialized successfully');
        if (game.aiEnabled) {
            console.log('AI Coach is active - providing guidance');
        }
    } catch (error) {
        console.error('Game initialization failed:', error);
    }
}

// Setup keyboard controls
function setupControls() {
    document.addEventListener('keydown', (e) => {
        switch(e.key.toLowerCase()) {
            case 'arrowup':
            case 'w':
                game.keys.up = true;
                e.preventDefault();
                break;
            case 'arrowdown':
            case 's':
                game.keys.down = true;
                e.preventDefault();
                break;
            case 'arrowleft':
            case 'a':
                game.keys.left = true;
                e.preventDefault();
                break;
            case 'arrowright':
            case 'd':
                game.keys.right = true;
                e.preventDefault();
                break;
        }
    });

    document.addEventListener('keyup', (e) => {
        switch(e.key.toLowerCase()) {
            case 'arrowup':
            case 'w':
                game.keys.up = false;
                break;
            case 'arrowdown':
            case 's':
                game.keys.down = false;
                break;
            case 'arrowleft':
            case 'a':
                game.keys.left = false;
                break;
            case 'arrowright':
            case 'd':
                game.keys.right = false;
                break;
        }
    });
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
    
    // Handle player movement
    if (game.keys.up && game.player.y > game.player.size/2) {
        game.player.y -= game.player.speed;
    }
    if (game.keys.down && game.player.y < canvas.height - game.player.size/2) {
        game.player.y += game.player.speed;
    }
    if (game.keys.left && game.player.x > game.player.size/2) {
        game.player.x -= game.player.speed;
    }
    if (game.keys.right && game.player.x < canvas.width - game.player.size/2) {
        game.player.x += game.player.speed;
    }
    
    // Update Safe Zone status
    updateSafeZoneStatus();
    
    // Check collision with target (green circle)
    const distanceToTarget = Math.sqrt(
        Math.pow(game.player.x - game.target.x, 2) + 
        Math.pow(game.player.y - game.target.y, 2)
    );
    
    if (distanceToTarget < (game.player.size/2 + game.target.size/2)) {
        game.score++;
        // Spawn new target
        game.target.x = Math.random() * (canvas.width - 40) + 20;
        game.target.y = Math.random() * (canvas.height - 40) + 20;
        console.log('Target hit! Score:', game.score);
    }
    
    // Update touch feedback timer
    if (game.touchFeedback && game.touchFeedback.active) {
        game.touchFeedback.timer--;
        if (game.touchFeedback.timer <= 0) {
            game.touchFeedback.active = false;
        }
    }
    
    // AI Coach Analysis
    if (game.aiEnabled && frameCount % 60 === 0) { // Every second
        aiCoachAnalysis();
    }
}

// Safe Zone collision detection system with touch event detection
function updateSafeZoneStatus() {
    const distanceToCenter = Math.sqrt(
        Math.pow(game.player.x - game.safeZone.x, 2) + 
        Math.pow(game.player.y - game.safeZone.y, 2)
    );
    
    const boundaryThreshold = 5; // Pixels for boundary detection
    
    // Store previous status for entry detection
    game.previousZoneStatus = game.zoneStatus;
    
    // Define zone regions
    if (distanceToCenter <= game.safeZone.radius - boundaryThreshold) {
        game.zoneStatus = 'inside';
        game.dangerZone.active = false; // Safe zone = no danger
    } else if (distanceToCenter >= game.safeZone.radius + boundaryThreshold) {
        game.zoneStatus = 'outside';
        
        // Trigger danger zone if exceeding distance threshold
        if (distanceToCenter > game.dangerZone.distanceThreshold) {
            triggerDangerZone("⚠️ Danger Zone: You're leaving the optimal area");
        }
    } else {
        game.zoneStatus = 'boundary';
        game.dangerZone.active = false; // Boundary is still acceptable
    }
    
    // CIRCLE TOUCH EVENT DETECTION
    // Count only when entering the circle (inside or boundary), not while staying
    const isEnteringCircle = (
        (game.previousZoneStatus === 'outside') && 
        (game.zoneStatus === 'inside' || game.zoneStatus === 'boundary')
    );
    
    if (isEnteringCircle) {
        game.touchCounter++;
        console.log(`🎯 CIRCLE TOUCH EVENT! Count: ${game.touchCounter}`);
        
        // Visual feedback for touch event
        triggerTouchFeedback();
    }
    
    // Update danger zone flash timer
    if (game.dangerZone.flashTimer > 0) {
        game.dangerZone.flashTimer--;
        if (game.dangerZone.flashTimer <= 0) {
            game.dangerZone.active = false;
        }
    }
    
    // Log zone transitions
    if (game.previousZoneStatus !== game.zoneStatus) {
        console.log(`Zone Status: ${game.previousZoneStatus} → ${game.zoneStatus}`);
        
        // Trigger zone-specific events
        switch(game.zoneStatus) {
            case 'inside':
                console.log('✅ Entered Safe Zone - Well done!');
                break;
            case 'outside':
                console.log('⚠️ Left Safe Zone - Return for safety!');
                break;
            case 'boundary':
                console.log('🎯 On Safe Zone boundary - Careful positioning!');
                break;
        }
    }
}

// Visual feedback for successful circle touch
function triggerTouchFeedback() {
    // Add a brief visual effect for successful touch
    game.touchFeedback = {
        active: true,
        timer: 30, // 0.5 seconds at 60fps
        scale: 1.5
    };
}

// Trigger danger zone warning with visual feedback
function triggerDangerZone(warningMessage) {
    if (!game.dangerZone.active) { // Only trigger if not already active
        game.dangerZone.active = true;
        game.dangerZone.flashTimer = game.dangerZone.flashDuration;
        game.dangerZone.warningText = warningMessage;
        console.log('🚨 DANGER ZONE ACTIVATED:', warningMessage);
    }
}

// AI Coach provides guidance
function aiCoachAnalysis() {
    const edgeThreshold = 50;
    const screenDangerZones = [];
    
    // Check for screen edge danger zones
    if (game.player.x < edgeThreshold) screenDangerZones.push("left edge");
    if (game.player.x > canvas.width - edgeThreshold) screenDangerZones.push("right edge");
    if (game.player.y < edgeThreshold) screenDangerZones.push("top edge");
    if (game.player.y > canvas.height - edgeThreshold) screenDangerZones.push("bottom edge");
    
    // Distance to target
    const distanceToTarget = Math.sqrt(
        Math.pow(game.player.x - game.target.x, 2) + 
        Math.pow(game.player.y - game.target.y, 2)
    );
    
    // Distance from safe zone center
    const distanceFromSafeZone = Math.sqrt(
        Math.pow(game.player.x - game.safeZone.x, 2) + 
        Math.pow(game.player.y - game.safeZone.y, 2)
    );
    
    let coachMessage = "";
    
    // Priority 1: Active danger zone (highest priority)
    if (game.dangerZone.active) {
        coachMessage = game.dangerZone.warningText;
    }
    // Priority 2: Screen edge danger zones
    else if (screenDangerZones.length > 0) {
        coachMessage = `⚠️ SCREEN EDGE: Near ${screenDangerZones.join(", ")}`;
        // Also trigger danger zone for screen edges
        triggerDangerZone(`⚠️ Danger Zone: Too close to ${screenDangerZones.join(", ")}`);
    }
    // Priority 3: Safe Zone status with distance feedback
    else if (game.zoneStatus === 'inside') {
        coachMessage = "✅ SAFE ZONE: Perfect positioning!";
    } else if (game.zoneStatus === 'boundary') {
        coachMessage = "🎯 SAFE ZONE EDGE: Stay centered for safety";
    } else if (game.zoneStatus === 'outside') {
        const distanceText = Math.round(distanceFromSafeZone - game.safeZone.radius);
        coachMessage = `🏃 OUTSIDE SAFE ZONE: ${distanceText}px away - return!`;
    }
    // Priority 4: Target guidance
    else if (distanceToTarget < 100) {
        coachMessage = "🎯 Close to target - good positioning!";
    } else if (distanceToTarget > 200) {
        coachMessage = "🏃 Target is far - move closer";
    } else {
        coachMessage = "✅ Good position - keep moving";
    }
    
    aiThoughts.push(coachMessage);
    
    // Keep only last 3 thoughts
    if (aiThoughts.length > 3) {
        aiThoughts.shift();
    }
    
    console.log('AI Coach:', coachMessage);
}

// Render game
function render() {
    // Clear canvas
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw Safe Zone (green circle) - Always visible
    ctx.fillStyle = game.safeZone.color;
    ctx.beginPath();
    ctx.arc(game.safeZone.x, game.safeZone.y, game.safeZone.radius, 0, 2 * Math.PI);
    ctx.fill();
    
    // Draw Safe Zone border with touch feedback effect
    ctx.strokeStyle = game.safeZone.borderColor;
    ctx.lineWidth = 2;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.arc(game.safeZone.x, game.safeZone.y, game.safeZone.radius, 0, 2 * Math.PI);
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Touch feedback visual effect
    if (game.touchFeedback && game.touchFeedback.active) {
        const progress = 1 - (game.touchFeedback.timer / 30);
        const alpha = 1 - progress;
        const scale = 1 + (progress * 0.5);
        
        ctx.strokeStyle = `rgba(0, 255, 255, ${alpha})`;
        ctx.lineWidth = 4;
        ctx.beginPath();
        ctx.arc(game.safeZone.x, game.safeZone.y, game.safeZone.radius * scale, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Touch success text
        ctx.fillStyle = `rgba(0, 255, 255, ${alpha})`;
        ctx.font = 'bold 20px Arial';
        const touchText = '🎯 CIRCLE TOUCHED!';
        const textWidth = ctx.measureText(touchText).width;
        ctx.fillText(touchText, (canvas.width - textWidth) / 2, game.safeZone.y - 50);
    }
    
    // Draw danger zones (red areas near edges)
    if (game.aiEnabled) {
        ctx.fillStyle = 'rgba(255, 0, 0, 0.1)';
        const dangerZone = 50;
        // Top danger zone
        ctx.fillRect(0, 0, canvas.width, dangerZone);
        // Bottom danger zone
        ctx.fillRect(0, canvas.height - dangerZone, canvas.width, dangerZone);
        // Left danger zone
        ctx.fillRect(0, 0, dangerZone, canvas.height);
        // Right danger zone
        ctx.fillRect(canvas.width - dangerZone, 0, dangerZone, canvas.height);
    }
    
    // Draw target (small green circle to collect)
    ctx.fillStyle = game.target.color;
    ctx.beginPath();
    ctx.arc(game.target.x, game.target.y, game.target.size, 0, 2 * Math.PI);
    ctx.fill();
    
    // Draw player (neon square) with zone-based coloring and danger effects
    let playerColor = game.player.color;
    let outlineColor = null;
    
    if (game.dangerZone.active) {
        // Flashing red when in danger zone
        const flashIntensity = Math.sin(frameCount * 0.3) * 0.5 + 0.5;
        playerColor = `rgb(${255}, ${Math.floor(100 * flashIntensity)}, 0)`;
        outlineColor = '#ff0000'; // Red outline in danger
    } else if (game.zoneStatus === 'inside') {
        playerColor = '#00ff00'; // Bright green when safe
        outlineColor = '#00cc00'; // Darker green outline
    } else if (game.zoneStatus === 'boundary') {
        playerColor = '#ffff00'; // Yellow on boundary
        outlineColor = '#cccc00'; // Darker yellow outline
    } else {
        playerColor = '#ff6600'; // Orange when outside
        outlineColor = '#cc4400'; // Darker orange outline
    }
    
    // Draw player square
    ctx.fillStyle = playerColor;
    ctx.fillRect(
        game.player.x - game.player.size / 2,
        game.player.y - game.player.size / 2,
        game.player.size,
        game.player.size
    );
    
    // Draw outline for danger zone or status indication
    if (outlineColor) {
        ctx.strokeStyle = outlineColor;
        ctx.lineWidth = game.dangerZone.active ? 3 : 2;
        ctx.strokeRect(
            game.player.x - game.player.size / 2,
            game.player.y - game.player.size / 2,
            game.player.size,
            game.player.size
        );
    }
    
    // Draw UI
    ctx.fillStyle = '#00ff00';
    ctx.font = '20px Arial';
    ctx.fillText(`Score: ${game.score}`, canvas.width - 120, 30);
    
    // Touch Counter Display (prominent)
    ctx.fillStyle = '#00ffff';
    ctx.font = 'bold 24px Arial';
    ctx.fillText(`Touches: ${game.touchCounter}`, canvas.width - 180, 60);
    
    // Zone Status Display
    ctx.fillStyle = '#ffffff';
    ctx.font = '16px Arial';
    ctx.fillText(`Zone: ${game.zoneStatus.toUpperCase()}`, canvas.width - 150, 85);
    
    // Danger Zone Warning Display (highest priority)
    if (game.dangerZone.active) {
        const flashAlpha = Math.sin(frameCount * 0.4) * 0.5 + 0.5;
        ctx.fillStyle = `rgba(255, 0, 0, ${flashAlpha})`;
        ctx.font = 'bold 24px Arial';
        
        // Center the warning text
        const warningText = game.dangerZone.warningText;
        const textWidth = ctx.measureText(warningText).width;
        ctx.fillText(warningText, (canvas.width - textWidth) / 2, 100);
        
        // Add warning background
        ctx.fillStyle = `rgba(255, 0, 0, ${flashAlpha * 0.3})`;
        ctx.fillRect((canvas.width - textWidth) / 2 - 10, 75, textWidth + 20, 35);
    }
    
    // AI Coach display
    if (game.aiEnabled) {
        ctx.fillStyle = '#00ff00';
        ctx.font = '16px Arial';
        ctx.fillText('AI Coach: ON', 10, 25);
        
        // Display AI coaching thoughts
        ctx.font = '12px Arial';
        ctx.fillStyle = '#88ff88';
        aiThoughts.forEach((thought, index) => {
            ctx.fillText(thought, 10, 50 + (index * 15));
        });
    }
    
    // Controls instruction
    ctx.fillStyle = '#666';
    ctx.font = '12px Arial';
    ctx.fillText('Use WASD or Arrow Keys to move', 10, canvas.height - 25);
    ctx.fillText('Stay in the green Safe Zone!', 10, canvas.height - 10);
}