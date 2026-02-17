/**
 * E2E Test: Basic User Flow
 * 
 * Tests the complete user journey:
 * 1. Landing → Explore
 * 2. View resource detail
 * 3. Register → Login
 * 4. Vote on resource
 * 5. Publish new resource
 */

import { test, expect } from '@playwright/test';

test.describe('Basic User Flow', () => {
  const testEmail = `test-${Date.now()}@example.com`;
  const testPassword = 'TestPass123!';
  const testName = 'Test User E2E';

  test('should complete full user journey', async ({ page }) => {
    // Step 1: Visit home and navigate to explore
    await page.goto('/');
    await expect(page).toHaveTitle(/BioAI Hub/);
    
    // Should see hero section with new design
    await expect(page.locator('text=Institutional AI Repository for Scientific Collaboration')).toBeVisible();
    
    // Navigate to explore via sidebar (new design)
    await page.click('a[href="/explore"]:has-text("Explore")');
    await expect(page).toHaveURL(/\/explore/);
    await expect(page.locator('h1:has-text("Explore Resources")')).toBeVisible();

    // Step 2: View a resource detail (if any resources exist)
    const resourceCard = page.locator('a[href^="/resources/"]').first();
    const hasResources = await resourceCard.isVisible().catch(() => false);
    
    if (hasResources) {
      await resourceCard.click();
      await expect(page).toHaveURL(/\/resources\//);
      
      // Should see new tabs design
      await expect(page.locator('button:has-text("Description")')).toBeVisible();
      await expect(page.locator('button:has-text("Notebook")')).toBeVisible();
      
      // Go back via back button (new design)
      await page.click('text=Back to Dashboard');
    }

    // Step 3: Register - Navigate via navbar (new design)
    await page.click('a[href="/register"]:has-text("Sign Up")');
    await expect(page).toHaveURL('/register');
    
    await page.fill('input[name="email"]', testEmail);
    await page.fill('input[name="name"]', testName);
    await page.fill('input[name="password"]', testPassword);
    await page.fill('input[name="password_confirm"]', testPassword);
    
    await page.click('button[type="submit"]:has-text("Crear cuenta")');
    
    // Should see success toast (react-hot-toast)
    await expect(page.locator('text=/¡Cuenta creada!|¡Registro exitoso!/i')).toBeVisible({ timeout: 10000 });

    // Step 4: Login
    await page.goto('/login');
    await expect(page).toHaveURL('/login');
    
    await page.fill('input[name="email"]', testEmail);
    await page.fill('input[name="password"]', testPassword);
    
    await page.click('button[type="submit"]:has-text("Iniciar sesión")');
    
    // Should see welcome toast and redirect
    await expect(page.locator('text=/¡Bienvenido/i')).toBeVisible({ timeout: 10000 });
    
    // Should see user in navbar (new design with avatar)
    await expect(page.locator(`text=${testName}`)).toBeVisible();

    // Step 5: Publish a resource via sidebar
    await page.click('a[href="/publish"]:has-text("Publish")');
    await expect(page).toHaveURL('/publish');
    
    // Fill resource form
    const resourceTitle = `Test Resource ${Date.now()}`;
    await page.fill('input[name="title"]', resourceTitle);
    await page.fill('textarea[name="description"]', 'This is a test resource created by E2E test');
    await page.selectOption('select[name="type"]', 'Prompt');
    
    // Add tags (assuming tag input exists)
    await page.fill('textarea[name="content"]', 'Test content for E2E testing purposes');
    
    await page.click('button[type="submit"]');
    
    // Should redirect to resource detail
    await expect(page).toHaveURL(/\/resources\//, { timeout: 10000 });
    await expect(page.locator(`h1:has-text("${resourceTitle}")`)).toBeVisible();

    // Step 6: Check profile page (new feature)
    await page.click('a[href="/profile"]:has-text("My Profile")');
    await expect(page).toHaveURL(/\/profile/);
    await expect(page.locator(`text=${testName}`)).toBeVisible();
    
    // Should see metrics dashboard
    await expect(page.locator('text=Contributions')).toBeVisible();
    await expect(page.locator('text=Total Impact')).toBeVisible();

    // Step 7: Logout via user dropdown (new design)
    await page.click(`text=${testName}`); // Open dropdown
    await page.click('text=Sign Out');
    
    // Should see Sign In button again
    await expect(page.locator('a[href="/login"]:has-text("Sign In")')).toBeVisible();
  });

  test('should show proper validation errors', async ({ page }) => {
    // Test registration validation
    await page.goto('/register');
    
    // Try to submit empty form
    await page.click('button[type="submit"]');
    
    // Should show validation errors (updated text)
    await expect(page.locator('text=/required|obligatorio/i')).toBeVisible();
    
    // Test weak password
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="name"]', 'Test');
    await page.fill('input[name="password"]', '123'); // Too short
    await page.fill('input[name="password_confirm"]', '123');
    
    await page.click('button[type="submit"]');
    await expect(page.locator('text=/mínimo 8|minimum 8/i')).toBeVisible();
  });

  test('should handle login errors', async ({ page }) => {
    await page.goto('/login');
    
    // Try with wrong credentials
    await page.fill('input[name="email"]', 'nonexistent@example.com');
    await page.fill('input[name="password"]', 'WrongPass123!');
    
    await page.click('button[type="submit"]');
    
    // Should show error toast (react-hot-toast)
    await expect(page.locator('text=/Credenciales incorrectas|Invalid credentials/i')).toBeVisible({ timeout: 5000 });
  });
});
