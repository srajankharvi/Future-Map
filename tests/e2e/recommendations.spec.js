const { test, expect } = require('@playwright/test');
const { registerAndLogin } = require('./helpers/auth-helper');

test.describe('Career & Course Recommendation Flow', () => {
  const timestamp = Date.now();
  const testUser = `reco_${timestamp}`;
  const testEmail = `reco_${timestamp}@example.com`;
  const testPassword = `Pass_${timestamp}!`;

  // Register and login once before running recommendation tests
  test.beforeEach(async ({ page }) => {
    await registerAndLogin(page, testUser, testEmail, testPassword, 'Recommendation Tester');
  });

  test('Should generate recommendations and view details in modal', async ({ page }) => {
    await page.goto('/recommendation.html');
    await expect(page.locator('h1')).toContainText('Recommendation');

    // 1. Select Education Level from Custom Dropdown
    const selectWrapper = page.locator('select#educationLevel + .custom-select-wrapper');
    await selectWrapper.locator('.custom-select-trigger').click();
    
    // Click 'Degree' in the dropdown
    const degreeOption = selectWrapper.locator('.custom-select-item').filter({ hasText: 'Degree' });
    await degreeOption.click();

    // Verify trigger text updated
    await expect(selectWrapper.locator('.custom-select-trigger-text')).toHaveText('Degree');

    // 2. Set Academic Marks
    await page.fill('#marks', '85');

    // 3. Select Skills (select Technical and Problem-Solving)
    await page.check('input[value="technical"]');
    await page.check('input[value="problem-solving"]');

    // 4. Submit Form
    await page.click('button[data-action="generate-recommendations"]');

    // 5. Verify results section shows up
    const resultsSection = page.locator('#resultsSection');
    await expect(resultsSection).toBeVisible();

    // Verify matching careers are rendered
    const careerResults = page.locator('#careerResults');
    await expect(careerResults.locator('.career-card')).toHaveCount({ min: 1 });

    // 6. Click on the first career card to open details modal
    const firstCareerCard = careerResults.locator('.career-card').first();
    const careerTitle = await firstCareerCard.locator('h3').textContent();
    await firstCareerCard.click();

    // Verify modal is displayed and titles match
    const careerModal = page.locator('#careerModal');
    await expect(careerModal).toBeVisible();
    await expect(careerModal.locator('#modalCareerName')).toHaveText(careerTitle);

    // 7. Close the modal
    await careerModal.locator('.close-modal').click();
    await expect(careerModal).toBeHidden();
  });
});
