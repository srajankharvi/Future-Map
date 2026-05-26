// ==================== INTERVIEW PAGE MODULE ====================

document.addEventListener('DOMContentLoaded', () => {
    const interviewCategories = document.getElementById('interviewCategories');
    if (interviewCategories) {
        // Setup close button for the static questions panel
        const closeBtn = document.querySelector('[data-action="close-interview"]');
        if (closeBtn) {
            closeBtn.addEventListener('click', closeInterview);
        }
    }

    // Always initialize the AI generator UI
    setupAIGenerator();
    setupMockInterview();
    checkAndDisplayLimits(); // New: check limits on load
    updateResetTimer();
    setInterval(updateResetTimer, 60000); // Update every minute
});

// Prevent accidental refresh during interview
window.addEventListener('beforeunload', (e) => {
    if (typeof isMockActive !== 'undefined' && isMockActive) {
        e.preventDefault();
        e.returnValue = 'Interview in progress. Are you sure you want to leave?';
    }
});

function updateResetTimer() {
    const timerEls = [document.getElementById('resetTimer'), document.getElementById('resetTimerGen')];

    const now = new Date();
    const nextReset = new Date();
    nextReset.setUTCHours(24, 0, 0, 0); // Next UTC midnight

    const diff = nextReset - now;
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    timerEls.forEach(el => {
        if (el) el.textContent = `(Resets in ${hours}h ${minutes}m)`;
    });
}

/**
 * Fetch current usage counts and update the UI
 */
async function checkAndDisplayLimits() {
    try {
        const response = await apiFetch(`${API_BASE}/interview/limits`);
        if (response.success) {
            const { mock, gen } = response.limits;
            
            // Update Mock Interview UI
            const mockLimitEl = document.getElementById('resetTimer');
            if (mockLimitEl) {
                const parent = mockLimitEl.parentElement;
                if (parent) {
                    parent.innerHTML = `Used today: ${mock.count}/${mock.limit} interviews <span id="resetTimer"></span>`;
                    updateResetTimer(); // Refresh the timer span content
                }
            }
            
            const startBtn = document.getElementById('startMockBtn');
            if (startBtn && mock.count >= mock.limit) {
                // If they have an active session in this tab, don't disable yet
                if (sessionStorage.getItem('mockSessionActive') !== 'true') {
                    startBtn.disabled = true;
                    startBtn.innerHTML = `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg> Daily Limit Reached`;
                }
            }

            // Update AI Generator UI
            const genLimitEl = document.getElementById('resetTimerGen');
            if (genLimitEl) {
                const parent = genLimitEl.parentElement;
                if (parent) {
                    parent.innerHTML = `Used today: ${gen.count}/${gen.limit} generations <span id="resetTimerGen"></span>`;
                    updateResetTimer(); // Refresh the timer span content
                }
            }

            const generateBtn = document.getElementById('generateBtn');
            if (generateBtn && gen.count >= gen.limit) {
                generateBtn.disabled = true;
                generateBtn.title = "Daily limit reached. Come back tomorrow!";
            }
        }
    } catch (err) {
        console.error('Failed to fetch limits:', err);
    }
}


// ==================== MOCK INTERVIEW ====================

let mockMessages = [];
let mockQuestionCount = 0;
const MAX_MOCK_QUESTIONS = 10;
let isMockActive = false;
let mockSelectedLevel = 'beginner';
let mockPendingIntegrityNotice = '';
let lastMockIntegrityNotice = '';
let lastMockIntegrityNoticeAt = 0;
let lastMockTabViolationAt = 0;

const MOCK_CLIPBOARD_WARNING = 'Copy, paste and cut are disabled during the mock interview.';
const MOCK_TAB_WARNING = 'Warning: tab switching is not allowed during the mock interview.';
const MOCK_MOBILE_CLOSE_WARNING = 'Mock interview closed because switching apps or tabs is not allowed on mobile.';

