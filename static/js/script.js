// Global variables
let isMonitoring = false;
let activityLog = [];

// DOM Content Loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    updateStats();
    setupAnimalCards();
});

// Initialize the application
function initializeApp() {
    console.log('🚀 Wildlife Guardian AI Initialized');
    showNotification('System ready for monitoring', 'success');
    addActivityLog('🟢 System initialized and ready');
}

// Setup event listeners
function setupEventListeners() {
    // File upload handling
    const fileInput = document.getElementById('fileInput');
    if (fileInput) {
        fileInput.addEventListener('change', handleFileUpload);
    }
    
    // Periodic stats update
    setInterval(updateStats, 3000);
    
    // Setup animal cards
    setupAnimalCards();
}

// Setup animal cards with click animations
function setupAnimalCards() {
    const animalCards = document.querySelectorAll('.animal-card');
    
    animalCards.forEach(card => {
        card.addEventListener('click', function() {
            // Add click animation
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 150);
        });
    });
}

// Start live monitoring
async function startMonitoring() {
    try {
        const response = await fetch('/api/start_monitoring', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            isMonitoring = true;
            updateUI();
            startVideoFeed();
            showNotification('Live monitoring started successfully', 'success');
            addActivityLog('🎬 Live monitoring started');
            
            // Enable alert status
            const alertStatus = document.getElementById('alertStatus');
            if (alertStatus) {
                alertStatus.classList.remove('hidden');
            }
        }
    } catch (error) {
        console.error('Error starting monitoring:', error);
        showNotification('Failed to start monitoring', 'error');
    }
}

// Stop live monitoring
async function stopMonitoring() {
    try {
        const response = await fetch('/api/stop_monitoring', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            isMonitoring = false;
            updateUI();
            showNotification('Monitoring stopped', 'info');
            addActivityLog('⏹️ Monitoring stopped');
            
            // Disable alert status
            const alertStatus = document.getElementById('alertStatus');
            if (alertStatus) {
                alertStatus.classList.add('hidden');
            }
        }
    } catch (error) {
        console.error('Error stopping monitoring:', error);
        showNotification('Failed to stop monitoring', 'error');
    }
}

// Start video feed
function startVideoFeed() {
    const cameraFeed = document.getElementById('cameraFeed');
    if (cameraFeed) {
        cameraFeed.src = '/video_feed';
    }
}

// Take snapshot
async function takeSnapshot() {
    if (!isMonitoring) {
        showNotification('Please start monitoring first', 'warning');
        return;
    }
    
    try {
        const response = await fetch('/api/take_snapshot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('Snapshot captured successfully!', 'success');
            addActivityLog('📸 Snapshot captured');
            
            // Show detections in overlay
            if (data.detections && data.detections.length > 0) {
                updateDetectionOverlay(data.detections);
            }
        } else {
            showNotification('Failed to capture snapshot', 'error');
        }
    } catch (error) {
        console.error('Error taking snapshot:', error);
        showNotification('Error capturing snapshot', 'error');
    }
}

// Handle file upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Update file name display
    const fileName = document.getElementById('fileName');
    if (fileName) {
        fileName.textContent = file.name;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showNotification('Processing file...', 'info');
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showNotification('File processed successfully!', 'success');
            displayUploadResults(data);
            addActivityLog(`📁 ${file.name} processed - ${data.detections.length} detections`);
        } else {
            showNotification(data.message || 'Failed to process file', 'error');
        }
    } catch (error) {
        console.error('Error uploading file:', error);
        showNotification('Error processing file', 'error');
    }
}

// Display upload results
function displayUploadResults(data) {
    const resultsDiv = document.getElementById('uploadResults');
    const detectionsDiv = document.getElementById('uploadDetections');
    
    if (!resultsDiv || !detectionsDiv) return;
    
    resultsDiv.classList.remove('hidden');
    detectionsDiv.innerHTML = '';
    
    if (data.detections.length === 0) {
        detectionsDiv.innerHTML = '<p class="text-gray-500 text-center py-4">No animals detected in this file.</p>';
        return;
    }
    
    data.detections.forEach(detection => {
        const detectionElement = document.createElement('div');
        detectionElement.className = 'bg-green-50 border border-green-200 rounded-lg p-3';
        detectionElement.innerHTML = `
            <div class="flex justify-between items-center">
                <div>
                    <span class="font-semibold text-green-800">${detection.class}</span>
                    <span class="text-sm text-green-600 ml-2">${(detection.confidence * 100).toFixed(1)}% confidence</span>
                </div>
                <span class="text-sm text-gray-500">${detection.timestamp}</span>
            </div>
        `;
        detectionsDiv.appendChild(detectionElement);
    });
    
    // Show processed image if available
    if (data.processed_image) {
        const imgElement = document.createElement('img');
        imgElement.src = data.processed_image;
        imgElement.className = 'w-full mt-4 rounded-lg shadow-md';
        imgElement.alt = 'Processed image with detections';
        detectionsDiv.appendChild(imgElement);
    }
}

// Update detection overlay
function updateDetectionOverlay(detections) {
    const overlay = document.getElementById('detectionOverlay');
    if (!overlay) return;
    
    if (detections.length > 0) {
        const animals = detections.map(d => d.class).join(', ');
        overlay.innerHTML = `
            <div class="pulse-animation bg-red-500 text-white p-4 rounded-lg">
                <div class="flex items-center">
                    <i class="fas fa-bell mr-3 text-xl"></i>
                    <div>
                        <h4 class="font-bold text-lg">🚨 Animals Detected!</h4>
                        <p class="mt-1">${animals}</p>
                    </div>
                </div>
            </div>
        `;
        
        // Play alert sound
        playAlertSound();
    } else {
        overlay.innerHTML = `
            <div class="bg-green-500 text-white p-4 rounded-lg">
                <div class="flex items-center">
                    <i class="fas fa-check mr-3 text-xl"></i>
                    <div>
                        <h4 class="font-bold text-lg">✅ All Clear</h4>
                        <p class="mt-1">No animals detected</p>
                    </div>
                </div>
            </div>
        `;
    }
}

