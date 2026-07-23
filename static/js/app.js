let wheelChartInstance = null;
let wheelLabels = [];

// ==========================================
// 0. ПЕРЕМИКАННЯ СТОРІНОК
// ==========================================
const PAGE_IDS = ['today', 'wheel', 'chat']; // SPA-панелі, що живуть на "/"

function goToPage(pageId) {
    if (!PAGE_IDS.includes(pageId)) return;

    document.querySelectorAll('.page').forEach(el => {
        el.classList.toggle('active', el.dataset.page === pageId);
    });
    document.querySelectorAll('.nav-btn[data-page]').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.page === pageId);
    });

    if (pageId === 'chat') {
        const chatHistory = document.getElementById('chat-history');
        if (chatHistory) chatHistory.scrollTop = chatHistory.scrollHeight;
    }
}

function showToast(text) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = text;
    toast.classList.add('visible');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(() => toast.classList.remove('visible'), 2200);
}

// today/wheel/chat are SPA panels living only on "/" — if the matching
// .page exists (we're on "/"), switch instantly; otherwise (we're on
// /week, /vision, etc.) let the browser follow the href="/#today" link.
function initPageNav() {
    document.querySelectorAll('.nav-btn[data-page]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const pageId = btn.dataset.page;
            if (document.querySelector(`.page[data-page="${pageId}"]`)) {
                e.preventDefault();
                goToPage(pageId);
                history.replaceState(null, '', `#${pageId}`);
            }
        });
    });
}

// ==========================================
// 1. ІНІЦІАЛІЗАЦІЯ ПРИ ЗАВАНТАЖЕННІ СТОРІНКИ
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
    updateTodayDate();
    initPageNav();

    // deep-link support: /#wheel, /#chat coming from another page's nav
    const initialPage = (location.hash || '').slice(1);
    if (document.querySelector('.page')) {
        goToPage(PAGE_IDS.includes(initialPage) ? initialPage : 'today');
    }

    loadWheel();
    loadChatHistory();

    setInterval(updateTodayDate, 1000 * 30);

    markOverdueTasks();
    checkDueNotifications();
    setInterval(checkDueNotifications, 1000 * 60);

    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', handleSendMessage);
    }
});

// ==========================================
// 2. ЛОГІКА КОЛЕСА БАЛАНСУ (CHART.JS)
// ==========================================
function initWheelChart(labels, dataValues) {
    const ctx = document.getElementById('wheelChart');
    if (!ctx) return;

    if (wheelChartInstance) {
        wheelChartInstance.destroy();
    }

    wheelChartInstance = new Chart(ctx.getContext('2d'), {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Рівень задоволеності',
                data: dataValues,
                backgroundColor: 'rgba(44, 76, 59, 0.7)',
                borderColor: '#2C4C3B',
                pointBackgroundColor: '#BFA07A',
                pointBorderColor: '#FFF',
                pointHoverBackgroundColor: '#FFF',
                pointHoverBorderColor: '#BFA07A',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    min: 0,
                    max: 9,
                    ticks: {
                        stepSize: 3,
                        display: false
                    },
                    grid: { color: 'rgba(0, 0, 0, 0.1)' },
                    angleLines: { color: 'rgba(0, 0, 0, 0.1)' },
                    pointLabels: {
                        font: { family: "'Lato', sans-serif", size: 11, weight: 'bold' },
                        color: '#1a2332'
                    }
                }
            },
            plugins: { legend: { display: false } }
        }
    });
}

async function loadWheel() {
    try {
        const res = await fetch('/wheel');
        if (!res.ok) throw new Error('Не вдалося завантажити Колесо Балансу');
        const data = await res.json();

        wheelLabels = data.categories.map(c => c.category);
        const values = data.categories.map(c => c.score);

        initWheelChart(wheelLabels, values);
        updateWheelInsight(data.categories);
        renderPriorityBoard(data.categories);
    } catch (err) {
        console.error(err);
    }
}

function updateWheelInsight(categories) {
    const el = document.getElementById('wheel-insight-text');
    if (!el || !categories.length) return;

    const lowest = categories.reduce((a, b) => (b.score < a.score ? b : a));
    const avg = (categories.reduce((s, c) => s + c.score, 0) / categories.length).toFixed(1);

    el.innerHTML = `Your balance: <strong>${avg}/9</strong><br>` +
        `<span class="insight-subtext">Weakest area — "${lowest.category}" (${lowest.score}/9)</span>`;
}

