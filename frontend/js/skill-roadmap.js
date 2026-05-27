// ==================== CAREER SKILL ROADMAP TRACKER ====================

const skillRoadmapState = {
    selectedCareer: '',
    completedSkills: [],
    roadmap: null,
    progress: { completed: 0, total: 0, percent: 0 },
    loading: false,
};

document.addEventListener('DOMContentLoaded', () => {
    const section = document.getElementById('skillRoadmapSection');
    if (!section) return;

    const saveBtn = document.getElementById('saveCareerBtn');
    const careerSelect = document.getElementById('careerSelect');
    const categorySelect = document.getElementById('careerCategorySelect');

    if (saveBtn) {
        saveBtn.addEventListener('click', saveSelectedCareer);
    }
    if (careerSelect) {
        careerSelect.addEventListener('change', onSkillRoadmapCareerChange);
    }
    if (categorySelect) {
        categorySelect.addEventListener('change', filterSkillRoadmapCareers);
    }

    const initDropdowns = () => {
        populateSkillRoadmapCategoryFilter();
        populateSkillRoadmapCareerDropdown();
        initSkillRoadmap();
    };

    if (typeof careerData !== 'undefined' && careerData.length > 0) {
        initDropdowns();
    } else {
        document.addEventListener('app:data-loaded', initDropdowns, { once: true });
    }
});

function populateSkillRoadmapCategoryFilter() {
    const select = document.getElementById('careerCategorySelect');
    if (!select || typeof careerData === 'undefined') return;

    const categories = [...new Set(careerData.map(c => c.category).filter(Boolean))].sort();
    select.innerHTML = '<option value="">All Categories</option>';
    categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        select.appendChild(option);
    });

    refreshCustomSelects();
}

function populateSkillRoadmapCareerDropdown(filteredCareers = null) {
    const select = document.getElementById('careerSelect');
    if (!select || typeof careerData === 'undefined') return;

    const careers = filteredCareers || careerData;
    const previous = select.value;

    select.innerHTML = '<option value="">-- Choose a Career --</option>';
    careers.forEach(career => {
        const option = document.createElement('option');
        option.value = career.name;
        option.textContent = `${career.name} — ${career.category}`;
        select.appendChild(option);
    });

    if (previous && careers.some(c => c.name === previous)) {
        select.value = previous;
    }

    refreshCustomSelects();
}

function filterSkillRoadmapCareers() {
    const categorySelect = document.getElementById('careerCategorySelect');
    const category = categorySelect ? categorySelect.value : '';
    const filtered = category
        ? careerData.filter(c => c.category === category || (c.category && c.category.includes(category)))
        : careerData;

    populateSkillRoadmapCareerDropdown(filtered);

    const careerSelect = document.getElementById('careerSelect');
    if (careerSelect && !careerSelect.value) {
        updateSelectedCareerPreview();
    }
}

function onSkillRoadmapCareerChange() {
    updateSelectedCareerPreview();
}

function updateSelectedCareerPreview() {
    const select = document.getElementById('careerSelect');
    const label = document.getElementById('selectedCareerLabel');
    if (!label) return;

    if (select && select.value && select.value !== skillRoadmapState.selectedCareer) {
        label.textContent = `Preview: ${select.value}`;
        label.classList.remove('hidden');
    } else if (!skillRoadmapState.selectedCareer) {
        label.classList.add('hidden');
    }
}

function syncCareerSelectsFromSaved() {
    const name = skillRoadmapState.selectedCareer;
    if (!name || typeof careerData === 'undefined' || !careerData.length) return;

    const career = careerData.find(c => c.name === name);
    const categorySelect = document.getElementById('careerCategorySelect');
    const careerSelect = document.getElementById('careerSelect');

    if (career && categorySelect) {
        categorySelect.value = career.category || '';
        const filtered = categorySelect.value
            ? careerData.filter(c => c.category === categorySelect.value || (c.category && c.category.includes(categorySelect.value)))
            : careerData;
        populateSkillRoadmapCareerDropdown(filtered);
    }

    if (careerSelect) {
        careerSelect.value = name;
        refreshCustomSelects();
    }

    updateSelectedCareerLabel();
}

