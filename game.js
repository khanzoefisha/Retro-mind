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
    lastTouchTime: 0, // Debounce rapid entries
    touchDebounceDelay: 30, // frames (0.5 seconds at 60fps)
    alphabetPrompt: {
        currentLetter: 'A',
        changeTimer: 0,
        changeInterval: 180, // 3 seconds at 60fps
        letters: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('')
    },
    speechRecognition: {
        isListening: false,
        recognition: null,
        lastHeardLetter: '',
        isInCircle: false,
        waitingForSpeech: false,
        timeoutTimer: 0,
        timeoutDuration: 300, // 5 seconds at 60fps to say the letter
        attemptProcessed: false, // Lock to prevent repeated triggers
        mustExitAndReenter: false // Flag requiring exit/re-entry
    },
    successCount: 0, // Count successful letter + touch combinations
    gameOver: {
        active: false,
        reason: '',
        finalScore: 0,
        finalSuccesses: 0
    },
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
    
    // Reset game over state
    game.gameOver.active = false;
    game.gameOver.reason = '';
    game.gameOver.finalScore = 0;
    game.gameOver.finalSuccesses = 0;
}

function restartGame() {
    // Reset all game state
    game.score = 0;
    game.successCount = 0;
    game.touchCounter = 0;
    game.player.x = canvas.width / 2;
    game.player.y = canvas.height / 2;
    game.safeZone.x = canvas.width / 2;
    game.safeZone.y = canvas.height / 2;
    game.target.x = Math.random() * (canvas.width - 40) + 20;
    game.target.y = Math.random() * (canvas.height - 40) + 20;
    game.alphabetPrompt.currentLetter = 'A';
    game.alphabetPrompt.changeTimer = 0;
    game.zoneStatus = 'outside';
    game.previousZoneStatus = 'outside';
    game.dangerZone.active = false;
    game.dangerZone.flashTimer = 0;
    game.speechRecognition.isInCircle = false;
    game.speechRecognition.waitingForSpeech = false;
    game.speechRecognition.attemptProcessed = false;
    game.speechRecognition.mustExitAndReenter = false;
    game.speechRecognition.lastHeardLetter = '';
    game.speechRecognition.timeoutTimer = 0;
    
    // Reset game over state
    game.gameOver.active = false;
    game.gameOver.reason = '';
    game.gameOver.finalScore = 0;
    game.gameOver.finalSuccesses = 0;
    
    // Restart the game
    game.running = true;
    
    // Restart speech recognition if it was active
    if (game.speechRecognition.recognition) {
        try {
            game.speechRecognition.recognition.stop();
        } catch (e) {
            // Ignore errors when stopping
        }
        setTimeout(() => {
            setupSpeechRecognition();
        }, 100);
    }
    
    gameLoop(); // Restart the game loop
    console.log('🔄 Game restarted');
    
    // Brief visual feedback
    setTimeout(() => {
        console.log('✅ Game restart complete');
    }, 100);
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
        setupSpeechRecognition();
        gameLoop();
        console.log('Game initialized successfully');
        if (game.aiEnabled) {
            console.log('AI Coach is active - providing guidance');
        }
    } catch (error) {
        console.error('Game initialization failed:', error);
    }
}

// Setup speech recognition for alphabet prompts
function setupSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        game.speechRecognition.recognition = new SpeechRecognition();
        
        game.speechRecognition.recognition.continuous = true;
        game.speechRecognition.recognition.interimResults = false;
        game.speechRecognition.recognition.lang = 'en-US';
        
        game.speechRecognition.recognition.onresult = function(event) {
            const lastResult = event.results[event.results.length - 1];
            if (lastResult.isFinal) {
                const spokenText = lastResult[0].transcript.trim().toUpperCase();
                handleSpeechResult(spokenText);
            }
        };
        
        game.speechRecognition.recognition.onerror = function(event) {
            console.log('Speech recognition error:', event.error);
            game.speechRecognition.isListening = false;
        };
        
        game.speechRecognition.recognition.onstart = function() {
            game.speechRecognition.isListening = true;
            console.log('🎤 Speech recognition started - listening...');
        };
        
        game.speechRecognition.recognition.onend = function() {
            game.speechRecognition.isListening = false;
            console.log('🎤 Speech recognition ended - restarting...');
            // Restart recognition to keep listening
            if (game.running) {
                setTimeout(() => {
                    try {
                        game.speechRecognition.recognition.start();
                    } catch (e) {
                        console.log('Speech recognition restart failed:', e);
                    }
                }, 100);
            }
        };
        
        // Start listening
        game.speechRecognition.recognition.start();
        console.log('🎤 Speech recognition activated - say letters out loud!');
    } else {
        console.log('⚠️ Speech recognition not supported in this browser');
    }
}