// Maps each wheel category to a suggested action + icon for the Priority Board
const CATEGORY_META = {
    'Health': { icon: 'fa-dumbbell', action: 'Regular Exercise' },
    'Relationships': { icon: 'fa-people-roof', action: 'Family Time' },
    'Environment': { icon: 'fa-leaf', action: 'Improve Environment' },
    'Career & Purpose': { icon: 'fa-briefcase', action: 'Career Advancement' },
    'Finances': { icon: 'fa-sack-dollar', action: 'Financial Planning' },
    'Personal Growth': { icon: 'fa-seedling', action: 'Personal Development' },
    'Fun & Recreation': { icon: 'fa-mask', action: 'Make Time to Recharge' },
    'Spirituality': { icon: 'fa-om', action: 'Spiritual Practice' },
};

// Top-3 weakest categories (lowest score = highest priority to work on)
function renderPriorityBoard(categories) {
    const list = document.getElementById('priority-board-list');
    if (!list) return;

    const ranked = [...categories].sort((a, b) => a.score - b.score).slice(0, 3);
    list.innerHTML = ranked.map((c, i) => {
        const meta = CATEGORY_META[c.category] || { icon: 'fa-star', action: c.category };
        return `
        <li class="priority-row">
            <span class="priority-rank">${i + 1}</span>
            <span class="priority-icon"><i class="fa-solid ${meta.icon}"></i></span>
            <span class="priority-text">
                <span class="priority-title">${escapeHtml(meta.action)}</span>
                <span class="priority-focus">Focus: ${escapeHtml(c.category)}</span>
            </span>
        </li>`;
    }).join('');
}

// ==========================================
// 5. ДІЇ ПАНЕЛІ "КОЛЕСО": Vision & Mission / Get Recommendations / Task Tracker
// ==========================================
function goToVisionMission() {
    window.location.href = '/vision';
}

function goToTaskTracker() {
    window.location.href = '/tracker';
}

// Reuses the existing /chat endpoint (agent already sees today's tasks +
// wheel scores in its system context) — asks it for a structured plan and
// surfaces the reply in the Chat panel. No new backend route required.
async function getRecommendations() {
    const btn = document.getElementById('recommend-btn');
    if (btn) btn.disabled = true;

    goToPage('chat');
    const prompt = 'Please analyze my current tasks, Wheel of Balance scores and priorities, ' +
        'and give me a structured action plan (short numbered steps).';
    appendMessage('user', prompt);
    showLoading(true);

    try {
        const formData = new FormData();
        formData.append('message', prompt);
        const response = await fetch('/chat', { method: 'POST', body: formData });
        if (!response.ok) throw new Error('Server error');
        const data = await response.json();
        showLoading(false);
        if (data.reply) appendMessage('ai', data.reply);
        renderQuickReplies(data.quick_replies);
        await Promise.all([loadWheel(), refreshTasks()]);
    } catch (err) {
        console.error('getRecommendations failed:', err);
        showLoading(false);
        appendMessage('ai', "Sorry, something went wrong while generating recommendations.");
    } finally {
        if (btn) btn.disabled = false;
    }
}

// ==========================================
// 3. ЛОГІКА ЧАТУ
// ==========================================
async function loadChatHistory() {
    try {
        const res = await fetch('/chat/history');
        if (!res.ok) return;
        const data = await res.json();
        data.messages.forEach(m => appendMessage(m.role === 'user' ? 'user' : 'ai', m.content));
    } catch (err) {
        console.error('Не вдалося завантажити історію чату:', err);
    }
}

async function handleSendMessage(e) {
    e.preventDefault();

    const inputField = document.getElementById('chat-input');
    const sendBtn = document.querySelector('.send-btn');
    const messageText = inputField.value.trim();

    if (!messageText) return;

    appendMessage('user', messageText);
    inputField.value = '';
    if (sendBtn) sendBtn.disabled = true;

    showLoading(true);

    try {
        // Бекенд (routers/chat.py) приймає message через Form(...),
        // тож надсилаємо саме form-data, а не JSON.
        const formData = new FormData();
        formData.append('message', messageText);

        const response = await fetch('/chat', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || 'Помилка сервера');
        }

        const data = await response.json();

        showLoading(false);

        if (data.reply) {
            appendMessage('ai', data.reply);
        }
        renderQuickReplies(data.quick_replies);

        // Агент міг створити/перенести задачі або оновити Колесо Балансу —
        // підтягуємо свіжий стан обох панелей.
        await Promise.all([loadWheel(), refreshTasks()]);

    } catch (error) {
        console.error("Помилка відправки повідомлення:", error);
        showLoading(false);
        appendMessage('ai', "Вибачте, виникла помилка під час зв'язку з сервером. Спробуйте ще раз.");
    } finally {
        if (sendBtn) sendBtn.disabled = false;
    }
}