function setupMockInterview() {
    const startBtn = document.getElementById('startMockBtn');
    const resetBtn = document.getElementById('resetMockBtn');
    const sendBtn = document.getElementById('sendMessageBtn');
    const chatInput = document.getElementById('chatInput');
    const mockDifficultyPills = document.querySelectorAll('#mockDifficultyPills .diff-pill');

    // Difficulty selection — only affects mock interview's own level
    mockDifficultyPills.forEach(pill => {
        pill.addEventListener('click', () => {
            mockDifficultyPills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            mockSelectedLevel = pill.getAttribute('data-level');
        });
    });

    if (startBtn) {
        startBtn.addEventListener('click', startMockInterview);
    }

    if (resetBtn) {
        resetBtn.addEventListener('click', resetMockInterview);
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', sendMockMessage);
    }

    if (chatInput) {
        chatInput.addEventListener('input', () => {
            sendBtn.disabled = !chatInput.value.trim() || !isMockActive;

            // Auto-resize textarea
            chatInput.style.height = 'auto';
            chatInput.style.height = (chatInput.scrollHeight) + 'px';
        });

        chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey && !sendBtn.disabled) {
                e.preventDefault();
                sendMockMessage();
            }
        });
    }

    setupMockIntegrityGuards();
}

function setupMockIntegrityGuards() {
    const mockSection = document.getElementById('mockInterview');
    const chatInput = document.getElementById('chatInput');

    if (mockSection) {
        ['copy', 'cut', 'paste', 'drop'].forEach(eventName => {
            mockSection.addEventListener(eventName, blockMockClipboardAction);
        });
        mockSection.addEventListener('contextmenu', blockMockContextMenu);
    }

    if (chatInput) {
        chatInput.addEventListener('beforeinput', blockMockPasteInput);
    }

    document.addEventListener('keydown', blockMockClipboardShortcut);
    document.addEventListener('visibilitychange', handleMockVisibilityChange);
}

function blockMockClipboardAction(event) {
    if (!isMockActive) return;

    event.preventDefault();
    showMockIntegrityWarning(MOCK_CLIPBOARD_WARNING);
}

function blockMockContextMenu(event) {
    if (!isMockActive) return;

    event.preventDefault();
    showMockIntegrityWarning(MOCK_CLIPBOARD_WARNING);
}

function blockMockPasteInput(event) {
    if (!isMockActive) return;

    const blockedInputTypes = ['insertFromPaste', 'insertFromPasteAsQuotation', 'insertFromDrop', 'insertFromYank'];
    if (blockedInputTypes.includes(event.inputType)) {
        event.preventDefault();
        showMockIntegrityWarning(MOCK_CLIPBOARD_WARNING);
    }
}

function blockMockClipboardShortcut(event) {
    if (!isMockActive) return;

    const key = event.key.toLowerCase();
    const isClipboardShortcut = (event.ctrlKey || event.metaKey) && ['c', 'v', 'x'].includes(key);
    const isInsertShortcut = key === 'insert' && (event.ctrlKey || event.shiftKey);

    if (isClipboardShortcut || isInsertShortcut) {
        event.preventDefault();
        showMockIntegrityWarning(MOCK_CLIPBOARD_WARNING);
    }
}

function handleMockVisibilityChange() {
    if (document.visibilityState === 'visible') {
        if (mockPendingIntegrityNotice) {
            const message = mockPendingIntegrityNotice;
            mockPendingIntegrityNotice = '';
            showMockIntegrityWarning(message);
        }
        return;
    }

    if (document.visibilityState === 'hidden') {
        handleMockTabViolation();
    }
}

function handleMockTabViolation() {
    if (!isMockActive) return;

    const now = Date.now();
    if (now - lastMockTabViolationAt < 1000) return;
    lastMockTabViolationAt = now;

    if (isMobileMockDevice()) {
        closeMockInterviewForIntegrity(MOCK_MOBILE_CLOSE_WARNING);
        return;
    }

    mockPendingIntegrityNotice = MOCK_TAB_WARNING;
}

function isMobileMockDevice() {
    const mobileUserAgent = /Android|iPhone|iPad|iPod|IEMobile|Opera Mini|Mobile/i.test(navigator.userAgent);
    const compactTouchViewport = window.matchMedia('(max-width: 768px) and (pointer: coarse)').matches;
    return mobileUserAgent || compactTouchViewport;
}

