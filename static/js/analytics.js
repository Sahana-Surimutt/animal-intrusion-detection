// Analytics Dashboard JavaScript
let trendsChart, distributionChart, hourlyChart;

// Initialize analytics dashboard
document.addEventListener('DOMContentLoaded', function() {
    initializeAnalytics();
    loadDashboardData();
    setInterval(loadDashboardData, 10000); // Refresh every 10 seconds
});

// Initialize charts and analytics
function initializeAnalytics() {
    console.log('📊 Analytics Dashboard Initialized');
    
    // Initialize charts with empty data
    initializeCharts();
    
    // Load initial data
    loadOverview();
    loadDetectionStats();
    loadInsights();
    loadRecentDetections();
    loadRiskAssessment();
}

// Initialize Chart.js instances
function initializeCharts() {
    const trendsCtx = document.getElementById('trendsChart').getContext('2d');
    trendsChart = new Chart(trendsCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Daily Detections',
                data: [],
                borderColor: '#10B981',
                backgroundColor: 'rgba(16, 185, 129, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: '7-Day Detection Trend'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Detections'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    }
                }
            }
        }
    });

    const distributionCtx = document.getElementById('distributionChart').getContext('2d');
    distributionChart = new Chart(distributionCtx, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#10B981', '#3B82F6', '#8B5CF6', '#F59E0B', '#EF4444',
                    '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1'
                ],
                borderWidth: 2,
                borderColor: '#FFFFFF'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 15
                    }
                },
                title: {
                    display: true,
                    text: 'Animal Distribution'
                }
            }
        }
    });

    const hourlyCtx = document.getElementById('hourlyChart').getContext('2d');
    hourlyChart = new Chart(hourlyCtx, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label: 'Detections per Hour',
                data: [],
                backgroundColor: 'rgba(59, 130, 246, 0.7)',
                borderColor: '#3B82F6',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Hourly Activity Pattern'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Detections'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Hour of Day'
                    }
                }
            }
        }
    });
}

// Load all dashboard data
async function loadDashboardData() {
    await loadOverview();
    await loadDetectionStats();
    await loadInsights();
    await loadRecentDetections();
    await loadRiskAssessment();
}

// Load overview statistics
async function loadOverview() {
    try {
        const response = await fetch('/api/analytics/overview');
        const data = await response.json();
        
        document.getElementById('todayDetections').textContent = data.today_detections;
        document.getElementById('weeklyTotal').textContent = data.weekly_total;
        document.getElementById('topAnimal').textContent = data.top_animal;
        
        // Calculate and display peak hour (simplified)
        const peakHour = data.peak_hour || '14:00';
        document.getElementById('peakHour').textContent = peakHour;
        
        // Today vs yesterday change
        const changeElement = document.getElementById('todayChange');
        const change = data.change_percentage || 0;
        changeElement.textContent = `${change >= 0 ? '+' : ''}${change}% from yesterday`;
        changeElement.className = `text-sm ${change >= 0 ? 'text-green-500' : 'text-red-500'} mt-1`;
        
    } catch (error) {
        console.error('Error loading overview:', error);
    }
}

// Load detailed detection statistics
async function loadDetectionStats() {
    try {
        const response = await fetch('/api/analytics/detection_stats?days=7');
        const data = await response.json();
        
        updateTrendsChart(data.daily_trends);
        updateDistributionChart(data.animal_stats);
        updateHourlyChart(data.hourly_patterns);
        
    } catch (error) {
        console.error('Error loading detection stats:', error);
    }
}