function refreshCustomSelects() {
    if (typeof setupCustomSelects === 'function') {
        setupCustomSelects();
    }
}

async function initSkillRoadmap() {
    await loadSkillTracker();
}

async function loadSkillTracker() {
    const stepsEl = document.getElementById('skillRoadmapSteps');
    if (!stepsEl) return;

    try {
        skillRoadmapState.loading = true;
        const result = await apiFetch(`${API_BASE}/skill-tracker`);

        if (result.status === 401) {
            window.location.href = 'login.html';
            return;
        }

        if (!result.success) {
            showSkillRoadmapMessage(result.error || 'Could not load roadmap', 'error');
            return;
        }

        skillRoadmapState.selectedCareer = result.selected_career || '';
        skillRoadmapState.completedSkills = result.completed_skills || [];
        skillRoadmapState.roadmap = result.roadmap || null;
        skillRoadmapState.progress = result.progress || { completed: 0, total: 0, percent: 0 };

        if (skillRoadmapState.selectedCareer && typeof careerData !== 'undefined' && careerData.length > 0) {
            syncCareerSelectsFromSaved();
        }

        updateSelectedCareerLabel();
        renderProgress();
        renderRoadmapSteps();
    } catch (err) {
        console.error('Skill tracker load error:', err);
        showSkillRoadmapMessage('Server error. Make sure the backend is running.', 'error');
    } finally {
        skillRoadmapState.loading = false;
    }
}

async function saveSelectedCareer() {
    const select = document.getElementById('careerSelect');
    const saveBtn = document.getElementById('saveCareerBtn');
    if (!select || !select.value) {
        showSkillRoadmapMessage('Please select a career first.', 'error');
        return;
    }

    const careerName = select.value;
    const labelSpan = saveBtn?.querySelector('.pearl-label > span:last-child');
    const originalLabel = labelSpan?.textContent || 'Save Career';

    if (saveBtn) {
        saveBtn.disabled = true;
        if (labelSpan) labelSpan.textContent = 'Saving...';
    }

    try {
        const result = await apiFetch(`${API_BASE}/skill-tracker/career`, {
            method: 'PUT',
            body: JSON.stringify({ career_name: careerName }),
        });

        if (result.status === 401) {
            window.location.href = 'login.html';
            return;
        }

        if (!result.success) {
            showSkillRoadmapMessage(result.error || 'Could not save career', 'error');
            return;
        }

        skillRoadmapState.selectedCareer = result.selected_career;
        skillRoadmapState.completedSkills = result.completed_skills || [];
        skillRoadmapState.roadmap = result.roadmap;
        skillRoadmapState.progress = result.progress;

        updateSelectedCareerLabel();
        renderProgress();
        renderRoadmapSteps();
        showSkillRoadmapMessage('Career saved! Your roadmap is ready.', 'success');
    } catch (err) {
        console.error('Save career error:', err);
        showSkillRoadmapMessage('Server error while saving career.', 'error');
    } finally {
        if (saveBtn) {
            saveBtn.disabled = false;
            if (labelSpan) labelSpan.textContent = originalLabel;
        }
    }
}

function updateSelectedCareerLabel() {
    const label = document.getElementById('selectedCareerLabel');
    const select = document.getElementById('careerSelect');
    if (!label) return;

    if (skillRoadmapState.selectedCareer) {
        label.textContent = `Active career: ${skillRoadmapState.selectedCareer}`;
        label.classList.remove('hidden');
        if (select && !select.value) {
            select.value = skillRoadmapState.selectedCareer;
            refreshCustomSelects();
        }
    } else {
        updateSelectedCareerPreview();
    }
}

function renderProgress() {
    const wrap = document.getElementById('skillRoadmapProgressWrap');
    const bar = document.getElementById('skillProgressBar');
    const pct = document.getElementById('skillProgressPercent');
    const detail = document.getElementById('skillProgressDetail');
    const { completed, total, percent } = skillRoadmapState.progress;

    if (!wrap || !skillRoadmapState.roadmap) {
        if (wrap) wrap.classList.add('hidden');
        return;
    }

    wrap.classList.remove('hidden');
    if (bar) bar.style.width = `${percent}%`;
    if (pct) pct.textContent = `${percent}%`;
    if (detail) detail.textContent = `${completed} of ${total} skills completed`;
}