function showMockIntegrityWarning(message) {
    if (document.visibilityState === 'hidden') {
        mockPendingIntegrityNotice = message;
        return;
    }

    const now = Date.now();
    if (message === lastMockIntegrityNotice && now - lastMockIntegrityNoticeAt < 1500) return;
    lastMockIntegrityNotice = message;
    lastMockIntegrityNoticeAt = now;

    removeMockIntegrityWarnings();

    const warning = document.createElement('div');
    warning.className = 'mock-integrity-warning';
    warning.setAttribute('role', 'alert');

    const title = document.createElement('strong');
    title.textContent = 'Warning';
    const text = document.createElement('span');
    text.textContent = message;

    warning.appendChild(title);
    warning.appendChild(text);

    const chatMessages = document.getElementById('chatMessages');
    const mockChatbox = document.getElementById('mockChatbox');
    const mockSetup = document.getElementById('mockSetup');
    const showInChat = isMockActive && chatMessages && mockChatbox && !mockChatbox.classList.contains('hidden');

    if (showInChat) {
        warning.classList.add('in-chat');
        chatMessages.appendChild(warning);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    } else if (mockSetup) {
        mockSetup.prepend(warning);
    }

    window.setTimeout(() => {
        if (warning.parentElement) {
            warning.remove();
        }
    }, 6000);
}

function removeMockIntegrityWarnings() {
    document.querySelectorAll('.mock-integrity-warning').forEach(warning => warning.remove());
}

async function startMockInterview() {
    const category = document.getElementById('mockCategory').value;
    const level = mockSelectedLevel;

    if (!category) {
        alert('Please select a category first');
        return;
    }

    const startBtn = document.getElementById('startMockBtn');
    if (startBtn) {
        const textSpan = startBtn.querySelector('.text');
        const originalHTML = textSpan ? textSpan.innerHTML : startBtn.innerHTML;
        if (textSpan) {
            textSpan.textContent = 'Preparing...';
        } else {
            startBtn.textContent = 'Preparing...';
        }
        startBtn.disabled = true;
        
        try {
            // Only call start API if this is a fresh start (not a resume after refresh)
            const isResuming = sessionStorage.getItem('mockSessionActive') === 'true';
            
            if (!isResuming) {
                const response = await apiFetch(`${API_BASE}/mock-interview/start`, { method: 'POST' });
                if (!response.success) {
                    alert(response.error || 'Daily mock interview limit reached. Please come back tomorrow!');
                    if (textSpan) { textSpan.innerHTML = originalHTML; } else { startBtn.innerHTML = originalHTML; }
                    startBtn.disabled = false;
                    return;
                }
                // Mark session as active in this tab
                sessionStorage.setItem('mockSessionActive', 'true');
            }
        } catch (e) {
            console.error('Start interview error:', e);
        }
        
        if (textSpan) { textSpan.innerHTML = originalHTML; } else { startBtn.innerHTML = originalHTML; }
        startBtn.disabled = false;
    }

    // UI transitions
    document.getElementById('mockSetup').classList.add('hidden');
    document.getElementById('mockChatbox').classList.remove('hidden');
    document.querySelector('.mock-interview-container').classList.add('chat-active');
    
    document.getElementById('chatTitle').textContent = `Interview: ${category}`;
    document.getElementById('chatQCount').textContent = `Starting...`;
    
    isMockActive = true;
    mockQuestionCount = 0;
    mockMessages = [];
    mockPendingIntegrityNotice = '';
    lastMockTabViolationAt = 0;
    removeMockIntegrityWarnings();
    
    // Enable input area
    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.disabled = false;
        chatInput.focus();
    }
    
    // Initial AI greeting
    addChatMessage('ai', "Hi! I'm your AI interviewer today. We'll be conducting a mock interview for a " + category + " position at a " + level + " level. Are you ready to begin?");
    updateChatQCount();
}

function resetMockInterview() {
    if (confirm('Are you sure you want to reset the interview? Progress will be lost.')) {
        clearMockInterviewState();
    }
}

function closeMockInterviewForIntegrity(message) {
    clearMockInterviewState({ clearWarnings: false });
    showMockIntegrityWarning(message);
}

