const { test, expect } = require('@playwright/test');
const { registerAndLogin } = require('./helpers/auth-helper');

test.describe('AI Interview Preparation Flow', () => {
  const timestamp = Date.now();
  const testUser = `intr_${timestamp}`;
  const testEmail = `intr_${timestamp}@example.com`;
  const testPassword = `Pass_${timestamp}!`;

  test.beforeEach(async ({ page }) => {
    await registerAndLogin(page, testUser, testEmail, testPassword, 'Interview Tester');
  });

  test('Should generate custom AI questions', async ({ page }) => {
    await page.goto('/interview.html');
    await expect(page.locator('h1')).toContainText('Interview Preparation');

    // 1. Select Career Category in AI Generator
    const categorySelect = page.locator('select#aiCategory + .custom-select-wrapper');
    await categorySelect.locator('.custom-select-trigger').click();
    await categorySelect.locator('.custom-select-item').filter({ hasText: 'Computer & IT' }).click();

    // 2. Select Difficulty Level (e.g. Intermediate)
    await page.locator('#difficultyPills button[data-level="intermediate"]').click();

    // 3. Set Question Count (default is 5, let's select 3 for quicker API response)
    const slider = page.locator('#aiCount');
    await slider.fill('3');

    // 4. Click Generate
    await page.click('#generateBtn');

    // 5. Verify results section renders
    const resultsEl = page.locator('#aiResults');
    await expect(resultsEl).toBeVisible({ timeout: 25000 });
    await expect(resultsEl.locator('.ai-question-card')).toHaveCount({ min: 1 });

    // 6. Click on the first question to expand answer
    const firstCard = resultsEl.locator('.ai-question-card').first();
    await firstCard.locator('.ai-question-header').click();
    await expect(firstCard).toHaveClass(/expanded/);
  });

  test('Should run interactive mock interview chat', async ({ page }) => {
    await page.goto('/interview.html');

    // 1. Select Career Category in Mock Interview Setup
    const mockSelect = page.locator('select#mockCategory + .custom-select-wrapper');
    await mockSelect.locator('.custom-select-trigger').click();
    await mockSelect.locator('.custom-select-item').filter({ hasText: 'Computer & IT' }).click();

    // 2. Start Interview
    await page.click('#startMockBtn');

    // 3. Verify chat UI visible and contains AI greeting
    const chatbox = page.locator('#mockChatbox');
    await expect(chatbox).toBeVisible();
    await expect(chatbox.locator('.message-ai')).toContainText('interviewer');

    // 4. Respond to greeting
    const input = page.locator('#chatInput');
    await input.fill('Yes, I am ready to start the interview.');
    await page.click('#sendMessageBtn');

    // 5. Wait for interviewer's response
    // Wait for the thinking loading state to disappear and the new AI message to appear
    await page.waitForSelector('#chatLoading.hidden', { timeout: 25000 });
    
    // Check that we have at least two AI messages now (greeting + first question)
    const aiMessages = chatbox.locator('.message-ai');
    await expect(aiMessages).toHaveCount({ min: 2 });
    
    // 6. Reset interview session
    // Intercept standard confirmation dialog
    page.once('dialog', async dialog => {
      expect(dialog.message()).toContain('Are you sure');
      await dialog.accept();
    });
    
    await page.click('#resetMockBtn');
    
    // Verify setup panel visible again
    await expect(page.locator('#mockSetup')).toBeVisible();
  });
});
