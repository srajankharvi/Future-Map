// ==================== ACCOUNT PAGE MODULE ====================

document.addEventListener('DOMContentLoaded', () => {
    loadUserProfile();
    loadUserProjects();

    // Edit profile button
    const editBtn = document.getElementById('editProfileBtn');
    if (editBtn) {
        editBtn.addEventListener('click', showEditForm);
    }

    // Cancel edit button
    const cancelBtn = document.getElementById('cancelEditBtn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', hideEditForm);
    }

    // Profile form submit
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', (e) => {
            e.preventDefault();
            saveProfile();
        });
    }

    // Logout button on account page
    const logoutBtn = document.getElementById('logoutBtnAccount');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }

    // Auto-fill username in project upload form
    const projectUsernameField = document.getElementById('projectUsername');
    if (projectUsernameField) {
        const username = sessionStorage.getItem('futureMapUser') || '';
        projectUsernameField.value = username;
        projectUsernameField.readOnly = true;
    }
});

/**
 * Load user profile from API
 */
async function loadUserProfile() {
    try {
        const result = await apiFetch(`${API_BASE}/auth/me`);

        if (result.success && result.user) {
            const user = result.user;
            document.getElementById('displayUsername').textContent = user.username || 'N/A';
            document.getElementById('displayEmail').textContent = user.email || 'N/A';
            document.getElementById('displayBirthday').textContent = user.birthday || 'Not set';
            document.getElementById('displayStatus').textContent = user.status || 'Not set';
            document.getElementById('displayBio').textContent = user.bio || 'No description provided.';

            // Pre-fill edit form inputs
            const inputBirthday = document.getElementById('inputBirthday');
            const inputStatus = document.getElementById('inputStatus');
            const inputBio = document.getElementById('inputBio');

            if (inputBirthday) inputBirthday.value = user.birthday || '';
            if (inputStatus) inputStatus.value = user.status || '';
            if (inputBio) inputBio.value = user.bio || '';

            // Auto-fill project upload username
            const projectUsernameField = document.getElementById('projectUsername');
            if (projectUsernameField) {
                projectUsernameField.value = user.username;
                projectUsernameField.readOnly = true;
            }
        }
    } catch (err) {
        console.error('Failed to load profile:', err);
    }
}

/**
 * Load user's uploaded projects
 */
async function loadUserProjects() {
    const grid = document.getElementById('userProjectsGrid');
    if (!grid) return;

    try {
        const result = await apiFetch(`${API_BASE}/user/projects`);

        if (result.success && result.data && result.data.length > 0) {
            // Render project cards with delete controls for the account page
            grid.innerHTML = result.data.map(project => `
                <div class="project-display-card mini" data-project-id="${project._id}">
                    <h4 class="project-display-title">${escapeHTML(project.title)}</h4>
                    <p class="project-display-desc">${escapeHTML(project.description)}</p>
                    <div style="display:flex; gap:8px; margin-top:8px; align-items:center;">
                        ${safeExternalUrl(project.link) ? `
                            <a href="${escapeHTML(safeExternalUrl(project.link))}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm pearl-button project-display-link">
                                <span class="wrap">
                                    <span class="pearl-label">
                                        <span class="pearl-star">✧</span>
                                        <span class="pearl-star-alt">✦</span>
                                        <span>View Project</span>
                                    </span>
                                </span>
                            </a>
                        ` : '<span class="text-muted-padded">Invalid project link</span>'}

                        <button class="btn btn-primary btn-sm pearl-button project-delete-btn" data-project-id="${project._id}" title="Delete project" aria-label="Delete project">
                            <span class="wrap">
                                <span class="pearl-label">
                                    <span class="pearl-star">✧</span>
                                    <span class="pearl-star-alt">✦</span>
                                    ${typeof icon === 'function' ? icon('xCircle', 16) : ''}
                                    <span>Delete</span>
                                </span>
                            </span>
                        </button>
                    </div>
                </div>
            `).join('');

            // Attach delete button handlers (event delegation)
            grid.querySelectorAll('.project-delete-btn').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const pid = btn.getAttribute('data-project-id');
                    const titleEl = btn.closest('.project-display-card')?.querySelector('.project-display-title');
                    const titleText = titleEl ? titleEl.textContent : '';
                    showConfirmDelete(pid, titleText);
                });
            });
        } else {
            grid.innerHTML = '<p class="text-muted-padded">You haven\'t uploaded any projects yet.</p>';
        }
    } catch (err) {
        grid.innerHTML = '<p class="text-muted-padded">Could not load your projects.</p>';
    }
}


// ==================== DELETE PROJECT (ACCOUNT PAGE) ====================
/**
 * Show confirmation modal before deleting a project
 */