// Handle speech recognition results with child-friendly matching
function handleSpeechResult(spokenText) {
    console.log(`🎤 Heard: "${spokenText}"`);
    
    // Enhanced letter extraction with child-friendly rules
    const detectedLetter = extractSingleLetter(spokenText);
    if (detectedLetter) {
        game.speechRecognition.lastHeardLetter = detectedLetter;
        console.log(`📝 Detected letter: ${game.speechRecognition.lastHeardLetter}`);
        
        // Check if player is in circle and said the correct letter
        checkLetterMatch();
    } else {
        console.log(`❌ No clear single letter detected in: "${spokenText}"`);
    }
}

// Child-friendly letter extraction with robust matching rules
function extractSingleLetter(spokenText) {
    // Convert to uppercase for case-insensitive matching
    const upperText = spokenText.toUpperCase();
    
    // Common letter pronunciations and variations
    const letterMappings = {
        'A': ['A', 'AY', 'EH'],
        'B': ['B', 'BE', 'BEE'],
        'C': ['C', 'SEE', 'CEE'],
        'D': ['D', 'DEE'],
        'E': ['E', 'EE'],
        'F': ['F', 'EF', 'EFF'],
        'G': ['G', 'GEE', 'JEE'],
        'H': ['H', 'AITCH', 'HAITCH'],
        'I': ['I', 'EYE'],
        'J': ['J', 'JAY'],
        'K': ['K', 'KAY'],
        'L': ['L', 'EL', 'ELL'],
        'M': ['M', 'EM'],
        'N': ['N', 'EN'],
        'O': ['O', 'OH'],
        'P': ['P', 'PEE'],
        'Q': ['Q', 'CUE', 'QUEUE'],
        'R': ['R', 'AR', 'ARE'],
        'S': ['S', 'ES', 'ESS'],
        'T': ['T', 'TEE'],
        'U': ['U', 'YOU'],
        'V': ['V', 'VEE'],
        'W': ['W', 'DOUBLE U', 'DOUBLE YOU'],
        'X': ['X', 'EX'],
        'Y': ['Y', 'WHY'],
        'Z': ['Z', 'ZED', 'ZEE']
    };
    
    // First, try exact single letter match (most common)
    const singleLetters = upperText.match(/\b[A-Z]\b/g);
    if (singleLetters && singleLetters.length === 1) {
        return singleLetters[0];
    }
    
    // Then try letter name pronunciations
    for (const [letter, pronunciations] of Object.entries(letterMappings)) {
        for (const pronunciation of pronunciations) {
            if (upperText.includes(pronunciation)) {
                // Make sure it's not part of a larger word
                const regex = new RegExp(`\\b${pronunciation}\\b`);
                if (regex.test(upperText)) {
                    return letter;
                }
            }
        }
    }
    
    // Fallback: extract any single letter from the text
    const anyLetters = upperText.match(/[A-Z]/g);
    if (anyLetters && anyLetters.length === 1) {
        return anyLetters[0];
    }
    
    // If multiple letters found, prioritize the current target letter
    if (anyLetters && anyLetters.length > 1) {
        const currentTarget = game.alphabetPrompt.currentLetter;
        if (anyLetters.includes(currentTarget)) {
            console.log(`🎯 Found target letter "${currentTarget}" among multiple letters`);
            return currentTarget;
        }
        // Otherwise, take the first letter
        return anyLetters[0];
    }
    
    return null; // No clear letter found
}

// Check if spoken letter matches current prompt while in circle
function checkLetterMatch() {
    const heardLetter = game.speechRecognition.lastHeardLetter;
    const targetLetter = game.alphabetPrompt.currentLetter;
    
    // STEP 2.6: Check lock condition - prevent repeated triggers
    if (game.speechRecognition.attemptProcessed) {
        console.log(`🔒 Attempt already processed - ignoring speech until exit/re-entry`);
        return;
    }
    
    // Case-insensitive comparison (child-friendly)
    if (game.speechRecognition.isInCircle && 
        heardLetter.toUpperCase() === targetLetter.toUpperCase()) {
        
        // SUCCESS! Execute complete success sequence
        executeSuccessPath(heardLetter, targetLetter);
        
        // Reset speech state
        game.speechRecognition.lastHeardLetter = '';
        game.speechRecognition.waitingForSpeech = false;
    } else if (game.speechRecognition.isInCircle && heardLetter) {
        // Wrong letter - execute failure path
        executeFailurePath('wrong_letter', heardLetter, targetLetter);
    }
}

