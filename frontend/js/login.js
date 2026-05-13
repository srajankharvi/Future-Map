// ==================== LOGIN PAGE MODULE ====================
// Fixes applied: Issues #4, #23, #24, #25, #26, #27, #28, #29

// --- Constants (Issue #26: no magic numbers) ---
const REDIRECT_DELAY_MS = 1200;
const SIGNUP_TOGGLE_DELAY_MS = 1500;
const MSG_AUTO_DISMISS_MS = 8000;

document.addEventListener('DOMContentLoaded', () => {
    // Issue #23: Verify global dependencies from main.js exist
    if (typeof apiFetch !== 'function' || typeof API_BASE === 'undefined') {
        console.error('[login.js] CRITICAL: main.js globals (apiFetch, API_BASE) not loaded.');
        const body = document.querySelector('.login-container');
        if (body) {
            body.innerHTML = '<div style="padding:40px;text-align:center;color:#ef4444;">' +
                '<h2>Loading Error</h2><p>Core scripts failed to load. Please refresh the page.</p></div>';
        }
        return;
    }

    // Issue #25: Redirect already-authenticated users away from login page
    redirectIfAuthenticated();

    // --- Form Submissions ---
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            handleLogin();
        });
    }

    if (signupForm) {
        signupForm.addEventListener('submit', (e) => {
            e.preventDefault();
            handleSignup();
        });
    }

    // --- Toggle signup/login links ---
    document.querySelectorAll('[data-action="toggle-signup"]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            toggleSignup();
        });
    });

    // --- Issue #17: Password visibility toggles ---
    document.querySelectorAll('.password-toggle').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetId = btn.getAttribute('data-target');
            const input = document.getElementById(targetId);
            if (!input) return;

            const isPassword = input.type === 'password';
            input.type = isPassword ? 'text' : 'password';

            const eyeIcon = btn.querySelector('.eye-icon');
            const eyeOffIcon = btn.querySelector('.eye-off-icon');
            if (eyeIcon && eyeOffIcon) {
                eyeIcon.classList.toggle('hidden', !isPassword);
                eyeOffIcon.classList.toggle('hidden', isPassword);
            }
        });
    });

    // --- Issue #33: Password strength meter ---
    const signupPassword = document.getElementById('signupPassword');
    if (signupPassword) {
        signupPassword.addEventListener('input', () => {
            updatePasswordStrength(signupPassword.value);
        });
    }
});


/**
 * Issue #25: Redirect to index if already logged in
 */
async function redirectIfAuthenticated() {
    try {
        if (typeof checkAuth === 'function') {
            const user = await checkAuth(false); // Don't redirect on fail
            if (user) {
                window.location.href = 'index.html';
            }
        }
    } catch (err) {
        // Not authenticated — stay on login page
    }
}


/**
 * Handle login form submission
 */
async function handleLogin() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value; // Issue #24: Don't trim password

    clearAllMessages();

    if (!username || !password) {
        showMessage('loginErrorMsg', 'Please enter both username and password');
        return;
    }

    // Issue #27: Show loading spinner
    setButtonLoading('loginSubmitBtn', true);

    try {
        const result = await apiFetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (result.success) {
            // Issue #4: Use sessionStorage only (not localStorage — XSS-safe)
            sessionStorage.setItem('futureMapUser', result.user.username);

            showMessage('loginSuccessMsg', 'Login successful! Welcome ' + escapeHTML(result.user.username));
            setTimeout(() => {
                window.location.href = 'index.html';
            }, REDIRECT_DELAY_MS);
        } else {
            showMessage('loginErrorMsg', result.error || 'Invalid credentials');
        }
    } catch (err) {
        console.error('Login error:', err);
        showMessage('loginErrorMsg', 'Server error. Make sure the backend is running.');
    } finally {
        setButtonLoading('loginSubmitBtn', false);
    }
}


/**
 * Handle signup form submission
 */
async function handleSignup() {
    const full_name = document.getElementById('signupFullName').value.trim();  // Issue #15/#29
    const username = document.getElementById('signupUsername').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;  // Issue #24: Don't trim
    const confirmPassword = document.getElementById('signupConfirmPassword').value;

    clearAllMessages();

    // --- Client-side validation ---
    if (!username || !email || !password || !confirmPassword) {
        showMessage('signupErrorMsg', 'Please fill in all required fields');
        return;
    }

    if (!/^[a-zA-Z0-9_]{3,30}$/.test(username)) {
        showMessage('signupErrorMsg', 'Username must be 3-30 characters (letters, numbers, underscore only)');
        return;
    }

    if (password.length < 6) {
        showMessage('signupErrorMsg', 'Password must be at least 6 characters');
        return;
    }

    if (password.length > 128) {
        showMessage('signupErrorMsg', 'Password is too long (max 128 characters)');
        return;
    }

    if (password !== confirmPassword) {
        showMessage('signupErrorMsg', 'Passwords do not match');
        return;
    }

    // Issue #27: Show loading spinner
    setButtonLoading('signupSubmitBtn', true);

    try {
        // Issue #29: Send full_name + confirm_password to backend (Issue #10)
        const result = await apiFetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            body: JSON.stringify({
                username,
                email,
                password,
                confirm_password: confirmPassword,
                full_name
            })
        });

        if (result.success) {
            showMessage('signupSuccessMsg', 'Account created successfully! Redirecting to login...');
            document.getElementById('signupForm').reset();
            // Reset password strength meter
            resetPasswordStrength();
            setTimeout(() => {
                toggleSignup();
                clearAllMessages();
            }, SIGNUP_TOGGLE_DELAY_MS);
        } else {
            showMessage('signupErrorMsg', result.error || 'Error during registration');
        }
    } catch (err) {
        console.error('Signup error:', err);
        showMessage('signupErrorMsg', 'Server error. Make sure the backend is running.');
    } finally {
        setButtonLoading('signupSubmitBtn', false);
    }
}


