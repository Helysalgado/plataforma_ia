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
    
    // Navigate to explore
    await page.click('text=Explorar');
    await expect(page).toHaveURL(/\/explore/);
    await expect(page.locator('h1')).toContainText('Explorar Recursos');

    // Step 2: View a resource detail (if any resources exist)
    const resourceCard = page.locator('[data-testid="resource-card"]').first();
    const hasResources = await resourceCard.isVisible().catch(() => false);
    
    if (hasResources) {
      await resourceCard.click();
      await expect(page).toHaveURL(/\/resources\//);
      
      // Should see vote and fork buttons (disabled for anonymous)
      await expect(page.locator('button:has-text("Votar")')).toBeVisible();
      await expect(page.locator('button:has-text("Reutilizar")')).toBeVisible();
      
      // Go back to explore
      await page.click('text=Volver a Explorar');
    }

    // Step 3: Register
    await page.click('text=Registrarse');
    await expect(page).toHaveURL('/register');
    
    await page.fill('input[name="email"]', testEmail);
    await page.fill('input[name="name"]', testName);
    await page.fill('input[name="password"]', testPassword);
    await page.fill('input[name="password_confirm"]', testPassword);
    
    await page.click('button[type="submit"]:has-text("Crear cuenta")');
    
    // Should see success message
    await expect(page.locator('text=¡Registro exitoso!')).toBeVisible({ timeout: 10000 });
    await expect(page.locator(`text=${testEmail}`)).toBeVisible();

    // Step 4: Login (simulating email verification)
    // Note: In real E2E, you'd need to verify email first
    // For testing purposes, we'll proceed to login
    await page.click('text=Ir a iniciar sesión');
    await expect(page).toHaveURL('/login');
    
    await page.fill('input[name="email"]', testEmail);
    await page.fill('input[name="password"]', testPassword);
    
    await page.click('button[type="submit"]:has-text("Iniciar sesión")');
    
    // Should redirect to explore after login
    await expect(page).toHaveURL(/\/explore/, { timeout: 10000 });
    
    // Should see user name in navbar
    await expect(page.locator(`text=${testName}`)).toBeVisible();

    // Step 5: Publish a resource
    await page.click('text=Publicar');
    await expect(page).toHaveURL('/publish');
    
    // Fill resource form
    const resourceTitle = `Test Resource ${Date.now()}`;
    await page.fill('input[name="title"]', resourceTitle);
    await page.fill('textarea[name="description"]', 'This is a test resource created by E2E test');
    await page.selectOption('select[name="type"]', 'Prompt');
    await page.fill('input[name="tags"]', 'test, e2e, automation');
    await page.fill('textarea[name="content"]', 'Test content for E2E testing purposes');
    
    await page.click('button[type="submit"]:has-text("Publicar Recurso")');
    
    // Should redirect to resource detail
    await expect(page).toHaveURL(/\/resources\//, { timeout: 10000 });
    await expect(page.locator(`text=${resourceTitle}`)).toBeVisible();
    
    // Should see success toast
    await expect(page.locator('text=publicado exitosamente')).toBeVisible();

    // Step 6: Vote on own resource
    await page.click('button:has-text("Votar")');
    
    // Should see vote success toast
    await expect(page.locator('text=Voto registrado')).toBeVisible({ timeout: 5000 });
    
    // Vote button should change state
    await expect(page.locator('button:has-text("Votado")')).toBeVisible();

    // Step 7: Edit resource
    await page.click('button:has-text("Editar")');
    await expect(page).toHaveURL(/\/resources\/.*\/edit/);
    
    const updatedDescription = 'Updated description from E2E test';
    await page.fill('textarea[name="description"]', updatedDescription);
    await page.click('button[type="submit"]:has-text("Guardar Cambios")');
    
    // Should redirect back to detail
    await expect(page).toHaveURL(/\/resources\//);
    await expect(page.locator(`text=${updatedDescription}`)).toBeVisible();

    // Step 8: Logout
    await page.click(`text=${testName}`); // Open user menu
    await page.click('text=Cerrar sesión');
    
    // Should see login/register buttons again
    await expect(page.locator('text=Iniciar sesión')).toBeVisible();
    await expect(page.locator('text=Registrarse')).toBeVisible();
  });

  test('should show proper validation errors', async ({ page }) => {
    // Test registration validation
    await page.goto('/register');
    
    // Try to submit empty form
    await page.click('button[type="submit"]');
    
    // Should show validation errors
    await expect(page.locator('text=obligatorio')).toBeVisible();
    
    // Test weak password
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="name"]', 'Test');
    await page.fill('input[name="password"]', '123'); // Too short
    await page.fill('input[name="password_confirm"]', '123');
    
    await page.click('button[type="submit"]');
    await expect(page.locator('text=mínimo 8 caracteres')).toBeVisible();
  });

  test('should handle login errors', async ({ page }) => {
    await page.goto('/login');
    
    // Try with wrong credentials
    await page.fill('input[name="email"]', 'nonexistent@example.com');
    await page.fill('input[name="password"]', 'WrongPass123!');
    
    await page.click('button[type="submit"]');
    
    // Should show error message
    await expect(page.locator('text=Credenciales incorrectas')).toBeVisible({ timeout: 5000 });
  });
});
