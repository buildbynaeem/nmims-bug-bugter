// Dashboard JavaScript - API calls and UI interactions

const API_BASE = window.location.origin;

// Check authentication on page load
document.addEventListener('DOMContentLoaded', function() {
    checkAuthAndLoadData();
});

// ==================== Authentication ====================

async function checkAuthAndLoadData() {
    try {
        // Load user details
        const userResponse = await fetch(`${API_BASE}/api/user-details`);
        if (userResponse.status === 401) {
            window.location.href = '/login';
            return;
        }
        const user = await userResponse.json();
        updateWelcomeMessage(user);
        
        // Load all dashboard data
        loadWeatherSuggestion();
        loadDroneImages();
        loadSoilReports();
    } catch (error) {
        console.error('Error loading dashboard:', error);
        showNotification('Error loading dashboard data', 'error');
    }
}

function updateWelcomeMessage(user) {
    const welcomeElement = document.getElementById('welcomeMessage');
    const farmInfoElement = document.getElementById('farmInfo');
    
    if (user.farmer_name) {
        welcomeElement.textContent = `Welcome back, ${user.farmer_name}!`;
    }
    
    const infoParts = [];
    if (user.farm_location) infoParts.push(user.farm_location);
    if (user.crop_type) infoParts.push(`Growing: ${user.crop_type}`);
    if (user.soil_type) infoParts.push(`Soil: ${user.soil_type}`);
    
    farmInfoElement.textContent = infoParts.length > 0 
        ? infoParts.join(' • ') 
        : 'Update your profile to see personalized information';
}

