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

    // Ticker initialization
    if (typeof careerData !== 'undefined' && careerData.length > 0) {
        initTicker();
    }
    document.addEventListener('app:data-loaded', () => {
        initTicker();
    });
});

/**
 * Initialize popular courses and careers moving ticker
 */
function initTicker() {
    const track = document.getElementById('tickerTrack');
    if (!track) return;

    if (!careerData || careerData.length === 0 || !courseData || courseData.length === 0) {
        return;
    }

    // Curated popular career names to look for
    const popularCareerNames = [
        "Data Science",
        "Software Engineering",
        "Aeronautical Engineering",
        "Cyber Security",
        "Investment Banking",
        "UI/UX Design",
        "Artificial Intelligence",
        "Full Stack Development"
    ];

    // Curated popular course names to look for
    const popularCourseNames = [
        "Computer Science Engineering (CSE)",
        "Bachelor of Computer Applications (BCA)",
        "Master of Business Administration (MBA)",
        "Bachelor of Design (B.Des)",
        "MBBS",
        "Software Engineering",
        "Data Science",
        "Cyber Security"
    ];

    let items = [];

    // Map careers
    popularCareerNames.forEach(name => {
        const career = careerData.find(c => c.name.toLowerCase().includes(name.toLowerCase()));
        if (career) {
            items.push({
                type: 'career',
                name: career.name,
                rawObj: career
            });
        }
    });

    // Map courses
    popularCourseNames.forEach(name => {
        const course = courseData.find(c => c.name.toLowerCase().includes(name.toLowerCase()));
        if (course) {
            items.push({
                type: 'course',
                name: course.name,
                rawObj: course
            });
        }
    });

    // Fallback if not enough data
    if (items.length < 5) {
        careerData.slice(0, 8).forEach(c => {
            items.push({
                type: 'career',
                name: c.name,
                rawObj: c
            });
        });
    }

    const buildItemHTML = (item, idx) => {
        const badgeClass = item.type === 'course' ? 'course-badge' : 'career-badge';
        const badgeText = item.type === 'course' ? 'Course' : 'Career';
        const iconName = item.type === 'course' ? 'graduationCap' : 'briefcase';
        const iconHtml = typeof icon === 'function' ? icon(iconName, 14) : '';

        return `
            <div class="ticker-item" data-type="${item.type}" data-index="${idx}">
                ${iconHtml ? `<span class="ticker-icon">${iconHtml}</span>` : ''}
                <span class="ticker-badge ${badgeClass}">${badgeText}</span>
                <span class="ticker-name">${escapeHTML(item.name)}</span>
            </div>
        `;
    };

    // Duplicate original items to ensure smooth infinite loop
    const originalHTML = items.map((item, idx) => buildItemHTML(item, idx)).join('');
    const duplicatedHTML = items.map((item, idx) => buildItemHTML(item, idx)).join('');

    track.innerHTML = originalHTML + duplicatedHTML;

    // Attach click events
    track.querySelectorAll('.ticker-item').forEach(el => {
        el.addEventListener('click', () => {
            const idx = parseInt(el.getAttribute('data-index'), 10);
            const item = items[idx];
            if (!item) return;

            if (item.type === 'career') {
                showCareerModalFromObject(item.rawObj);
            } else {
                showCourseModalFromObject(item.rawObj);
            }
        });
    });
}

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

function hasDisplayValue(value) {
    if (value === null || value === undefined) return false;
    if (typeof value === 'string') {
        const normalized = value.trim().toLowerCase();
        return normalized !== '' && normalized !== 'n/a' && normalized !== 'not specified' && normalized !== 'undefined' && normalized !== 'null';
    }
    if (Array.isArray(value)) return value.length > 0;
    if (typeof value === 'object') return Object.values(value).some(hasDisplayValue);
    return true;
}

function pickDisplayValue(...values) {
    return values.find(hasDisplayValue);
}

function getSalarySummary(item, fallback = 'Competitive') {
    const salary = pickDisplayValue(item?.expected_salary, item?.salary);
    if (salary && typeof salary === 'object' && !Array.isArray(salary)) {
        return pickDisplayValue(salary.entry_level, salary.fresher, salary.mid_level, salary.experienced) || fallback;
    }
    return hasDisplayValue(salary) ? salary : fallback;
}

function getEducationSummary(item) {
    const requirements = item?.requirements;
    if (hasDisplayValue(item?.education)) return item.education;
    if (requirements && typeof requirements === 'object' && !Array.isArray(requirements)) {
        return pickDisplayValue(requirements.minimum_qualification, requirements.qualification) || 'Not specified';
    }
    return hasDisplayValue(requirements) ? requirements : 'Not specified';
}

