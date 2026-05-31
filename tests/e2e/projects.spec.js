const { test, expect } = require('@playwright/test');
const { registerAndLogin } = require('./helpers/auth-helper');

test.describe('Community Projects Flow', () => {
  const timestamp = Date.now();
  const testUser = `proj_${timestamp}`;
  const testEmail = `proj_${timestamp}@example.com`;
  const testPassword = `Pass_${timestamp}!`;
  
  const projectTitle = `E2E Automated Project ${timestamp}`;
  const projectLink = `https://github.com/test/project-${timestamp}`;
  const projectDescription = `This is a test project description created automatically by Playwright E2E tests at ${timestamp}.`;

  test.beforeEach(async ({ page }) => {
    await registerAndLogin(page, testUser, testEmail, testPassword, 'Project Uploader');
  });

  test('Should upload a new project from account page and view it on projects page', async ({ page }) => {
    // 1. Open account page
    await page.goto('/account.html');
    await expect(page.locator('h2').first()).toHaveText('User Profile');

    // 2. Fill out project upload form
    await page.fill('#projectTitle', projectTitle);
    await page.fill('#projectLink', projectLink);
    await page.fill('#projectDescription', projectDescription);

    // 3. Submit form
    await page.click('#uploadBtn');

    // 4. Verify success message
    const successMsg = page.locator('#uploadSuccessMsg');
    await expect(successMsg).toBeVisible();
    await expect(successMsg).toContainText('Project uploaded successfully');

    // 5. Navigate to Projects showcase page
    await page.goto('/projects.html');
    await expect(page.locator('h1')).toHaveText('Community Projects');

    // 6. Search for our project
    await page.fill('#projectSearch', projectTitle);

    // 7. Verify the project appears in the grid
    const projectsGrid = page.locator('#projectsGrid');
    const projectCard = projectsGrid.locator('.career-card').first();
    await expect(projectCard).toBeVisible();
    await expect(projectCard.locator('h3')).toHaveText(projectTitle);
    await expect(projectCard.locator('.card-body p').first()).toHaveText(projectDescription);
    
    // Verify the project link
    const viewButton = projectCard.locator('.card-footer a');
    await expect(viewButton).toHaveAttribute('href', projectLink);
  });
});
