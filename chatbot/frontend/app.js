// Smart Reminder AI Enhancement
const BASE_URL = window.location.port === "8000" ? "" : "http://127.0.0.1:8000";
let token = localStorage.getItem("token") || null;
let isLoginMode = true;
let glucoseChart = null;
let authSection, mainAppContainer, messagesContainer, chatInput, userInfo, typingIndicator;
let _neuralLinkOnline = false;
let _connectionBanner = null;
let _retryCountdown = 0;
let _retryTimer = null;

let reminders = [];
let glucoseData = [];

// Non-intrusive toast notification system
function _showToast(msg, type = 'error') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.cssText = 'position:fixed;bottom:2rem;right:2rem;z-index:10001;display:flex;flex-direction:column;gap:0.5rem;';
        const style = document.createElement('style');
        style.textContent = `
            .toast-msg { padding:0.85rem 1.25rem; border-radius:12px; font-size:0.85rem; font-weight:500;
                color:#e2e8f0; backdrop-filter:blur(12px); border:1px solid rgba(255,255,255,0.1);
                animation: toastIn 0.3s ease, toastOut 0.3s ease 4s forwards;
                max-width: 380px; line-height:1.4; }
            .toast-msg.error { background:rgba(239,68,68,0.2); border-color:rgba(239,68,68,0.4); }
            .toast-msg.warn { background:rgba(245,158,11,0.2); border-color:rgba(245,158,11,0.4); }
            .toast-msg.info { background:rgba(59,130,246,0.2); border-color:rgba(59,130,246,0.4); }
            .toast-msg.success { background:rgba(16,185,129,0.2); border-color:rgba(16,185,129,0.4); }
            @keyframes toastIn { from { opacity:0; transform:translateY(1rem); } to { opacity:1; transform:none; } }
            @keyframes toastOut { to { opacity:0; transform:translateY(-0.5rem); } }
        `;
        document.head.appendChild(style);
        document.body.appendChild(container);
    }
    const el = document.createElement('div');
    el.className = `toast-msg ${type}`;
    el.textContent = msg;
    container.appendChild(el);
    setTimeout(() => el.remove(), 4500);
}

// Initialization
document.addEventListener("DOMContentLoaded", () => {
    authSection = document.getElementById("auth-section");
    mainAppContainer = document.getElementById("main-app-container");
    messagesContainer = document.getElementById("messages-container");
    chatInput = document.getElementById("chat-input");
    userInfo = document.getElementById("user-info");
    typingIndicator = document.getElementById("typing-indicator");

    _createConnectionBanner();

    if (token) {
        showDashboard();
    }
    checkNeuralLink();
    // Re-check periodically
    setInterval(checkNeuralLink, 15000);
});