function appendMessage(sender, text) {
    const chatHistory = document.getElementById('chat-history');
    if (!chatHistory) return; // сторінка без чат-панелі (напр. /vision, /week)
    const loadingIndicator = document.getElementById('chat-loading');

    const messageRow = document.createElement('div');
    messageRow.classList.add('message-row', sender === 'user' ? 'user-row' : 'ai-row');

    if (sender === 'ai') {
        const formattedText = escapeHtml(text).replace(/\n/g, '<br>');
        messageRow.innerHTML = `
            <div class="avatar ai-avatar">GPT</div>
            <div class="message-bubble ai-bubble">${formattedText}</div>
        `;
    } else {
        messageRow.innerHTML = `
            <div class="message-bubble user-bubble">${escapeHtml(text)}</div>
        `;
    }

    chatHistory.insertBefore(messageRow, loadingIndicator);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

// Quick-reply chips: rendered under the AI's last message when the agent
// calls the offer_quick_replies tool (e.g. picking a focus category).
function renderQuickReplies(options) {
    const chatHistory = document.getElementById('chat-history');
    const loadingIndicator = document.getElementById('chat-loading');
    if (!chatHistory || !options || !options.length) return;

    const row = document.createElement('div');
    row.className = 'quick-replies-row';
    row.innerHTML = options.map(opt =>
        `<button type="button" class="quick-reply-chip" onclick="sendQuickReply(this)">${escapeHtml(opt)}</button>`
    ).join('');
    chatHistory.insertBefore(row, loadingIndicator);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function sendQuickReply(btnEl) {
    const text = btnEl.textContent;
    const row = btnEl.closest('.quick-replies-row');
    if (row) row.remove();

    const inputField = document.getElementById('chat-input');
    const chatForm = document.getElementById('chat-form');
    if (inputField) inputField.value = text;
    if (chatForm) chatForm.requestSubmit();
}

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function showLoading(isVisible) {
    const loadingIndicator = document.getElementById('chat-loading');
    if (loadingIndicator) {
        loadingIndicator.style.display = isVisible ? 'block' : 'none';
        if (isVisible) {
            const chatHistory = document.getElementById('chat-history');
            chatHistory.scrollTop = chatHistory.scrollHeight;
        }
    }
}

// ==========================================
// 4. ПАНЕЛЬ "СЬОГОДНІ"
// ==========================================
// Only the actual Today view carries data-live="true" (day-detail pages for
// other dates keep their static server-rendered title). Combines the date
// and a live clock into one line: "TODAY, FRIDAY, JULY 24 | 10:30 AM".
function updateTodayDate() {
    const dateTitle = document.getElementById('today-date-title');
    if (!dateTitle || !dateTitle.dataset.live) return;

    const now = new Date();
    const weekday = now.toLocaleDateString('en-US', { weekday: 'long' }).toUpperCase();
    const dateStr = now.toLocaleDateString('en-US', { month: 'long', day: 'numeric' }).toUpperCase();
    const time = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
    dateTitle.textContent = `TODAY, ${weekday}, ${dateStr} | ${time}`;
}

// ==========================================
// 4b. ВІДМІТКА "ВИКОНАНО" / ПЕРЕНЕСЕННЯ / СПОВІЩЕННЯ
// ==========================================
async function toggleTaskDone(checkboxEl) {
    const id = checkboxEl.dataset.id;
    const li = checkboxEl.closest('.task-item');
    const done = checkboxEl.checked;

    if (li) li.classList.toggle('done', done);

    try {
        const res = await fetch(`/api/tasks/${id}/done`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ done }),
        });
        if (!res.ok) throw new Error('request failed');
    } catch (err) {
        console.error('toggleTaskDone failed:', err);
        if (li) li.classList.toggle('done', !done);
        checkboxEl.checked = !done;
    }
}

async function forwardTask(id) {
    try {
        const res = await fetch(`/api/tasks/${id}/forward`, { method: 'POST' });
        if (!res.ok) throw new Error('request failed');
        showToast('Task pushed to the next slot');
        await refreshTasks();
    } catch (err) {
        console.error('forwardTask failed:', err);
        showToast('Could not forward the task — try again');
    }
}

// Marks tasks whose deadline date has already passed as "overdue"
// (reveals the forward button). Deadline is date-only for now.
function markOverdueTasks() {
    const todayStr = new Date().toISOString().slice(0, 10);
    document.querySelectorAll('.task-item[data-deadline]').forEach(li => {
        if (li.classList.contains('done')) return;
        if (li.dataset.deadline < todayStr) {
            li.classList.add('overdue');
        }
    });
}