function clearMockInterviewState(options = {}) {
    const { refreshLimits = true, clearWarnings = true } = options;

    sessionStorage.removeItem('mockSessionActive');

    hideElement(document.getElementById('mockChatbox'));
    showElement(document.getElementById('mockSetup'));

    const mockContainer = document.querySelector('.mock-interview-container');
    if (mockContainer) {
        mockContainer.classList.remove('chat-active');
    }

    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.innerHTML = '';
    }

    const chatLoading = document.getElementById('chatLoading');
    if (chatLoading) {
        hideElement(chatLoading);
    }

    const chatInput = document.getElementById('chatInput');
    if (chatInput) {
        chatInput.value = '';
        chatInput.style.height = 'auto';
        chatInput.disabled = false;
    }

    const sendBtn = document.getElementById('sendMessageBtn');
    if (sendBtn) {
        sendBtn.disabled = true;
    }

    isMockActive = false;
    mockMessages = [];
    mockQuestionCount = 0;
    mockPendingIntegrityNotice = '';
    lastMockTabViolationAt = 0;

    if (clearWarnings) {
        removeMockIntegrityWarnings();
    }

    if (refreshLimits) {
        checkAndDisplayLimits();
    }
}

async function sendMockMessage() {
    const input = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendMessageBtn');
    const text = input.value.trim();

    if (!text || !isMockActive) return;

    // Capture current history BEFORE adding new message
    const currentHistory = [...mockMessages];

    // Add user message to UI and history
    addChatMessage('user', text);

    input.value = '';
    input.style.height = 'auto';
    sendBtn.disabled = true;
    input.disabled = true;

    // Show loading
    showElement(document.getElementById('chatLoading'));

    try {
        const category = document.getElementById('mockCategory').value;
        const level = mockSelectedLevel;

        const response = await apiFetch(`${API_BASE}/mock-interview`, {
            method: 'POST',
            body: JSON.stringify({
                category,
                level,
                message: text,
                history: currentHistory,
                question_count: mockQuestionCount
            })
        });

        if (!isMockActive) return;

        if (response.success) {
            addChatMessage('ai', response.reply);
            if (response.isQuestion) {
                mockQuestionCount++;
                updateChatQCount();
            }

            if (mockQuestionCount >= MAX_MOCK_QUESTIONS) {
                isMockActive = false;
                addChatMessage('ai', "That concludes our mock interview session! You've successfully practiced " + MAX_MOCK_QUESTIONS + " questions. You can reset to try a different category.");
                // Keep input disabled after interview ends
                input.disabled = true;
                sendBtn.disabled = true;
                return;
            }
        } else {
            addChatMessage('ai', "I'm sorry, " + (response.error || "I encountered an error. Please try again."));
        }
    } catch (err) {
        if (isMockActive) {
            addChatMessage('ai', "Network error. Please check your connection.");
        }
        console.error('Mock interview error:', err);
    } finally {
        hideElement(document.getElementById('chatLoading'));

        // Re-enable inputs only if interview is still active
        if (isMockActive) {
            input.disabled = false;
            sendBtn.disabled = false;
            input.focus();
        }
    }
}