async function handleLogout() {
    try {
        const response = await fetch(`${API_BASE}/api/logout`, {
            method: 'POST'
        });
        
        if (response.ok) {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Logout error:', error);
        window.location.href = '/login';
    }
}

// ==================== Weather Suggestion ====================

let currentWeatherData = {};

async function loadWeatherSuggestion() {
    try {
        const response = await fetch(`${API_BASE}/api/weather-suggestion`);
        if (!response.ok) throw new Error('Failed to load weather suggestion');
        
        const data = await response.json();
        currentWeatherData = data;
        
        displayWeatherSuggestion('en');
    } catch (error) {
        console.error('Error loading weather suggestion:', error);
        document.getElementById('weatherSuggestion').textContent = 'Unable to load weather suggestion';
    }
}

function displayWeatherSuggestion(lang) {
    const suggestionElement = document.getElementById('weatherSuggestion');
    const langMap = {
        'en': 'suggestion_text',
        'hi': 'suggestion_hindi',
        'mr': 'suggestion_marathi'
    };
    
    const text = currentWeatherData[langMap[lang]] || currentWeatherData.suggestion_text || 'No suggestion available';
    suggestionElement.textContent = text;
}

// Language tab switching
document.addEventListener('DOMContentLoaded', function() {
    const langTabs = document.querySelectorAll('.lang-tab');
    langTabs.forEach(tab => {
        tab.addEventListener('click', function() {
            langTabs.forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            const lang = this.getAttribute('data-lang');
            displayWeatherSuggestion(lang);
        });
    });
});

// ==================== Drone Images ====================

async function loadDroneImages() {
    try {
        const response = await fetch(`${API_BASE}/api/drone-images`);
        if (!response.ok) throw new Error('Failed to load images');
        
        const images = await response.json();
        displayDroneImages(images);
    } catch (error) {
        console.error('Error loading images:', error);
        document.getElementById('recentImages').innerHTML = '<div class="error">Error loading images</div>';
    }
}

function displayDroneImages(images) {
    const container = document.getElementById('recentImages');
    
    if (images.length === 0) {
        container.innerHTML = '<div class="empty-state">No images uploaded yet. Upload your first field image!</div>';
        return;
    }
    
    container.innerHTML = images.slice(0, 6).map(image => `
        <div class="image-card">
            <img src="${API_BASE}/${image.file_path}" alt="${image.filename}" onerror="this.src='data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' width=\'200\' height=\'200\'%3E%3Crect fill=\'%23ddd\' width=\'200\' height=\'200\'/%3E%3Ctext fill=\'%23999\' font-family=\'sans-serif\' font-size=\'14\' dy=\'10.5\' font-weight=\'bold\' x=\'50%25\' y=\'50%25\' text-anchor=\'middle\'%3ENo Image%3C/text%3E%3C/svg%3E'">
            <div class="image-info">
                <h4>${image.filename}</h4>
                <div class="image-stats">
                    ${image.crop_stress_level ? `<span class="badge ${getStressBadgeClass(image.crop_stress_level)}">Stress: ${image.crop_stress_level}</span>` : ''}
                    ${image.pest_detected ? `<span class="badge badge-danger"><i class="fas fa-bug"></i> Pest Detected</span>` : ''}
                    ${image.nutrient_deficiency ? `<span class="badge badge-warning"><i class="fas fa-exclamation-triangle"></i> ${image.nutrient_deficiency.substring(0, 30)}...</span>` : ''}
                </div>
                <small>${new Date(image.created_at).toLocaleDateString()}</small>
            </div>
        </div>
    `).join('');
}

function getStressBadgeClass(level) {
    if (level === 'Low') return 'badge-success';
    if (level === 'Medium') return 'badge-warning';
    return 'badge-danger';
}

// ==================== Soil Reports ====================

async function loadSoilReports() {
    try {
        const response = await fetch(`${API_BASE}/api/soil-reports`);
        if (!response.ok) throw new Error('Failed to load reports');
        
        const reports = await response.json();
        displaySoilReports(reports);
    } catch (error) {
        console.error('Error loading reports:', error);
        document.getElementById('recentReports').innerHTML = '<div class="error">Error loading reports</div>';
    }
}

function displaySoilReports(reports) {
    const container = document.getElementById('recentReports');
    
    if (reports.length === 0) {
        container.innerHTML = '<div class="empty-state">No soil reports uploaded yet. Upload your first report!</div>';
        return;
    }
    
    container.innerHTML = reports.slice(0, 5).map(report => `
        <div class="report-card">
            <div class="report-header">
                <h4><i class="fas fa-file-alt"></i> ${report.filename}</h4>
                <small>${new Date(report.created_at).toLocaleDateString()}</small>
            </div>
            <div class="report-content">
                <p><strong>Summary:</strong> ${report.analysis_summary ? report.analysis_summary.substring(0, 150) + '...' : 'Analysis pending'}</p>
                ${report.recommendations ? `<p><strong>Recommendations:</strong> ${report.recommendations.substring(0, 100)}...</p>` : ''}
            </div>
            <div class="report-actions">
                <button class="btn btn-sm" onclick="viewFullReport(${report.id})">View Full Report</button>
            </div>
        </div>
    `).join('');
}

// ==================== Image Upload ====================

function openImageUpload() {
    document.getElementById('imageUploadModal').style.display = 'block';
}

function closeImageUpload() {
    document.getElementById('imageUploadModal').style.display = 'none';
    document.getElementById('imageUploadForm').reset();
    document.getElementById('imageAnalysisResult').innerHTML = '';
}

async function handleImageUpload(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const resultDiv = document.getElementById('imageAnalysisResult');
    
    resultDiv.innerHTML = '<div class="loading">Analyzing image...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/analyze-image`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            resultDiv.innerHTML = `
                <div class="success-message">
                    <h4><i class="fas fa-check-circle"></i> Analysis Complete!</h4>
                    <div class="analysis-details">
                        <p><strong>Crop Stress Level:</strong> <span class="badge ${getStressBadgeClass(data.analysis.crop_stress_level)}">${data.analysis.crop_stress_level}</span></p>
                        ${data.analysis.pest_detected ? '<p><strong>Pest Status:</strong> <span class="badge badge-danger">Pest Detected</span></p>' : '<p><strong>Pest Status:</strong> <span class="badge badge-success">No Pests</span></p>'}
                        ${data.analysis.nutrient_deficiency ? `<p><strong>Issue:</strong> ${data.analysis.nutrient_deficiency}</p>` : ''}
                        ${data.analysis.image_health_score ? `<p><strong>Health Score:</strong> ${data.analysis.image_health_score}%</p>` : ''}
                    </div>
                </div>
            `;
            
            // Reload images list
            loadDroneImages();
            
            // Reset form after delay
            setTimeout(() => {
                closeImageUpload();
            }, 3000);
        } else {
            resultDiv.innerHTML = `<div class="error-message">Error: ${data.error || 'Analysis failed'}</div>`;
        }
    } catch (error) {
        console.error('Upload error:', error);
        resultDiv.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
    }
}

// ==================== Soil Report Upload ====================

function openSoilUpload() {
    document.getElementById('soilUploadModal').style.display = 'block';
}

function closeSoilUpload() {
    document.getElementById('soilUploadModal').style.display = 'none';
    document.getElementById('soilUploadForm').reset();
    document.getElementById('soilAnalysisResult').innerHTML = '';
}

async function handleSoilUpload(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const resultDiv = document.getElementById('soilAnalysisResult');
    
    resultDiv.innerHTML = '<div class="loading">Processing soil report...<br>Extracting text, analyzing with AI, and translating...</div>';
    
    try {
        const response = await fetch(`${API_BASE}/api/analyze-soil`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            resultDiv.innerHTML = `
                <div class="success-message">
                    <h4><i class="fas fa-check-circle"></i> Analysis Complete!</h4>
                    <div class="language-tabs">
                        <button class="lang-tab active" onclick="showSoilAnalysis('en', '${escapeHtml(data.analysis_summary)}', '${escapeHtml(data.analysis_marathi)}', '${escapeHtml(data.analysis_hindi)}')">English</button>
                        <button class="lang-tab" onclick="showSoilAnalysis('hi', '${escapeHtml(data.analysis_summary)}', '${escapeHtml(data.analysis_marathi)}', '${escapeHtml(data.analysis_hindi)}')">हिंदी</button>
                        <button class="lang-tab" onclick="showSoilAnalysis('mr', '${escapeHtml(data.analysis_summary)}', '${escapeHtml(data.analysis_marathi)}', '${escapeHtml(data.analysis_hindi)}')">मराठी</button>
                    </div>
                    <div id="soilAnalysisContent" class="soil-analysis-content">
                        <p>${data.analysis_summary}</p>
                    </div>
                    ${data.recommendations ? `<div class="recommendations"><h5>Recommendations:</h5><p>${data.recommendations}</p></div>` : ''}
                </div>
            `;
            
            // Reload reports list
            loadSoilReports();
        } else {
            resultDiv.innerHTML = `<div class="error-message">Error: ${data.error || 'Analysis failed'}</div>`;
        }
    } catch (error) {
        console.error('Upload error:', error);
        resultDiv.innerHTML = `<div class="error-message">Error: ${error.message}</div>`;
    }
}

function showSoilAnalysis(lang, enText, mrText, hiText) {
    const contentDiv = document.getElementById('soilAnalysisContent');
    const textMap = { 'en': enText, 'mr': mrText, 'hi': hiText };
    contentDiv.innerHTML = `<p>${textMap[lang] || enText}</p>`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ==================== Chatbot ====================

let chatHistory = [];

function openChatbot() {
    document.getElementById('chatbotModal').style.display = 'block';
    loadChatHistory();
}

function closeChatbot() {
    document.getElementById('chatbotModal').style.display = 'none';
}

async function loadChatHistory() {
    try {
        const response = await fetch(`${API_BASE}/api/chat-history`);
        if (response.ok) {
            chatHistory = await response.json();
            displayChatHistory();
        }
    } catch (error) {
        console.error('Error loading chat history:', error);
    }
}

function displayChatHistory() {
    const messagesDiv = document.getElementById('chatMessages');
    messagesDiv.innerHTML = chatHistory.reverse().map(chat => `
        <div class="chat-message user-message">
            <div class="message-content">${chat.message}</div>
        </div>
        <div class="chat-message bot-message">
            <div class="message-content">${chat.response}</div>
        </div>
    `).join('');
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

async function handleChatSubmit(event) {
    event.preventDefault();
    
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    
    if (!message) return;
    
    // Display user message
    const messagesDiv = document.getElementById('chatMessages');
    messagesDiv.innerHTML += `
        <div class="chat-message user-message">
            <div class="message-content">${escapeHtml(message)}</div>
        </div>
    `;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    input.value = '';
    input.disabled = true;
    
    // Show typing indicator
    const typingId = 'typing-' + Date.now();
    messagesDiv.innerHTML += `
        <div id="${typingId}" class="chat-message bot-message">
            <div class="message-content typing">AI is thinking...</div>
        </div>
    `;
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        document.getElementById(typingId).remove();
        
        if (response.ok && data.success) {
            messagesDiv.innerHTML += `
                <div class="chat-message bot-message">
                    <div class="message-content">${escapeHtml(data.response)}</div>
                </div>
            `;
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
            
            // Reload chat history
            loadChatHistory();
        } else {
            messagesDiv.innerHTML += `
                <div class="chat-message bot-message">
                    <div class="message-content error">Error: ${data.error || 'Failed to get response'}</div>
                </div>
            `;
        }
    } catch (error) {
        document.getElementById(typingId).remove();
        messagesDiv.innerHTML += `
            <div class="chat-message bot-message">
                <div class="message-content error">Error: ${error.message}</div>
            </div>
        `;
    }
    
    input.disabled = false;
    input.focus();
}

// Close modals when clicking outside
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

// Utility function for notifications
function showNotification(message, type = 'info') {
    // Simple notification - can be enhanced with a toast library
    console.log(`[${type.toUpperCase()}] ${message}`);
}
