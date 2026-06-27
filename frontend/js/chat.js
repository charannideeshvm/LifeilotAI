// =============================================
// LIFEPILOT AI - AI CHAT
// =============================================

let chatHistory = [];
let chatUser = null;

auth.onAuthStateChanged(user => {
  if (!user) return;
  chatUser = user;
  if (document.getElementById('sidebarName')) {
    document.getElementById('sidebarName').textContent  = user.displayName || 'User';
    document.getElementById('sidebarEmail').textContent = user.email;
    document.getElementById('sidebarAvatar').textContent = (user.displayName || 'U')[0].toUpperCase();
  }
});

function handleChatKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
}

function sendQuick(msg) {
  document.getElementById('chatInput').value = msg;
  sendMessage();
}

async function sendMessage() {
  const input = document.getElementById('chatInput');
  const msg   = input.value.trim();
  if (!msg) return;

  appendMessage('user', msg);
  input.value = '';
  chatHistory.push({ role: 'user', content: msg });

  const btn = document.getElementById('sendBtn');
  btn.disabled = true;
  btn.textContent = '...';

  appendTypingIndicator();

  try {
    const data = await apiCall('/api/chat', 'POST', {
      message: msg,
      history: chatHistory.slice(-10)
    });
    removeTypingIndicator();
    appendMessage('ai', data.response);
    chatHistory.push({ role: 'assistant', content: data.response });
  } catch (e) {
    removeTypingIndicator();
    appendMessage('ai', '⚠️ Sorry, I could not connect to the AI backend. Please make sure it is running at localhost:8000.');
  }

  btn.disabled = false;
  btn.textContent = 'Send ✈️';
}

function appendMessage(role, content) {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = `message ${role}`;
  div.innerHTML = `
    <div class="msg-avatar">${role === 'user' ? '👤' : '🤖'}</div>
    <div class="msg-bubble">${content.replace(/\n/g, '<br>')}</div>
  `;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function appendTypingIndicator() {
  const container = document.getElementById('chatMessages');
  const div = document.createElement('div');
  div.className = 'message ai';
  div.id = 'typingIndicator';
  div.innerHTML = `
    <div class="msg-avatar">🤖</div>
    <div class="msg-bubble" style="display:flex;gap:4px;align-items:center">
      <span class="spinner"></span> <span style="color:var(--text-muted)">Gemini is thinking...</span>
    </div>`;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function removeTypingIndicator() {
  document.getElementById('typingIndicator')?.remove();
}

function clearChat() {
  chatHistory = [];
  const container = document.getElementById('chatMessages');
  container.innerHTML = `
    <div class="message ai">
      <div class="msg-avatar">🤖</div>
      <div class="msg-bubble"><strong>Chat cleared.</strong> How can I help you?</div>
    </div>`;
}