function _createConnectionBanner() {
    if (_connectionBanner) return;
    const banner = document.createElement("div");
    banner.id = "neural-connection-banner";
    banner.innerHTML = `
        <div class="ncb-inner">
            <div class="ncb-pulse"></div>
            <div class="ncb-content">
                <span class="ncb-icon">⚡</span>
                <span class="ncb-msg">Establishing Neural Link to backend server...</span>
                <span class="ncb-countdown"></span>
            </div>
            <button class="ncb-retry" onclick="_forceRetryNeuralLink()">Retry Now</button>
        </div>
    `;
    // Inject styles
    if (!document.getElementById("ncb-styles")) {
        const style = document.createElement("style");
        style.id = "ncb-styles";
        style.textContent = `
            #neural-connection-banner {
                position: fixed; top: 0; left: 0; right: 0; z-index: 10000;
                background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
                border-bottom: 2px solid #f59e0b;
                transform: translateY(-100%); opacity: 0;
                transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.4s ease;
                font-family: inherit;
            }
            #neural-connection-banner.ncb-visible {
                transform: translateY(0); opacity: 1;
            }
            #neural-connection-banner.ncb-online {
                border-bottom-color: #10b981;
                background: linear-gradient(135deg, #064e3b 0%, #0f172a 100%);
            }
            .ncb-inner {
                max-width: 900px; margin: 0 auto;
                display: flex; align-items: center; justify-content: center;
                gap: 1rem; padding: 0.75rem 1.5rem;
            }
            .ncb-pulse {
                width: 10px; height: 10px; border-radius: 50%;
                background: #f59e0b; flex-shrink: 0;
                animation: ncb-blink 1.5s ease-in-out infinite;
            }
            #neural-connection-banner.ncb-online .ncb-pulse {
                background: #10b981; animation: none;
            }
            @keyframes ncb-blink {
                0%, 100% { opacity: 1; box-shadow: 0 0 8px #f59e0b; }
                50% { opacity: 0.3; box-shadow: none; }
            }
            .ncb-content { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
            .ncb-icon { font-size: 1.1rem; }
            .ncb-msg { font-size: 0.85rem; color: #e2e8f0; font-weight: 500; }
            .ncb-countdown { font-size: 0.8rem; color: #94a3b8; font-weight: 600; }
            .ncb-retry {
                background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2);
                color: #e2e8f0; padding: 0.35rem 1rem; border-radius: 100px;
                font-size: 0.8rem; font-weight: 600; cursor: pointer;
                transition: background 0.2s;
            }
            .ncb-retry:hover { background: rgba(255,255,255,0.2); }
        `;
        document.head.appendChild(style);
    }
    document.body.prepend(banner);
    _connectionBanner = banner;
}

function _showBanner(msg, isOnline = false) {
    if (!_connectionBanner) return;
    const msgEl = _connectionBanner.querySelector(".ncb-msg");
    if (msgEl) msgEl.textContent = msg;
    _connectionBanner.classList.toggle("ncb-online", isOnline);
    _connectionBanner.classList.add("ncb-visible");
}

function _hideBanner() {
    if (_connectionBanner) _connectionBanner.classList.remove("ncb-visible");
}

function _startRetryCountdown(seconds) {
    clearInterval(_retryTimer);
    _retryCountdown = seconds;
    const countdownEl = _connectionBanner ? _connectionBanner.querySelector(".ncb-countdown") : null;
    _retryTimer = setInterval(() => {
        _retryCountdown--;
        if (countdownEl) countdownEl.textContent = `(retrying in ${_retryCountdown}s)`;
        if (_retryCountdown <= 0) {
            clearInterval(_retryTimer);
            checkNeuralLink();
        }
    }, 1000);
}

function _forceRetryNeuralLink() {
    clearInterval(_retryTimer);
    const countdownEl = _connectionBanner ? _connectionBanner.querySelector(".ncb-countdown") : null;
    if (countdownEl) countdownEl.textContent = "(connecting...)";
    checkNeuralLink();
}

async function checkNeuralLink() {
    const statusEl = document.getElementById("neural-status");
    const statusText = statusEl ? statusEl.querySelector(".status-text") : null;
    
    try {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 5000);
        const response = await fetch(`${BASE_URL}/health`, { signal: controller.signal });
        clearTimeout(timeout);

        if (response.ok) {
            // Connection restored
            if (!_neuralLinkOnline) {
                _showBanner("Neural Link connected successfully!", true);
                setTimeout(_hideBanner, 2500);
            }
            _neuralLinkOnline = true;
            clearInterval(_retryTimer);
            if (statusEl) statusEl.classList.add("online");
            if (statusText) statusText.innerText = "Neural Link: Active";
            return true;
        }
    } catch (err) {
        console.warn("Neural Link disconnected.");
    }
    
    // Offline
    _neuralLinkOnline = false;
    if (statusEl) statusEl.classList.remove("online");
    if (statusText) statusText.innerText = "Neural Link: Offline";
    _showBanner("Backend server unreachable. Ensure the server is running on " + (BASE_URL || "this host") + "/health");
    _startRetryCountdown(10);
    return false;
}

