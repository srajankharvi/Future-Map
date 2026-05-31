/**
 * Reusable Authentication Helpers for Playwright E2E Tests
 */

/**
 * Registers a new user via the UI.
 * @param {import('@playwright/test').Page} page
 * @param {string} username
 * @param {string} email
 * @param {string} password
 * @param {string} fullName
 */
async function registerUser(page, username, email, password, fullName) {
  await page.goto('/login.html');
  
  // Toggle to Signup form
  await page.click('#showSignupLink');
  await page.waitForSelector('#signupBox:not(.hidden)');

  // Fill signup fields
  if (fullName) {
    await page.fill('#signupFullName', fullName);
  }
  await page.fill('#signupUsername', username);
  await page.fill('#signupEmail', email);
  await page.fill('#signupPassword', password);
  await page.fill('#signupConfirmPassword', password);

  // Submit form
  await page.click('#signupSubmitBtn');

  // Wait for success message or auto-toggle transition
  await page.waitForSelector('#signupSuccessMsg:not(.hidden)', { timeout: 10000 });
}

/**
 * Log in a user via the UI.
 * @param {import('@playwright/test').Page} page
 * @param {string} username
 * @param {string} password
 */
async function loginUser(page, username, password) {
  await page.goto('/login.html');
  await page.waitForSelector('#loginBox:not(.hidden)');

  // Fill login fields
  await page.fill('#username', username);
  await page.fill('#password', password);

  // Submit login
  await page.click('#loginSubmitBtn');

  // Verify successful authentication and redirection to index.html
  await page.waitForURL('**/index.html', { timeout: 10000 });
  
  // Wait for the user session avatar to appear in the header to confirm DOM is loaded
  await page.waitForSelector('.user-section .user-avatar', { timeout: 8000 });
}

/**
 * Registers a new user and immediately logs them in.
 * @param {import('@playwright/test').Page} page
 * @param {string} username
 * @param {string} email
 * @param {string} password
 * @param {string} fullName
 */
async function registerAndLogin(page, username, email, password, fullName) {
  await registerUser(page, username, email, password, fullName);
  
  // Wait for signup redirection to complete (1.5s in code) or transition to login form
  await page.waitForSelector('#loginBox:not(.hidden)', { timeout: 5000 });
  
  // Submit the login
  await loginUser(page, username, password);
}

/**
 * Logs out a user via the UI.
 * @param {import('@playwright/test').Page} page
 */
async function logoutUser(page) {
  // Wait for the user avatar/section dropdown
  await page.waitForSelector('.user-section');
  
  // Wait for logout button to be visible and click it
  const logoutBtn = page.locator('#navLogoutBtn a[data-action="logout"]');
  await logoutBtn.scrollIntoViewIfNeeded();
  await logoutBtn.click();
  
  // Verify redirect back to login page
  await page.waitForURL('**/login.html');
}

module.exports = {
  registerUser,
  loginUser,
  registerAndLogin,
  logoutUser,
};