function findByName(items, name) {
    if (!Array.isArray(items) || !name) return null;
    const normalizedName = String(name).toLowerCase();
    return items.find(item => item.name && item.name.toLowerCase() === normalizedName)
        || items.find(item => item.name && (
            item.name.toLowerCase().includes(normalizedName) || normalizedName.includes(item.name.toLowerCase())
        ))
        || null;
}

function mergeWithFullRecord(item, records) {
    if (!item) return item;
    const fullRecord = findByName(records, item.name);
    if (!fullRecord) return item;

    const merged = { ...fullRecord, ...item };
    Object.keys(fullRecord).forEach(key => {
        if (!hasDisplayValue(item[key])) {
            merged[key] = fullRecord[key];
        }
    });
    return merged;
}

function getCareerDetailRecord(career) {
    const records = typeof careerData !== 'undefined' ? careerData : [];
    return mergeWithFullRecord(career, records);
}

function getCourseDetailRecord(course) {
    const records = typeof courseData !== 'undefined' ? courseData : [];
    return mergeWithFullRecord(course, records);
}

function renderRequirements(requirements, fallback) {
    if (requirements && typeof requirements === 'object' && !Array.isArray(requirements)) {
        const labels = {
            minimum_qualification: 'Qualification',
            qualification: 'Qualification',
            minimum_marks: 'Minimum Marks',
            age_limit: 'Age Limit',
            entrance_exam: 'Entrance Exam'
        };
        const html = Object.entries(requirements)
            .filter(([, value]) => hasDisplayValue(value))
            .map(([key, value]) => {
                const label = labels[key] || key.replace(/_/g, ' ').replace(/\b\w/g, char => char.toUpperCase());
                const displayValue = Array.isArray(value) ? value.join(', ') : value;
                return `<li><strong>${escapeHTML(label)}:</strong> ${escapeHTML(displayValue)}</li>`;
            })
            .join('');
        return html ? `<ul class="detail-list">${html}</ul>` : `<p>${escapeHTML(fallback || 'Not specified')}</p>`;
    }

    return `<p>${escapeHTML(pickDisplayValue(requirements, fallback, 'Not specified'))}</p>`;
}

function renderSalaryDetails(item) {
    const salary = pickDisplayValue(item?.expected_salary, item?.salary);
    if (salary && typeof salary === 'object' && !Array.isArray(salary)) {
        const labels = {
            entry_level: 'Entry Level',
            fresher: 'Fresher',
            mid_level: 'Mid Level',
            experienced: 'Experienced'
        };
        const html = Object.entries(labels)
            .filter(([key]) => hasDisplayValue(salary[key]))
            .map(([key, label]) => `
                <div class="salary-item">
                    <span class="salary-label">${label}</span>
                    <span class="salary-value">${escapeHTML(salary[key])}</span>
                </div>
            `)
            .join('');
        return html ? `<div class="salary-grid">${html}</div>` : '<p>Not specified</p>';
    }

    return `<p>${escapeHTML(pickDisplayValue(salary, 'Not specified'))}</p>`;
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
    let originalHTML = '';
    if (generateBtn) {
        const textSpan = generateBtn.querySelector('.text');
        originalHTML = textSpan ? textSpan.innerHTML : generateBtn.innerHTML;
        if (textSpan) {
            textSpan.textContent = 'Generating...';
        } else {
            generateBtn.textContent = 'Generating...';
        }
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
            const textSpan = generateBtn.querySelector('.text');
            if (textSpan) {
                textSpan.innerHTML = originalHTML;
            } else {
                generateBtn.innerHTML = originalHTML;
            }
            generateBtn.disabled = false;
        }
    }
}

/**
 * Display recommendations results
 */