function switchTab(tabId) {
    document.querySelectorAll(".tab-content").forEach(t => t.classList.add("hidden"));
    document.getElementById(`tab-${tabId}`).classList.remove("hidden");
    
    document.querySelectorAll(".nav-item").forEach(item => {
        item.classList.remove("active");
        if (item.getAttribute("onclick").includes(tabId)) {
            item.classList.add("active");
        }
    });

    if (tabId === 'dashboard') {
        loadGlucoseData();
    } else if (tabId === 'reminders') {
        loadReminders();
        generateAIWellnessInsight();
    } else if (tabId === 'appointments') {
        loadAppointments();
    }
}

// ... (handleAuth, toggleAuthMode, showDashboard, loadUserProfile remain largely the same)

async function logGlucose() {
    const valueInput = document.getElementById("glucose-value");
    const value = valueInput.value;
    const type = document.getElementById("reading-type").value;

    if (!value) return _showToast("Magnitude value is required.", "warn");

    try {
        const response = await fetch(`${BASE_URL}/glucose/`, {
            method: "POST",
            headers: { 
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({ value: parseInt(value), reading_type: type })
        });

        if (response.ok) {
            valueInput.value = "";
            loadGlucoseData();
            
            // Trigger AI Guidance based on reading
            const aiMsg = getGlucoseGuidance(parseInt(value));
            addMessage(`Biometric Transmitted: ${value} mg/dL (${type}).`, "user");
            setTimeout(() => addMessage(aiMsg, "ai"), 600);
        } else {
            const err = await response.json();
            if (response.status === 401) logout();
            else _showToast("Transmission failed: " + err.detail);
        }
    } catch (err) { console.error(err); }
}

function getGlucoseGuidance(val) {
    if (val > 250) return "⚠️ **Critical Alert**: Your glucose is very high. Please prioritize hydration (water) and follow your prescribed insulin/medication routine. Monitor closely for symptoms like confusion or shortness of breath.";
    if (val > 180) return "Your glucose is elevated. I recommend drinking extra water and perhaps a 10-minute light walk to help your body process the excess sugar.";
    if (val < 70) return "⚠️ **Low Sugar Alert**: Your level is low. Please consume 15g of fast-acting carbs (juice, honey, or glucose tabs) immediately and rest until you feel stable.";
    return "Great job! Your glucose is within an optimal range. Consistency is the key to long-term health.";
}

async function loadGlucoseData() {
    try {
        const response = await fetch(`${BASE_URL}/glucose/`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        if (!response.ok) return;
        glucoseData = await response.json();
        updateVibrantDashboard(glucoseData);
        initChart([...glucoseData].reverse());
    } catch (err) { console.error(err); }
}

function updateVibrantDashboard(data) {
    if (!data || data.length === 0) return;
    const latest = data[0];
    const statEl = document.getElementById("latest-reading-stat");
    const statusEl = document.getElementById("latest-reading-status");
    const timeEl = document.getElementById("last-reading-time");
    const card = document.getElementById("stat-card-reading");

    statEl.innerText = `${latest.value} mg/dL`;
    const time = new Date(latest.timestamp);
    timeEl.innerText = time.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Logic for status and colors
    let status = "Optimal Range";
    let colorClass = "stat-blue";
    
    if (latest.value > 250) {
        status = "Critical High";
        colorClass = "stat-orange"; // Using orange for high as per existing CSS
        card.style.borderColor = "var(--error)";
    } else if (latest.value > 180) {
        status = "Elevated";
        colorClass = "stat-orange";
    } else if (latest.value < 70) {
        status = "Low Alert";
        colorClass = "stat-orange";
        card.style.borderColor = "var(--error)";
    } else {
        card.style.borderColor = "var(--glass-border)";
    }

    statusEl.innerText = status;
    card.className = `stat-card ${colorClass}`;
}

function initChart(data) {
    const ctx = document.getElementById('glucoseChart').getContext('2d');
    if (glucoseChart) glucoseChart.destroy();

    glucoseChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => new Date(d.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })),
            datasets: [{
                label: 'Glucose (mg/dL)',
                data: data.map(d => d.value),
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#3b82f6',
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            }
        }
    });
}


