// =============================================
// LIFEPILOT AI - UTILITY FUNCTIONS
// =============================================

// --- Dark Mode ---
function initDarkMode() {
  const saved = localStorage.getItem('darkMode') === 'true';
  if (saved) document.body.classList.add('dark');
}

function toggleDarkMode() {
  document.body.classList.toggle('dark');
  localStorage.setItem('darkMode', document.body.classList.contains('dark'));
  const btn = document.getElementById('darkToggle');
  if (btn) btn.textContent = document.body.classList.contains('dark') ? '☀️' : '🌙';
}

// --- Toast Notifications ---
function showToast(message, type = 'info', duration = 3500) {
  let container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const icons = { success: '✅', error: '❌', warning: '⚠️', info: 'ℹ️' };
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span style="font-size:1.1rem">${icons[type] || 'ℹ️'}</span>
    <span style="font-size:0.875rem;color:var(--text-main);flex:1">${message}</span>
    <button onclick="this.parentElement.remove()" style="background:none;border:none;cursor:pointer;color:var(--text-muted);font-size:1rem">×</button>
  `;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

// --- Date Helpers ---
function formatDate(dateStr) {
  if (!dateStr) return '—';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

function formatDateTime(dateStr) {
  if (!dateStr) return '—';
  const date = new Date(dateStr);
  return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
}

function timeAgo(dateStr) {
  const now = new Date();
  const past = new Date(dateStr);
  const diff = Math.floor((now - past) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff/60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff/3600)}h ago`;
  return `${Math.floor(diff/86400)}d ago`;
}

function getDaysLeft(deadlineStr) {
  if (!deadlineStr) return null;
  const now = new Date();
  const deadline = new Date(deadlineStr);
  const diff = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24));
  return diff;
}

function daysLeftLabel(deadlineStr) {
  const days = getDaysLeft(deadlineStr);
  if (days === null) return '';
  if (days < 0)  return `<span style="color:var(--danger)">${Math.abs(days)}d overdue</span>`;
  if (days === 0) return `<span style="color:var(--danger)">Due today</span>`;
  if (days === 1) return `<span style="color:var(--warning)">Due tomorrow</span>`;
  return `<span style="color:var(--text-muted)">${days}d left</span>`;
}

function getTodayString() {
  return new Date().toISOString().split('T')[0];
}

function getGreeting() {
  const hour = new Date().getHours();
  if (hour < 12) return 'Good morning';
  if (hour < 17) return 'Good afternoon';
  return 'Good evening';
}

// --- Priority Helpers ---
function priorityBadge(priority) {
  const map = {
    urgent: 'priority-urgent',
    high:   'priority-high',
    medium: 'priority-medium',
    low:    'priority-low'
  };
  return `<span class="badge ${map[priority] || 'badge-gray'}">${priority || 'medium'}</span>`;
}

function categoryIcon(category) {
  const map = {
    'Study':    '📚',
    'Work':     '💼',
    'Personal': '👤',
    'Health':   '💪',
    'Finance':  '💰',
    'Other':    '📌'
  };
  return map[category] || '📌';
}

// --- Risk Score Display ---
function riskBadge(score) {
  if (score >= 0.7) return `<span class="risk-badge risk-high">🔴 High Risk</span>`;
  if (score >= 0.4) return `<span class="risk-badge risk-medium">🟡 Medium</span>`;
  return `<span class="risk-badge risk-low">🟢 Low Risk</span>`;
}

// --- API Helper ---
const API_BASE = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
  ? 'http://localhost:8000'
  : 'https://lifeilotai-491066567011.europe-west1.run.app';

async function apiCall(endpoint, method = 'GET', body = null) {
  const token = await getAuthToken();
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
    }
  };
  if (body) options.body = JSON.stringify(body);

  const response = await fetch(`${API_BASE}${endpoint}`, options);
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || `API error: ${response.status}`);
  }
  return response.json();
}

async function getAuthToken() {
  if (typeof firebase === 'undefined') return null;
  try {
    const user = firebase.auth().currentUser;
    return user ? await user.getIdToken() : null;
  } catch { return null; }
}

// --- Local Storage Helpers ---
function saveLocal(key, data) {
  localStorage.setItem(`lifepilot_${key}`, JSON.stringify(data));
}

function loadLocal(key) {
  try {
    return JSON.parse(localStorage.getItem(`lifepilot_${key}`)) || null;
  } catch { return null; }
}

// --- Mobile Sidebar ---
function initMobileSidebar() {
  const hamburger = document.getElementById('hamburger');
  const sidebar = document.querySelector('.sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  if (!hamburger || !sidebar) return;

  hamburger.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('active');
  });

  if (overlay) {
    overlay.addEventListener('click', () => {
      sidebar.classList.remove('open');
      overlay.classList.remove('active');
    });
  }
}

// --- Initialize on every page ---
document.addEventListener('DOMContentLoaded', () => {
  initDarkMode();
  initMobileSidebar();

  const darkToggle = document.getElementById('darkToggle');
  if (darkToggle) {
    darkToggle.textContent = document.body.classList.contains('dark') ? '☀️' : '🌙';
    darkToggle.addEventListener('click', toggleDarkMode);
  }
});