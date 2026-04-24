// ===== Your Path Page Logic =====

// ===== Data fetched from API (initialized empty) =====
let careerCourseMapping = {};
let roadmapTemplates = {};
let careerDetailedInfo = {};
let careerProjects = {};
let careerResources = {};

// Skill icons mapping — using SVG icon system from script.js
const skillIconMap = {
    "technical": "laptop",
    "analytical": "chart",
    "creative": "palette",
    "communication": "mic",
    "leadership": "users",
    "problem-solving": "puzzle",
    "teamwork": "handshake",
    "design": "sparkles",
    "strategic planning": "building"
};

/** Get skill icon SVG — uses Icons from script.js */
function getSkillIcon(skillName) {
    const key = skillIconMap[(skillName || '').toLowerCase()] || 'star';
    return (typeof icon === 'function') ? icon(key, 18) : '';
}

/** Load all yourpath reference data from the API */
async function loadYourPathData() {
    try {
        const res = await apiFetch(`${API_BASE}/yourpath-data`);
        if (res.success && res.data) {
            careerCourseMapping = res.data.careerCourseMapping || {};
            roadmapTemplates = res.data.roadmapTemplates || {};
            careerDetailedInfo = res.data.careerDetailedInfo || {};
            careerProjects = res.data.careerProjects || {};
            careerResources = res.data.careerResources || {};
        }
    } catch (err) {
        console.error('Failed to load yourpath data:', err);
    }
}

// Populate career dropdown
function populateCareerDropdown(filteredCareers = null) {
    const select = document.getElementById('careerSelect');
    if (!select) return;
    
    const careers = filteredCareers || careerData;
    select.innerHTML = '<option value="">-- Choose a Career --</option>';
    
    careers.forEach(career => {
        const option = document.createElement('option');
        option.value = career.name;
        option.textContent = `${career.name} — ${career.category}`;
        select.appendChild(option);
    });
}

// Populate course dropdown
function populateCourseDropdown(filteredCourses = null) {
    const select = document.getElementById('courseSelect');
    if (!select) return;
    
    const courses = filteredCourses || courseData;
    select.innerHTML = '<option value="">-- Choose a Course --</option>';
    
    courses.forEach(course => {
        const option = document.createElement('option');
        option.value = course.name;
        option.textContent = `${course.name} — ${course.type} (${course.duration})`;
        select.appendChild(option);
    });
}

// Filter career dropdown by category
function filterCareerOptions() {
    const category = document.getElementById('careerCategorySelect').value;
    const filtered = category 
        ? careerData.filter(c => c.category === category || c.category.includes(category))
        : careerData;
    populateCareerDropdown(filtered);
    
    // Hide preview if selection cleared
    hideElement('careerPreview');
    checkGenerateButton();
}

// Filter course dropdown by type
function filterCourseOptions() {
    const type = document.getElementById('courseTypeSelect').value;
    const filtered = type ? courseData.filter(c => c.type === type) : courseData;
    populateCourseDropdown(filtered);
    
    hideElement('coursePreview');
    checkGenerateButton();
}

// On career selected
function onCareerSelected() {
    const careerName = document.getElementById('careerSelect').value;
    const preview = document.getElementById('careerPreview');
    
    if (!careerName) {
        hideElement(preview);
        checkGenerateButton();
        return;
    }
    
    const career = careerData.find(c => c.name === careerName);
    if (!career) return;
    
    document.getElementById('careerPreviewName').textContent = career.name;
    document.getElementById('careerPreviewDesc').textContent = career.description;
    document.getElementById('careerPreviewEdu').textContent = `${career.education}`;
    document.getElementById('careerPreviewSalary').textContent = `${career.salary}`;
    showElement(preview);
    
    checkGenerateButton();
}

// On course selected
function onCourseSelected() {
    const courseName = document.getElementById('courseSelect').value;
    const preview = document.getElementById('coursePreview');
    
    if (!courseName) {
        hideElement(preview);
        checkGenerateButton();
        return;
    }
    
    const course = courseData.find(c => c.name === courseName);
    if (!course) return;
    
    document.getElementById('coursePreviewName').textContent = course.name;
    document.getElementById('coursePreviewDesc').textContent = course.description;
    document.getElementById('coursePreviewDuration').textContent = `${course.duration}`;
    document.getElementById('coursePreviewType').textContent = `${course.type}`;
    showElement(preview);
    
    checkGenerateButton();
}

// Show/hide generate button
function checkGenerateButton() {
    const careerId = document.getElementById('careerSelect').value;
    const courseId = document.getElementById('courseSelect').value;
    const wrapper = document.getElementById('generatePathWrapper');
    
    if (careerId && courseId) {
        showElement(wrapper);
    } else {
        hideElement(wrapper);
    }
}