// --- SMART REMINDER LOGIC ---

async function loadReminders() {
    try {
        const response = await fetch(`${BASE_URL}/reminders/`, {
            headers: { "Authorization": `Bearer ${token}` }
        });
        reminders = await response.json();
        renderReminders();
        updateAnalytics();
    } catch (err) { console.error(err); }
}

function renderReminders() {
    const container = document.getElementById("reminders-list");
    if (!reminders.length) {
        container.innerHTML = '<p style="color: var(--text-gray); grid-column: span 3;">No active neural links found.</p>';
        return;
    }

    container.innerHTML = reminders.map(r => {
        const isUpcoming = r.status === 'Upcoming';
        const isMissed = r.status === 'Missed';
        const isCompleted = r.status === 'Completed';
        
        return `
            <div class="reminder-card ${isUpcoming ? 'pulse-active' : ''} ${isMissed ? 'emergency-glow' : ''}">
                <div class="reminder-type-tag">${r.reminder_type}</div>
                <div class="reminder-info">
                    <h4>${r.title}</h4>
                    <p>${r.dosage || ''} ${r.meal_timing !== 'None' ? '• ' + r.meal_timing : ''}</p>
                    <div style="margin-top: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                        <i data-lucide="clock" style="width: 14px; color: var(--text-gray);"></i>
                        <span style="font-size: 0.9rem; font-weight: 600;">${r.reminder_time}</span>
                        <span style="font-size: 0.7rem; color: var(--text-gray); margin-left: 0.5rem;">${r.frequency}</span>
                    </div>
                    ${isUpcoming ? `<div class="countdown-timer">Next: ${calculateCountdown(r.reminder_time)}</div>` : ''}
                </div>
                
                <div class="reminder-status status-${r.status.toLowerCase()}">
                    <i data-lucide="${getStatusIcon(r.status)}" style="width: 12px;"></i>
                    ${r.status}
                </div>

                <div class="reminder-actions">
                    ${isUpcoming ? `
                        <button onclick="updateReminderStatus(${r.id}, 'Completed')" class="btn-pill primary">Complete</button>
                        <button onclick="updateReminderStatus(${r.id}, 'Missed')" class="btn-pill">Miss</button>
                    ` : ''}
                    <button onclick="deleteReminder(${r.id})" class="btn-pill" style="color: var(--error);">Delete</button>
                </div>
            </div>
        `;
    }).join("");
    lucide.createIcons();
}

function getStatusIcon(status) {
    if (status === 'Completed') return 'check-circle';
    if (status === 'Missed') return 'x-circle';
    if (status === 'Delayed') return 'clock';
    return 'circle';
}

function calculateCountdown(timeStr) {
    const now = new Date();
    const [hours, minutes] = timeStr.split(':').map(Number);
    let target = new Date();
    target.setHours(hours, minutes, 0, 0);
    
    if (target < now) target.setDate(target.getDate() + 1);
    
    const diff = target - now;
    const h = Math.floor(diff / 3600000);
    const m = Math.floor((diff % 3600000) / 60000);
    return `${h}h ${m}m`;
}

