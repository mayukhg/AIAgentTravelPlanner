// Chat functionality for Multi-Agent Assistant System

class ChatInterface {
    constructor(sessionId) {
        this.sessionId = sessionId;
        this.chatMessages = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.chatForm = document.getElementById('chatForm');
        this.sendButton = document.getElementById('sendButton');
        this.typingIndicator = document.getElementById('typingIndicator');
        this.statusBadge = document.getElementById('status-badge');
        
        this.isProcessing = false;
        this.messageHistory = [];
        
        this.init();
    }
    
    init() {
        // Bind event listeners
        this.chatForm.addEventListener('submit', (e) => this.handleSubmit(e));
        this.messageInput.addEventListener('keydown', (e) => this.handleKeyDown(e));
        
        // Auto-scroll to bottom
        this.scrollToBottom();
        
        console.log('Chat interface initialized with session:', this.sessionId);
    }
    
    handleKeyDown(e) {
        // Send message on Ctrl+Enter or Cmd+Enter
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            this.sendMessage();
        }
    }
    
    async handleSubmit(e) {
        e.preventDefault();
        await this.sendMessage();
    }
    
    async sendMessage() {
        const message = this.messageInput.value.trim();
        
        if (!message || this.isProcessing) {
            return;
        }
        
        // Add user message to chat
        this.addMessage('user', message);
        this.messageInput.value = '';
        
        // Show loading state
        this.setProcessing(true);
        
        try {
            const response = await this.callChatAPI(message);
            
            if (response.success) {
                this.addMessage('assistant', response.message, {
                    agentType: response.agent_type,
                    metadata: response.metadata,
                    citations: response.citations,
                    eventData: response.event_data
                });
                
                // Update session ID if provided
                if (response.session_id && response.session_id !== this.sessionId) {
                    this.sessionId = response.session_id;
                    this.updateSessionDisplay();
                }
            } else {
                this.addErrorMessage(response.error || 'An unknown error occurred');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addErrorMessage('Failed to send message. Please check your connection and try again.');
        } finally {
            this.setProcessing(false);
        }
    }
    
    async callChatAPI(message) {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                session_id: this.sessionId
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    addMessage(role, content, options = {}) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}`;
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble';
        
        // Format content with proper HTML rendering
        bubbleDiv.innerHTML = this.formatMessageContent(content);
        
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        
        if (role === 'assistant' && options.agentType) {
            const agentBadge = document.createElement('span');
            agentBadge.className = `agent-badge agent-${options.agentType}`;
            agentBadge.textContent = this.formatAgentName(options.agentType);
            metaDiv.appendChild(agentBadge);
        }
        
        // Add timestamp
        const timestamp = new Date().toLocaleTimeString();
        const timeSpan = document.createElement('span');
        timeSpan.textContent = timestamp;
        metaDiv.appendChild(timeSpan);
        
        messageDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(metaDiv);
        
        // Add citations if available
        if (options.citations && options.citations.length > 0) {
            const citationsDiv = this.createCitationsElement(options.citations);
            bubbleDiv.appendChild(citationsDiv);
        }
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Store in history
        this.messageHistory.push({
            role,
            content,
            timestamp: new Date().toISOString(),
            ...options
        });
    }
    
    addErrorMessage(error) {
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message assistant';
        
        const bubbleDiv = document.createElement('div');
        bubbleDiv.className = 'message-bubble error-message';
        bubbleDiv.innerHTML = `<strong>Error:</strong> ${this.escapeHtml(error)}`;
        
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        
        const agentBadge = document.createElement('span');
        agentBadge.className = 'badge bg-danger';
        agentBadge.textContent = 'System Error';
        metaDiv.appendChild(agentBadge);
        
        const timeSpan = document.createElement('span');
        timeSpan.textContent = new Date().toLocaleTimeString();
        metaDiv.appendChild(timeSpan);
        
        messageDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(metaDiv);
        
        this.chatMessages.appendChild(messageDiv);
        this.scrollToBottom();
    }
    
    formatMessageContent(content) {
        // Convert markdown-like formatting to HTML
        let formatted = this.escapeHtml(content);
        
        // Convert **bold** to <strong>
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert *italic* to <em>
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');
        
        // Convert code blocks ```code``` to <pre><code>
        formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
        
        // Convert inline `code` to <code>
        formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Convert URLs to links
        formatted = formatted.replace(
            /(https?:\/\/[^\s<>"{}|\\^`[\]]+)/g,
            '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>'
        );
        
        // Convert newlines to <br>
        formatted = formatted.replace(/\n/g, '<br>');
        
        // Convert numbered lists
        formatted = formatted.replace(/^(\d+)\.\s(.+)$/gm, '<li>$2</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ol>$1</ol>');
        
        // Convert bullet lists
        formatted = formatted.replace(/^[-•]\s(.+)$/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)/s, '<ul>$1</ul>');
        
        return formatted;
    }
    
    createCitationsElement(citations) {
        const citationsDiv = document.createElement('div');
        citationsDiv.className = 'citations';
        
        const heading = document.createElement('strong');
        heading.textContent = 'Sources:';
        citationsDiv.appendChild(heading);
        
        const citationsList = document.createElement('ol');
        citationsList.style.fontSize = '0.8rem';
        citationsList.style.marginTop = '0.5rem';
        citationsList.style.marginBottom = '0';
        
        citations.slice(0, 5).forEach(citation => {
            const listItem = document.createElement('li');
            const link = document.createElement('a');
            link.href = citation;
            link.target = '_blank';
            link.rel = 'noopener noreferrer';
            link.textContent = this.formatCitationText(citation);
            listItem.appendChild(link);
            citationsList.appendChild(listItem);
        });
        
        citationsDiv.appendChild(citationsList);
        return citationsDiv;
    }
    
    formatCitationText(url) {
        try {
            const urlObj = new URL(url);
            return urlObj.hostname + urlObj.pathname;
        } catch {
            return url;
        }
    }
    
    formatAgentName(agentType) {
        const agentNames = {
            'personal_assistant': 'Personal Assistant',
            'calendar_agent': 'Calendar Agent',
            'search_agent': 'Search Agent',
            'code_assistant': 'Code Assistant'
        };
        
        return agentNames[agentType] || agentType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    setProcessing(isProcessing) {
        this.isProcessing = isProcessing;
        
        if (isProcessing) {
            this.sendButton.disabled = true;
            this.sendButton.classList.add('btn-loading');
            this.messageInput.disabled = true;
            this.typingIndicator.style.display = 'flex';
        } else {
            this.sendButton.disabled = false;
            this.sendButton.classList.remove('btn-loading');
            this.messageInput.disabled = false;
            this.typingIndicator.style.display = 'none';
            this.messageInput.focus();
        }
        
        this.scrollToBottom();
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        }, 100);
    }
    
    updateSessionDisplay() {
        const sessionDisplay = document.getElementById('session-id');
        if (sessionDisplay) {
            sessionDisplay.textContent = `Session: ${this.sessionId}`;
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    async checkSystemStatus() {
        try {
            const response = await fetch('/api/health');
            const health = await response.json();
            
            if (response.ok && health.workflow === 'healthy') {
                this.updateStatusBadge('success', 'Connected');
            } else {
                this.updateStatusBadge('warning', 'Degraded');
            }
        } catch (error) {
            console.warn('Health check failed:', error);
            this.updateStatusBadge('danger', 'Disconnected');
        }
    }
    
    updateStatusBadge(type, text) {
        this.statusBadge.className = `badge bg-${type}`;
        this.statusBadge.innerHTML = `<i data-feather="wifi" class="me-1" style="width: 12px; height: 12px;"></i>${text}`;
        
        // Re-initialize feather icons
        if (typeof feather !== 'undefined') {
            feather.replace();
        }
    }
    
    // Public methods for external use
    clearChat() {
        this.chatMessages.innerHTML = '';
        this.messageHistory = [];
    }
    
    exportChatHistory() {
        return {
            sessionId: this.sessionId,
            messages: this.messageHistory,
            exportedAt: new Date().toISOString()
        };
    }
}

// Global chat instance
let chatInstance;

// Initialize chat function
function initializeChat(sessionId) {
    chatInstance = new ChatInterface(sessionId);
    
    // Add some helpful keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Focus on input when typing (except when in input already)
        if (e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA' && !e.ctrlKey && !e.metaKey && !e.altKey) {
            if (e.key.length === 1 || e.key === 'Backspace') {
                const messageInput = document.getElementById('messageInput');
                if (messageInput) {
                    messageInput.focus();
                }
            }
        }
        
        // Clear chat with Ctrl+L
        if ((e.ctrlKey || e.metaKey) && e.key === 'l') {
            e.preventDefault();
            if (confirm('Clear chat history?')) {
                chatInstance.clearChat();
            }
        }
    });
}

// System status checker
async function checkSystemStatus() {
    if (chatInstance) {
        await chatInstance.checkSystemStatus();
    }
}

// Export for global use
window.ChatInterface = ChatInterface;
window.initializeChat = initializeChat;
window.checkSystemStatus = checkSystemStatus;
