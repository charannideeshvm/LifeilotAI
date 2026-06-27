// =============================================
// LIFEPILOT AI - AUTHENTICATION
// =============================================

// Redirect to dashboard if already logged in
auth.onAuthStateChanged(user => {
  const publicPages = ['index.html', 'login.html', 'register.html', ''];
  const currentPage = window.location.pathname.split('/').pop();
  if (user && publicPages.includes(currentPage)) {
    window.location.href = 'dashboard.html';
  }
  if (!user && !publicPages.includes(currentPage)) {
    window.location.href = 'login.html';
  }
});

function showError(msg) {
  const el = document.getElementById('errorMsg');
  if (!el) return;
  el.textContent = msg;
  el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 5000);
}

function setLoading(btnId, loading) {
  const btn = document.getElementById(btnId);
  if (!btn) return;
  btn.disabled = loading;
  btn.innerHTML = loading
    ? '<span class="spinner"></span> Please wait...'
    : btn.getAttribute('data-label') || btn.textContent;
}

// Login
async function handleLogin() {
  const email = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;

  if (!email || !password) { showError('Please fill in all fields.'); return; }

  document.getElementById('loginBtn').setAttribute('data-label', 'Sign In');
  setLoading('loginBtn', true);

  try {
    await auth.signInWithEmailAndPassword(email, password);
    window.location.href = 'dashboard.html';
  } catch (err) {
    const messages = {
      'auth/user-not-found':  'No account found with this email.',
      'auth/wrong-password':  'Incorrect password.',
      'auth/invalid-email':   'Invalid email address.',
      'auth/too-many-requests': 'Too many attempts. Try again later.'
    };
    showError(messages[err.code] || 'Login failed. Please try again.');
    setLoading('loginBtn', false);
  }
}

// Register
async function handleRegister() {
  const name     = document.getElementById('name').value.trim();
  const email    = document.getElementById('email').value.trim();
  const password = document.getElementById('password').value;
  const confirm  = document.getElementById('confirmPassword').value;

  if (!name || !email || !password || !confirm) { showError('Please fill in all fields.'); return; }
  if (password !== confirm) { showError('Passwords do not match.'); return; }
  if (password.length < 8) { showError('Password must be at least 8 characters.'); return; }

  document.getElementById('registerBtn').setAttribute('data-label', 'Create Account');
  setLoading('registerBtn', true);

  try {
    const cred = await auth.createUserWithEmailAndPassword(email, password);
    await cred.user.updateProfile({ displayName: name });

    // Save user profile to Firestore
    await db.collection('users').doc(cred.user.uid).set({
      email,
      displayName: name,
      photoURL: '',
      createdAt: firebase.firestore.FieldValue.serverTimestamp(),
      settings: { darkMode: false, notifications: true, timezone: 'Asia/Kolkata' },
      stats: { totalTasksCompleted: 0, currentStreak: 0, productivityScore: 0 }
    });

    window.location.href = 'dashboard.html';
  } catch (err) {
    const messages = {
      'auth/email-already-in-use': 'An account with this email already exists.',
      'auth/invalid-email':        'Invalid email address.',
      'auth/weak-password':        'Password is too weak.'
    };
    showError(messages[err.code] || 'Registration failed. Please try again.');
    setLoading('registerBtn', false);
  }
}

// Logout
async function handleLogout() {
  try {
    await auth.signOut();
    window.location.href = 'login.html';
  } catch (err) {
    showToast('Logout failed. Try again.', 'error');
  }
}

// Allow pressing Enter to submit
document.addEventListener('keydown', (e) => {
  if (e.key !== 'Enter') return;
  if (document.getElementById('loginBtn'))    handleLogin();
  if (document.getElementById('registerBtn')) handleRegister();
});