// Update trends chart
function updateTrendsChart(dailyTrends) {
    const labels = dailyTrends.map(day => {
        const date = new Date(day.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    
    const data = dailyTrends.map(day => day.count);
    
    trendsChart.data.labels = labels;
    trendsChart.data.datasets[0].data = data;
    trendsChart.update();
}

// Update distribution chart
function updateDistributionChart(animalStats) {
    const labels = animalStats.map(animal => animal.animal_type);
    const data = animalStats.map(animal => animal.count);
    
    distributionChart.data.labels = labels;
    distributionChart.data.datasets[0].data = data;
    distributionChart.update();
}

// Update hourly chart
function updateHourlyChart(hourlyPatterns) {
    // Create array for all 24 hours
    const hourlyData = Array(24).fill(0);
    
    hourlyPatterns.forEach(hour => {
        const hourIndex = parseInt(hour.hour);
        hourlyData[hourIndex] = hour.count;
    });
    
    const labels = Array.from({length: 24}, (_, i) => `${i.toString().padStart(2, '0')}:00`);
    
    hourlyChart.data.labels = labels;
    hourlyChart.data.datasets[0].data = hourlyData;
    hourlyChart.update();
}

// Load AI insights
async function loadInsights() {
    try {
        const response = await fetch('/api/analytics/insights?days=30');
        const insights = await response.json();
        
        const container = document.getElementById('insightsContainer');
        container.innerHTML = '';
        
        if (insights.length === 0) {
            container.innerHTML = `
                <div class="text-center text-gray-500 py-8">
                    <i class="fas fa-chart-line text-4xl mb-4"></i>
                    <p>No insights available yet. Continue monitoring to generate insights.</p>
                </div>
            `;
            return;
        }
        
        insights.forEach(insight => {
            const insightElement = document.createElement('div');
            const priorityClass = getPriorityClass(insight.priority);
            
            insightElement.className = `p-4 rounded-lg border-l-4 ${priorityClass} bg-white shadow-sm`;
            insightElement.innerHTML = `
                <div class="flex items-start">
                    <div class="flex-shrink-0">
                        <i class="fas fa-lightbulb text-lg mt-1"></i>
                    </div>
                    <div class="ml-4">
                        <h4 class="font-semibold text-gray-800">${insight.title}</h4>
                        <p class="text-gray-600 mt-1">${insight.message}</p>
                    </div>
                </div>
            `;
            container.appendChild(insightElement);
        });
        
    } catch (error) {
        console.error('Error loading insights:', error);
    }
}

// Load risk assessment
async function loadRiskAssessment() {
    try {
        const response = await fetch('/api/analytics/predictions');
        const data = await response.json();
        
        const container = document.getElementById('riskAssessment');
        container.innerHTML = '';
        
        const riskLevels = data.risk_levels || {};
        
        if (Object.keys(riskLevels).length === 0) {
            container.innerHTML = `
                <div class="text-center text-gray-500 py-4">
                    <p>No risk assessment data available yet.</p>
                </div>
            `;
            return;
        }
        
        Object.entries(riskLevels).forEach(([animal, riskData]) => {
            const riskElement = document.createElement('div');
            const riskClass = getRiskClass(riskData.level);
            
            riskElement.className = 'bg-white p-4 rounded-lg shadow-sm border';
            riskElement.innerHTML = `
                <div class="flex justify-between items-start">
                    <div>
                        <h4 class="font-semibold text-gray-800">${animal.charAt(0).toUpperCase() + animal.slice(1)}</h4>
                        <p class="text-sm text-gray-600 mt-1">${riskData.advice}</p>
                    </div>
                    <div class="text-right">
                        <span class="risk-badge ${riskClass}">${riskData.level.toUpperCase()}</span>
                        <div class="text-xs text-gray-500 mt-1">${riskData.detections} detections</div>
                    </div>
                </div>
            `;
            container.appendChild(riskElement);
        });
        
    } catch (error) {
        console.error('Error loading risk assessment:', error);
    }
}

// Load recent detections table
async function loadRecentDetections() {
    try {
        const response = await fetch('/api/analytics/recent_detections?limit=10');
        const detections = await response.json();
        
        const tableBody = document.getElementById('recentDetectionsTable');
        tableBody.innerHTML = '';
        
        if (detections.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="4" class="px-4 py-8 text-center text-gray-500">
                        <i class="fas fa-inbox text-2xl mb-2"></i>
                        <p>No detections recorded yet.</p>
                    </td>
                </tr>
            `;
            return;
        }
        
        detections.forEach(detection => {
            const row = document.createElement('tr');
            row.className = 'border-b hover:bg-gray-50';
            row.innerHTML = `
                <td class="px-4 py-3">
                    <div class="flex items-center">
                        <span class="text-lg mr-3">${getAnimalEmoji(detection.animal)}</span>
                        <span class="font-medium">${detection.animal}</span>
                    </div>
                </td>
                <td class="px-4 py-3">
                    <div class="flex items-center">
                        <div class="w-16 bg-gray-200 rounded-full h-2 mr-2">
                            <div class="bg-green-500 h-2 rounded-full" 
                                 style="width: ${(detection.confidence * 100)}%"></div>
                        </div>
                        <span class="text-sm text-gray-600">${(detection.confidence * 100).toFixed(1)}%</span>
                    </div>
                </td>
                <td class="px-4 py-3 text-gray-600">${formatTimestamp(detection.timestamp)}</td>
                <td class="px-4 py-3">
                    <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        ${detection.source}
                    </span>
                </td>
            `;
            tableBody.appendChild(row);
        });
        
    } catch (error) {
        console.error('Error loading recent detections:', error);
    }
}

// Helper functions
function getPriorityClass(priority) {
    switch (priority) {
        case 'high': return 'border-red-500';
        case 'medium': return 'border-yellow-500';
        case 'low': return 'border-green-500';
        default: return 'border-gray-500';
    }
}

function getRiskClass(riskLevel) {
    switch (riskLevel) {
        case 'high': return 'risk-high';
        case 'medium': return 'risk-medium';
        case 'low': return 'risk-low';
        default: return 'risk-low';
    }
}

function getAnimalEmoji(animal) {
    const emojiMap = {
        'dog': '🐕',
        'cat': '🐈',
        'bird': '🐦',
        'cow': '🐄',
        'horse': '🐎',
        'sheep': '🐑',
        'bear': '🐻',
        'elephant': '🐘',
        'zebra': '🦓',
        'giraffe': '🦒'
    };
    return emojiMap[animal.toLowerCase()] || '🐾';
}

function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Export functionality (optional)
function exportData() {
    showNotification('Export feature coming soon!', 'info');
}

// Refresh dashboard manually
function refreshDashboard() {
    loadDashboardData();
    showNotification('Dashboard refreshed', 'success');
}

// Add to window object for global access
window.refreshDashboard = refreshDashboard;
window.exportData = exportData;