async function addReminder() {
    const type = document.getElementById("rem-type").value;
    const title = document.getElementById("rem-title").value;
    const dosage = document.getElementById("rem-dosage").value;
    const time = document.getElementById("rem-time").value;
    const freq = document.getElementById("rem-freq").value;
    const meal = document.getElementById("rem-meal").value;

    if (!title || !time) return _showToast("Title and Time are required.", "warn");

    const response = await fetch(`${BASE_URL}/reminders/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({
            reminder_type: type,
            title: title,
            dosage: dosage,
            reminder_time: time,
            frequency: freq,
            meal_timing: meal,
            status: "Upcoming"
        })
    });

    if (response.ok) {
        loadReminders();
        // Clear fields
        document.getElementById("rem-title").value = "";
        document.getElementById("rem-dosage").value = "";
        document.getElementById("rem-time").value = "";
    }
}

async function updateReminderStatus(id, newStatus) {
    await fetch(`${BASE_URL}/reminders/${id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ status: newStatus })
    });
    loadReminders();
}

async function deleteReminder(id) {
    await fetch(`${BASE_URL}/reminders/${id}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
    });
    loadReminders();
}

async function createReminderFromAI() {
    const input = document.getElementById("ai-reminder-input");
    const text = input.value.trim();
    if (!text) return;

    input.value = "Processing intent...";
    try {
        const response = await fetch(`${BASE_URL}/chat/?message=${encodeURIComponent(`I want to set a reminder: ${text}. Please extract the details and respond with the [REMINDER_ACTION] tag.`)}`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await response.json();
        
        // Handle Action Tag
        const match = data.response.match(/\[REMINDER_ACTION: (.*?)\]/);
        if (match) {
            const remData = JSON.parse(match[1]);
            const createResponse = await fetch(`${BASE_URL}/reminders/`, {
                method: "POST",
                headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                body: JSON.stringify({
                    reminder_type: remData.type || "MEDICINE",
                    title: remData.title,
                    dosage: remData.dosage || "",
                    reminder_time: remData.time,
                    frequency: "Daily",
                    meal_timing: remData.meal_timing || "None",
                    status: "Upcoming"
                })
            });
            if (createResponse.ok) {
                input.value = "";
                loadReminders();
                addMessage(data.response.split('[')[0], "ai");
            }
        } else {
            input.value = text;
            _showToast("AI could not extract structured data. Please try the manual form.", "warn");
        }
    } catch (e) {
        input.value = text;
        console.error(e);
    }
}

function updateAnalytics() {
    const total = reminders.length;
    const completed = reminders.filter(r => r.status === 'Completed').length;
    const consistency = total > 0 ? Math.round((completed / total) * 100) : 0;
    
    document.getElementById("med-consistency").innerText = `${consistency}%`;
    document.getElementById("active-reminders-count").innerText = reminders.filter(r => r.status === 'Upcoming').length;
    
    const waterReminders = reminders.filter(r => r.reminder_type === 'WATER');
    const waterCompleted = waterReminders.filter(r => r.status === 'Completed').length;
    document.getElementById("water-stat-mini").innerText = `${waterCompleted}/8`;
    
    // Update main hydration stat on dashboard
    const hydrationStat = document.getElementById("hydration-stat");
    const hydrationMsg = document.getElementById("hydration-status-msg");
    const hydrationCard = hydrationStat ? hydrationStat.closest('.stat-card') : null;

    if (hydrationStat && hydrationMsg) {
        if (waterCompleted >= 8) {
            hydrationStat.innerText = "Optimal";
            hydrationMsg.innerText = "System Balanced";
            hydrationMsg.style.color = "var(--success)";
            if (hydrationCard) hydrationCard.className = "stat-card stat-green";
        } else if (waterCompleted >= 4) {
            hydrationStat.innerText = "Moderate";
            hydrationMsg.innerText = "Fluid Sync Needed";
            hydrationMsg.style.color = "var(--cyan)";
            if (hydrationCard) hydrationCard.className = "stat-card stat-cyan";
        } else {
            hydrationStat.innerText = "Dehydrated";
            hydrationMsg.innerText = "Critical Fluid Deficit";
            hydrationMsg.style.color = "var(--error)";
            if (hydrationCard) hydrationCard.className = "stat-card stat-orange";
        }
    }
}

async function generateAIWellnessInsight() {
    const insightEl = document.getElementById("ai-wellness-insight");
    try {
        const response = await fetch(`${BASE_URL}/chat/?message=${encodeURIComponent("Generate a very short intelligent wellness summary of my glucose consistency and reminder completion for today.")}`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await response.json();
        insightEl.innerText = data.response;
    } catch (e) {
        insightEl.innerText = "Wellness systems optimal. Maintain current routine.";
    }
}

// --- CHAT LOGIC ---

async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;

    addMessage(text, "user");
    chatInput.value = "";
    
    showTyping(true);
    const aiTitle = document.getElementById("ai-core-title");
    if (aiTitle) aiTitle.classList.add("neural-active");

    try {
        const response = await fetch(`${BASE_URL}/chat/?message=${encodeURIComponent(text)}`, {
            method: "POST",
            headers: { "Authorization": `Bearer ${token}` }
        });
        const data = await response.json();
        
        if (aiTitle) aiTitle.classList.remove("neural-active");
        showTyping(false);
        
        // Handle potential [REMINDER_ACTION] in chat
        if (data.response.includes("[REMINDER_ACTION:")) {
            const match = data.response.match(/\[REMINDER_ACTION: (.*?)\]/);
            if (match) {
                const remData = JSON.parse(match[1]);
                await fetch(`${BASE_URL}/reminders/`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
                    body: JSON.stringify({
                        reminder_type: remData.type || "MEDICINE",
                        title: remData.title,
                        dosage: remData.dosage || "",
                        reminder_time: remData.time,
                        frequency: "Daily",
                        meal_timing: remData.meal_timing || "None",
                        status: "Upcoming"
                    })
                });
                loadReminders();
            }
            addMessage(data.response.split('[')[0], "ai");
        } else {
            addMessage(data.response, "ai");
        }
    } catch (err) {
        showTyping(false);
        addMessage(`Connection failed. Check neural bridge.`, "ai");
    }
}

function quickSend(text) {
    chatInput.value = text;
    sendMessage();
}

function showTyping(show) {
    typingIndicator.style.display = show ? "flex" : "none";
}

function addMessage(text, type) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${type}`;
    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    msgDiv.appendChild(contentDiv);
    messagesContainer.appendChild(msgDiv);

    if (type === "ai") {
        let i = 0;
        const speed = 15;
        function typeWriter() {
            if (i < text.length) {
                contentDiv.innerText = text.substring(0, i + 1);
                i++;
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
                setTimeout(typeWriter, speed);
            } else {
                contentDiv.innerHTML = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }
        }
        typeWriter();
    } else {
        contentDiv.innerText = text;
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}

function handleKeyPress(e) { if (e.key === "Enter") sendMessage(); }

function logout() {
    token = null;
    localStorage.removeItem("token");
    location.reload();
}

function _showAuthError(msg) {
    let errEl = document.getElementById("auth-error-msg");
    if (!errEl) {
        errEl = document.createElement("div");
        errEl.id = "auth-error-msg";
        errEl.style.cssText = "background: rgba(239,68,68,0.15); border: 1px solid rgba(239,68,68,0.4); color: #fca5a5; padding: 0.75rem 1rem; border-radius: 12px; font-size: 0.85rem; text-align: center; margin-bottom: 1rem; animation: fadeIn 0.3s ease;";
        const btn = document.getElementById("auth-submit");
        btn.parentElement.insertBefore(errEl, btn);
    }
    errEl.textContent = msg;
    errEl.style.display = "block";
    setTimeout(() => { if (errEl) errEl.style.display = "none"; }, 8000);
}

async function handleAuth() {
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    if (!email || !password) return _showAuthError("Email and password are required.");
    
    const submitBtn = document.getElementById("auth-submit");
    const originalText = submitBtn.textContent;
    submitBtn.textContent = "Connecting...";
    submitBtn.disabled = true;

    try {
        if (isLoginMode) {
            const formData = new FormData();
            formData.append("username", email);
            formData.append("password", password);
            const response = await fetch(`${BASE_URL}/token`, { method: "POST", body: formData });
            if (response.ok) {
                const data = await response.json();
                token = data.access_token;
                localStorage.setItem("token", token);
                showDashboard();
            } else {
                _showAuthError("Authorization failed. Check your credentials.");
            }
        } else {
            const response = await fetch(`${BASE_URL}/register`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email, password, name: email.split('@')[0] })
            });
            if (response.ok) {
                _showAuthError("✅ Identity registered successfully! You can now log in.");
                toggleAuthMode();
            } else {
                const err = await response.json().catch(() => ({}));
                _showAuthError(err.detail || "Registration failed.");
            }
        }
    } catch (err) { 
        // No alert! The banner system handles offline state automatically.
        checkNeuralLink();
        _showAuthError("Cannot reach the server. The connection banner above will auto-retry.");
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
}

