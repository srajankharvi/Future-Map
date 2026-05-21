// ==================== COURSES PAGE MODULE ====================

document.addEventListener('DOMContentLoaded', () => {
    const coursesGrid = document.getElementById('coursesGrid');
    const courseSearch = document.getElementById('courseSearch');
    const courseTypeFilter = document.getElementById('courseTypeFilter');
    const courseCategoryFilter = document.getElementById('courseCategoryFilter');

    if (!coursesGrid) return;

    if (courseSearch) {
        courseSearch.addEventListener('keyup', filterCourses);
    }

    if (courseTypeFilter) {
        courseTypeFilter.addEventListener('change', filterCourses);
    }

    if (courseCategoryFilter) {
        courseCategoryFilter.addEventListener('change', filterCourses);
    }

    const closeBtn = document.querySelector('#courseModal .close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeCourseModal);
    }
});

// Display courses when global data is loaded
document.addEventListener('app:data-loaded', () => {
    if (courseData.length > 0) {
        populateCourseFilters(courseData);
        displayCourses(courseData);
    }
});

/**
 * Dynamically populate type and category filters from course data
 */
function populateCourseFilters(courses) {
    const typeFilter = document.getElementById('courseTypeFilter');
    const categoryFilter = document.getElementById('courseCategoryFilter');

    if (typeFilter) {
        const types = [...new Set(courses.map(c => c.type).filter(Boolean))].sort();
        typeFilter.innerHTML = '<option value="">All Types</option>';
        types.forEach(type => {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type.charAt(0) + type.slice(1).toLowerCase() + ' Programs';
            typeFilter.appendChild(option);
        });
    }

    if (categoryFilter) {
        const categories = [...new Set(courses.map(c => c.category).filter(Boolean))].sort();
        categoryFilter.innerHTML = '<option value="">All Categories</option>';
        categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat;
            option.textContent = cat;
            categoryFilter.appendChild(option);
        });
    }

    if (typeof setupCustomSelects === 'function') {
        setupCustomSelects();
    }
}

/**
 * Display courses in grid format
 */
function displayCourses(courseList) {
    const grid = document.getElementById('coursesGrid');
    if (!grid) return;

    if (courseList.length === 0) {
        grid.innerHTML = '<p class="text-center-muted-grid">No courses found matching your search.</p>';
        return;
    }

    const html = courseList.map(course => {
        let salaryText = '';
        if (typeof course.salary === 'object' && course.salary !== null) {
            salaryText = course.salary.fresher || course.salary.entry_level || '';
        } else if (typeof course.salary === 'string') {
            salaryText = course.salary;
        }

        return `
        <div class="course-card" role="button" tabindex="0" data-course-name="${escapeHTML(course.name)}">
            <div class="course-icon">${icon('book', 24)}</div>
            <h3 class="course-title">${escapeHTML(course.name)}</h3>
            <div class="course-meta">
                <span class="course-type">${escapeHTML(course.type || '')}</span>
                ${course.category ? `<span class="course-category-badge">${escapeHTML(course.category)}</span>` : ''}
            </div>
            <p class="course-description">${escapeHTML(course.description || '')}</p>
            ${course.duration ? `<span class="course-duration">${icon('clock', 14)} ${escapeHTML(course.duration)}</span>` : ''}
        </div>
    `;
    }).join('');

    grid.innerHTML = html;

    grid.querySelectorAll('.course-card').forEach(card => {
        card.addEventListener('click', () => {
            const courseName = card.getAttribute('data-course-name');
            showCourseDetails(courseName);
        });
        
        card.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                const courseName = card.getAttribute('data-course-name');
                showCourseDetails(courseName);
            }
        });
    });
}

/**
 * Render an array as a list of tags
 */
function renderCourseTags(arr, className) {
    if (!arr || !Array.isArray(arr) || arr.length === 0) return '<p>Not specified</p>';
    return arr.map(item => `<span class="${className}">${escapeHTML(item)}</span>`).join('');
}

/**
 * Render an array as a bullet list
 */
function renderCourseList(arr) {
    if (!arr || !Array.isArray(arr) || arr.length === 0) return '<p>Not specified</p>';
    return '<ul class="detail-list">' + arr.map(item => `<li>${escapeHTML(item)}</li>`).join('') + '</ul>';
}

/**
 * Show course details in modal
 */
