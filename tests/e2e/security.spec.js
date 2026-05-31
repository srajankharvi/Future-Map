const { test, expect } = require('@playwright/test');
const { loginUser } = require('./helpers/auth-helper');

test.describe('Security & Protection validation', () => {
  const timestamp = Date.now();
  const testUser = `sec_${timestamp}`;
  const testEmail = `sec_${timestamp}@example.com`;
  const testPassword = `Pass_${timestamp}!`;

  test('Auth Guard: Direct access to protected page without cookies should redirect to login.html', async ({ page }) => {
    // Clear cookies to simulate unauthenticated user
    await page.context().clearCookies();

    // Try navigating to a protected page
    await page.goto('/account.html');

    // Verify redirect to login.html
    await page.waitForURL('**/login.html');
    await expect(page.locator('#loginBox')).toBeVisible();
  });

  test('Cookie Security: Verify session cookies have HttpOnly flags and Lax samesite setting', async ({ page }) => {
    // 1. Register and Login to set session cookies
    await page.goto('/login.html');
    await page.click('#showSignupLink');
    await page.waitForSelector('#signupBox:not(.hidden)');
    await page.fill('#signupFullName', 'Security Tester');
    await page.fill('#signupUsername', testUser);
    await page.fill('#signupEmail', testEmail);
    await page.fill('#signupPassword', testPassword);
    await page.fill('#signupConfirmPassword', testPassword);
    await page.click('#signupSubmitBtn');
    
    // Success redirect wait
    await page.waitForSelector('#loginBox:not(.hidden)', { timeout: 5000 });
    await loginUser(page, testUser, testPassword);

    // 2. Extract cookies
    const cookies = await page.context().cookies();
    
    // Find the Flask session cookie (default is 'session')
    const sessionCookie = cookies.find(c => c.name === 'session');
    
    expect(sessionCookie).toBeDefined();
    
    // Verify security flags
    expect(sessionCookie.httpOnly).toBe(true);
    expect(sessionCookie.sameSite).toBe('Lax');
  });

  test('CSRF Protection: POST/PUT requests without a valid X-CSRF-Token should return 403 Forbidden', async ({ request }) => {
    // Perform a request mutating state without sending X-CSRF-Token
    const response = await request.post('/api/auth/register', {
      data: {
        username: 'forbid_user',
        email: 'forbid@example.com',
        password: 'Password123!',
        confirm_password: 'Password123!'
      },
      headers: {
        // Explicitly omitting X-CSRF-Token
        'Content-Type': 'application/json'
      }
    });

    // Expect 403 Forbidden
    expect(response.status()).toBe(403);
    
    const body = await response.json();
    expect(body.success).toBe(false);
    expect(body.error).toContain('CSRF token');
  });
});