// Complete success path execution
function executeSuccessPath(heardLetter, targetLetter) {
    // 1. Score +5
    game.score += 5;
    
    // 2. Touch counter +1 (success count)
    game.successCount++;
    game.touchCounter++; // Also increment basic touch counter
    
    // 3. Change alphabet to new random letter (not sequential)
    const availableLetters = game.alphabetPrompt.letters.filter(letter => letter !== targetLetter);
    const randomIndex = Math.floor(Math.random() * availableLetters.length);
    game.alphabetPrompt.currentLetter = availableLetters[randomIndex];
    game.alphabetPrompt.changeTimer = 0; // Reset timer
    
    // 4. Relocate green circle to new random position (inside black area)
    relocateGreenCircle();
    
    // 5. AI feedback with celebration
    const celebrationMessages = [
        "Great job! You said it correctly 🎉",
        "Perfect! Excellent pronunciation 🎉",
        "Amazing! You nailed that letter 🎉",
        "Wonderful! Keep up the great work 🎉",
        "Outstanding! Letter mastery achieved 🎉"
    ];
    const randomMessage = celebrationMessages[Math.floor(Math.random() * celebrationMessages.length)];
    aiThoughts.push(randomMessage);
    
    console.log(`🎉 SUCCESS! "${heardLetter}" = "${targetLetter}" | +5 points | New letter: ${game.alphabetPrompt.currentLetter}`);
    
    // 6. Trigger special success feedback
    triggerLetterSuccessFeedback();
    
    // 7. Reset speech state for next challenge
    game.speechRecognition.lastHeardLetter = '';
    game.speechRecognition.isInCircle = false;
    game.speechRecognition.waitingForSpeech = false;
    game.speechRecognition.attemptProcessed = true; // Lock further attempts
    game.speechRecognition.mustExitAndReenter = false; // Success allows immediate new attempts
}

// Relocate green circle to new random position
function relocateGreenCircle() {
    // Ensure circle stays within canvas bounds with margin
    const margin = game.safeZone.radius + 20;
    const minX = margin;
    const maxX = canvas.width - margin;
    const minY = margin + 100; // Extra margin from top for alphabet display
    const maxY = canvas.height - margin - 50; // Extra margin from bottom for controls
    
    // Generate new random position
    game.safeZone.x = Math.random() * (maxX - minX) + minX;
    game.safeZone.y = Math.random() * (maxY - minY) + minY;
    
    console.log(`🎯 Green circle relocated to (${Math.round(game.safeZone.x)}, ${Math.round(game.safeZone.y)})`);
}

// Complete failure path execution (child-friendly, encouraging)
function executeFailurePath(failureType, heardLetter, targetLetter) {
    console.log(`❌ FAILURE PATH: ${failureType} | Heard: "${heardLetter}" | Target: "${targetLetter}"`);
    
    // STEP 2.7: Updated Score Rules
    // +5 points → correct spoken letter (handled in success path)
    // +0 points → touch without speaking (this function)
    // +0 points → wrong spoken letter (this function)
    
    // 1. Alphabet does NOT change (stays the same for retry)
    // 2. Score does NOT increment (+0 points for wrong/no speech)
    // 3. Square stays controllable (player can move freely)
    
    // 4. Child-friendly AI feedback based on failure type
    let encouragingMessage = '';
    
    if (failureType === 'wrong_letter') {
        const wrongLetterMessages = [
            "Try again — say the letter clearly",
            `You said "${heardLetter}" — try saying "${targetLetter}"`,
            "Almost there! Say the letter you see",
            "Good try! Look at the letter and say it",
            "Keep trying! You can do this"
        ];
        encouragingMessage = wrongLetterMessages[Math.floor(Math.random() * wrongLetterMessages.length)];
        
        // Visual feedback for wrong letter
        game.wrongLetterFeedback = {
            active: true,
            timer: 120, // 2 seconds (longer for encouragement)
            heardLetter: heardLetter,
            targetLetter: targetLetter,
            message: encouragingMessage
        };
        
    } else if (failureType === 'timeout') {
        const timeoutMessages = [
            "Try again — say the letter clearly",
            "I didn't hear you — speak up!",
            "Say the letter out loud when you're ready",
            "Take your time — say the letter clearly",
            "Try speaking the letter again"
        ];
        encouragingMessage = timeoutMessages[Math.floor(Math.random() * timeoutMessages.length)];
        
        // Visual feedback for timeout
        game.timeoutFeedback = {
            active: true,
            timer: 120, // 2 seconds
            targetLetter: targetLetter,
            message: encouragingMessage
        };
    }
    
    // Add encouraging message to AI thoughts
    aiThoughts.push(`💪 ${encouragingMessage}`);
    
    // 5. STEP 2.6: Implement lock condition to prevent repeated triggers
    game.speechRecognition.lastHeardLetter = '';
    game.speechRecognition.timeoutTimer = 0;
    game.speechRecognition.waitingForSpeech = false; // Stop listening
    game.speechRecognition.attemptProcessed = true; // Lock further attempts
    game.speechRecognition.mustExitAndReenter = true; // Require exit/re-entry
    
    console.log(`🔒 Attempt processed - must exit and re-enter circle to try again`);
    
    console.log(`💪 Encouraging retry: ${encouragingMessage}`);
}