function showCourseDetails(courseName) {
    const course = courseData.find(c => c.name === courseName);
    if (!course) return;

    // Handle salary display
    let salaryHtml = '';
    if (typeof course.salary === 'object' && course.salary !== null) {
        salaryHtml = `
            <div class="salary-grid">
                ${course.salary.fresher ? `<div class="salary-item"><span class="salary-label">Fresher</span><span class="salary-value">${escapeHTML(course.salary.fresher)}</span></div>` : ''}
                ${course.salary.entry_level ? `<div class="salary-item"><span class="salary-label">Entry Level</span><span class="salary-value">${escapeHTML(course.salary.entry_level)}</span></div>` : ''}
                ${course.salary.mid_level ? `<div class="salary-item"><span class="salary-label">Mid Level</span><span class="salary-value">${escapeHTML(course.salary.mid_level)}</span></div>` : ''}
                ${course.salary.experienced ? `<div class="salary-item"><span class="salary-label">Experienced</span><span class="salary-value">${escapeHTML(course.salary.experienced)}</span></div>` : ''}
            </div>
        `;
    } else if (typeof course.salary === 'string') {
        salaryHtml = `<p>${escapeHTML(course.salary)}</p>`;
    } else {
        salaryHtml = '<p>Not specified</p>';
    }

    // Handle requirements display
    let requirementsHtml = '';
    if (typeof course.requirements === 'object' && course.requirements !== null && !Array.isArray(course.requirements)) {
        requirementsHtml = '<ul class="detail-list">';
        if (course.requirements.minimum_qualification) requirementsHtml += `<li><strong>Qualification:</strong> ${escapeHTML(course.requirements.minimum_qualification)}</li>`;
        if (course.requirements.minimum_marks) requirementsHtml += `<li><strong>Minimum Marks:</strong> ${escapeHTML(course.requirements.minimum_marks)}</li>`;
        if (course.requirements.entrance_exam) {
            const exams = Array.isArray(course.requirements.entrance_exam) ? course.requirements.entrance_exam.join(', ') : course.requirements.entrance_exam;
            requirementsHtml += `<li><strong>Entrance Exam:</strong> ${escapeHTML(exams)}</li>`;
        }
        requirementsHtml += '</ul>';
    } else if (typeof course.requirements === 'string') {
        requirementsHtml = `<p>${escapeHTML(course.requirements)}</p>`;
    } else {
        requirementsHtml = '<p>Not specified</p>';
    }

    // Handle fees display
    let feesHtml = '';
    if (course.fees && typeof course.fees === 'object') {
        feesHtml = '<ul class="detail-list">';
        if (course.fees.government_college) feesHtml += `<li><strong>Government College:</strong> ${escapeHTML(course.fees.government_college)}</li>`;
        if (course.fees.private_college) feesHtml += `<li><strong>Private College:</strong> ${escapeHTML(course.fees.private_college)}</li>`;
        feesHtml += '</ul>';
    }

    const skills = course.skills_gained || [];

    const html = `
        <h2>${escapeHTML(course.name)}</h2>
        <div class="modal-meta">
            ${course.type ? `<span class="modal-tag type-tag">${escapeHTML(course.type)}</span>` : ''}
            ${course.category ? `<span class="modal-tag">${escapeHTML(course.category)}</span>` : ''}
            ${course.duration ? `<span class="modal-tag duration-tag">${icon('clock', 14)} ${escapeHTML(course.duration)}</span>` : ''}
        </div>

        <div class="detail-section">
            <h3>${icon('book', 18)} Program Overview</h3>
            <p>${escapeHTML(course.details || course.description || '')}</p>
        </div>

        <div class="detail-section">
            <h3>${icon('graduationCap', 18)} Admission Requirements</h3>
            ${requirementsHtml}
        </div>

        ${course.eligibility ? `
        <div class="detail-section">
            <h3>${icon('checkCircle', 18)} Eligibility</h3>
            ${renderCourseList(course.eligibility)}
        </div>
        ` : ''}

        ${course.course_objectives ? `
        <div class="detail-section">
            <h3>${icon('target', 18)} Course Objectives</h3>
            ${renderCourseList(course.course_objectives)}
        </div>
        ` : ''}

        ${course.subjects ? `
        <div class="detail-section">
            <h3>${icon('bookOpen', 18)} Subjects</h3>
            ${renderCourseList(course.subjects)}
        </div>
        ` : ''}

        ${skills.length > 0 ? `
        <div class="detail-section">
            <h3>${icon('star', 18)} Skills Gained</h3>
            <div class="skills-list">${renderCourseTags(skills, 'skill-tag')}</div>
        </div>
        ` : ''}

        <div class="detail-section">
            <h3>${icon('dollar', 18)} Expected Salary</h3>
            ${salaryHtml}
        </div>

        ${course.career_options ? `
        <div class="detail-section">
            <h3>${icon('briefcase', 18)} Career Options</h3>
            <div class="skills-list">${renderCourseTags(course.career_options, 'career-option-tag')}</div>
        </div>
        ` : ''}

        ${course.higher_studies ? `
        <div class="detail-section">
            <h3>${icon('trendingUp', 18)} Higher Studies</h3>
            ${renderCourseList(course.higher_studies)}
        </div>
        ` : ''}

        ${course.top_colleges ? `
        <div class="detail-section">
            <h3>${icon('building', 18)} Top Colleges</h3>
            ${renderCourseList(course.top_colleges)}
        </div>
        ` : ''}

        ${course.top_recruiters ? `
        <div class="detail-section">
            <h3>${icon('users', 18)} Top Recruiters</h3>
            ${renderCourseList(course.top_recruiters)}
        </div>
        ` : ''}

        ${feesHtml ? `
        <div class="detail-section">
            <h3>${icon('dollar', 18)} Fees Structure</h3>
            ${feesHtml}
        </div>
        ` : ''}

        ${course.scope ? `
        <div class="detail-section">
            <h3>${icon('compass', 18)} Career Scope</h3>
            <p>${escapeHTML(course.scope)}</p>
        </div>
        ` : ''}
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

/**
 * Filter courses based on search, type, and category
 */
function filterCourses() {
    const searchEl = document.getElementById('courseSearch');
    const typeEl = document.getElementById('courseTypeFilter');
    const categoryEl = document.getElementById('courseCategoryFilter');
    if (!searchEl) return;

    const search = searchEl.value.toLowerCase();
    const type = typeEl ? typeEl.value : '';
    const category = categoryEl ? categoryEl.value : '';

    const filtered = courseData.filter(course => {
        const matchesSearch = course.name.toLowerCase().includes(search) || 
                             (course.description || '').toLowerCase().includes(search) ||
                             (course.category || '').toLowerCase().includes(search);
        const matchesType = type === '' || course.type === type;
        const matchesCategory = category === '' || course.category === category;
        return matchesSearch && matchesType && matchesCategory;
    });

    displayCourses(filtered);
}