// Prefers the exact scheduled_time (HH:MM) when the agent captured one;
// falls back to a once-per-day "due today" nudge when only a date exists.
// Polled every 60s, so a time-based alert fires within ~1-5 min of the mark.
const _notifiedTaskIds = new Set();
function checkDueNotifications() {
    const now = new Date();
    const todayStr = now.toISOString().slice(0, 10);
    document.querySelectorAll('.task-item[data-deadline], .task-item[data-scheduled]').forEach(li => {
        if (li.classList.contains('done')) return;
        const id = li.dataset.id;
        if (_notifiedTaskIds.has(id)) return;
        const title = li.querySelector('.task-text')?.textContent || 'A task';

        if (li.dataset.scheduled) {
            const when = new Date(li.dataset.scheduled);
            if (when <= now && now - when < 5 * 60 * 1000) {
                showNotificationBanner(`Time's up: "${title}"`);
                _notifiedTaskIds.add(id);
            }
            return;
        }
        if (li.dataset.deadline === todayStr) {
            showNotificationBanner(`Due today: "${title}"`);
            _notifiedTaskIds.add(id);
        }
    });
}

function showNotificationBanner(text) {
    const banner = document.getElementById('notification-banner');
    if (!banner) return;
    banner.textContent = text;
    banner.classList.add('visible');
    clearTimeout(showNotificationBanner._t);
    showNotificationBanner._t = setTimeout(() => banner.classList.remove('visible'), 4000);
}

async function logTaskTime(id) {
    const minutesEl = document.getElementById(`log-minutes-${id}`);
    const typeEl = document.getElementById(`log-type-${id}`);
    const minutes = parseInt(minutesEl.value, 10);
    if (!minutes || minutes <= 0) {
        showToast('Enter minutes first');
        return;
    }

    try {
        const res = await fetch(`/api/tasks/${id}/log-time`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ actual_minutes: minutes, task_type: typeEl.value || null }),
        });
        if (!res.ok) throw new Error('request failed');
        showToast('Time logged');
        location.reload();
    } catch (err) {
        console.error('logTaskTime failed:', err);
        showToast('Could not log time — try again');
    }
}

function toggleAddTaskForm() {
    const form = document.getElementById('add-task-form');
    if (form) form.style.display = form.style.display === 'none' ? 'flex' : 'none';
}

async function submitQuickTask() {
    const titleEl = document.getElementById('add-task-title');
    const timeEl = document.getElementById('add-task-time');
    const topEl = document.getElementById('add-task-top');
    const title = titleEl.value.trim();
    if (!title) {
        showToast('Enter a task title');
        return;
    }

    try {
        const res = await fetch('/api/tasks/quick-add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                title,
                is_top_task: topEl.checked,
                scheduled_time: timeEl.value || null,
            }),
        });
        if (!res.ok) throw new Error('request failed');
        titleEl.value = '';
        timeEl.value = '';
        topEl.checked = false;
        toggleAddTaskForm();
        showToast('Task added');
        await refreshTasks();
    } catch (err) {
        console.error('submitQuickTask failed:', err);
        showToast('Could not add task — try again');
    }
}

async function refreshTasks() {
    try {
        const res = await fetch('/api/today');
        if (!res.ok) return;
        const data = await res.json();
        renderTaskList('top-tasks-list', data.top_tasks, 'No priority tasks yet — add one via chat.');
        renderTaskList('small-tasks-list', data.minor_tasks, 'No minor tasks yet.');
        markOverdueTasks();
    } catch (err) {
        console.error('Failed to refresh task list:', err);
    }
}

function renderTaskList(listId, tasks, emptyText) {
    const list = document.getElementById(listId);
    if (!list) return;

    list.innerHTML = '';

    if (!tasks.length) {
        const li = document.createElement('li');
        li.className = 'task-item empty-item';
        li.innerHTML = `<span class="task-text">${escapeHtml(emptyText)}</span>`;
        list.appendChild(li);
        return;
    }

    tasks.forEach(task => {
        const done = task.completed;
        const li = document.createElement('li');
        li.className = 'task-item' + (done ? ' done' : '');
        li.dataset.id = task.id;
        if (task.deadline) li.dataset.deadline = task.deadline;
        if (task.scheduled_time) li.dataset.scheduled = task.scheduled_time;
        li.innerHTML = `
            <label class="custom-checkbox">
                <input type="checkbox" data-id="${task.id}" ${done ? 'checked' : ''} onchange="toggleTaskDone(this)">
                <span class="checkmark"></span>
                <span class="task-text">${escapeHtml(task.title)}</span>
            </label>
            <button class="task-forward-btn" data-id="${task.id}" onclick="forwardTask(${task.id})" title="Push to next slot">
                <i class="fa-solid fa-forward"></i>
            </button>
        `;
        list.appendChild(li);
    });
}