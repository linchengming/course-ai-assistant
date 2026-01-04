// Course AI Assistant - Frontend JavaScript

// Global state
let sessionId = null;
let isProcessing = false;

// DOM Elements
const messagesContainer = document.getElementById('messages');
const userInput = document.getElementById('userInput');
const sendButton = document.getElementById('sendButton');
const clearButton = document.getElementById('clearButton');
const statsButton = document.getElementById('statsButton');
const statsModal = document.getElementById('statsModal');
const closeModal = document.querySelector('.close');

// API Base URL
const API_BASE = window.location.origin;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    loadChatHistory();
    userInput.focus();
});

// Setup event listeners
function setupEventListeners() {
    sendButton.addEventListener('click', sendMessage);
    clearButton.addEventListener('click', clearChat);
    statsButton.addEventListener('click', showStats);
    closeModal.addEventListener('click', () => {
        statsModal.style.display = 'none';
    });

    // Enter to send, Shift+Enter for new line
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = userInput.scrollHeight + 'px';
    });

    // Close modal on outside click
    window.addEventListener('click', (e) => {
        if (e.target === statsModal) {
            statsModal.style.display = 'none';
        }
    });
}

// Send message to backend
async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message || isProcessing) {
        return;
    }

    // Clear input and reset height
    userInput.value = '';
    userInput.style.height = 'auto';

    // Add user message to UI
    addMessage(message, 'user');

    // Show typing indicator
    const typingId = showTypingIndicator();

    // Disable input
    isProcessing = true;
    sendButton.disabled = true;
    userInput.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/api/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: sessionId
            })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();

        // Update session ID
        sessionId = data.session_id;

        // Remove typing indicator
        removeTypingIndicator(typingId);

        // Add bot response
        addMessage(data.answer, 'bot', data.sources);

        // Save to history
        saveChatHistory();

    } catch (error) {
        console.error('Error sending message:', error);
        removeTypingIndicator(typingId);
        addMessage('抱歉，发生了错误。请稍后重试。', 'bot');
    } finally {
        // Re-enable input
        isProcessing = false;
        sendButton.disabled = false;
        userInput.disabled = false;
        userInput.focus();
    }
}

// Add message to chat
function addMessage(text, type, sources = []) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';

    const textP = document.createElement('p');
    textP.textContent = text;
    contentDiv.appendChild(textP);

    // Add sources if available
    if (sources && sources.length > 0) {
        const sourcesDiv = document.createElement('div');
        sourcesDiv.className = 'message-sources';
        sourcesDiv.textContent = `📚 参考文档: ${sources.join(', ')}`;
        contentDiv.appendChild(sourcesDiv);
    }

    messageDiv.appendChild(contentDiv);
    messagesContainer.appendChild(messageDiv);

    // Scroll to bottom
    scrollToBottom();
}

// Show typing indicator
function showTypingIndicator() {
    const id = 'typing-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.id = id;
    messageDiv.className = 'message bot-message';

    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;

    messageDiv.appendChild(typingDiv);
    messagesContainer.appendChild(messageDiv);

    scrollToBottom();

    return id;
}

// Remove typing indicator
function removeTypingIndicator(id) {
    const element = document.getElementById(id);
    if (element) {
        element.remove();
    }
}

// Scroll to bottom of messages
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Clear chat
function clearChat() {
    if (confirm('确定要清空对话吗？')) {
        // Keep only the welcome message
        const welcomeMessage = messagesContainer.firstElementChild;
        messagesContainer.innerHTML = '';
        messagesContainer.appendChild(welcomeMessage);
        
        // Clear session
        sessionId = null;
        localStorage.removeItem('chatHistory');
        
        userInput.focus();
    }
}

// Show statistics modal
async function showStats() {
    statsModal.style.display = 'block';

    try {
        // Fetch stats
        const statsResponse = await fetch(`${API_BASE}/api/stats`);
        const stats = await statsResponse.json();

        // Fetch health
        const healthResponse = await fetch(`${API_BASE}/api/health`);
        const health = await healthResponse.json();

        // Update modal content
        document.getElementById('totalQueries').textContent = stats.total_queries;
        document.getElementById('avgResponseTime').textContent = `${stats.avg_response_time}秒`;
        document.getElementById('accuracyRate').textContent = `${(stats.accuracy_rate * 100).toFixed(1)}%`;
        document.getElementById('docCount').textContent = health.vector_db_count;

    } catch (error) {
        console.error('Error fetching stats:', error);
        document.getElementById('statsContent').innerHTML = '<p>无法加载统计数据</p>';
    }
}

// Save chat history to localStorage
function saveChatHistory() {
    const messages = [];
    const messageElements = messagesContainer.querySelectorAll('.message');
    
    messageElements.forEach(el => {
        const content = el.querySelector('.message-content p');
        const sources = el.querySelector('.message-sources');
        
        if (content) {
            messages.push({
                text: content.textContent,
                type: el.classList.contains('user-message') ? 'user' : 'bot',
                sources: sources ? sources.textContent : null
            });
        }
    });

    localStorage.setItem('chatHistory', JSON.stringify({
        sessionId: sessionId,
        messages: messages
    }));
}

// Load chat history from localStorage
function loadChatHistory() {
    const history = localStorage.getItem('chatHistory');
    
    if (!history) {
        return;
    }

    try {
        const data = JSON.parse(history);
        sessionId = data.sessionId;

        // Clear existing messages except welcome
        const welcomeMessage = messagesContainer.firstElementChild;
        messagesContainer.innerHTML = '';
        messagesContainer.appendChild(welcomeMessage);

        // Restore messages (skip the first welcome message)
        data.messages.slice(1).forEach(msg => {
            const sources = msg.sources ? 
                msg.sources.replace('📚 参考文档: ', '').split(', ') : 
                [];
            addMessage(msg.text, msg.type, sources);
        });

    } catch (error) {
        console.error('Error loading chat history:', error);
        localStorage.removeItem('chatHistory');
    }
}