function displayRecommendations(careers, courses) {
    const detailedCareers = Array.isArray(careers) ? careers.map(getCareerDetailRecord) : [];
    const detailedCourses = Array.isArray(courses) ? courses.map(getCourseDetailRecord) : [];

    const careerHtml = detailedCareers.length > 0 
        ? detailedCareers.map((career, idx) => {
            const salaryText = getSalarySummary(career);
            const educationText = getEducationSummary(career);
            return `
                <div class="result-card" role="button" tabindex="0" data-career-index="${idx}">
                    <div class="result-header">
                        <div class="result-title">${escapeHTML(career.name)}</div>
                        <div class="match-score">${escapeHTML(career.score)}% Match</div>
                    </div>
                    <p class="result-description">${escapeHTML(career.description)}</p>
                    <p class="result-description result-meta">
                        <strong>Education:</strong> ${escapeHTML(educationText)} | <strong>Salary:</strong> ${escapeHTML(salaryText)}
                    </p>
                </div>
            `;
        }).join('')
        : '<p class="text-center-muted">No matching careers found. Aim for higher marks and select relevant skills to unlock more opportunities!</p>';

    const courseHtml = detailedCourses.length > 0
        ? detailedCourses.map((course, idx) => `
            <div class="result-card" role="button" tabindex="0" data-course-index="${idx}">
                <div class="result-header">
                    <div class="result-title">${escapeHTML(course.name)}</div>
                    <div class="match-score">${escapeHTML(course.score)}% Match</div>
                </div>
                <p class="result-description">${escapeHTML(course.description)}</p>
                <p class="result-description result-meta">
                    <strong>Duration:</strong> ${escapeHTML(course.duration || 'Not specified')} | <strong>Type:</strong> ${escapeHTML(course.type || 'Not specified')}
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
    if (careerResults && detailedCareers.length > 0) {
        careerResults.querySelectorAll('.result-card').forEach(card => {
            card.addEventListener('click', () => {
                const idx = parseInt(card.getAttribute('data-career-index'), 10);
                const career = detailedCareers[idx];
                if (career) showCareerModalFromObject(career);
            });

            card.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const idx = parseInt(card.getAttribute('data-career-index'), 10);
                    const career = detailedCareers[idx];
                    if (career) showCareerModalFromObject(career);
                }
            });
        });
    }

    if (courseResults && detailedCourses.length > 0) {
        courseResults.querySelectorAll('.result-card').forEach(card => {
            card.addEventListener('click', () => {
                const idx = parseInt(card.getAttribute('data-course-index'), 10);
                const course = detailedCourses[idx];
                if (course) showCourseModalFromObject(course);
            });

            card.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    const idx = parseInt(card.getAttribute('data-course-index'), 10);
                    const course = detailedCourses[idx];
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
 * Render tags for modal
 */
function renderModalTags(arr, className) {
    if (!hasDisplayValue(arr)) return '<p>Not specified</p>';
    const values = Array.isArray(arr) ? arr : [arr];
    return values.map(item => `<span class="${className}">${escapeHTML(item)}</span>`).join('');
}

/**
 * Render list for modal
 */
function renderModalList(arr) {
    if (!hasDisplayValue(arr)) return '<p>Not specified</p>';
    const values = Array.isArray(arr) ? arr : [arr];
    return '<ul class="detail-list">' + values.map(item => `<li>${escapeHTML(item)}</li>`).join('') + '</ul>';
}

/**
 * Show career details modal using a career object (used by recommendation results)
 */
function showCareerModalFromObject(careerInput) {
    if (!careerInput) return;

    const career = getCareerDetailRecord(careerInput);
    const skills = career.skills_gained || career.skills || [];
    const salaryHtml = renderSalaryDetails(career);
    const requirementsHtml = renderRequirements(career.requirements, getEducationSummary(career));

    let feesHtml = '';
    if (career.fees && typeof career.fees === 'object') {
        feesHtml = '<ul class="detail-list">';
        if (career.fees.government_college) feesHtml += `<li><strong>Government College:</strong> ${escapeHTML(career.fees.government_college)}</li>`;
        if (career.fees.private_college) feesHtml += `<li><strong>Private College:</strong> ${escapeHTML(career.fees.private_college)}</li>`;
        feesHtml += '</ul>';
    }

    const html = `
        <h2>${escapeHTML(career.name)}</h2>
        <div class="modal-meta">
            ${career.category ? `<span class="modal-tag">${escapeHTML(career.category)}</span>` : ''}
            ${career.type ? `<span class="modal-tag type-tag">${escapeHTML(career.type)}</span>` : ''}
            ${career.duration ? `<span class="modal-tag duration-tag">${escapeHTML(career.duration)}</span>` : ''}
            ${career.industry_demand ? `<span class="modal-tag demand-tag">Demand: ${escapeHTML(career.industry_demand)}</span>` : ''}
            ${career.placement_rate ? `<span class="modal-tag placement-tag">Placement: ${escapeHTML(career.placement_rate)}</span>` : ''}
        </div>

        <div class="detail-section">
            <h3>Overview</h3>
            <p>${escapeHTML(career.details || career.description || '')}</p>
        </div>

        <div class="detail-section">
            <h3>Requirements</h3>
            ${requirementsHtml}
        </div>

        ${career.eligibility ? `
        <div class="detail-section">
            <h3>Eligibility</h3>
            ${renderModalList(career.eligibility)}
        </div>
        ` : ''}

        <div class="detail-section">
            <h3>Salary Range</h3>
            ${salaryHtml}
        </div>

        <div class="detail-section">
            <h3>Skills Needed</h3>
            <div class="skills-list">${renderModalTags(skills, 'skill-tag')}</div>
        </div>

        ${career.subjects ? `
        <div class="detail-section">
            <h3>Subjects</h3>
            ${renderModalList(career.subjects)}
        </div>
        ` : ''}

        ${career.career_options ? `
        <div class="detail-section">
            <h3>Career Options</h3>
            <div class="skills-list">${renderModalTags(career.career_options, 'career-option-tag')}</div>
        </div>
        ` : ''}

        ${career.job_roles ? `
        <div class="detail-section">
            <h3>Typical Job Roles</h3>
            <div class="skills-list">${renderModalTags(career.job_roles, 'skill-tag')}</div>
        </div>
        ` : ''}

        ${career.higher_studies ? `
        <div class="detail-section">
            <h3>Higher Studies</h3>
            ${renderModalList(career.higher_studies)}
        </div>
        ` : ''}

        ${career.top_colleges ? `
        <div class="detail-section">
            <h3>Top Colleges</h3>
            ${renderModalList(career.top_colleges)}
        </div>
        ` : ''}

        ${career.top_recruiters ? `
        <div class="detail-section">
            <h3>Top Recruiters</h3>
            ${renderModalList(career.top_recruiters)}
        </div>
        ` : ''}

        ${feesHtml ? `
        <div class="detail-section">
            <h3>Fees Structure</h3>
            ${feesHtml}
        </div>
        ` : ''}

        ${career.scope ? `
        <div class="detail-section">
            <h3>Scope</h3>
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
 * Show course details modal using a course object (used by recommendation results)
 */
function showCourseModalFromObject(courseInput) {
    if (!courseInput) return;

    const course = getCourseDetailRecord(courseInput);
    const requirementsHtml = renderRequirements(course.requirements);
    const salaryHtml = renderSalaryDetails(course);
    let feesHtml = '';
    if (course.fees && typeof course.fees === 'object') {
        feesHtml = '<ul class="detail-list">';
        if (course.fees.government_college) feesHtml += `<li><strong>Government College:</strong> ${escapeHTML(course.fees.government_college)}</li>`;
        if (course.fees.private_college) feesHtml += `<li><strong>Private College:</strong> ${escapeHTML(course.fees.private_college)}</li>`;
        feesHtml += '</ul>';
    }

    const html = `
        <h2>${escapeHTML(course.name)}</h2>
        <div class="modal-meta">
            ${course.type ? `<span class="modal-tag type-tag">${escapeHTML(course.type)}</span>` : ''}
            ${course.category ? `<span class="modal-tag">${escapeHTML(course.category)}</span>` : ''}
            ${course.duration ? `<span class="modal-tag duration-tag">${escapeHTML(course.duration)}</span>` : ''}
        </div>

        <div class="detail-section">
            <h3>Program Overview</h3>
            <p>${escapeHTML(course.details || course.description || '')}</p>
        </div>

        ${course.course_objectives ? `
        <div class="detail-section">
            <h3>Course Objectives</h3>
            ${renderModalList(course.course_objectives)}
        </div>
        ` : ''}

        ${course.subjects ? `
        <div class="detail-section">
            <h3>Core Subjects</h3>
            ${renderModalList(course.subjects)}
        </div>
        ` : ''}

        ${course.skills_gained ? `
        <div class="detail-section">
            <h3>Skills Acquired</h3>
            <div class="skills-list">${renderModalTags(course.skills_gained, 'skill-tag')}</div>
        </div>
        ` : ''}

        <div class="detail-section">
            <h3>Admission Requirements</h3>
            ${requirementsHtml}
        </div>

        ${course.eligibility ? `
        <div class="detail-section">
            <h3>Eligibility</h3>
            ${renderModalList(course.eligibility)}
        </div>
        ` : ''}

        <div class="detail-section">
            <h3>Expected Salary</h3>
            ${salaryHtml}
        </div>

        ${course.career_options ? `
        <div class="detail-section">
            <h3>Career Options</h3>
            <div class="skills-list">${renderModalTags(course.career_options, 'career-option-tag')}</div>
        </div>
        ` : ''}

        ${course.higher_studies ? `
        <div class="detail-section">
            <h3>Higher Studies</h3>
            ${renderModalList(course.higher_studies)}
        </div>
        ` : ''}

        ${feesHtml ? `
        <div class="detail-section">
            <h3>Fees Structure</h3>
            ${feesHtml}
        </div>
        ` : ''}

        ${course.top_colleges ? `
        <div class="detail-section">
            <h3>Top Colleges</h3>
            ${renderModalList(course.top_colleges)}
        </div>
        ` : ''}

        ${course.top_recruiters ? `
        <div class="detail-section">
            <h3>Top Recruiters</h3>
            ${renderModalList(course.top_recruiters)}
        </div>
        ` : ''}

        <div class="detail-section">
            <h3>Career Scope</h3>
            <p>${escapeHTML(course.scope || 'Not specified')}</p>
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
