// ==================== RECOMMENDATION PAGE MODULE ====================

document.addEventListener('DOMContentLoaded', () => {
    // Setup marks input display
    const marksInput = document.getElementById('marks');
    const marksPercentage = document.getElementById('marksPercentage');

    if (marksInput && marksPercentage) {
        marksInput.addEventListener('input', () => {
            marksPercentage.textContent = marksInput.value + '%';
        });
    }

    // Setup education level dropdown
    const educationLevel = document.getElementById('educationLevel');
    const marksLabel = document.getElementById('marksLabel');

    if (educationLevel && marksLabel) {
        educationLevel.addEventListener('change', () => {
            const level = educationLevel.value;
            // Smooth transition effect
            marksLabel.style.opacity = '0';
            setTimeout(() => {
                marksLabel.textContent = `${level} Academic Marks (0-100) *`;
                marksLabel.style.opacity = '1';
            }, 200);
        });
    }

    // Setup generate recommendations button
    const generateBtn = document.querySelector('[data-action="generate-recommendations"]');
    if (generateBtn) {
        generateBtn.addEventListener('click', generateRecommendations);
    }

    // Setup reset form button
    const resetBtn = document.querySelector('[data-action="reset-form"]');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetForm);
    }

    // Setup modify profile button
    const modifyBtn = document.querySelector('[data-action="modify-profile"]');
    if (modifyBtn) {
        modifyBtn.addEventListener('click', () => {
            const resultsSection = document.getElementById('resultsSection');
            if (resultsSection) hideElement(resultsSection);
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // Setup tab buttons
    document.querySelectorAll('[data-tab]').forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');
            showTab(tabName, btn);
        });
    });

    // Setup modal close buttons
    const careerCloseBtn = document.querySelector('#careerModal .close');
    const courseCloseBtn = document.querySelector('#courseModal .close');

    if (careerCloseBtn) {
        careerCloseBtn.addEventListener('click', closeCareerModal);
    }

    if (courseCloseBtn) {
        courseCloseBtn.addEventListener('click', closeCourseModal);
    }
});

/**
 * Reset the recommendation form
 */
function resetForm() {
    const marksInput = document.getElementById('marks');
    const educationLevel = document.getElementById('educationLevel');
    const marksLabel = document.getElementById('marksLabel');
    const marksPercentage = document.getElementById('marksPercentage');
    const resultsSection = document.getElementById('resultsSection');

    if (marksInput) marksInput.value = 75;
    if (educationLevel) {
        educationLevel.value = 'SSLC';
        if (marksLabel) marksLabel.textContent = 'SSLC Academic Marks (0-100) *';
    }
    if (marksPercentage) marksPercentage.textContent = '75%';
    
    document.querySelectorAll('.skill-input').forEach(skill => {
        skill.checked = false;
    });
    
    if (resultsSection) hideElement(resultsSection);
}

/**
 * Show/switch between tabs
 */
function showTab(tabName, clickedBtn) {
    const tabs = document.querySelectorAll('.tab-content');
    const buttons = document.querySelectorAll('.tab-btn');

    tabs.forEach(tab => tab.classList.remove('active'));
    buttons.forEach(btn => btn.classList.remove('active'));

    const targetTab = document.getElementById(tabName);
    if (targetTab) {
        targetTab.classList.add('active');
    }
    
    if (clickedBtn) {
        clickedBtn.classList.add('active');
    }
}

/**
 * Generate recommendations based on user input
 */
async function generateRecommendations() {
    const marksInput = document.getElementById('marks');
    const marksValue = marksInput ? Number(marksInput.value) : 0;
    
    const selectedSkills = Array.from(document.querySelectorAll('.skill-input:checked'))
        .map(checkbox => checkbox.value);

    if (selectedSkills.length === 0) {
        alert('Please select at least one skill');
        return;
    }

    if (isNaN(marksValue) || marksValue < 0 || marksValue > 100) {
        alert('Please enter marks between 0 and 100');
        return;
    }

    // Loading state
    const generateBtn = document.querySelector('[data-action="generate-recommendations"]');
    let originalText = '';
    if (generateBtn) {
        originalText = generateBtn.textContent;
        generateBtn.textContent = 'Generating...';
        generateBtn.disabled = true;
    }

    try {
        const educationLevelValue = document.getElementById('educationLevel')?.value || 'SSLC';
        
        const result = await apiFetch(`${API_BASE}/recommendations`, {
            method: 'POST',
            body: JSON.stringify({ 
                marks: marksValue, 
                skills: selectedSkills,
                education_level: educationLevelValue
            })
        });

        if (result.success) {
            displayRecommendations(result.data.careers, result.data.courses);
        } else {
            alert(result.error || 'Error fetching recommendations');
        }
    } catch (err) {
        console.error("Recommendation error:", err);
        alert('Could not connect to server. Make sure the backend is running.');
    } finally {
        if (generateBtn) {
            generateBtn.textContent = originalText;
            generateBtn.disabled = false;
        }
    }
}