// Play alert sound
function playAlertSound() {
    const alertSound = document.getElementById('alertSound');
    if (alertSound) {
        alertSound.play().catch(e => console.log('Audio play failed:', e));
    }
}

// Play animal sound when animal card is clicked
async function playAnimalSound(animal) {
    try {
        showNotification(`Playing ${animal} sound...`, 'info');
        console.log(`🔊 Attempting to play ${animal} sound`);
        
        const response = await fetch('/api/play_animal_sound', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            'Accept': 'application/json'
            },
            body: JSON.stringify({ animal: animal })
        });
        
        const data = await response.json();
        console.log('Animal sound response:', data);
        
        if (data.status === 'success') {
            showNotification(`${animal.charAt(0).toUpperCase() + animal.slice(1)} sound playing!`, 'success');
            addActivityLog(`🔊 Played ${animal} sound`);
        } else {
            showNotification(data.message || 'Failed to play animal sound', 'error');
            console.error('Animal sound error:', data.message);
        }
    } catch (error) {
        console.error('Error playing animal sound:', error);
        showNotification('Error playing animal sound. Check console for details.', 'error');
    }
}

// Test alert
async function testAlert() {
    try {
        const response = await fetch('/api/play_alert');
        const data = await response.json();
        
        if (data.status === 'success') {
            playAlertSound();
            showNotification('Test alert played successfully', 'success');
            addActivityLog('🔊 Test alert played');
        }
    } catch (error) {
        console.error('Error testing alert:', error);
        showNotification('Error playing test alert', 'error');
    }
}

// Clear activity log
function clearActivity() {
    const activityLog = document.getElementById('activityLog');
    if (activityLog) {
        activityLog.innerHTML = `
            <div class="text-center text-gray-500 py-8">
                <i class="fas fa-broom text-2xl mb-2"></i>
                <p>Activity log cleared</p>
            </div>
        `;
    }
    showNotification('Activity log cleared', 'info');
    addActivityLog('🗑️ Activity log cleared');
}

// Update UI based on monitoring state
function updateUI() {
    const startBtn = document.getElementById('startBtn');
    const stopBtn = document.getElementById('stopBtn');
    const statusIcon = document.getElementById('statusIcon');
    const systemStatus = document.getElementById('systemStatus');
    
    if (!startBtn || !stopBtn || !statusIcon || !systemStatus) return;
    
    if (isMonitoring) {
        startBtn.disabled = true;
        stopBtn.disabled = false;
        statusIcon.className = 'fas fa-circle text-green-500 text-2xl';
        systemStatus.textContent = 'Active';
        systemStatus.className = 'text-lg font-semibold text-green-700';
    } else {
        startBtn.disabled = false;
        stopBtn.disabled = true;
        statusIcon.className = 'fas fa-circle text-red-500 text-2xl';
        systemStatus.textContent = 'Inactive';
        systemStatus.className = 'text-lg font-semibold text-red-700';
    }
}

// Update statistics
async function updateStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        const totalDetections = document.getElementById('totalDetections');
        const lastAnimal = document.getElementById('lastAnimal');
        
        if (totalDetections) {
            totalDetections.textContent = data.total_detections || 0;
        }
        if (lastAnimal) {
            lastAnimal.textContent = data.last_animal || 'None';
        }
        
        // Update monitoring state
        if (data.is_monitoring !== undefined && data.is_monitoring !== isMonitoring) {
            isMonitoring = data.is_monitoring;
            updateUI();
        }
        
    } catch (error) {
        console.error('Error updating stats:', error);
    }
}

// Add entry to activity log
function addActivityLog(message) {
    const activityLog = document.getElementById('activityLog');
    if (!activityLog) return;
    
    const timestamp = new Date().toLocaleTimeString();
    
    // Remove placeholder if it exists
    if (activityLog.querySelector('.text-center')) {
        activityLog.innerHTML = '';
    }
    
    const logEntry = document.createElement('div');
    logEntry.className = 'fade-in bg-gray-50 p-3 rounded-lg border-l-4 border-green-500';
    logEntry.innerHTML = `
        <div class="flex justify-between items-center">
            <span class="text-gray-700">${message}</span>
            <span class="text-sm text-gray-500">${timestamp}</span>
        </div>
    `;
    
    activityLog.insertBefore(logEntry, activityLog.firstChild);
    
    // Limit to 50 entries
    if (activityLog.children.length > 50) {
        activityLog.removeChild(activityLog.lastChild);
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existingNotifications = document.querySelectorAll('.notification');
    existingNotifications.forEach(notif => notif.remove());
    
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="flex items-center">
            <i class="fas fa-${getNotificationIcon(type)} mr-3"></i>
            <span>${message}</span>
        </div>
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.parentNode.removeChild(notification);
        }
    }, 5000);
}

// Get icon for notification type
function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        case 'info': return 'info-circle';
        default: return 'bell';
    }
}

// View analytics dashboard
function viewAnalytics() {
    window.location.href = '/dashboard';
}

// System health check
async function systemHealthCheck() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.system_status === 'Active') {
            showNotification('System health: OK', 'success');
        } else {
            showNotification('System health: Issues detected', 'warning');
        }
    } catch (error) {
        showNotification('System health: Unable to check', 'error');
    }
}

console.log('🐾 Wildlife Guardian AI Frontend Loaded Successfully');
