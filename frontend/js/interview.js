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
});

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
    // Difficulty pills
    const pills = document.querySelectorAll('.diff-pill');
    pills.forEach(pill => {
        pill.addEventListener('click', () => {
            pills.forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            selectedLevel = pill.getAttribute('data-level');
        });
    });

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
        generateBtn.innerHTML = `
            <svg class="spin-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg>
            Generating...
        `;
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
            generateBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.912 5.813a2 2 0 0 1-1.275 1.275L3 12l5.813 1.912a2 2 0 0 1 1.275 1.275L12 21l1.912-5.813a2 2 0 0 1 1.275-1.275L21 12l-5.813-1.912a2 2 0 0 1-1.275-1.275L12 3Z"/></svg>
                Generate Questions
            `;
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
        const sourceLabel = source === 'ai' ? 'AI Generated' : 'Question Bank';
        const sourceIcon = source === 'ai'
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
