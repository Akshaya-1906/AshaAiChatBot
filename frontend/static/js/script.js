const chatWindow = document.getElementById('chat-window');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const toggleButton = document.getElementById('toggle-button');
const suggestions = document.querySelectorAll('.suggestion');
const clearButton = document.getElementById('clear-btn');

// Scroll to bottom
function scrollToBottom() {
  chatWindow.scrollTo({
    top: chatWindow.scrollHeight,
    behavior: 'smooth'
  });
}

// Add message to chat window
function addMessage(message, sender = 'bot') {
  const messageElement = document.createElement('div');
  messageElement.classList.add('message', sender === 'bot' ? 'bot-message' : 'user-message');

  // Format any links nicely
  const formattedMessage = message.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">🔗 View</a>');
  messageElement.innerHTML = formattedMessage;

  chatWindow.appendChild(messageElement);
  scrollToBottom();
}

// Send message to backend
async function handleSend(messageText) {
  const message = messageText || userInput.value.trim();
  if (!message) return;

  addMessage(message, 'user');
  userInput.value = '';
  userInput.focus();

  // Show "thinking" loading message
  const loadingMessage = document.createElement('div');
  loadingMessage.classList.add('message', 'bot-message');
  loadingMessage.innerHTML = '⏳ Asha AI is thinking...';
  chatWindow.appendChild(loadingMessage);
  scrollToBottom();

  try {
    const response = await fetch('/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include', // Include cookies for session
      body: JSON.stringify({ message })
    });

    const data = await response.json();

    loadingMessage.remove();
    addMessage(data.reply, 'bot');
  } catch (error) {
    console.error('Chat fetch failed', error);
    loadingMessage.remove();
    addMessage("⚠️ Failed to connect to chatbot. Try again later.", 'bot');
  }
}

// Load full chat history on page load
async function loadChatHistory() {
  try {
    const response = await fetch('/history', {
      method: 'GET',
      credentials: 'include'
    });

    const data = await response.json();
    const history = data.history;

    history.forEach(message => {
      addMessage(message.content, message.role === 'assistant' ? 'bot' : 'user');
    });
  } catch (error) {
    console.error('Failed to load chat history', error);
  }
}

// Delete conversation
clearButton.addEventListener('click', async () => {
  if (!confirm("Are you sure you want to clear the conversation?")) return;

  try {
    const response = await fetch('/delete_conversation', {
      method: 'DELETE',
      credentials: 'include'
    });

    if (response.ok) {
      chatWindow.innerHTML = '';
      addMessage("🗑️ Chat history cleared!", 'bot');
    } else {
      addMessage("⚠️ Couldn't clear chat.", 'bot');
    }
  } catch (error) {
    console.error('Clear chat error:', error);
    addMessage("⚠️ Something went wrong while clearing the chat.", 'bot');
  }
});

// Button & keyboard event listeners
sendButton.addEventListener('click', () => handleSend());

userInput.addEventListener('keypress', function (e) {
  if (e.key === 'Enter') {
    e.preventDefault();
    handleSend();
  }
});

toggleButton.addEventListener('click', () => {
  const chatContainer = document.querySelector('.chatbot-container');
  chatContainer.classList.toggle('minimized');
  toggleButton.textContent = chatContainer.classList.contains('minimized') ? '+' : '−';
});

suggestions.forEach(suggestion => {
  suggestion.addEventListener('click', () => {
    handleSend(suggestion.textContent);
  });
});

// Load previous chat when page loads
window.addEventListener('load', loadChatHistory);
