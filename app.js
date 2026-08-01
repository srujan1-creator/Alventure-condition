// Data Store
let messagesData = [];
let currentAction = 'all';
let currentMedia = 'all';
let currentChannel = 'all';
let searchQuery = '';
let selectedMessageId = '';

// DOM Elements
const messageFeed = document.getElementById('messageFeed');
const searchInput = document.getElementById('searchInput');
const inspectorContent = document.getElementById('inspectorContent');
const inspMessageId = document.getElementById('inspMessageId');
const testerModal = document.getElementById('testerModal');
const btnOpenTester = document.getElementById('btnOpenTester');
const btnCloseTester = document.getElementById('btnCloseTester');
const testerForm = document.getElementById('testerForm');

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    fetchMessages();

    // Event Listeners for Filters
    document.querySelectorAll('#actionFilters .filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#actionFilters .filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentAction = btn.dataset.filter;
            renderFeed();
        });
    });

    document.querySelectorAll('#mediaFilters .filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#mediaFilters .filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentMedia = btn.dataset.media;
            renderFeed();
        });
    });

    document.querySelectorAll('#channelFilters .filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#channelFilters .filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentChannel = btn.dataset.channel;
            renderFeed();
        });
    });

    searchInput.addEventListener('input', (e) => {
        searchQuery = e.target.value.toLowerCase().trim();
        renderFeed();
    });

    // Modal Listeners
    btnOpenTester.addEventListener('click', () => testerModal.classList.add('open'));
    btnCloseTester.addEventListener('click', () => testerModal.classList.remove('open'));

    testerForm.addEventListener('submit', (e) => {
        e.preventDefault();
        runPythonAPIRouteTest();
    });
});

async function fetchStats() {
    try {
        const res = await fetch('/api/stats');
        if (res.ok) {
            const data = await res.json();
            document.getElementById('totalCount').textContent = data.total;
            document.getElementById('countNotify').textContent = data.notify;
            document.getElementById('countDigest').textContent = data.digest;
            document.getElementById('countMute').textContent = data.mute;
            document.getElementById('scamCountMetric').textContent = data.scam_prevented;
            document.getElementById('accMetric').textContent = `${(data.accuracy * 100).toFixed(1)}%`;

            // Update Progress Bar Ratio
            const total = data.total || 1;
            document.getElementById('barNotify').style.width = `${(data.notify / total) * 100}%`;
            document.getElementById('barDigest').style.width = `${(data.digest / total) * 100}%`;
            document.getElementById('barMute').style.width = `${(data.mute / total) * 100}%`;
        }
    } catch (err) {
        console.log("Stats fallback to local calculation", err);
    }
}

async function fetchMessages() {
    try {
        const res = await fetch('/api/messages');
        if (res.ok) {
            const data = await res.json();
            messagesData = data.messages;
            if (messagesData.length > 0) {
                selectedMessageId = messagesData[0].message_id;
                renderFeed();
                selectMessage(selectedMessageId);
            }
        }
    } catch (err) {
        console.error("Failed to fetch messages from API", err);
    }
}

function renderFeed() {
    messageFeed.innerHTML = '';

    const filtered = messagesData.filter(m => {
        if (currentAction !== 'all' && m.action !== currentAction) return false;
        if (currentMedia !== 'all') {
            if (currentMedia === 'text' && (m.media_type && m.media_type !== 'none' && m.media_type !== '')) return false;
            if (currentMedia === 'image' && m.media_type !== 'image') return false;
            if (currentMedia === 'voice' && m.media_type !== 'voice') return false;
        }
        if (currentChannel !== 'all' && m.conversation_type !== currentChannel) return false;
        if (searchQuery) {
            const matchesText = (m.message_text || '').toLowerCase().includes(searchQuery);
            const matchesUser = (m.user_id || '').toLowerCase().includes(searchQuery);
            const matchesId = (m.message_id || '').toLowerCase().includes(searchQuery);
            if (!matchesText && !matchesUser && !matchesId) return false;
        }
        return true;
    });

    if (filtered.length === 0) {
        messageFeed.innerHTML = '<div style="text-align:center; padding:40px; color:#64748b;">No messages match the selected filters.</div>';
        return;
    }

    filtered.forEach(msg => {
        const card = document.createElement('div');
        card.className = `msg-card ${msg.message_id === selectedMessageId ? 'selected' : ''}`;
        
        let mediaTagHtml = '';
        if (msg.media_type === 'image') {
            mediaTagHtml = `<div class="media-preview-tag"><i data-lucide="image"></i> Image Attachment</div>`;
        } else if (msg.media_type === 'voice') {
            mediaTagHtml = `<div class="media-preview-tag"><i data-lucide="mic"></i> Voice Note Audio</div>`;
        }

        let iconName = msg.action === 'notify' ? 'bell' : (msg.action === 'digest' ? 'inbox' : 'volume-x');

        card.innerHTML = `
            <div class="card-top">
                <div class="sender-info">
                    <div class="avatar">${(msg.user_id || 'U').substring(0, 2).toUpperCase()}</div>
                    <div>
                        <div class="sender-name">${msg.user_id || 'User'}</div>
                        <div class="channel-tag">${msg.conversation_type || 'chat'}</div>
                    </div>
                </div>
                <span class="action-badge ${msg.action}">
                    <i data-lucide="${iconName}" style="width:12px; height:12px;"></i> ${msg.action}
                </span>
            </div>
            <div class="card-content">${msg.message_text || 'Voice/Media Message'}</div>
            ${mediaTagHtml}
            <div class="card-bottom">
                <span class="type-tag">Category: <strong>${msg.message_type}</strong></span>
                <span>${msg.created_at ? msg.created_at.substring(11, 16) : 'Recent'}</span>
            </div>
        `;

        card.addEventListener('click', () => selectMessage(msg.message_id));
        messageFeed.appendChild(card);
    });

    lucide.createIcons();
}

