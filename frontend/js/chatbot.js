// Style Coach Chatbot powered by IBM Granite model

let conversationHistory = [];

async function sendMessage(message) {
  if (!message.trim()) return;
  
  // Add user message to UI
  addMessageToUI('user', message);
  
  // Add to conversation history
  conversationHistory.push({ role: 'user', content: message });
  
  // Clear input
  const input = document.getElementById('chat-input');
  if (input) input.value = '';
  
  // Show typing indicator
  showTypingIndicator();
  
  try {
    const data = await SmartStyle.apiRequest('/api/chatbot/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: message,
        conversation_history: conversationHistory.slice(-10), // Last 10 messages
      }),
    });
    
    // Remove typing indicator
    removeTypingIndicator();
    
    // Add assistant response to UI
    addMessageToUI('assistant', data.response);
    
    // Add to conversation history
    conversationHistory.push({ role: 'assistant', content: data.response });
    
  } catch (error) {
    removeTypingIndicator();
    addMessageToUI('assistant', 'Sorry, I encountered an error. Please try again.');
  }
}

function addMessageToUI(role, content) {
  const messagesContainer = document.getElementById('chat-messages');
  if (!messagesContainer) return;
  
  const messageDiv = document.createElement('div');
  messageDiv.className = `chat-message ${role}`;
  messageDiv.textContent = content;
  
  messagesContainer.appendChild(messageDiv);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
  const messagesContainer = document.getElementById('chat-messages');
  if (!messagesContainer) return;
  
  const indicator = document.createElement('div');
  indicator.className = 'chat-message assistant';
  indicator.id = 'typing-indicator';
  indicator.innerHTML = '<em>Typing...</em>';
  
  messagesContainer.appendChild(indicator);
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function removeTypingIndicator() {
  const indicator = document.getElementById('typing-indicator');
  if (indicator) indicator.remove();
}

function startVoiceChat() {
  SmartStyle.startVoiceInput((transcript) => {
    sendMessage(transcript);
  });
}

// Quick tips
async function loadQuickTips() {
  try {
    const data = await SmartStyle.apiRequest('/api/chatbot/quick-tips');
    displayQuickTips(data.tips);
  } catch (error) {
    console.error('Failed to load quick tips');
  }
}

function displayQuickTips(tips) {
  const container = document.getElementById('quick-tips');
  if (!container) return;
  
  container.innerHTML = tips.map(tip => `
    <div class="card">
      <p>💡 ${tip}</p>
    </div>
  `).join('');
}

// Initialize chatbot
document.addEventListener('DOMContentLoaded', () => {
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-btn');
  
  if (sendBtn) {
    sendBtn.addEventListener('click', () => {
      const message = chatInput.value;
      sendMessage(message);
    });
  }
  
  if (chatInput) {
    chatInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        const message = chatInput.value;
        sendMessage(message);
      }
    });
  }
  
  // Load quick tips if on style coach page
  if (document.getElementById('quick-tips')) {
    loadQuickTips();
  }
  
  // Initial greeting
  if (document.getElementById('chat-messages')) {
    addMessageToUI('assistant', "Hi! I'm your personal Style Coach powered by IBM Granite AI. I can help you with outfit suggestions, fashion advice, and styling tips. What would you like to know?");
  }
});