/**
 * Display recommendations results
 */
function displayRecommendations(careers, courses) {
    const careerHtml = Array.isArray(careers) && careers.length > 0 
        ? careers.map((career, idx) => `
            <div class="result-card" role="button" tabindex="0" data-career-index="${idx}">
                <div class="result-header">
                    <div class="result-title">${escapeHTML(career.name)}</div>
                    <div class="match-score">${escapeHTML(career.score)}% Match</div>
                </div>
                <p class="result-description">${escapeHTML(career.description)}</p>
                <p class="result-description result-meta">
                    <strong>Education:</strong> ${escapeHTML(career.education)} | <strong>Salary:</strong> ${escapeHTML(career.salary)}
                </p>
            </div>
        `).join('')
        : '<p class="text-center-muted">No matching careers found. Aim for higher marks and select relevant skills to unlock more opportunities!</p>';

    const courseHtml = Array.isArray(courses) && courses.length > 0
        ? courses.map((course, idx) => `
            <div class="result-card" role="button" tabindex="0" data-course-index="${idx}">
                <div class="result-header">
                    <div class="result-title">${escapeHTML(course.name)}</div>
                    <div class="match-score">${escapeHTML(course.score)}% Match</div>
                </div>
                <p class="result-description">${escapeHTML(course.description)}</p>
                <p class="result-description result-meta">
                    <strong>Duration:</strong> ${escapeHTML(course.duration)} | <strong>Type:</strong> ${escapeHTML(course.type)}
                </p>
            </div>
        `).join('')
        : '<p class="text-center-muted">No matching courses found. We recommend focusing on your current studies to improve your academic profile.</p>';

    const careerResults = document.getElementById('careerResults');
    const courseResults = document.getElementById('courseResults');
    const resultsSection = document.getElementById('resultsSection');

    if (careerResults) careerResults.innerHTML = careerHtml;
    if (courseResults) courseResults.innerHTML = courseHtml;
    if (resultsSection) showElement(resultsSection);

    // Add click handlers to open details modal for each result
    if (careerResults && Array.isArray(careers)) {
        careerResults.querySelectorAll('.result-card').forEach(card => {
            card.addEventListener('click', () => {
                const idx = parseInt(card.getAttribute('data-career-index'), 10);
                const career = careers[idx];
                if (career) showCareerModalFromObject(career);
            });

            card.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const idx = parseInt(card.getAttribute('data-career-index'), 10);
                    const career = careers[idx];
                    if (career) showCareerModalFromObject(career);
                }
            });
        });
    }

    if (courseResults && Array.isArray(courses)) {
        courseResults.querySelectorAll('.result-card').forEach(card => {
            card.addEventListener('click', () => {
                const idx = parseInt(card.getAttribute('data-course-index'), 10);
                const course = courses[idx];
                if (course) showCourseModalFromObject(course);
            });

            card.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const idx = parseInt(card.getAttribute('data-course-index'), 10);
                    const course = courses[idx];
                    if (course) showCourseModalFromObject(course);
                }
            });
        });
    }

    // Smooth scroll to results
    setTimeout(() => {
        if (resultsSection) {
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }, 100);
}

/**
 * Show career details modal using a career object (used by recommendation results)
 */
function showCareerModalFromObject(career) {
    if (!career) return;

    const skillsHtml = (career.skills || [])
        .map(skill => `<span class="skill-tag">${escapeHTML(skill)}</span>`)
        .join('');

    const html = `
        <h2>${escapeHTML(career.name)}</h2>
        <div class="detail-section">
            <h3>Overview</h3>
            <p>${escapeHTML(career.details || career.description || '')}</p>
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
 * Show course details modal using a course object (used by recommendation results)
 */
function showCourseModalFromObject(course) {
    if (!course) return;

    const html = `
        <h2>${escapeHTML(course.name)}</h2>
        <div class="detail-section">
            <h3>Program Overview</h3>
            <p>${escapeHTML(course.details || course.description || '')}</p>
        </div>
        <div class="detail-section">
            <h3>Duration</h3>
            <p>${escapeHTML(course.duration || 'Not specified')}</p>
        </div>
        <div class="detail-section">
            <h3>Admission Requirements</h3>
            <p>${escapeHTML(course.requirements || 'Not specified')}</p>
        </div>
        <div class="detail-section">
            <h3>Career Scope</h3>
            <p>${escapeHTML(course.scope || 'Not specified')}</p>
        </div>
        <div class="detail-section">
            <h3>Type</h3>
            <p>${escapeHTML(course.type || 'Not specified')}</p>
        </div>
    `;

    const modal = document.getElementById('courseModal');
    if (modal) {
        const detailsDiv = modal.querySelector('#courseDetails');
        if (detailsDiv) {
            detailsDiv.innerHTML = html;
            showElement(modal);
        }
    }
}