function addChatMessage(role, text) {
    const container = document.getElementById('chatMessages');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message message-${role}`;
    msgDiv.textContent = text;

    container.appendChild(msgDiv);

    // Add to history for API
    mockMessages.push({ role, content: text });

    // Scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function updateChatQCount() {
    const countEl = document.getElementById('chatQCount');
    if (countEl) {
        countEl.textContent = `Question ${mockQuestionCount}/${MAX_MOCK_QUESTIONS}`;
    }
}


// Display interview categories when global data is loaded
document.addEventListener('app:data-loaded', () => {
    if (Object.keys(interviewQuestions).length > 0) {
        displayInterviewCategories();
    }
});


// ==================== AI GENERATOR ====================

let selectedLevel = 'beginner';
let generatedQuestions = [];
let allExpanded = false;

function setupAIGenerator() {
    // Difficulty pills — only target the AI Generator section's pills
    const genPillsContainer = document.getElementById('difficultyPills');
    if (genPillsContainer) {
        const pills = genPillsContainer.querySelectorAll('.diff-pill');
        pills.forEach(pill => {
            pill.addEventListener('click', () => {
                pills.forEach(p => p.classList.remove('active'));
                pill.classList.add('active');
                selectedLevel = pill.getAttribute('data-level');
            });
        });
    }

    // Count slider
    const slider = document.getElementById('aiCount');
    const display = document.getElementById('countDisplay');
    if (slider && display) {
        slider.addEventListener('input', () => {
            display.textContent = slider.value;
            // Update slider fill
            const val = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
            slider.style.setProperty('--slider-fill', `${val}%`);
        });
        // Init fill
        const initVal = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
        slider.style.setProperty('--slider-fill', `${initVal}%`);
    }

    // Generate button
    const generateBtn = document.getElementById('generateBtn');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateAIQuestions);
    }

    // Expand All button
    const expandBtn = document.getElementById('expandAllBtn');
    if (expandBtn) {
        expandBtn.addEventListener('click', toggleExpandAll);
    }
}


async function generateAIQuestions() {
    const category = document.getElementById('aiCategory').value;
    const count = parseInt(document.getElementById('aiCount').value);
    const errorEl = document.getElementById('aiError');
    const loadingEl = document.getElementById('aiLoading');
    const resultsEl = document.getElementById('aiResults');
    const generateBtn = document.getElementById('generateBtn');

    // Validate
    if (!category) {
        showAIError('Please select a career category');
        return;
    }

    // Hide previous results and errors
    hideElement(errorEl);
    hideElement(resultsEl);
    showElement(loadingEl);

    // Disable button
    if (generateBtn) {
        generateBtn.disabled = true;
        const textSpan = generateBtn.querySelector('.text');
        if (textSpan) {
            textSpan.innerHTML = `
                <svg class="spin-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
                Generating...
            `;
        } else {
            generateBtn.innerHTML = `
                <svg class="spin-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
                Generating...
            `;
        }
    }

    try {
        const response = await apiFetch(`${API_BASE}/generate-interview-questions`, {
            method: 'POST',
            body: JSON.stringify({
                category: category,
                level: selectedLevel,
                count: count
            })
        });

        if (response.success && response.data) {
            generatedQuestions = response.data;
            renderGeneratedQuestions(response.data, category, response.source);
            hideElement(loadingEl);
            showElement(resultsEl);

            // Scroll to results
            setTimeout(() => {
                resultsEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }, 200);
        } else {
            hideElement(loadingEl);
            showAIError(response.error || 'Failed to generate questions. Please try again.');
        }

    } catch (err) {
        hideElement(loadingEl);
        showAIError('Network error. Please check your connection and try again.');
        console.error('AI generation error:', err);
    } finally {
        // Re-enable button
        if (generateBtn) {
            generateBtn.disabled = false;
            const textSpan = generateBtn.querySelector('.text');
            const restoreHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
                Generate Questions
            `;
            if (textSpan) {
                textSpan.innerHTML = restoreHTML;
            } else {
                generateBtn.innerHTML = restoreHTML;
            }
        }
    }
}


function renderGeneratedQuestions(questions, category, source) {
    const listEl = document.getElementById('aiQuestionsList');
    const titleEl = document.getElementById('aiResultsTitle');
    const metaEl = document.getElementById('aiResultsMeta');

    if (!listEl) return;

    // Update header
    const levelLabel = selectedLevel.charAt(0).toUpperCase() + selectedLevel.slice(1);
    if (titleEl) titleEl.textContent = `${escapeHTML(category)} Questions`;
    if (metaEl) {
        const isAI = source === 'gemini' || source === 'groq' || source === 'ai';
        const sourceLabel = isAI ? 'AI Generated' : 'Question Bank';
        const sourceIcon = isAI
            ? '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>'
            : '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>';
        metaEl.innerHTML = `${sourceIcon} ${sourceLabel} &middot; ${levelLabel} &middot; ${questions.length} questions`;
    }

    // Render questions
    const html = questions.map((q, index) => {
        const typeClass = getTypeClass(q.type);
        const typeLabel = getTypeLabel(q.type);

        return `
            <div class="ai-question-card" style="animation-delay: ${index * 0.05}s">
                <div class="ai-question-header" data-index="${index}">
                    <div class="ai-question-left">
                        <span class="ai-q-number">${index + 1}</span>
                        <span class="ai-q-text">${escapeHTML(q.question)}</span>
                    </div>
                    <div class="ai-question-right">
                        <span class="ai-type-badge ${typeClass}">${typeLabel}</span>
                        <span class="ai-toggle-arrow">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>
                        </span>
                    </div>
                </div>
                <div class="ai-answer-content">
                    <div class="ai-answer-label">Answer</div>
                    <p>${escapeHTML(q.answer)}</p>
                </div>
            </div>
        `;
    }).join('');

    listEl.innerHTML = html;
    allExpanded = false;
    updateExpandBtnText();

    // Add click handlers for toggle
    listEl.querySelectorAll('.ai-question-header').forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', () => {
            const card = header.closest('.ai-question-card');
            card.classList.toggle('expanded');
        });
    });
}