function renderRoadmapSteps() {
    const container = document.getElementById('skillRoadmapSteps');
    if (!container) return;

    const roadmap = skillRoadmapState.roadmap;
    if (!roadmap || !roadmap.steps || roadmap.steps.length === 0) {
        container.innerHTML = '<p class="skill-roadmap-placeholder">Select and save a career to view your personalized skill roadmap.</p>';
        return;
    }

    const completedSet = new Set(
        (skillRoadmapState.completedSkills || []).map(s => normalizeSkillKey(s))
    );

    container.innerHTML = roadmap.steps.map((step, stepIndex) => `
        <article class="skill-roadmap-step glass-card" style="animation-delay: ${stepIndex * 0.08}s">
            <h3 class="skill-roadmap-step-title">${escapeHTML(step.title)}</h3>
            <ul class="skill-roadmap-skill-list">
                ${(step.skills || []).map(skill => renderSkillItem(skill, completedSet)).join('')}
            </ul>
        </article>
    `).join('');

    container.querySelectorAll('.skill-check-input').forEach(input => {
        input.addEventListener('change', onSkillCheckboxChange);
    });
}

function renderSkillItem(skill, completedSet) {
    const key = normalizeSkillKey(skill.key || skill.name);
    const checked = completedSet.has(key);
    const checkedAttr = checked ? 'checked' : '';
    const doneClass = checked ? ' skill-roadmap-item--done' : '';

    return `
        <li class="skill-roadmap-item${doneClass}" data-skill-key="${escapeHTML(key)}">
            <label class="skill-check-container" aria-label="Mark ${escapeHTML(skill.name)} complete">
                <input type="checkbox" class="skill-check-input" data-skill-key="${escapeHTML(key)}" ${checkedAttr}>
                <div class="checkmark">
                    <svg xmlns="http://www.w3.org/2000/svg" class="ionicon" viewBox="0 0 512 512" aria-hidden="true">
                        <path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32" d="M416 128L192 384l-96-96"></path>
                    </svg>
                </div>
            </label>
            <div class="skill-roadmap-item-body">
                <h4 class="skill-roadmap-skill-name">${escapeHTML(skill.name)}</h4>
                <p class="skill-roadmap-skill-desc">${escapeHTML(skill.description || '')}</p>
                <p class="skill-roadmap-skill-why"><strong>Why learn this?</strong> ${escapeHTML(skill.why_learn || '')}</p>
            </div>
        </li>
    `;
}

function normalizeSkillKey(key) {
    return (key || '').trim().toLowerCase();
}

async function onSkillCheckboxChange(e) {
    const input = e.target;
    const skillKey = input.getAttribute('data-skill-key');
    const completed = input.checked;

    input.disabled = true;

    try {
        const result = await apiFetch(`${API_BASE}/skill-tracker/skills`, {
            method: 'PATCH',
            body: JSON.stringify({ skill_key: skillKey, completed }),
        });

        if (result.status === 401) {
            window.location.href = 'login.html';
            return;
        }

        if (!result.success) {
            input.checked = !completed;
            showSkillRoadmapMessage(result.error || 'Could not update skill', 'error');
            return;
        }

        skillRoadmapState.completedSkills = result.completed_skills || [];
        skillRoadmapState.progress = result.progress || skillRoadmapState.progress;
        renderProgress();

        const item = input.closest('.skill-roadmap-item');
        if (item) {
            item.classList.toggle('skill-roadmap-item--done', completed);
        }
    } catch (err) {
        console.error('Toggle skill error:', err);
        input.checked = !completed;
        showSkillRoadmapMessage('Server error while updating skill.', 'error');
    } finally {
        input.disabled = false;
    }
}

function showSkillRoadmapMessage(message, type) {
    const el = document.getElementById('skillRoadmapMessage');
    if (!el) return;

    el.textContent = message;
    el.className = `skill-roadmap-msg skill-roadmap-msg--${type}`;
    el.classList.remove('hidden');

    clearTimeout(el._hideTimer);
    el._hideTimer = setTimeout(() => el.classList.add('hidden'), 5000);
}