function showConfirmDelete(projectId, title) {
    const modal = document.getElementById('confirmDeleteModal');
    const msg = document.getElementById('confirmDeleteMessage');
    const deleteBtn = document.getElementById('confirmDeleteBtn');
    const cancelBtn = document.getElementById('confirmCancelBtn');
    const closeBtn = document.getElementById('confirmDeleteClose');

    if (!modal || !deleteBtn || !cancelBtn || !msg) {
        // Fallback to native confirm
        if (window.confirm('Are you sure you want to delete this project?')) {
            deleteProject(projectId);
        }
        return;
    }

    msg.textContent = title ? `Are you sure you want to delete "${title}"?` : 'Are you sure you want to delete this project?';

    // Ensure previous listeners are removed
    deleteBtn.onclick = null;
    cancelBtn.onclick = null;
    closeBtn.onclick = null;

    deleteBtn.onclick = async function () {
        // show loading state inside the .text span to preserve structure
        deleteBtn.disabled = true;
        const textSpan = deleteBtn.querySelector('.text');
        const originalInner = textSpan ? textSpan.innerHTML : deleteBtn.innerHTML;
        if (textSpan) {
            textSpan.innerHTML = '<span class="btn-spinner" aria-hidden="true"></span> Deleting...';
        } else {
            deleteBtn.innerHTML = '<span class="btn-spinner" aria-hidden="true"></span> Deleting...';
        }

        try {
            await deleteProject(projectId);
        } finally {
            deleteBtn.disabled = false;
            if (textSpan) {
                textSpan.innerHTML = originalInner;
            } else {
                deleteBtn.innerHTML = originalInner;
            }
        }
    };

    cancelBtn.onclick = function () { hideConfirmDeleteModal(); };
    closeBtn.onclick = function () { hideConfirmDeleteModal(); };

    modal.classList.remove('hidden');
}

function hideConfirmDeleteModal() {
    const modal = document.getElementById('confirmDeleteModal');
    if (modal) modal.classList.add('hidden');
}

/**
 * Delete project API call and DOM update
 */
async function deleteProject(projectId) {
    if (!projectId) return;
    console.debug('[account] deleteProject()', projectId);
    try {
        const result = await apiFetch(`${API_BASE}/projects/${projectId}`, { method: 'DELETE' });
        console.debug('[account] deleteProject result', result);

        if (result.status === 401) {
            window.location.href = 'login.html';
            return;
        }

        // Handle common error statuses explicitly
        if (result.status === 403) {
            showAccountMessage(result.message || result.error || 'Unauthorized', 'error');
            return;
        }
        if (result.status === 404) {
            showAccountMessage(result.message || result.error || 'Project not found', 'error');
            return;
        }
        if (result.status === 400) {
            showAccountMessage(result.message || result.error || 'Invalid request', 'error');
            return;
        }

        if (result.success) {
            // Remove card from UI
            const el = document.querySelector(`.project-display-card[data-project-id='${projectId}']`);
            if (el) el.remove();

            // Refresh user's projects to ensure UI sync
            if (typeof loadUserProjects === 'function') {
                try { await loadUserProjects(); } catch (e) { /* ignore */ }
            }

            // Hide modal if open
            hideConfirmDeleteModal();

            // Show success message
            showAccountMessage('Project deleted successfully', 'success');
        } else {
            hideConfirmDeleteModal();
            showAccountMessage(result.message || result.error || 'Could not delete project', 'error');
        }
    } catch (err) {
        console.error('Delete project error:', err);
        hideConfirmDeleteModal();
        showAccountMessage('Server error while deleting project', 'error');
    }
}

/**
 * Show an inline account-level message (success/error)
 */
function showAccountMessage(message, type) {
    const successEl = document.getElementById('uploadSuccessMsg');
    const errorEl = document.getElementById('uploadErrorMsg');

    if (type === 'success') {
        if (errorEl) hideElement(errorEl);
        if (successEl) {
            successEl.textContent = message;
            successEl.classList.remove('hidden');
            setTimeout(() => successEl.classList.add('hidden'), 4000);
        } else {
            alert(message);
        }
    } else {
        if (successEl) hideElement(successEl);
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.classList.remove('hidden');
            setTimeout(() => errorEl.classList.add('hidden'), 6000);
        } else {
            alert(message);
        }
    }
}

/**
 * Show the edit profile form
 */
function showEditForm() {
    const profileView = document.getElementById('profileView');
    const profileForm = document.getElementById('profileForm');
    if (profileView) hideElement(profileView);
    if (profileForm) showElement(profileForm);
}

/**
 * Hide the edit profile form
 */
function hideEditForm() {
    const profileView = document.getElementById('profileView');
    const profileForm = document.getElementById('profileForm');
    if (profileView) showElement(profileView);
    if (profileForm) hideElement(profileForm);
}

/**
 * Save profile changes
 */
async function saveProfile() {
    const birthday = document.getElementById('inputBirthday').value;
    const status = document.getElementById('inputStatus').value.trim();
    const bio = document.getElementById('inputBio').value.trim();

    const saveBtn = document.querySelector('#profileForm button[type="submit"]');
    let originalText = '';
    if (saveBtn) {
        originalText = saveBtn.textContent;
        saveBtn.textContent = 'Saving...';
        saveBtn.disabled = true;
    }

    try {
        const result = await apiFetch(`${API_BASE}/auth/update-profile`, {
            method: 'PUT',
            body: JSON.stringify({ birthday, status, bio })
        });

        if (result.success) {
            // Update display values
            document.getElementById('displayBirthday').textContent = birthday || 'Not set';
            document.getElementById('displayStatus').textContent = status || 'Not set';
            document.getElementById('displayBio').textContent = bio || 'No description provided.';

            hideEditForm();
        } else {
            alert(result.error || 'Could not update profile');
        }
    } catch (err) {
        console.error('Save profile error:', err);
        alert('Server error. Make sure the backend is running.');
    } finally {
        if (saveBtn) {
            saveBtn.textContent = originalText;
            saveBtn.disabled = false;
        }
    }
}