function getTypeClass(type) {
    switch ((type || '').toLowerCase()) {
        case 'scenario': return 'type-scenario';
        case 'problem': return 'type-problem';
        default: return 'type-conceptual';
    }
}

function getTypeLabel(type) {
    switch ((type || '').toLowerCase()) {
        case 'scenario': return 'Scenario';
        case 'problem': return 'Problem';
        default: return 'Conceptual';
    }
}


function showAIError(message) {
    const errorEl = document.getElementById('aiError');
    if (errorEl) {
        errorEl.innerHTML = `
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/></svg>
            ${escapeHTML(message)}
        `;
        showElement(errorEl);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            hideElement(errorEl);
        }, 5000);
    }
}


function toggleExpandAll() {
    const cards = document.querySelectorAll('.ai-question-card');
    allExpanded = !allExpanded;

    cards.forEach(card => {
        if (allExpanded) {
            card.classList.add('expanded');
        } else {
            card.classList.remove('expanded');
        }
    });

    updateExpandBtnText();
}

function updateExpandBtnText() {
    const btn = document.getElementById('expandAllBtn');
    if (!btn) return;

    if (allExpanded) {
        btn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="17 11 12 6 7 11"/><polyline points="17 18 12 13 7 18"/></svg>
            Collapse All
        `;
    } else {
        btn.innerHTML = `
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="7 13 12 18 17 13"/><polyline points="7 6 12 11 17 6"/></svg>
            Expand All
        `;
    }
}


// ==================== EXISTING STATIC QUESTION FUNCTIONS ====================

/**
 * Display interview categories as buttons
 */
function displayInterviewCategories() {
    const container = document.getElementById('interviewCategories');
    if (!container) return;

    const html = Object.keys(interviewQuestions).map(category => `
        <button class="category-btn" data-category="${escapeHTML(category)}">${escapeHTML(category)}</button>
    `).join('');

    container.innerHTML = html;

    // Add event listeners to category buttons
    container.querySelectorAll('.category-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const category = btn.getAttribute('data-category');
            showInterviewQuestions(category);
        });
    });
}

/**
 * Show interview questions for a selected category
 */
function showInterviewQuestions(category) {
    const questions = interviewQuestions[category];
    if (!questions) return;

    document.getElementById('selectedCategory').textContent = category;

    const html = questions.map((q, index) => `
        <div class="question-item">
            <h4 class="question-title" data-index="${index}">
                <span class="question-number">Q${index + 1}</span>
                <span class="question-text">${escapeHTML(q.question)}</span>
                <span class="toggle-arrow">▼</span>
            </h4>
            <div class="answer-content">
                <p><strong>Answer:</strong></p>
                <p>${escapeHTML(q.answer)}</p>
            </div>
        </div>
    `).join('');

    const questionsPanel = document.getElementById('interviewQuestions');
    if (questionsPanel) {
        questionsPanel.innerHTML = html;

        // Add event listeners to question titles
        questionsPanel.querySelectorAll('.question-title').forEach(title => {
            title.style.cursor = 'pointer';
            title.addEventListener('click', () => {
                toggleAnswer(title);
            });

            title.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    toggleAnswer(title);
                }
            });
        });
    }

    const panel = document.getElementById('questionsPanel');
    if (panel) {
        showElement(panel);
    }

    // Highlight active category button
    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-category') === category) {
            btn.classList.add('active');
        }
    });

    // Scroll to questions panel
    setTimeout(() => {
        if (panel) {
            panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 100);
}

/**
 * Close interview questions panel
 */
function closeInterview() {
    const panel = document.getElementById('questionsPanel');
    if (panel) hideElement(panel);

    document.querySelectorAll('.category-btn').forEach(btn => {
        btn.classList.remove('active');
    });
}

/**
 * Toggle answer visibility
 */
function toggleAnswer(element) {
    const answerContent = element.closest('.question-item').querySelector('.answer-content');
    const arrow = element.querySelector('.toggle-arrow');

    if (!answerContent) return;

    if (answerContent.classList.contains('show')) {
        answerContent.classList.remove('show');
        if (arrow) arrow.classList.remove('open');
    } else {
        answerContent.classList.add('show');
        if (arrow) arrow.classList.add('open');
    }
}
