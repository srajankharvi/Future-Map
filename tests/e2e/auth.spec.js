const { test, expect } = require('@playwright/test');
const { registerUser, loginUser, logoutUser } = require('./helpers/auth-helper');

test.describe('Authentication Flow', () => {
  // Generate a random username to prevent database unique index conflicts
  const timestamp = Date.now();
  const testUser = `user_${timestamp}`;
  const testEmail = `user_${timestamp}@example.com`;
  const testPassword = `Pass_${timestamp}!`;
  const testFullName = `E2E Test User ${timestamp}`;

  test('Should render login page correctly', async ({ page }) => {
    await page.goto('/login.html');
    await expect(page.locator('h1')).toHaveText('Future Map');
    await expect(page.locator('#username')).toBeVisible();
    await expect(page.locator('#password')).toBeVisible();
    await expect(page.locator('#loginSubmitBtn')).toBeVisible();
  });

  test('Should toggle password visibility', async ({ page }) => {
    await page.goto('/login.html');
    const passwordInput = page.locator('#password');
    const toggleButton = page.locator('.password-toggle').first();

    // Initial state should be password
    await expect(passwordInput).toHaveAttribute('type', 'password');

    // Click to show password
    await toggleButton.click();
    await expect(passwordInput).toHaveAttribute('type', 'text');

    // Click to hide password again
    await toggleButton.click();
    await expect(passwordInput).toHaveAttribute('type', 'password');
  });

  test('Should register a new user successfully', async ({ page }) => {
    await registerUser(page, testUser, testEmail, testPassword, testFullName);
    
    // Success message should contain success text
    const successMsg = page.locator('#signupSuccessMsg');
    await expect(successMsg).toBeVisible();
    await expect(successMsg).toContainText('Account created successfully');
  });

  test('Should show error when registering with a duplicate username/email', async ({ page }) => {
    // Attempt to register with the same username and email as the previous test
    await page.goto('/login.html');
    await page.click('#showSignupLink');
    await page.waitForSelector('#signupBox:not(.hidden)');

    await page.fill('#signupFullName', testFullName);
    await page.fill('#signupUsername', testUser); // duplicate
    await page.fill('#signupEmail', testEmail); // duplicate
    await page.fill('#signupPassword', testPassword);
    await page.fill('#signupConfirmPassword', testPassword);

    await page.click('#signupSubmitBtn');

    // Error message should appear
    const errorMsg = page.locator('#signupErrorMsg');
    await expect(errorMsg).toBeVisible();
    await expect(errorMsg).toContainText('already exists');
  });

  test('Should log in successfully with valid credentials', async ({ page }) => {
    await loginUser(page, testUser, testPassword);
    
    // Verify user avatar contains the first initial uppercase
    const expectedInitial = testUser.charAt(0).toUpperCase();
    const avatar = page.locator('.user-section .user-avatar');
    await expect(avatar).toBeVisible();
    await expect(avatar).toHaveText(expectedInitial);
  });

  test('Should show error with invalid credentials', async ({ page }) => {
    await page.goto('/login.html');
    await page.fill('#username', testUser);
    await page.fill('#password', 'WrongPassword123');
    await page.click('#loginSubmitBtn');

    const errorMsg = page.locator('#loginErrorMsg');
    await expect(errorMsg).toBeVisible();
    await expect(errorMsg).toContainText('Invalid username or password');
  });

  test('Should log out successfully and redirect to login page', async ({ page }) => {
    // First login
    await loginUser(page, testUser, testPassword);
    
    // Then logout
    await logoutUser(page);
  });
});