// Special feedback for successful letter + touch combination
function triggerLetterSuccessFeedback() {
    game.letterSuccessFeedback = {
        active: true,
        timer: 90, // 1.5 seconds
        scale: 2.0
    };
    
    // Add circle relocation animation
    game.circleRelocationFeedback = {
        active: true,
        timer: 60, // 1 second
        oldX: game.safeZone.x,
        oldY: game.safeZone.y
    };
}

// Setup keyboard controls
function setupControls() {
    document.addEventListener('keydown', (e) => {
        // Game over controls
        if (game.gameOver.active) {
            switch(e.key.toLowerCase()) {
                case 'r':
                    restartGame();
                    e.preventDefault();
                    break;
                case 'escape':
                    showLanding();
                    e.preventDefault();
                    break;
            }
            return; // Don't process movement when game over
        }
        
        // Normal game controls
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
    
    // Check for danger zone collision (GAME OVER condition)
    checkDangerZoneCollision();
    
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
    
    // Update letter success feedback timer
    if (game.letterSuccessFeedback && game.letterSuccessFeedback.active) {
        game.letterSuccessFeedback.timer--;
        if (game.letterSuccessFeedback.timer <= 0) {
            game.letterSuccessFeedback.active = false;
        }
    }
    
    // Update wrong letter feedback timer
    if (game.wrongLetterFeedback && game.wrongLetterFeedback.active) {
        game.wrongLetterFeedback.timer--;
        if (game.wrongLetterFeedback.timer <= 0) {
            game.wrongLetterFeedback.active = false;
        }
    }
    
    // Update timeout feedback timer
    if (game.timeoutFeedback && game.timeoutFeedback.active) {
        game.timeoutFeedback.timer--;
        if (game.timeoutFeedback.timer <= 0) {
            game.timeoutFeedback.active = false;
        }
    }
    
    // Update circle relocation feedback timer
    if (game.circleRelocationFeedback && game.circleRelocationFeedback.active) {
        game.circleRelocationFeedback.timer--;
        if (game.circleRelocationFeedback.timer <= 0) {
            game.circleRelocationFeedback.active = false;
        }
    }
    
    // Update speech timeout when waiting for voice input
    if (game.speechRecognition.waitingForSpeech) {
        game.speechRecognition.timeoutTimer++;
        
        // Check for timeout (no voice detected within time window)
        if (game.speechRecognition.timeoutTimer >= game.speechRecognition.timeoutDuration) {
            executeFailurePath('timeout', '', game.alphabetPrompt.currentLetter);
        }
    }
    
    // Update alphabet prompt system
    updateAlphabetPrompt();
    
    // AI Coach Analysis
    if (game.aiEnabled && frameCount % 60 === 0) { // Every second
        aiCoachAnalysis();
    }
}

// Alphabet prompt system for cognitive load
function updateAlphabetPrompt() {
    game.alphabetPrompt.changeTimer++;
    
    // Change letter every 3 seconds
    if (game.alphabetPrompt.changeTimer >= game.alphabetPrompt.changeInterval) {
        const currentIndex = game.alphabetPrompt.letters.indexOf(game.alphabetPrompt.currentLetter);
        const nextIndex = (currentIndex + 1) % game.alphabetPrompt.letters.length;
        game.alphabetPrompt.currentLetter = game.alphabetPrompt.letters[nextIndex];
        game.alphabetPrompt.changeTimer = 0;
        
        console.log(`📝 Alphabet Prompt: ${game.alphabetPrompt.currentLetter}`);
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
    
    // CIRCLE TOUCH EVENT DETECTION WITH RESET LOGIC
    // Count only when entering the circle (outside → inside/boundary), not while staying
    const isEnteringCircle = (
        (game.previousZoneStatus === 'outside') && 
        (game.zoneStatus === 'inside' || game.zoneStatus === 'boundary')
    );
    
    // Debounce rapid re-entries to prevent exploitation
    const timeSinceLastTouch = frameCount - game.lastTouchTime;
    const canRegisterTouch = timeSinceLastTouch >= game.touchDebounceDelay;
    
    if (isEnteringCircle && canRegisterTouch) {
        // Check if player must exit and re-enter due to previous attempt
        if (game.speechRecognition.mustExitAndReenter) {
            console.log(`🔒 Must exit and re-enter circle after previous attempt`);
            return; // Block entry until they exit first
        }
        
        game.touchCounter++;
        game.lastTouchTime = frameCount;
        
        // Mark that player is in circle for speech recognition
        game.speechRecognition.isInCircle = true;
        game.speechRecognition.waitingForSpeech = true;
        game.speechRecognition.timeoutTimer = 0; // Start timeout countdown
        game.speechRecognition.attemptProcessed = false; // Reset attempt lock
        
        console.log(`🎯 CIRCLE ENTERED! Say "${game.alphabetPrompt.currentLetter}" out loud! (5 second window)`);
        
        // Check if we already heard the correct letter
        checkLetterMatch();
        
        // Visual feedback for circle entry (not full success yet)
        triggerTouchFeedback();
    } else if (isEnteringCircle && !canRegisterTouch) {
        console.log(`⏱️ TOUCH DEBOUNCED: Too rapid (${timeSinceLastTouch}/${game.touchDebounceDelay} frames)`);
    }
    
    // Reset speech state when leaving circle
    if (game.previousZoneStatus !== 'outside' && game.zoneStatus === 'outside') {
        game.speechRecognition.isInCircle = false;
        game.speechRecognition.waitingForSpeech = false;
        game.speechRecognition.mustExitAndReenter = false; // Reset lock when exiting
        console.log(`🔓 Exited circle - lock reset, can re-enter for new attempt`);
    }
    
    // RESET LOGIC: Leaving circle doesn't reset anything
    // Re-entering always counts (after debounce period)
    // This encourages deliberate, controlled movement patterns
    
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
    
    // Add special AI message for successful touch with alphabet awareness
    const touchMessages = [
        "Circle entered! Now say the letter out loud",
        "Good positioning! Voice recognition ready",
        "Perfect entry! Speak clearly now",
        "Great movement! Time to say the letter",
        "Excellent! Ready for voice input",
        `In position for letter ${game.alphabetPrompt.currentLetter}!`,
        `Ready to hear letter ${game.alphabetPrompt.currentLetter}!`
    ];
    const randomMessage = touchMessages[Math.floor(Math.random() * touchMessages.length)];
    aiThoughts.push(`🎯 ${randomMessage}`);
    console.log('AI Coach (Circle Entry):', randomMessage);
}

// Check for danger zone collision and trigger game over
function checkDangerZoneCollision() {
    if (game.gameOver.active) return; // Already game over
    
    const dangerZoneSize = 50; // Same as visual danger zone
    const playerCenterX = game.player.x;
    const playerCenterY = game.player.y;
    const playerRadius = game.player.size / 2;
    
    // Check collision with each danger zone edge
    let inDangerZone = false;
    let dangerReason = '';
    
    // Top danger zone
    if (playerCenterY - playerRadius <= dangerZoneSize) {
        inDangerZone = true;
        dangerReason = 'top edge';
    }
    // Bottom danger zone
    else if (playerCenterY + playerRadius >= canvas.height - dangerZoneSize) {
        inDangerZone = true;
        dangerReason = 'bottom edge';
    }
    // Left danger zone
    else if (playerCenterX - playerRadius <= dangerZoneSize) {
        inDangerZone = true;
        dangerReason = 'left edge';
    }
    // Right danger zone
    else if (playerCenterX + playerRadius >= canvas.width - dangerZoneSize) {
        inDangerZone = true;
        dangerReason = 'right edge';
    }
    
    if (inDangerZone) {
        triggerGameOver(`Entered danger zone: ${dangerReason}`);
    }
}

// Trigger game over
function triggerGameOver(reason) {
    game.gameOver.active = true;
    game.gameOver.reason = reason;
    game.gameOver.finalScore = game.score;
    game.gameOver.finalSuccesses = game.successCount;
    game.running = false;
    
    console.log('🚨 GAME OVER:', reason);
    console.log(`Final Score: ${game.gameOver.finalScore}, Successes: ${game.gameOver.finalSuccesses}`);
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
    // Priority 3: Safe Zone status with varied, state-based feedback
    else if (game.zoneStatus === 'inside') {
        const insideMessages = [
            "Good control – you're inside the optimal zone",
            "Perfect positioning – maintaining safe zone",
            "Excellent! Staying centered in the green area",
            "Well done – you're in the sweet spot",
            "Great control – optimal zone mastered"
        ];
        
        if (game.touchCounter === 0) {
            coachMessage = "✅ First time in! Now exit and re-enter to score";
        } else if (game.touchCounter < 3) {
            coachMessage = insideMessages[game.touchCounter % insideMessages.length];
        } else if (game.touchCounter < 7) {
            coachMessage = `${insideMessages[Math.floor(Math.random() * insideMessages.length)]} (${game.touchCounter} touches!)`;
        } else {
            coachMessage = `🏆 Master level! ${game.touchCounter} touches – incredible control!`;
        }
    } else if (game.zoneStatus === 'boundary') {
        const boundaryMessages = [
            "Careful – approaching danger zone",
            "🎯 On the edge – stay centered for safety",
            "Close to boundary – move toward center",
            "Edge detected – careful positioning needed",
            "Boundary alert – return to safe center"
        ];
        coachMessage = boundaryMessages[frameCount % boundaryMessages.length];
    } else if (game.zoneStatus === 'outside') {
        const distanceText = Math.round(distanceFromSafeZone - game.safeZone.radius);
        const outsideMessages = [
            "Return to safety – green zone awaits",
            "Outside optimal area – head back to center",
            "Lost the zone – navigate back to green circle",
            "Drifting away – return to safe positioning",
            "Off course – green zone needs you back"
        ];
        
        if (game.touchCounter === 0) {
            coachMessage = "🏃 Enter the green circle to begin your journey!";
        } else if (distanceText < 50) {
            coachMessage = `Almost there – ${distanceText}px to safety!`;
        } else {
            const randomMessage = outsideMessages[Math.floor(Math.random() * outsideMessages.length)];
            coachMessage = `${randomMessage} (Touch ${game.touchCounter + 1} awaits)`;
        }
    }
    // Priority 4: Dynamic target and movement guidance
    else if (distanceToTarget < 100) {
        const closeMessages = [
            "🎯 Close to target – excellent positioning!",
            "Target nearby – you're doing great!",
            "Almost there – target within reach",
            "Good hunting – target is close",
            "Nice approach – target in sight"
        ];
        coachMessage = closeMessages[Math.floor(Math.random() * closeMessages.length)];
    } else if (distanceToTarget > 200) {
        const farMessages = [
            "🏃 Target distant – time to move closer",
            "Long journey ahead – start moving toward target",
            "Target far away – begin your approach",
            "Distance detected – navigate toward target",
            "Far from goal – start closing the gap"
        ];
        coachMessage = farMessages[Math.floor(Math.random() * farMessages.length)];
    } else {
        const generalMessages = [
            "✅ Good movement – keep exploring",
            "Steady progress – maintain your pace",
            "Nice control – continue navigating",
            "Smooth movement – you're learning well",
            "Great technique – keep it up",
            `Focus on letter ${game.alphabetPrompt.currentLetter} while moving`,
            "Excellent multitasking – reading and moving!"
        ];
        coachMessage = generalMessages[Math.floor(Math.random() * generalMessages.length)];
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
    
    // Letter Success Feedback (bigger, more prominent)
    if (game.letterSuccessFeedback && game.letterSuccessFeedback.active) {
        const progress = 1 - (game.letterSuccessFeedback.timer / 90);
        const alpha = 1 - progress;
        const scale = 1 + (progress * 1.0);
        
        ctx.strokeStyle = `rgba(255, 255, 0, ${alpha})`;
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.arc(game.safeZone.x, game.safeZone.y, game.safeZone.radius * scale, 0, 2 * Math.PI);
        ctx.stroke();
        
        // Success message
        ctx.fillStyle = `rgba(255, 255, 0, ${alpha})`;
        ctx.font = 'bold 32px Arial';
        ctx.textAlign = 'center';
        const successText = '🎉 LETTER + TOUCH SUCCESS! +5 POINTS!';
        ctx.fillText(successText, canvas.width / 2, game.safeZone.y - 80);
        ctx.textAlign = 'left';
    }
    
    // Wrong Letter Feedback (encouraging, child-friendly)
    if (game.wrongLetterFeedback && game.wrongLetterFeedback.active) {
        const alpha = game.wrongLetterFeedback.timer / 120;
        
        ctx.fillStyle = `rgba(255, 150, 100, ${alpha})`;
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        
        // Show encouraging message instead of harsh correction
        ctx.fillText(game.wrongLetterFeedback.message, canvas.width / 2, game.safeZone.y + 150);
        
        // Smaller, gentler correction below
        ctx.fillStyle = `rgba(255, 200, 150, ${alpha * 0.8})`;
        ctx.font = '16px Arial';
        const hintText = `(You said "${game.wrongLetterFeedback.heardLetter}" — try "${game.wrongLetterFeedback.targetLetter}")`;
        ctx.fillText(hintText, canvas.width / 2, game.safeZone.y + 175);
        
        ctx.textAlign = 'left';
    }
    
    // Timeout Feedback (encouraging voice prompt)
    if (game.timeoutFeedback && game.timeoutFeedback.active) {
        const alpha = game.timeoutFeedback.timer / 120;
        
        ctx.fillStyle = `rgba(100, 150, 255, ${alpha})`;
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        
        ctx.fillText(game.timeoutFeedback.message, canvas.width / 2, game.safeZone.y + 150);
        
        // Gentle reminder
        ctx.fillStyle = `rgba(150, 200, 255, ${alpha * 0.8})`;
        ctx.font = '16px Arial';
        const reminderText = `(Say "${game.timeoutFeedback.targetLetter}" out loud)`;
        ctx.fillText(reminderText, canvas.width / 2, game.safeZone.y + 175);
        
        ctx.textAlign = 'left';
    }
    
    // Circle Relocation Animation
    if (game.circleRelocationFeedback && game.circleRelocationFeedback.active) {
        const alpha = game.circleRelocationFeedback.timer / 60;
        
        // Show "NEW CHALLENGE!" message
        ctx.fillStyle = `rgba(0, 255, 255, ${alpha})`;
        ctx.font = 'bold 20px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('🎯 NEW CHALLENGE!', canvas.width / 2, game.safeZone.y - 130);
        ctx.textAlign = 'left';
        
        // Pulsing effect on new circle location
        const pulseScale = 1 + Math.sin(frameCount * 0.3) * 0.1;
        ctx.strokeStyle = `rgba(0, 255, 255, ${alpha})`;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(game.safeZone.x, game.safeZone.y, game.safeZone.radius * pulseScale, 0, 2 * Math.PI);
        ctx.stroke();
    }
    
    // Draw danger zones (white areas near edges)
    if (game.aiEnabled) {
        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
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
        // Flashing white when in danger zone
        const flashIntensity = Math.sin(frameCount * 0.3) * 0.5 + 0.5;
        playerColor = `rgb(${Math.floor(255 * flashIntensity)}, ${Math.floor(255 * flashIntensity)}, ${Math.floor(255 * flashIntensity)})`;
        outlineColor = '#ffffff'; // White outline in danger
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
    
    // Success Counter (Letter + Touch combinations)
    ctx.fillStyle = '#ffff00';
    ctx.font = 'bold 24px Arial';
    ctx.fillText(`Successes: ${game.successCount}`, canvas.width - 200, 60);
    
    // Removed Circle Touches and Zone displays for cleaner UI focused on multi-modal learning
    
    // Microphone Status Indicator (top-left corner)
    ctx.fillStyle = game.speechRecognition.isListening ? '#00ff00' : '#666666';
    ctx.font = 'bold 16px Arial';
    const micStatus = game.speechRecognition.isListening ? '🎤 Listening...' : '🎤 Not listening';
    ctx.fillText(micStatus, 10, 25);
    
    // Speech Status Indicator with timeout progress
    if (game.speechRecognition.waitingForSpeech && !game.speechRecognition.attemptProcessed) {
        ctx.fillStyle = '#ffff00';
        ctx.font = 'bold 18px Arial';
        ctx.fillText(`🎤 Say "${game.alphabetPrompt.currentLetter}"!`, canvas.width - 200, 85);
        
        // Timeout progress bar (child-friendly visual cue)
        const timeProgress = game.speechRecognition.timeoutTimer / game.speechRecognition.timeoutDuration;
        const barWidth = 150;
        const barHeight = 4;
        const barX = canvas.width - 200;
        const barY = 90;
        
        // Background bar
        ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        ctx.fillRect(barX, barY, barWidth, barHeight);
        
        // Progress bar (changes color as time runs out)
        const progressColor = timeProgress < 0.7 ? '#00ff00' : timeProgress < 0.9 ? '#ffff00' : '#ff6600';
        ctx.fillStyle = progressColor;
        ctx.fillRect(barX, barY, barWidth * (1 - timeProgress), barHeight);
    }
    
    // Lock Status Indicator (must exit and re-enter)
    if (game.speechRecognition.mustExitAndReenter && game.speechRecognition.isInCircle) {
        ctx.fillStyle = '#ffaa00';
        ctx.font = 'bold 16px Arial';
        ctx.fillText(`🔒 Exit and re-enter to try again`, canvas.width - 220, 85);
    }
    
    // Danger Zone Warning Display (highest priority)
    if (game.dangerZone.active) {
        const flashAlpha = Math.sin(frameCount * 0.4) * 0.5 + 0.5;
        ctx.fillStyle = `rgba(255, 255, 255, ${flashAlpha})`;
        ctx.font = 'bold 24px Arial';
        
        // Center the warning text
        const warningText = game.dangerZone.warningText;
        const textWidth = ctx.measureText(warningText).width;
        ctx.fillText(warningText, (canvas.width - textWidth) / 2, 100);
        
        // Add warning background
        ctx.fillStyle = `rgba(255, 255, 255, ${flashAlpha * 0.3})`;
        ctx.fillRect((canvas.width - textWidth) / 2 - 10, 75, textWidth + 20, 35);
    }
    
    // AI Coach display
    if (game.aiEnabled) {
        ctx.fillStyle = '#00ff00';
        ctx.font = '16px Arial';
        ctx.fillText('AI Coach: ON', 10, 45);
        
        // Display AI coaching thoughts
        ctx.font = '12px Arial';
        ctx.fillStyle = '#88ff88';
        aiThoughts.forEach((thought, index) => {
            ctx.fillText(thought, 10, 70 + (index * 15));
        });
    }
    
    // Alphabet Prompt Display (top center, high contrast)
    ctx.fillStyle = '#ffff00'; // Bright yellow
    ctx.font = 'bold 72px Arial';
    ctx.textAlign = 'center';
    
    // Add subtle glow effect for better visibility
    ctx.shadowColor = '#ffff00';
    ctx.shadowBlur = 10;
    
    ctx.fillText(game.alphabetPrompt.currentLetter, canvas.width / 2, 80);
    
    // Reset shadow and alignment
    ctx.shadowBlur = 0;
    ctx.textAlign = 'left';
    
    // Letter change progress indicator (subtle)
    const progress = game.alphabetPrompt.changeTimer / game.alphabetPrompt.changeInterval;
    ctx.fillStyle = 'rgba(255, 255, 0, 0.3)';
    ctx.fillRect(canvas.width / 2 - 50, 90, 100 * progress, 3);
    
    // Game Over Screen
    if (game.gameOver.active) {
        // Semi-transparent overlay
        ctx.fillStyle = 'rgba(0, 0, 0, 0.8)';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Game Over title
        ctx.fillStyle = '#ff0000';
        ctx.font = 'bold 48px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER', canvas.width / 2, canvas.height / 2 - 100);
        
        // Reason
        ctx.fillStyle = '#ffffff';
        ctx.font = 'bold 24px Arial';
        ctx.fillText(`Reason: ${game.gameOver.reason}`, canvas.width / 2, canvas.height / 2 - 50);
        
        // Final stats
        ctx.fillStyle = '#00ff00';
        ctx.font = '20px Arial';
        ctx.fillText(`Final Score: ${game.gameOver.finalScore}`, canvas.width / 2, canvas.height / 2);
        ctx.fillText(`Letter Successes: ${game.gameOver.finalSuccesses}`, canvas.width / 2, canvas.height / 2 + 30);
        
        // Instructions
        ctx.fillStyle = '#ffff00';
        ctx.font = '18px Arial';
        ctx.fillText('Press R to Restart or ESC to Return to Menu', canvas.width / 2, canvas.height / 2 + 80);
        
        ctx.textAlign = 'left';
        return; // Don't render game elements when game over
    }
    
    // Controls instruction
    ctx.fillStyle = '#666';
    ctx.font = '12px Arial';
    ctx.fillText('Use WASD or Arrow Keys to move', 10, canvas.height - 25);
    ctx.fillText('Stay in the green Safe Zone!', 10, canvas.height - 10);
}