const { test, expect } = require('@playwright/test');
const { registerAndLogin } = require('./helpers/auth-helper');

test.describe('Skill Tracker Flow', () => {
  const timestamp = Date.now();
  const testUser = `skil_${timestamp}`;
  const testEmail = `skil_${timestamp}@example.com`;
  const testPassword = `Pass_${timestamp}!`;

  test.beforeEach(async ({ page }) => {
    await registerAndLogin(page, testUser, testEmail, testPassword, 'Skill Learner');
  });

  test('Should choose a target career, load skills, and track progress', async ({ page }) => {
    await page.goto('/account.html');
    await expect(page.locator('#displayUsername')).toHaveText(testUser);

    // 1. Verify skill tracker placeholder is displayed initially
    const stepsContainer = page.locator('#skillRoadmapSteps');
    await expect(stepsContainer.locator('.skill-roadmap-placeholder')).toBeVisible();

    // 2. Select a target career in the skill tracker section
    const skillSection = page.locator('#skillRoadmapSection');
    const careerSelect = skillSection.locator('select#careerSelect + .custom-select-wrapper');
    await careerSelect.locator('.custom-select-trigger').click();
    await careerSelect.locator('.custom-select-item').filter({ hasText: 'Aeronautical Engineering' }).click();

    // 3. Save the career selection
    await page.click('#saveCareerBtn');

    // 4. Verify progress wraps are now visible
    const progressWrap = page.locator('#skillRoadmapProgressWrap');
    await expect(progressWrap).toBeVisible();
    await expect(page.locator('#skillProgressPercent')).toHaveText('0%');

    // 5. Verify checklist steps are rendered
    await expect(stepsContainer.locator('.skill-roadmap-step')).toHaveCount({ min: 1 });

    // 6. Check a skill item as completed
    const firstCheckbox = stepsContainer.locator('.skill-check-input').first();
    await firstCheckbox.check();

    // 7. Verify progress updates
    // It should now be greater than 0%
    const progressPercent = page.locator('#skillProgressPercent');
    await expect(progressPercent).not.toHaveText('0%');

    // 8. Toggle the checkbox off and verify progress drops back
    await firstCheckbox.uncheck();
    await expect(progressPercent).toHaveText('0%');
  });
});
