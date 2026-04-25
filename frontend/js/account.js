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
            grid.innerHTML = result.data.map(project => `
                <div class="project-display-card mini">
                    <h4 class="project-display-title">${escapeHTML(project.title)}</h4>
                    <p class="project-display-desc">${escapeHTML(project.description)}</p>
                    <a href="${escapeHTML(project.link)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm project-display-link">
                        View Project
                    </a>
                </div>
            `).join('');
        } else {
            grid.innerHTML = '<p class="text-muted-padded">You haven\'t uploaded any projects yet.</p>';
        }
    } catch (err) {
        grid.innerHTML = '<p class="text-muted-padded">Could not load your projects.</p>';
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
