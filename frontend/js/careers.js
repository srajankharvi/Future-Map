// ==================== CAREERS PAGE MODULE ====================

document.addEventListener('DOMContentLoaded', () => {
    const careersGrid = document.getElementById('careersGrid');
    const careerSearch = document.getElementById('careerSearch');
    const categoryFilter = document.getElementById('categoryFilter');

    if (!careersGrid) return;

    if (careerSearch) {
        careerSearch.addEventListener('keyup', filterCareers);
    }

    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterCareers);
    }

    const closeBtn = document.querySelector('#careerModal .close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeCareerModal);
    }
});

// Display careers when global data is loaded
document.addEventListener('app:data-loaded', () => {
    if (careerData.length > 0) {
        populateCareerCategories(careerData);
        displayCareers(careerData);
    }
});

/**
 * Dynamically populate category filter from career data
 */
function populateCareerCategories(careers) {
    const categoryFilter = document.getElementById('categoryFilter');
    if (!categoryFilter) return;

    const categories = [...new Set(careers.map(c => c.category).filter(Boolean))].sort();
    
    // Keep the first "All Categories" option, remove the rest
    categoryFilter.innerHTML = '<option value="">All Categories</option>';
    categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.textContent = cat;
        categoryFilter.appendChild(option);
    });

    // Re-init custom select dropdown if the function exists
    if (typeof setupCustomSelects === 'function') {
        setupCustomSelects();
    }
}

/**
 * Display careers in grid format
 */
function displayCareers(careerList) {
    const grid = document.getElementById('careersGrid');
    if (!grid) return;

    if (careerList.length === 0) {
        grid.innerHTML = '<p class="text-center-muted-grid">No careers found matching your search.</p>';
        return;
    }

    const html = careerList.map(career => {
        // Handle salary - could be string or object
        let salaryText = '';
        if (typeof career.salary === 'object' && career.salary !== null) {
            salaryText = career.salary.entry_level || career.salary.fresher || '';
        } else {
            salaryText = career.salary || '';
        }

        return `
        <div class="career-card" role="button" tabindex="0" data-career-name="${escapeHTML(career.name)}">
            <div class="career-icon">${icon('briefcase', 24)}</div>
            <h3 class="career-title">${escapeHTML(career.name)}</h3>
            <span class="career-category">${escapeHTML(career.category || '')}</span>
            <p class="career-description">${escapeHTML(career.description || '')}</p>
            ${salaryText ? `<span class="career-salary">${icon('dollar', 14)} ${escapeHTML(salaryText)}</span>` : ''}
            ${career.duration ? `<span class="career-duration">${icon('clock', 14)} ${escapeHTML(career.duration)}</span>` : ''}
        </div>
    `;
    }).join('');

    grid.innerHTML = html;

    grid.querySelectorAll('.career-card').forEach(card => {
        card.addEventListener('click', () => {
            const careerName = card.getAttribute('data-career-name');
            showCareerDetails(careerName);
        });
        
        card.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const careerName = card.getAttribute('data-career-name');
                showCareerDetails(careerName);
            }
        });
    });
}

/**
 * Render an array as a list of tags
 */
function renderTags(arr, className) {
    if (!arr || !Array.isArray(arr) || arr.length === 0) return '<p>Not specified</p>';
    return arr.map(item => `<span class="${className}">${escapeHTML(item)}</span>`).join('');
}

/**
 * Render an array as a bullet list
 */
function renderList(arr) {
    if (!arr || !Array.isArray(arr) || arr.length === 0) return '<p>Not specified</p>';
    return '<ul class="detail-list">' + arr.map(item => `<li>${escapeHTML(item)}</li>`).join('') + '</ul>';
}

/**
 * Show career details in modal
 */
