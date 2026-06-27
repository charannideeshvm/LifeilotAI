// =============================================
// LIFEPILOT AI - TASK MANAGEMENT
// =============================================

let allTasks = [];
let currentFilter = 'all';
let editingTaskId = null;
let currentUser = null;

auth.onAuthStateChanged(async user => {
  if (!user) return;
  currentUser = user;

  // Sidebar
  if (document.getElementById('sidebarName')) {
    document.getElementById('sidebarName').textContent  = user.displayName || 'User';
    document.getElementById('sidebarEmail').textContent = user.email;
    document.getElementById('sidebarAvatar').textContent = (user.displayName || 'U')[0].toUpperCase();
  }

  // Only run on tasks page
  if (document.getElementById('taskListContainer')) {
    await loadTasks();
  }
});

// Load all tasks for user
async function loadTasks() {
  try {
    const snap = await db.collection('tasks')
      .where('userId', '==', currentUser.uid)
      .orderBy('createdAt', 'desc')
      .get();

    allTasks = snap.docs.map(d => ({ id: d.id, ...d.data() }));
    renderTasks();
    updateTaskCount();
  } catch (e) {
    console.error('Load tasks error:', e);
    showToast('Failed to load tasks', 'error');
  }
}

function renderTasks() {
  const container = document.getElementById('taskListContainer');
  if (!container) return;

  const search = (document.getElementById('searchBox')?.value || '').toLowerCase();
  let tasks = allTasks;

  // Filter by status or priority
  if (currentFilter === 'completed') tasks = tasks.filter(t => t.status === 'completed');
  else if (currentFilter === 'pending') tasks = tasks.filter(t => t.status !== 'completed');
  else if (currentFilter === 'urgent') tasks = tasks.filter(t => t.priority === 'urgent');
  else if (currentFilter === 'high')   tasks = tasks.filter(t => t.priority === 'high');

  // Filter by search
  if (search) tasks = tasks.filter(t =>
    t.title.toLowerCase().includes(search) ||
    (t.description || '').toLowerCase().includes(search)
  );

  if (!tasks.length) {
    container.innerHTML = `<div class="empty-state"><div class="icon">📋</div><h3>No tasks found</h3><p>Create a new task to get started.</p><button class="btn btn-primary" style="margin-top:12px" onclick="openCreateModal()">+ Create Task</button></div>`;
    return;
  }

  container.innerHTML = `<div class="task-list">${tasks.map(t => renderTaskItem(t)).join('')}</div>`;
}

function renderTaskItem(t) {
  const deadline   = t.deadline?.toDate ? t.deadline.toDate() : null;
  const deadlineStr = deadline ? deadline.toISOString() : null;
  const isCompleted = t.status === 'completed';

  return `
  <div class="task-item ${isCompleted ? 'completed' : ''}" id="task-${t.id}">
    <div class="task-check ${isCompleted ? 'checked' : ''}" onclick="toggleTaskDone('${t.id}', '${t.status}')">
      ${isCompleted ? '✓' : ''}
    </div>
    <div class="task-body">
      <div class="task-title">${t.title}</div>
      <div class="task-meta">
        ${categoryIcon(t.category)} ${t.category || 'Other'}
        · ${priorityBadge(t.priority)}
        ${deadlineStr ? '· ' + daysLeftLabel(deadlineStr) : ''}
        ${t.estimatedMinutes ? '· ⏱ ' + t.estimatedMinutes + 'm' : ''}
        ${t.riskScore !== undefined ? '· ' + riskBadge(t.riskScore) : ''}
      </div>
      ${t.description ? `<div style="font-size:0.8rem;color:var(--text-muted);margin-top:4px">${t.description}</div>` : ''}
    </div>
    <div class="task-actions">
      <button class="btn btn-secondary btn-sm" onclick="openAIBreakdown('${t.id}', \`${t.title.replace(/`/g,'')}\`)">🤖 AI</button>
      <button class="btn btn-secondary btn-sm" onclick="openEditModal('${t.id}')">✏️</button>
      <button class="btn btn-danger btn-sm" onclick="deleteTask('${t.id}')">🗑</button>
    </div>
  </div>`;
}

function updateTaskCount() {
  const label = document.getElementById('taskCountLabel');
  if (!label) return;
  const pending   = allTasks.filter(t => t.status !== 'completed').length;
  const completed = allTasks.filter(t => t.status === 'completed').length;
  label.textContent = `${pending} pending · ${completed} completed`;
}

function setFilter(btn, filter) {
  currentFilter = filter;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
  renderTasks();
}

function filterTasks() { renderTasks(); }

