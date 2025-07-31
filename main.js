const form = document.getElementById('chat-form');
const input = document.getElementById('message-input');
const messagesEl = document.getElementById('messages');
const sendButton = document.getElementById('send-button');
const typingIndicator = document.getElementById('typing-indicator');
const conversationHistory = [];

// This will now work correctly with Vite's environment variable replacement
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/';

console.log('API_BASE_URL:', API_BASE_URL); // Debug log

// Text formatting functions
function formatLLMResponse(text) {
  // Convert markdown-like formatting to HTML
  let formatted = text
    // Headers
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')

    // Bold and italic
    .replace(/\*\*\*(.*?)\*\*\*/g, '<strong><em>$1</em></strong>')
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')

    // Code blocks and inline code
    .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')

    // Lists - handle numbered and bulleted
    .replace(/^\d+\.\s+(.*$)/gim, '<li>$1</li>')
    .replace(/^[\-\*\+]\s+(.*$)/gim, '<li>$1</li>')

    // Blockquotes
    .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')

    // Line breaks
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');

  // Wrap consecutive <li> elements in appropriate list tags
  formatted = formatted
    .replace(/(<li>.*?<\/li>)(\s*<li>.*?<\/li>)*/g, function(match) {
      // Check if it starts with numbers (ordered list) or bullets (unordered)
      const isOrdered = /^\d+\./.test(text.match(/(?:^|\n)[\d\-\*\+\.].*?(?=\n|$)/)?.[0] || '');
      const listTag = isOrdered ? 'ol' : 'ul';
      return `<${listTag}>${match}</${listTag}>`;
    });

  // Wrap in paragraphs if no other block elements
  if (!formatted.includes('<h') && !formatted.includes('<ul') && !formatted.includes('<ol') && !formatted.includes('<blockquote')) {
    formatted = `<p>${formatted}</p>`;
  }

  return formatted;
}

function appendMessage(text, sender) {
  const msgEl = document.createElement('div');
  msgEl.classList.add('message', sender);

  // Generate a unique ID for this message (so we can identify it later)
  const msgId = crypto.randomUUID();
  msgEl.dataset.id = msgId;

  const bubble = document.createElement('div');
  bubble.classList.add('bubble');

  if (sender === 'bot') {
    // Format the bot response
    bubble.innerHTML = formatLLMResponse(text);
  } else {
    // Keep user messages as plain text for security
    bubble.textContent = text;
  }

  msgEl.appendChild(bubble);

  // --- only for bot messages: add thumbs up/down ---
  if (sender === 'bot') {
    const feedbackEl = document.createElement('div');
    feedbackEl.classList.add('feedback');

    // Use emojis:
    feedbackEl.innerHTML = `
      <span class="thumb thumb-up">👍</span>
      <span class="thumb thumb-down">👎</span>
    `;

    msgEl.appendChild(feedbackEl);
    // Attach click handlers
    feedbackEl.querySelector('.thumb-up')
      .addEventListener('click', () => handleFeedback(msgId, 'up'));
    feedbackEl.querySelector('.thumb-down')
      .addEventListener('click', () => handleFeedback(msgId, 'down'));
  }

  const messagesEl = document.getElementById('messages');
  messagesEl.appendChild(msgEl);
  messagesEl.scrollTop = messagesEl.scrollHeight;

  const record = {
    id: msgId,
    sender,
    text: sender === 'user'
      ? text
      : bubble.innerText   // plain‑text version of the bot reply
  };
  conversationHistory.push(record);
}

function showTypingIndicator() {
  typingIndicator.classList.add('show');
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function hideTypingIndicator() {
  typingIndicator.classList.remove('show');
}

function setLoading(loading) {
  sendButton.disabled = loading;
  sendButton.textContent = loading ? 'Sending...' : 'Send';
  if (loading) {
    showTypingIndicator();
  } else {
    hideTypingIndicator();
  }
}

// Session management
let sessionId = localStorage.getItem('chat_session_id');
if (!sessionId) {
  sessionId = crypto.randomUUID();
  localStorage.setItem('chat_session_id', sessionId);
}

const modal = document.getElementById('feedback-modal');
const questionEl = document.getElementById('feedback-question');
const textarea = document.getElementById('feedback-text');
const btnSubmit = document.getElementById('feedback-submit');
const btnCancel = document.getElementById('feedback-cancel');

let pendingFeedback = null;  // will hold { messageId, type }

// Update handleFeedback to show modal instead of sending immediately
function handleFeedback(messageId, type) {
  // store so we can send after they type
  pendingFeedback = { messageId, type };
  // set the prompt text
  questionEl.textContent = (type === 'up')
    ? 'What went well?'
    : 'What went wrong?';
  textarea.value = '';
  // show the modal
  modal.style.display = 'flex';
}

// When they click Submit, send both rating and text
btnSubmit.addEventListener('click', async () => {
  if (!pendingFeedback) return;
  const { messageId, type } = pendingFeedback;
  const text = textarea.value.trim();
  const history = conversationHistory;  // snapshot of all messages so far
  // hide modal
  modal.style.display = 'none';

  // mark as selected in UI
  const msgEl = document.querySelector(`.message[data-id="${messageId}"]`);
  msgEl?.querySelector(`.thumb-${type}`)?.classList.add('selected');

  // send to server
  try {
    // feedback-submission in handleFeedback()
    await fetch(`${API_BASE_URL}/api/feedback/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
          session_id: sessionId,
          message_id: messageId,
          feedback: type,      // 'up' or 'down'
          comment: text,       // user's textual feedback
          history: history
      })
    });
  } catch (err) {
    console.error('Feedback error', err);
  }

  pendingFeedback = null;
});

// Cancel just closes it
btnCancel.addEventListener('click', () => {
  modal.style.display = 'none';
  pendingFeedback = null;
});

form.addEventListener('submit', async e => {
  e.preventDefault();
  const userMessage = input.value.trim();
  if (!userMessage) return;

  appendMessage(userMessage, 'user');
  input.value = '';
  setLoading(true);

  try {
    const payload = {
      message: userMessage,
      session_id: sessionId
    };

    const res = await fetch(`${API_BASE_URL}/api/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    const response = data.response || data.reply || 'No response received';

    appendMessage(response, 'bot');
  } catch (err) {
    console.error('Error:', err);
    appendMessage('Sorry, I encountered an error. Please try again.', 'bot');
  } finally {
    setLoading(false);
    input.focus();
  }
});

// Autofocus input on load
input.focus();

// Handle Enter key for better UX
input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    form.dispatchEvent(new Event('submit'));
  }
});