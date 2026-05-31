const { test, expect } = require('@playwright/test');
const { registerAndLogin } = require('./helpers/auth-helper');

test.describe('YourPath Roadmap Flow', () => {
  const timestamp = Date.now();
  const testUser = `path_${timestamp}`;
  const testEmail = `path_${timestamp}@example.com`;
  const testPassword = `Pass_${timestamp}!`;

  test.beforeEach(async ({ page }) => {
    await registerAndLogin(page, testUser, testEmail, testPassword, 'Path Finder');
  });

  test('Should select career/course and generate timeline roadmap', async ({ page }) => {
    await page.goto('/yourpath.html');
    await expect(page.locator('h1')).toHaveText('Your Path');

    // 1. Select Career from Custom Select Dropdown
    const careerSelect = page.locator('select#careerSelect + .custom-select-wrapper');
    await careerSelect.locator('.custom-select-trigger').click();
    await careerSelect.locator('.custom-select-item').filter({ hasText: 'Aeronautical Engineering' }).click();

    // Verify Career Preview becomes visible
    await expect(page.locator('#careerPreview')).toBeVisible();
    await expect(page.locator('#careerPreviewName')).toHaveText('Aeronautical Engineering');

    // 2. Select Course from Custom Select Dropdown
    const courseSelect = page.locator('select#courseSelect + .custom-select-wrapper');
    await courseSelect.locator('.custom-select-trigger').click();
    await courseSelect.locator('.custom-select-item').filter({ hasText: 'Bachelor of Science (B.Sc)' }).click();

    // Verify Course Preview becomes visible
    await expect(page.locator('#coursePreview')).toBeVisible();
    await expect(page.locator('#coursePreviewName')).toHaveText('Bachelor of Science (B.Sc)');

    // 3. Verify Generate Path Button is visible and click it
    const generateBtnWrapper = page.locator('#generatePathWrapper');
    await expect(generateBtnWrapper).toBeVisible();
    
    const generateBtn = page.locator('#generatePathBtn');
    await generateBtn.click();

    // 4. Verify Roadmap Section is displayed
    const roadmapSection = page.locator('#roadmapSection');
    await expect(roadmapSection).toBeVisible();
    await expect(page.locator('#roadmapTitle')).toContainText('Your Path to Aeronautical Engineering');

    // 5. Verify timeline cards exist
    const timeline = page.locator('#roadmapTimeline');
    await expect(timeline.locator('.timeline-item')).toHaveCount({ min: 1 });
    
    // Verify first timeline-item is visible and contains Phase 1
    const firstTimelineItem = timeline.locator('.timeline-item').first();
    await expect(firstTimelineItem.locator('.timeline-step-label')).toContainText('Phase 1');
  });
});