// Modal
function openCreateModal() {
  editingTaskId = null;
  document.getElementById('modalTitle').textContent = 'Create New Task';
  document.getElementById('saveTaskBtn').textContent = 'Create Task';
  document.getElementById('taskTitle').value    = '';
  document.getElementById('taskDesc').value     = '';
  document.getElementById('taskCategory').value = 'Study';
  document.getElementById('taskPriority').value = 'medium';
  document.getElementById('taskDeadline').value = '';
  document.getElementById('taskTime').value     = '';
  document.getElementById('taskModal').classList.add('active');
}

function openEditModal(taskId) {
  const t = allTasks.find(x => x.id === taskId);
  if (!t) return;
  editingTaskId = taskId;
  document.getElementById('modalTitle').textContent = 'Edit Task';
  document.getElementById('saveTaskBtn').textContent = 'Save Changes';
  document.getElementById('taskTitle').value    = t.title;
  document.getElementById('taskDesc').value     = t.description || '';
  document.getElementById('taskCategory').value = t.category || 'Other';
  document.getElementById('taskPriority').value = t.priority || 'medium';
  document.getElementById('taskTime').value     = t.estimatedMinutes || '';
  if (t.deadline?.toDate) {
    const d = t.deadline.toDate();
    document.getElementById('taskDeadline').value = new Date(d.getTime() - d.getTimezoneOffset() * 60000).toISOString().slice(0,16);
  }
  document.getElementById('taskModal').classList.add('active');
}

function closeModal() {
  document.getElementById('taskModal').classList.remove('active');
}

// Save (create or update)
async function saveTask() {
  const title    = document.getElementById('taskTitle').value.trim();
  const desc     = document.getElementById('taskDesc').value.trim();
  const category = document.getElementById('taskCategory').value;
  const priority = document.getElementById('taskPriority').value;
  const deadline = document.getElementById('taskDeadline').value;
  const time     = document.getElementById('taskTime').value;

  if (!title) { showToast('Task title is required', 'warning'); return; }

  const btn = document.getElementById('saveTaskBtn');
  btn.disabled = true;
  btn.innerHTML = '<span class="spinner"></span> Saving...';

  const data = {
    title, category, priority,
    description:       desc || '',
    estimatedMinutes:  time ? parseInt(time) : null,
    deadline:          deadline ? firebase.firestore.Timestamp.fromDate(new Date(deadline)) : null,
    userId:            currentUser.uid,
    updatedAt:         firebase.firestore.FieldValue.serverTimestamp()
  };

  try {
    if (editingTaskId) {
      await db.collection('tasks').doc(editingTaskId).update(data);
      showToast('Task updated!', 'success');
    } else {
      data.status    = 'pending';
      data.createdAt = firebase.firestore.FieldValue.serverTimestamp();
      data.riskScore = null;
      data.subtasks  = [];
      await db.collection('tasks').add(data);
      showToast('Task created!', 'success');
    }
    closeModal();
    await loadTasks();
  } catch (e) {
    showToast('Failed to save task: ' + e.message, 'error');
  }

  btn.disabled = false;
  btn.textContent = editingTaskId ? 'Save Changes' : 'Create Task';
}

// Toggle complete
async function toggleTaskDone(taskId, currentStatus) {
  const newStatus = currentStatus === 'completed' ? 'pending' : 'completed';
  try {
    await db.collection('tasks').doc(taskId).update({
      status:      newStatus,
      completedAt: newStatus === 'completed' ? firebase.firestore.FieldValue.serverTimestamp() : null
    });
    const t = allTasks.find(x => x.id === taskId);
    if (t) t.status = newStatus;
    renderTasks();
    showToast(newStatus === 'completed' ? '✅ Task completed!' : 'Task marked as pending', 'success');
  } catch (e) {
    showToast('Failed to update task', 'error');
  }
}

// Delete
async function deleteTask(taskId) {
  if (!confirm('Delete this task?')) return;
  try {
    await db.collection('tasks').doc(taskId).delete();
    allTasks = allTasks.filter(t => t.id !== taskId);
    renderTasks();
    updateTaskCount();
    showToast('Task deleted', 'info');
  } catch (e) {
    showToast('Failed to delete task', 'error');
  }
}

// AI Breakdown (calls backend)
async function openAIBreakdown(taskId, taskTitle) {
  showToast('🤖 Asking Gemini to break down this task...', 'info', 2000);
  try {
    const data = await apiCall('/api/ai/breakdown', 'POST', { task_id: taskId, task_title: taskTitle });
    alert(`📋 AI Breakdown for "${taskTitle}":\n\n${data.subtasks.map((s,i) => `${i+1}. ${s}`).join('\n')}`);
  } catch (e) {
    showToast('AI breakdown failed. Is the backend running?', 'error');
  }
}

// Close modal on overlay click
document.getElementById('taskModal')?.addEventListener('click', function(e) {
  if (e.target === this) closeModal();
});