function showCareerDetails(careerName) {
    const career = careerData.find(c => c.name === careerName);
    if (!career) return;

    // Handle salary display
    let salaryHtml = '';
    if (typeof career.salary === 'object' && career.salary !== null) {
        salaryHtml = `
            <div class="salary-grid">
                ${career.salary.entry_level ? `<div class="salary-item"><span class="salary-label">Entry Level</span><span class="salary-value">${escapeHTML(career.salary.entry_level)}</span></div>` : ''}
                ${career.salary.fresher ? `<div class="salary-item"><span class="salary-label">Fresher</span><span class="salary-value">${escapeHTML(career.salary.fresher)}</span></div>` : ''}
                ${career.salary.mid_level ? `<div class="salary-item"><span class="salary-label">Mid Level</span><span class="salary-value">${escapeHTML(career.salary.mid_level)}</span></div>` : ''}
                ${career.salary.experienced ? `<div class="salary-item"><span class="salary-label">Experienced</span><span class="salary-value">${escapeHTML(career.salary.experienced)}</span></div>` : ''}
            </div>
        `;
    } else {
        salaryHtml = `<p>${escapeHTML(career.salary || 'Not specified')}</p>`;
    }

    // Handle requirements display
    let requirementsHtml = '';
    if (typeof career.requirements === 'object' && career.requirements !== null && !Array.isArray(career.requirements)) {
        requirementsHtml = '<ul class="detail-list">';
        if (career.requirements.minimum_qualification) requirementsHtml += `<li><strong>Qualification:</strong> ${escapeHTML(career.requirements.minimum_qualification)}</li>`;
        if (career.requirements.minimum_marks) requirementsHtml += `<li><strong>Minimum Marks:</strong> ${escapeHTML(career.requirements.minimum_marks)}</li>`;
        if (career.requirements.age_limit) requirementsHtml += `<li><strong>Age Limit:</strong> ${escapeHTML(career.requirements.age_limit)}</li>`;
        if (career.requirements.entrance_exam) {
            const exams = Array.isArray(career.requirements.entrance_exam) ? career.requirements.entrance_exam.join(', ') : career.requirements.entrance_exam;
            requirementsHtml += `<li><strong>Entrance Exam:</strong> ${escapeHTML(exams)}</li>`;
        }
        requirementsHtml += '</ul>';
    } else if (typeof career.requirements === 'string') {
        requirementsHtml = `<p>${escapeHTML(career.requirements)}</p>`;
    } else {
        requirementsHtml = `<p>${escapeHTML(career.education || 'Not specified')}</p>`;
    }

    // Handle fees display
    let feesHtml = '';
    if (career.fees && typeof career.fees === 'object') {
        feesHtml = '<ul class="detail-list">';
        if (career.fees.government_college) feesHtml += `<li><strong>Government College:</strong> ${escapeHTML(career.fees.government_college)}</li>`;
        if (career.fees.private_college) feesHtml += `<li><strong>Private College:</strong> ${escapeHTML(career.fees.private_college)}</li>`;
        feesHtml += '</ul>';
    }

    // Handle skills - could be 'skills' or 'skills_gained'
    const skills = career.skills_gained || career.skills || [];

    const html = `
        <h2>${escapeHTML(career.name)}</h2>
        <div class="modal-meta">
            ${career.category ? `<span class="modal-tag">${escapeHTML(career.category)}</span>` : ''}
            ${career.type ? `<span class="modal-tag type-tag">${escapeHTML(career.type)}</span>` : ''}
            ${career.duration ? `<span class="modal-tag duration-tag">${icon('clock', 14)} ${escapeHTML(career.duration)}</span>` : ''}
            ${career.industry_demand ? `<span class="modal-tag demand-tag">Demand: ${escapeHTML(career.industry_demand)}</span>` : ''}
            ${career.placement_rate ? `<span class="modal-tag placement-tag">Placement: ${escapeHTML(career.placement_rate)}</span>` : ''}
        </div>

        <div class="detail-section">
            <h3>${icon('book', 18)} Overview</h3>
            <p>${escapeHTML(career.details || career.description || '')}</p>
        </div>

        <div class="detail-section">
            <h3>${icon('graduationCap', 18)} Requirements</h3>
            ${requirementsHtml}
        </div>

        ${career.eligibility ? `
        <div class="detail-section">
            <h3>${icon('checkCircle', 18)} Eligibility</h3>
            ${renderList(career.eligibility)}
        </div>
        ` : ''}

        <div class="detail-section">
            <h3>${icon('dollar', 18)} Salary Range</h3>
            ${salaryHtml}
        </div>

        <div class="detail-section">
            <h3>${icon('star', 18)} Skills</h3>
            <div class="skills-list">${renderTags(skills, 'skill-tag')}</div>
        </div>

        ${career.subjects ? `
        <div class="detail-section">
            <h3>${icon('bookOpen', 18)} Subjects</h3>
            ${renderList(career.subjects)}
        </div>
        ` : ''}

        ${career.career_options ? `
        <div class="detail-section">
            <h3>${icon('briefcase', 18)} Career Options</h3>
            <div class="skills-list">${renderTags(career.career_options, 'career-option-tag')}</div>
        </div>
        ` : ''}

        ${career.job_roles ? `
        <div class="detail-section">
            <h3>${icon('target', 18)} Job Roles</h3>
            <div class="skills-list">${renderTags(career.job_roles, 'skill-tag')}</div>
        </div>
        ` : ''}

        ${career.higher_studies ? `
        <div class="detail-section">
            <h3>${icon('trendingUp', 18)} Higher Studies</h3>
            ${renderList(career.higher_studies)}
        </div>
        ` : ''}

        ${career.top_colleges ? `
        <div class="detail-section">
            <h3>${icon('building', 18)} Top Colleges</h3>
            ${renderList(career.top_colleges)}
        </div>
        ` : ''}

        ${career.top_recruiters ? `
        <div class="detail-section">
            <h3>${icon('users', 18)} Top Recruiters</h3>
            ${renderList(career.top_recruiters)}
        </div>
        ` : ''}

        ${feesHtml ? `
        <div class="detail-section">
            <h3>${icon('dollar', 18)} Fees Structure</h3>
            ${feesHtml}
        </div>
        ` : ''}

        ${career.scope ? `
        <div class="detail-section">
            <h3>${icon('compass', 18)} Scope</h3>
            <p>${escapeHTML(career.scope)}</p>
        </div>
        ` : ''}
    `;

    const modal = document.getElementById('careerModal');
    if (modal) {
        const detailsDiv = modal.querySelector('#careerDetails');
        if (detailsDiv) {
            detailsDiv.innerHTML = html;
            showElement(modal);
        }
    }
}

/**
 * Filter careers based on search and category
 */
function filterCareers() {
    const searchEl = document.getElementById('careerSearch');
    const categoryEl = document.getElementById('categoryFilter');
    if (!searchEl || !categoryEl) return;

    const search = searchEl.value.toLowerCase();
    const category = categoryEl.value;

    const filtered = careerData.filter(career => {
        const matchesSearch = career.name.toLowerCase().includes(search) || 
                             (career.description || '').toLowerCase().includes(search) ||
                             (career.category || '').toLowerCase().includes(search);
        const matchesCategory = category === '' || career.category === category;
        return matchesSearch && matchesCategory;
    });

    displayCareers(filtered);
}