// Generate the roadmap
function generatePath() {
    const careerName = document.getElementById('careerSelect').value;
    const courseName = document.getElementById('courseSelect').value;
    
    const career = careerData.find(c => c.name === careerName);
    const course = courseData.find(c => c.name === courseName);
    
    if (!career || !course) return;
    
    // Get roadmap template
    const template = roadmapTemplates[career.category] || roadmapTemplates["Computer"];
    
    // Update header
    document.getElementById('roadmapTitle').textContent = `Your Path to ${career.name}`;
    document.getElementById('roadmapSubtitle').textContent = 
        `Through ${course.name} (${course.description}) — here's your step-by-step roadmap`;
    
    // Generate summary cards
    const summaryHtml = `
        <div class="summary-card">
            <div class="summary-icon">${icon('target', 24)}</div>
            <h4>Career Goal</h4>
            <div class="summary-value">${escapeHTML(career.name)}</div>
        </div>
        <div class="summary-card">
            <div class="summary-icon">${icon('book', 24)}</div>
            <h4>Course</h4>
            <div class="summary-value">${escapeHTML(course.name)}</div>
        </div>
        <div class="summary-card">
            <div class="summary-icon">${icon('clock', 24)}</div>
            <h4>Course Duration</h4>
            <div class="summary-value">${escapeHTML(course.duration)}</div>
        </div>
        <div class="summary-card">
            <div class="summary-icon">${icon('dollar', 24)}</div>
            <h4>Salary Potential</h4>
            <div class="summary-value">${escapeHTML(career.salary)}</div>
        </div>
    `;
    document.getElementById('roadmapSummary').innerHTML = summaryHtml;
    
    // Generate timeline
    const timelineHtml = template.map((item, index) => `
        <div class="timeline-item">
            <div class="timeline-dot step-${(index % 7) + 1}">${index + 1}</div>
            <div class="timeline-card" style="border-left-color: ${getStepColor(index)}">
                <span class="timeline-step-label">Step ${index + 1} — ${item.step}</span>
                <h3>${item.title}</h3>
                <p>${item.desc}</p>
                <div class="timeline-duration">
                    <span>${icon('clock', 16)}</span>
                    <span>${item.duration}</span>
                </div>
            </div>
        </div>
    `).join('');
    document.getElementById('roadmapTimeline').innerHTML = timelineHtml;
    
    // Generate skills section with descriptions
    const allSkills = [...new Set(career.skills)];
    const skillDetailData = getSkillDetails(career.category);
    const skillsHtml = `
        <h3>${icon('wrench', 22)} Skills You'll Need</h3>
        <p class="skills-subtitle">Focus on developing these key skills along your journey</p>
        <div class="skills-grid-path">
            ${allSkills.map(skill => `
                <div class="skill-chip">
                    <div class="skill-chip-icon">${getSkillIcon(skill)}</div>
                    <span class="skill-chip-text">${escapeHTML(skill)}</span>
                </div>
            `).join('')}
        </div>
    `;
    document.getElementById('roadmapSkills').innerHTML = skillsHtml;
    
    // Generate Career Details Section
    const detailInfo = careerDetailedInfo[career.category] || careerDetailedInfo["Computer"];
    const careerDetailsHtml = `
        <div class="detail-block">
            <div class="detail-block-header">
                <span class="detail-block-icon">${icon('clipboard', 22)}</span>
                <h3>Career Details — ${escapeHTML(career.name)}</h3>
            </div>
            <div class="detail-block-body">
                <p class="detail-overview">${escapeHTML(career.details)}</p>
                
                <div class="detail-grid">
                    <div class="detail-item">
                        <div class="detail-item-icon">${icon('graduationCap', 20)}</div>
                        <div>
                            <h4>Education Required</h4>
                            <p>${escapeHTML(career.education)}</p>
                        </div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-item-icon">${icon('dollar', 20)}</div>
                        <div>
                            <h4>Salary Range</h4>
                            <p>${escapeHTML(career.salary)}</p>
                        </div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-item-icon">${icon('folder', 20)}</div>
                        <div>
                            <h4>Industry</h4>
                            <p>${escapeHTML(career.category)}</p>
                        </div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-item-icon">${icon('trendingUp', 20)}</div>
                        <div>
                            <h4>Growth Outlook</h4>
                            <p>${detailInfo.growthOutlook}</p>
                        </div>
                    </div>
                </div>

                <div class="skill-breakdown">
                    <h4>${icon('target', 18)} Skills Breakdown — What to Learn</h4>
                    <div class="skill-breakdown-list">
                        ${detailInfo.skillBreakdown.map(s => `
                            <div class="skill-breakdown-item">
                                <div class="skill-breakdown-header">
                                    <span class="sbi-icon">${icon(s.icon, 18)}</span>
                                    <span class="sbi-name">${s.name}</span>
                                    <span class="sbi-level">${s.level}</span>
                                </div>
                                <p class="sbi-desc">${s.description}</p>
                                <div class="sbi-bar-bg"><div class="sbi-bar-fill" style="width: ${s.percentage}%; background: ${s.color}"></div></div>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;
    document.getElementById('careerDetailsSection').innerHTML = careerDetailsHtml;
    
    // Generate Projects Section
    const projectsData = careerProjects[career.category] || careerProjects["Computer"];
    const projectsHtml = `
        <div class="detail-block">
            <div class="detail-block-header">
                <span class="detail-block-icon">${icon('rocket', 22)}</span>
                <h3>Recommended Projects to Build</h3>
            </div>
            <div class="detail-block-body">
                <p class="detail-overview">Working on real projects is the best way to develop skills and build your portfolio. Here are project ideas for your career path:</p>
                <div class="projects-grid">
                    ${projectsData.map((project, i) => `
                        <div class="project-card" style="animation-delay: ${i * 0.1}s">
                            <div class="project-card-top">
                                <span class="project-number">${i + 1}</span>
                                <span class="project-difficulty ${project.difficulty.toLowerCase()}">${project.difficulty}</span>
                            </div>
                            <h4>${project.title}</h4>
                            <p>${project.description}</p>
                            <div class="project-skills">
                                ${project.skills.map(s => `<span class="project-skill-tag">${s}</span>`).join('')}
                            </div>
                            <div class="project-time">
                                <span>${icon('clock', 14)}</span> ${project.timeEstimate}
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    document.getElementById('projectsSection').innerHTML = projectsHtml;
    
    // Generate Resources Section
    const resourceData = careerResources[career.category] || careerResources["Computer"];
    const resourcesHtml = `
        <div class="detail-block">
            <div class="detail-block-header">
                <span class="detail-block-icon">${icon('bookOpen', 22)}</span>
                <h3>Tools & Resources to Master</h3>
            </div>
            <div class="detail-block-body">
                <div class="resources-grid">
                    <div class="resource-column">
                        <h4>${icon('wrench', 18)} Tools & Software</h4>
                        <ul class="resource-list">
                            ${resourceData.tools.map(t => `<li><span class="resource-dot"></span>${t}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="resource-column">
                        <h4>${icon('award', 18)} Certifications</h4>
                        <ul class="resource-list">
                            ${resourceData.certifications.map(c => `<li><span class="resource-dot cert"></span>${c}</li>`).join('')}
                        </ul>
                    </div>
                    <div class="resource-column">
                        <h4>${icon('book', 18)} Subjects to Study</h4>
                        <ul class="resource-list">
                            ${resourceData.subjects.map(s => `<li><span class="resource-dot subj"></span>${s}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    `;
    document.getElementById('resourcesSection').innerHTML = resourcesHtml;
    
    // Show roadmap and scroll to it
    showElement('roadmapSection');
    setTimeout(() => {
        document.getElementById('roadmapSection').scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 150);

    // Auto-save the roadmap
    saveRoadmapToServer(career, course);
}

function getStepColor(index) {
    const colors = ['#667eea', '#f093fb', '#4facfe', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];
    return colors[index % colors.length];
}

// Helper: get skill details for a category
function getSkillDetails(category) {
    return careerDetailedInfo[category] || careerDetailedInfo["Computer"];
}

// Reset path
function resetPath() {
    document.getElementById('careerSelect').value = '';
    document.getElementById('courseSelect').value = '';
    document.getElementById('careerCategorySelect').value = '';
    document.getElementById('courseTypeSelect').value = '';
    hideElement('careerPreview');
    hideElement('coursePreview');
    hideElement('generatePathWrapper');
    hideElement('roadmapSection');
    
    populateCareerDropdown();
    populateCourseDropdown();
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ===== Roadmap Persistence =====

/** Save the current roadmap to the server */
async function saveRoadmapToServer(career, course) {
    try {
        const result = await apiFetch(`${API_BASE}/roadmaps`, {
            method: 'POST',
            body: JSON.stringify({
                career_name: career.name,
                course_name: course.name,
                category: career.category,
                roadmap_data: {
                    career: career,
                    course: course,
                    generated_at: new Date().toISOString()
                }
            })
        });

        if (result.success) {
            showSaveNotification('Roadmap saved to your account!');
        }
    } catch (err) {
        // Silent fail — roadmap still visible, just not persisted
    }
}

/** Load saved roadmaps list */
async function loadSavedRoadmaps() {
    const container = document.getElementById('savedRoadmapsList');
    if (!container) return;

    try {
        const result = await apiFetch(`${API_BASE}/roadmaps`);
        if (result.success && result.data && result.data.length > 0) {
            container.innerHTML = result.data.map(r => `
                <div class="saved-roadmap-item" data-career="${escapeHTML(r.career_name)}" data-course="${escapeHTML(r.course_name)}">
                    <div class="saved-roadmap-info">
                        <strong>${escapeHTML(r.career_name)}</strong>
                        <span>via ${escapeHTML(r.course_name)}</span>
                    </div>
                    <div class="saved-roadmap-date">${new Date(r.updated_at).toLocaleDateString()}</div>
                    <button class="saved-roadmap-delete" data-roadmap-id="${escapeHTML(r._id)}" title="Delete">${icon('xCircle', 16)}</button>
                </div>
            `).join('');

            // Attach event listeners (no inline handlers)
            container.querySelectorAll('.saved-roadmap-item').forEach(item => {
                item.addEventListener('click', () => {
                    loadSavedRoadmap(item.dataset.career, item.dataset.course);
                });
            });
            container.querySelectorAll('.saved-roadmap-delete').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    deleteSavedRoadmap(btn.dataset.roadmapId);
                });
            });

            showElement(container.parentElement);
        } else {
            container.innerHTML = '<p class="text-muted-padded">No saved roadmaps yet. Generate one above!</p>';
        }
    } catch (err) {
        // Silent fail
    }
}

