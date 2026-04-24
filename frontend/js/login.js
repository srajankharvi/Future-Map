// ==================== LOGIN PAGE MODULE ====================

document.addEventListener('DOMContentLoaded', () => {
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

    // Setup toggle signup buttons
    document.querySelectorAll('[data-action="toggle-signup"]').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            toggleSignup();
        });
    });
});

/**
 * Handle login form submission
 */
async function handleLogin() {
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const rememberMe = document.getElementById('rememberMe');

    clearLoginErrors();

    if (!username || !password) {
        showLoginError('Please enter both username and password');
        return;
    }

    const loginBtn = document.querySelector('#loginForm .btn-block');
    let originalText = '';
    if (loginBtn) {
        originalText = loginBtn.textContent;
        loginBtn.textContent = 'Logging in...';
        loginBtn.disabled = true;
    }

    try {
        const result = await apiFetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });

        if (result.success) {
            if (rememberMe && rememberMe.checked) {
                localStorage.setItem('futureMapUser', result.user.username);
            }
            sessionStorage.setItem('futureMapUser', result.user.username);

            showLoginSuccess('Login successful! Welcome ' + escapeHTML(result.user.username));
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1200);
        } else {
            showLoginError(result.error || 'Invalid credentials');
        }
    } catch (err) {
        console.error('Login error:', err);
        showLoginError('Server error. Make sure the backend is running.');
    } finally {
        if (loginBtn) {
            loginBtn.textContent = originalText;
            loginBtn.disabled = false;
        }
    }
}

/**
 * Handle signup form submission
 */
async function handleSignup() {
    const username = document.getElementById('signupUsername').value.trim();
    const email = document.getElementById('signupEmail').value.trim();
    const password = document.getElementById('signupPassword').value;
    const confirmPassword = document.getElementById('signupConfirmPassword').value;

    clearLoginErrors();

    if (!username || !email || !password || !confirmPassword) {
        showSignupError('Please fill in all fields');
        return;
    }

    if (!/^[a-zA-Z0-9_]{3,30}$/.test(username)) {
        showSignupError('Username must be 3-30 characters (letters, numbers, underscore only)');
        return;
    }

    if (password.length < 6) {
        showSignupError('Password must be at least 6 characters');
        return;
    }

    if (password.length > 128) {
        showSignupError('Password is too long (max 128 characters)');
        return;
    }

    if (password !== confirmPassword) {
        showSignupError('Passwords do not match');
        return;
    }

    const signupBtn = document.querySelector('#signupForm .btn-block');
    let originalText = '';
    if (signupBtn) {
        originalText = signupBtn.textContent;
        signupBtn.textContent = 'Creating account...';
        signupBtn.disabled = true;
    }

    try {
        const result = await apiFetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            body: JSON.stringify({ username, email, password })
        });

        if (result.success) {
            showSignupSuccess('Account created successfully! Redirecting to login...');
            document.getElementById('signupForm').reset();
            setTimeout(() => {
                toggleSignup();
                clearLoginErrors();
            }, 1500);
        } else {
            showSignupError(result.error || 'Error during registration');
        }
    } catch (err) {
        console.error('Signup error:', err);
        showSignupError('Server error. Make sure the backend is running.');
    } finally {
        if (signupBtn) {
            signupBtn.textContent = originalText;
            signupBtn.disabled = false;
        }
    }
}

/**
 * Toggle between login and signup forms
 */
function toggleSignup() {
    const loginBox = document.querySelector('.login-box');
    const signupBox = document.getElementById('signupBox');
    if (!loginBox || !signupBox) return;

    clearLoginErrors();

    if (isHidden(loginBox)) {
        showElement(loginBox);
        hideElement(signupBox);
    } else {
        hideElement(loginBox);
        showElement(signupBox);
    }
}

/**
 * Show login error message
 */
function showLoginError(message) {
    let el = document.getElementById('loginErrorMsg');
    if (!el) {
        el = document.createElement('div');
        el.id = 'loginErrorMsg';
        el.className = 'upload-msg upload-error';
        const form = document.getElementById('loginForm');
        if (form) form.parentNode.insertBefore(el, form);
    }
    el.textContent = 'Error: ' + message;
    showElement(el);
}

/**
 * Show login success message
 */
function showLoginSuccess(message) {
    let el = document.getElementById('loginSuccessMsg');
    if (!el) {
        el = document.createElement('div');
        el.id = 'loginSuccessMsg';
        el.className = 'upload-msg upload-success';
        const form = document.getElementById('loginForm');
        if (form) form.parentNode.insertBefore(el, form);
    }
    el.textContent = 'Success: ' + message;
    showElement(el);
    const err = document.getElementById('loginErrorMsg');
    if (err) hideElement(err);
}

/**
 * Show signup error message
 */
function showSignupError(message) {
    let el = document.getElementById('signupErrorMsg');
    if (!el) {
        el = document.createElement('div');
        el.id = 'signupErrorMsg';
        el.className = 'upload-msg upload-error';
        const form = document.getElementById('signupForm');
        if (form) form.parentNode.insertBefore(el, form);
    }
    el.textContent = 'Error: ' + message;
    showElement(el);
}

/**
 * Show signup success message
 */
function showSignupSuccess(message) {
    let el = document.getElementById('signupSuccessMsg');
    if (!el) {
        el = document.createElement('div');
        el.id = 'signupSuccessMsg';
        el.className = 'upload-msg upload-success';
        const form = document.getElementById('signupForm');
        if (form) form.parentNode.insertBefore(el, form);
    }
    el.textContent = 'Success: ' + message;
    showElement(el);
    const err = document.getElementById('signupErrorMsg');
    if (err) hideElement(err);
}

/**
 * Clear all error and success messages
 */
function clearLoginErrors() {
    ['loginErrorMsg', 'loginSuccessMsg', 'signupErrorMsg', 'signupSuccessMsg'].forEach(id => {
        const el = document.getElementById(id);
        if (el) hideElement(el);
    });
}