function toggleAuthMode() {
    isLoginMode = !isLoginMode;
    const title = document.querySelector("#auth-section h1");
    const submitBtn = document.getElementById("auth-submit");
    if (isLoginMode) {
        title.innerText = "DiaBeat AI";
        submitBtn.innerText = "Initialize Session";
    } else {
        title.innerText = "New Identity";
        submitBtn.innerText = "Register Identity";
    }
}

function showDashboard() {
    authSection.classList.add("hidden");
    mainAppContainer.classList.remove("hidden");
    userInfo.classList.remove("hidden");
    loadUserProfile();
    loadGlucoseData();
    if (messagesContainer.children.length === 0) {
        addMessage("Neural core online. I am DiaBeat AI. How can I help you today?", "ai");
    }
}



async function loadUserProfile() {
    const response = await fetch(`${BASE_URL}/users/me`, { headers: { "Authorization": `Bearer ${token}` } });
    if (response.ok) {
        const user = await response.json();
        document.getElementById("user-name-display").innerText = `ID: ${user.name || user.email}`;
    }
}

async function loadAppointments() {
    const response = await fetch(`${BASE_URL}/appointments/`, { headers: { "Authorization": `Bearer ${token}` } });
    const data = await response.json();
    const container = document.getElementById("appointments-list");
    container.innerHTML = data.map(a => `
        <div class="list-card">
            <div>
                <div style="font-weight: 700;">${a.doctor_name}</div>
                <div style="font-size: 0.8rem; color: var(--text-gray);">${new Date(a.appointment_time).toLocaleString()}</div>
            </div>
            <div class="chip">${a.status}</div>
        </div>
    `).join("");
}

async function bookAppointment() {
    const doctor = document.getElementById("doctor-name").value;
    const time = document.getElementById("app-time").value;
    if (!doctor || !time) return;
    await fetch(`${BASE_URL}/appointments/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify({ doctor_name: doctor, appointment_time: time })
    });
    loadAppointments();
}

async function analyzeRisk() {
    const data = {
        age: document.getElementById("risk-age").value,
        time_in_hospital: parseInt(document.getElementById("risk-time").value),
        num_lab_procedures: parseInt(document.getElementById("risk-lab").value),
        num_medications: parseInt(document.getElementById("risk-meds").value),
        number_diagnoses: parseInt(document.getElementById("risk-diag").value),
        insulin: document.getElementById("risk-insulin").value,
        change: "No",
        diabetesMed: "Yes"
    };
    const response = await fetch(`${BASE_URL}/risk/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
        body: JSON.stringify(data)
    });
    const result = await response.json();
    document.getElementById("risk-result").classList.remove("hidden");
    document.getElementById("risk-score-display").innerText = `${result.risk_score}%`;
    document.getElementById("risk-level-display").innerText = result.risk_level + " RISK";
    document.getElementById("risk-msg-display").innerText = result.message;
}

