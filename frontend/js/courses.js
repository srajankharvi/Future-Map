// ==================== COURSES PAGE MODULE ====================

document.addEventListener('DOMContentLoaded', () => {
    const coursesGrid = document.getElementById('coursesGrid');
    const courseSearch = document.getElementById('courseSearch');
    const courseTypeFilter = document.getElementById('courseTypeFilter');

    if (!coursesGrid) return;

    // Setup event listeners
    if (courseSearch) {
        courseSearch.addEventListener('keyup', filterCourses);
    }

    if (courseTypeFilter) {
        courseTypeFilter.addEventListener('change', filterCourses);
    }

    // Setup modal close button
    const closeBtn = document.querySelector('#courseModal .close');
    if (closeBtn) {
        closeBtn.addEventListener('click', closeCourseModal);
    }
});

// Display courses when global data is loaded
document.addEventListener('app:data-loaded', () => {
    if (courseData.length > 0) {
        displayCourses(courseData);
    }
});

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

    const html = courseList.map(course => `
        <div class="course-card" role="button" tabindex="0" data-course-name="${escapeHTML(course.name)}">
            <div class="course-icon">${icon('book', 24)}</div>
            <h3 class="course-title">${escapeHTML(course.name)}</h3>
            <span class="course-type">${escapeHTML(course.type)}</span>
            <p class="course-description">${escapeHTML(course.description)}</p>
        </div>
    `).join('');

    grid.innerHTML = html;

    // Add event listeners to course cards
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
 * Show course details in modal
 */
function showCourseDetails(courseName) {
    const course = courseData.find(c => c.name === courseName);
    if (!course) return;

    const html = `
        <h2>${escapeHTML(course.name)}</h2>
        <div class="detail-section">
            <h3>Program Overview</h3>
            <p>${escapeHTML(course.details || course.description)}</p>
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

/**
 * Filter courses based on search and type
 */
function filterCourses() {
    const searchEl = document.getElementById('courseSearch');
    const typeEl = document.getElementById('courseTypeFilter');
    if (!searchEl || !typeEl) return;

    const search = searchEl.value.toLowerCase();
    const type = typeEl.value;

    const filtered = courseData.filter(course => {
        const matchesSearch = course.name.toLowerCase().includes(search) || 
                             course.description.toLowerCase().includes(search);
        const matchesType = type === '' || course.type === type;
        return matchesSearch && matchesType;
    });

    displayCourses(filtered);
}
