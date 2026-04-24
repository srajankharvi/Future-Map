// ==================== CAREERS PAGE MODULE ====================

document.addEventListener('DOMContentLoaded', () => {
    const careersGrid = document.getElementById('careersGrid');
    const careerSearch = document.getElementById('careerSearch');
    const categoryFilter = document.getElementById('categoryFilter');

    if (!careersGrid) return;

    // Setup event listeners
    if (careerSearch) {
        careerSearch.addEventListener('keyup', filterCareers);
    }

    if (categoryFilter) {
        categoryFilter.addEventListener('change', filterCareers);
    }

    // Setup modal close button
    const closeBtn = document.querySelector('#careerModal .close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeCareerModal);
    }
});

// Display careers when global data is loaded
document.addEventListener('app:data-loaded', () => {
    if (careerData.length > 0) {
        displayCareers(careerData);
    }
});

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

    const html = careerList.map(career => `
        <div class="career-card" role="button" tabindex="0" data-career-name="${escapeHTML(career.name)}">
            <div class="career-icon">${icon('briefcase', 24)}</div>
            <h3 class="career-title">${escapeHTML(career.name)}</h3>
            <span class="career-category">${escapeHTML(career.category)}</span>
            <p class="career-description">${escapeHTML(career.description)}</p>
        </div>
    `).join('');

    grid.innerHTML = html;

    // Add event listeners to career cards
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
 * Show career details in modal
 */
function showCareerDetails(careerName) {
    const career = careerData.find(c => c.name === careerName);
    if (!career) return;

    const skillsHtml = (career.skills || [])
        .map(skill => `<span class="skill-tag">${escapeHTML(skill)}</span>`)
        .join('');

    const html = `
        <h2>${escapeHTML(career.name)}</h2>
        <div class="detail-section">
            <h3>Overview</h3>
            <p>${escapeHTML(career.details || career.description)}</p>
        </div>
        <div class="detail-section">
            <h3>Required Skills</h3>
            <div class="skills-list">${skillsHtml || '<p>Not specified</p>'}</div>
        </div>
        <div class="detail-section">
            <h3>Education Required</h3>
            <p>${escapeHTML(career.education || 'Not specified')}</p>
        </div>
        <div class="detail-section">
            <h3>Salary Range</h3>
            <p>${escapeHTML(career.salary || 'Not specified')}</p>
        </div>
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
                             career.description.toLowerCase().includes(search);
        const matchesCategory = category === '' || 
                               career.category === category || 
                               career.category.includes(category);
        return matchesSearch && matchesCategory;
    });

    displayCareers(filtered);
}