/** Load a saved roadmap by re-selecting the career and course */
function loadSavedRoadmap(careerName, courseName) {
    const careerSelect = document.getElementById('careerSelect');
    const courseSelect = document.getElementById('courseSelect');
    if (!careerSelect || !courseSelect) return;

    careerSelect.value = careerName;
    onCareerSelected();
    courseSelect.value = courseName;
    onCourseSelected();

    setTimeout(() => generatePath(), 300);
}

/** Delete a saved roadmap */
async function deleteSavedRoadmap(roadmapId) {
    try {
        const result = await apiFetch(`${API_BASE}/roadmaps/${roadmapId}`, { method: 'DELETE' });
        if (result.success) {
            loadSavedRoadmaps(); // Refresh list
        }
    } catch (err) {
        // Silent fail
    }
}

/** Show a brief save notification */
function showSaveNotification(message) {
    let notif = document.getElementById('roadmapSaveNotif');
    if (!notif) {
        notif = document.createElement('div');
        notif.id = 'roadmapSaveNotif';
        notif.className = 'save-notification hidden';
        document.body.appendChild(notif);
    }
    notif.innerHTML = `${icon('checkCircle', 16)} <span class="notif-icon-gap">${message}</span>`;
    notif.classList.remove('hidden');
    notif.classList.add('visible');
    setTimeout(() => { notif.classList.remove('visible'); }, 3000);
    setTimeout(() => { notif.classList.add('hidden'); }, 3400);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', async function() {
    if (document.getElementById('careerSelect')) {
        // Load yourpath reference data from API first
        await loadYourPathData();

        populateCareerDropdown();
        populateCourseDropdown();
        // Load saved roadmaps if container exists
        loadSavedRoadmaps();
    }

    // Setup select change listeners
    const careerCategorySelect = document.getElementById('careerCategorySelect');
    if (careerCategorySelect) {
        careerCategorySelect.addEventListener('change', filterCareerOptions);
    }

    const careerSelect = document.getElementById('careerSelect');
    if (careerSelect) {
        careerSelect.addEventListener('change', onCareerSelected);
    }

    const courseTypeSelect = document.getElementById('courseTypeSelect');
    if (courseTypeSelect) {
        courseTypeSelect.addEventListener('change', filterCourseOptions);
    }

    const courseSelect = document.getElementById('courseSelect');
    if (courseSelect) {
        courseSelect.addEventListener('change', onCourseSelected);
    }

    // Setup button listeners
    const generatePathBtn = document.querySelector('[data-action="generate-path"]');
    if (generatePathBtn) {
        generatePathBtn.addEventListener('click', generatePath);
    }

    const resetPathBtn = document.querySelector('[data-action="reset-path"]');
    if (resetPathBtn) {
        resetPathBtn.addEventListener('click', resetPath);
    }


});