/**
 * Toggle between login and signup forms with smooth transitions
 */
function toggleSignup() {
    const loginBox = document.getElementById('loginBox');
    const signupBox = document.getElementById('signupBox');
    if (!loginBox || !signupBox) return;

    clearAllMessages();

    if (loginBox.classList.contains('hidden')) {
        loginBox.classList.remove('hidden');
        loginBox.classList.add('auth-fade-in');
        signupBox.classList.add('hidden');
        signupBox.classList.remove('auth-fade-in');
    } else {
        signupBox.classList.remove('hidden');
        signupBox.classList.add('auth-fade-in');
        loginBox.classList.add('hidden');
        loginBox.classList.remove('auth-fade-in');
    }
}


// ==================== MESSAGE HELPERS ====================

/**
 * Issue #28: Show a message in a pre-existing container with fade-in animation
 * @param {string} elementId - ID of the message container
 * @param {string} message - Message text to display
 */
function showMessage(elementId, message) {
    const el = document.getElementById(elementId);
    if (!el) return;

    el.textContent = message;
    el.classList.remove('hidden');
    el.classList.add('auth-msg-visible');

    // Auto-dismiss after timeout
    clearTimeout(el._dismissTimer);
    el._dismissTimer = setTimeout(() => {
        el.classList.remove('auth-msg-visible');
        el.classList.add('hidden');
    }, MSG_AUTO_DISMISS_MS);
}

/**
 * Clear all error and success messages
 */
function clearAllMessages() {
    ['loginErrorMsg', 'loginSuccessMsg', 'signupErrorMsg', 'signupSuccessMsg'].forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.classList.add('hidden');
            el.classList.remove('auth-msg-visible');
            el.textContent = '';
            clearTimeout(el._dismissTimer);
        }
    });
}


// ==================== BUTTON LOADING STATE ====================

/**
 * Issue #27: Toggle loading spinner on a button
 * @param {string} btnId - Button element ID
 * @param {boolean} loading - Whether to show loading state
 */
function setButtonLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    if (!btn) return;

    const textEl = btn.querySelector('.btn-text');
    const spinnerEl = btn.querySelector('.btn-spinner');

    if (loading) {
        btn.disabled = true;
        btn.classList.add('btn-loading');
        if (textEl) textEl.classList.add('hidden');
        if (spinnerEl) spinnerEl.classList.remove('hidden');
    } else {
        btn.disabled = false;
        btn.classList.remove('btn-loading');
        if (textEl) textEl.classList.remove('hidden');
        if (spinnerEl) spinnerEl.classList.add('hidden');
    }
}


// ==================== PASSWORD STRENGTH METER ====================

/**
 * Issue #33: Calculate and display password strength
 * @param {string} password - Current password value
 */
function updatePasswordStrength(password) {
    const fill = document.getElementById('passwordStrengthFill');
    const text = document.getElementById('passwordStrengthText');
    if (!fill || !text) return;

    let score = 0;
    if (password.length >= 6) score++;
    if (password.length >= 10) score++;
    if (/[a-z]/.test(password) && /[A-Z]/.test(password)) score++;
    if (/\d/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;

    const levels = [
        { label: 'Min 6 characters', color: 'transparent', width: '0%' },
        { label: 'Weak', color: '#ef4444', width: '20%' },
        { label: 'Fair', color: '#f59e0b', width: '40%' },
        { label: 'Good', color: '#3b82f6', width: '60%' },
        { label: 'Strong', color: '#10b981', width: '80%' },
        { label: 'Very Strong', color: '#059669', width: '100%' }
    ];

    const level = levels[Math.min(score, levels.length - 1)];
    fill.style.width = level.width;
    fill.style.background = level.color;
    text.textContent = password.length === 0 ? 'Min 6 characters' : level.label;
    text.style.color = level.color === 'transparent' ? 'var(--text-muted)' : level.color;
}

/**
 * Reset password strength meter to initial state
 */
function resetPasswordStrength() {
    const fill = document.getElementById('passwordStrengthFill');
    const text = document.getElementById('passwordStrengthText');
    if (fill) {
        fill.style.width = '0%';
        fill.style.background = 'transparent';
    }
    if (text) {
        text.textContent = 'Min 6 characters';
        text.style.color = 'var(--text-muted)';
    }
}
