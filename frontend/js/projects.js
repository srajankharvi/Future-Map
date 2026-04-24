// ==================== PROJECTS PAGE ====================

// Store all projects for filtering
let allProjects = [];

document.addEventListener('DOMContentLoaded', function () {
    loadProjects();
    setupUploadForm();
    setupProjectSearch();
});


// ==================== LOAD PROJECTS ====================

async function loadProjects() {
    const grid = document.getElementById('projectsGrid');
    const loading = document.getElementById('projectsLoading');
    const empty = document.getElementById('projectsEmpty');
    const error = document.getElementById('projectsError');
    const searchInput = document.getElementById('projectSearch');

    if (!grid) return;

    // Clear search input
    if (searchInput) searchInput.value = '';

    // Show loading
    if (loading) showElement(loading);
    if (empty) hideElement(empty);
    if (error) hideElement(error);
    grid.innerHTML = '';

    try {
        const response = await fetch(`${API_BASE}/projects`, {
            credentials: 'include'
        });
        const result = await response.json();

        if (loading) hideElement(loading);

        if (response.status === 401) {
            window.location.href = 'login.html';
            return;
        }

        if (result.success && result.data && result.data.length > 0) {
            allProjects = result.data;
            
            // Show database status warning if using SQLite fallback
            if (result.source === 'sqlite' && error) {
                showElement(error);
                error.innerHTML = '<strong>⚠️ Database Status:</strong> Projects are being stored locally (SQLite). MongoDB is currently unavailable - your projects will sync when connection is restored.';
                error.style.backgroundColor = '#e3f2fd';
                error.style.color = '#1565c0';
                error.style.border = '1px solid #90caf9';
            } else if (result.source === 'demo' && error) {
                showElement(error);
                error.innerHTML = '<strong>ℹ️ Demo Mode:</strong> Showing sample projects. Submit your own projects to get started!';
                error.style.backgroundColor = '#f3e5f5';
                error.style.color = '#6a1b9a';
                error.style.border = '1px solid #ce93d8';
            }
            
            displayProjects(result.data, grid);
        } else {
            allProjects = [];
            if (empty) showElement(empty);
        }
    } catch (err) {
        console.error('Error loading projects:', err);
        if (loading) hideElement(loading);
        if (error) {
            showElement(error);
            error.textContent = 'Could not load projects. Please check your connection.';
        }
    }
}


// ==================== DISPLAY PROJECTS ====================

function displayProjects(projects, grid) {
    if (!grid) return;

    const html = projects.map(project => {
        const username = escapeHTML(project.username || 'Anonymous');
        const title = escapeHTML(project.title || 'Untitled');
        const description = escapeHTML(project.description || 'No description provided.');
        const link = escapeHTML(project.link || '#');
        const initial = username.charAt(0).toUpperCase();
        const date = project.created_at
            ? new Date(project.created_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
            : 'Unknown date';

        return `
            <div class="project-display-card">
                <div class="project-display-header">
                    <div class="project-display-avatar">${escapeHTML(initial)}</div>
                    <div class="project-display-meta">
                        <span class="project-display-username">${username}</span>
                        <span class="project-display-date">${escapeHTML(date)}</span>
                    </div>
                </div>
                <h3 class="project-display-title">${title}</h3>
                <p class="project-display-desc">${description}</p>
                <a href="${link}" target="_blank" rel="noopener noreferrer" class="btn btn-primary project-display-link">
                    ${typeof icon === 'function' ? icon('link', 16) : ''} View Project
                </a>
            </div>
        `;
    }).join('');

    grid.innerHTML = html;
}


// ==================== SEARCH PROJECTS ====================

function setupProjectSearch() {
    const searchInput = document.getElementById('projectSearch');
    if (!searchInput) return;

    searchInput.addEventListener('input', function(e) {
        const searchQuery = e.target.value.toLowerCase().trim();
        const grid = document.getElementById('projectsGrid');
        const empty = document.getElementById('projectsEmpty');

        if (searchQuery === '') {
            // Show all projects if search is empty
            if (allProjects.length > 0) {
                displayProjects(allProjects, grid);
                if (empty) hideElement(empty);
            } else {
                if (empty) showElement(empty);
            }
        } else {
            // Filter projects based on project name or username
            const filteredProjects = allProjects.filter(project => {
                const username = (project.username || 'Anonymous').toLowerCase();
                const title = (project.title || 'Untitled').toLowerCase();
                const description = (project.description || '').toLowerCase();
                
                return username.includes(searchQuery) || 
                       title.includes(searchQuery) || 
                       description.includes(searchQuery);
            });

            if (filteredProjects.length > 0) {
                displayProjects(filteredProjects, grid);
                if (empty) hideElement(empty);
            } else {
                grid.innerHTML = '<p class="text-center-muted-grid">No projects found matching your search.</p>';
                if (empty) hideElement(empty);
            }
        }
    });
}


// ==================== UPLOAD FORM ====================

function setupUploadForm() {
    const form = document.getElementById('uploadProjectForm');
    if (!form) return;

    form.addEventListener('submit', async function (e) {
        e.preventDefault();

        const title = document.getElementById('projectTitle').value.trim();
        const link = document.getElementById('projectLink').value.trim();
        const description = document.getElementById('projectDescription').value.trim();

        // Validation
        if (!title || !link || !description) {
            showUploadMessage('Please fill in all fields', 'error');
            return;
        }

        // URL validation
        try {
            new URL(link);
        } catch {
            showUploadMessage('Please enter a valid URL (e.g., https://github.com/...)', 'error');
            return;
        }

        // Loading state
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn ? submitBtn.textContent : '';
        if (submitBtn) {
            submitBtn.textContent = 'Uploading...';
            submitBtn.disabled = true;
        }

        try {
            const response = await fetch(`${API_BASE}/projects`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ title, link, description })
            });

            const result = await response.json();

            if (response.status === 401) {
                window.location.href = 'login.html';
                return;
            }

            if (result.success) {
                const storageMsg = result.stored_in === 'mongodb' ? 
                    'Project uploaded to MongoDB!' : 
                    'Project saved locally! (will sync to database when available)';
                showUploadMessage(storageMsg, 'success');
                form.reset();
                // Refresh project list
                setTimeout(() => loadProjects(), 1000);
            } else {
                showUploadMessage(result.error || 'Could not upload project', 'error');
            }
        } catch (err) {
            console.error('Upload error:', err);
            showUploadMessage('Server error. Make sure the backend is running.', 'error');
        } finally {
            if (submitBtn) {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            }
        }
    });
}


// ==================== UPLOAD MESSAGE ====================

function showUploadMessage(message, type) {
    let msgEl = document.getElementById('uploadMessage');
    if (!msgEl) {
        msgEl = document.createElement('div');
        msgEl.id = 'uploadMessage';
        const form = document.getElementById('uploadProjectForm');
        if (form) form.parentNode.insertBefore(msgEl, form);
    }

    msgEl.className = `upload-msg ${type === 'success' ? 'upload-success' : 'upload-error'}`;
    const iconHtml = (typeof icon === 'function')
        ? (type === 'success' ? icon('checkCircle', 16) : icon('xCircle', 16))
        : '';
    msgEl.innerHTML = `<span class="msg-inline-flex">${iconHtml} ${escapeHTML(message)}</span>`;
    showElement(msgEl);

    setTimeout(() => {
        hideElement(msgEl);
    }, 5000);
}