function selectMessage(msgId) {
    selectedMessageId = msgId;
    inspMessageId.textContent = msgId;
    
    document.querySelectorAll('.msg-card').forEach(c => c.classList.remove('selected'));
    renderFeed();

    const msg = messagesData.find(m => m.message_id === msgId);
    if (!msg) return;

    let iconName = msg.action === 'notify' ? 'bell' : (msg.action === 'digest' ? 'inbox' : 'shield-alert');

    let securityCardHtml = '';
    if (msg.message_type === 'scam' || msg.message_type === 'spam' || msg.action === 'mute') {
        securityCardHtml = `
            <div class="insp-card security-card">
                <div class="security-head"><i data-lucide="shield-alert"></i> Security & Safety Override</div>
                <div style="font-size:0.84rem; color:#fca5a5;">
                    This message was evaluated for phishing, domain spoofing, and spam risk. Muted to prevent interruption and risk.
                </div>
            </div>
        `;
    }

    inspectorContent.innerHTML = `
        <div class="insp-card">
            <span class="insp-title">Final Action & Confidence</span>
            <div class="decision-hero">
                <div class="decision-icon-box ${msg.action}">
                    <i data-lucide="${iconName}" style="width:24px; height:24px;"></i>
                </div>
                <div class="decision-meta">
                    <div class="action-name" style="color: var(--color-${msg.action})">${msg.action}</div>
                    <div class="confidence-score">Confidence Calibration: <strong>${((msg.confidence || 0.95) * 100).toFixed(0)}%</strong></div>
                </div>
            </div>
        </div>

        ${securityCardHtml}

        <div class="insp-card">
            <span class="insp-title">AI Decision Reason</span>
            <div class="reason-text">${msg.reason || 'Processed via context graph rules'}</div>
        </div>

        <div class="insp-card">
            <span class="insp-title">Category & Evidence</span>
            <div class="signals-grid">
                <div class="signal-item">
                    <span class="s-label">Message Type</span>
                    <span class="s-val">${msg.message_type}</span>
                </div>
                <div class="signal-item">
                    <span class="s-label">Evidence IDs</span>
                    <span class="s-val" style="font-family: var(--font-mono)">${msg.evidence_message_ids || 'none'}</span>
                </div>
            </div>
        </div>

        <div class="insp-card">
            <span class="insp-title">Contextual Signals</span>
            <div class="signals-grid">
                <div class="signal-item">
                    <span class="s-label">Channel</span>
                    <span class="s-val">${msg.conversation_type}</span>
                </div>
                <div class="signal-item">
                    <span class="s-label">Media Attachment</span>
                    <span class="s-val">${msg.media_type || 'none'}</span>
                </div>
                <div class="signal-item">
                    <span class="s-label">User ID</span>
                    <span class="s-val">${msg.user_id}</span>
                </div>
                <div class="signal-item">
                    <span class="s-label">Forward Count</span>
                    <span class="s-val">${msg.forwarded_count || 0}</span>
                </div>
            </div>
        </div>
    `;

    lucide.createIcons();
}

async function runPythonAPIRouteTest() {
    const convType = document.getElementById('testConvType').value;
    const text = document.getElementById('testText').value.trim();
    const media = document.getElementById('testMedia').value;
    const isQuiet = document.getElementById('testQuiet').value === 'true';
    const isGroupMuted = document.getElementById('testGroupMuted').value === 'true';
    const isBizVerified = document.getElementById('testBizVerified').value === 'true';

    if (!text) {
        alert("Please enter a message content to test.");
        return;
    }

    try {
        const res = await fetch('/api/route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message_text: text,
                conversation_type: convType,
                media_type: media,
                is_quiet_hours: isQuiet,
                is_group_muted: isGroupMuted,
                is_verified_business: isBizVerified
            })
        });

        if (res.ok) {
            const data = await res.json();
            const pred = data.prediction;

            const newMsg = {
                message_id: pred.message_id,
                user_id: "sandbox_user",
                conversation_type: convType,
                message_text: text,
                media_type: media === 'none' ? 'none' : media,
                action: pred.action,
                message_type: pred.message_type,
                reason: pred.reason,
                confidence: pred.confidence,
                evidence_message_ids: pred.evidence_message_ids || "none",
                created_at: "Just now"
            };

            messagesData.unshift(newMsg);
            fetchStats();
            testerModal.classList.remove('open');
            renderFeed();
            selectMessage(newMsg.message_id);
            testerForm.reset();
        }
    } catch (err) {
        console.error("API error during live test", err);
        alert("API execution error: " + err.message);
    }
}
