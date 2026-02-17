# E2E TEST PLAN — BioAI Hub

**Proyecto:** BioAI Hub — Institutional AI Repository  
**Versión:** 1.0  
**Fecha:** 2026-02-16  
**Fase:** FASE 6 — Estrategia de Testing  
**Rol activo:** QA / Testing Engineer

---

## 1. OBJETIVO

Definir el plan de **tests End-to-End (E2E)** para validar el flujo crítico del MVP mediante navegación automatizada en navegador real.

**Meta:** 1 test E2E completo que cubre el flujo prioritario de 14 pasos definido en [`E2E_PRIORITY_FLOW.md`](../product/E2E_PRIORITY_FLOW.md).

---

## 2. HERRAMIENTA

### 2.1 Playwright (seleccionada)

| Criterio | Playwright | Selenium | Cypress |
|---|---|---|---|
| **Velocidad** | ⚡⚡⚡ (más rápido) | ⚡ (lento) | ⚡⚡ (rápido) |
| **Auto-wait** | ✅ Automático | ❌ Manual | ✅ Automático |
| **Multi-browser** | ✅ Chromium, Firefox, WebKit | ✅ Todos | ❌ Solo Chromium |
| **Debugging** | ✅ Codegen, trace viewer | ⚠️ Limitado | ✅ Time-travel |
| **API Testing** | ✅ Sí | ❌ No | ⚠️ Limitado |
| **Madurez** | ✅ (2020, Microsoft) | ✅ (2004) | ✅ (2017) |

**Decisión:** Playwright por velocidad, auto-wait y soporte multi-browser.

### 2.2 Instalación

```bash
cd frontend/
npm install -D @playwright/test
npx playwright install

# Opcional: para debugging visual
npx playwright install chromium --with-deps
```

---

## 3. CONFIGURACIÓN

### 3.1 playwright.config.ts

```typescript
// playwright.config.ts

import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './e2e/tests',
  
  // Timeout global
  timeout: 60 * 1000, // 60 segundos por test
  
  // Expect timeout
  expect: {
    timeout: 10 * 1000, // 10 segundos para expect()
  },
  
  // Fullfilled parallelization
  fullyParallel: false, // 1 test secuencial (flujo E2E)
  
  // Retries en CI
  retries: process.env.CI ? 2 : 0,
  
  // Workers
  workers: process.env.CI ? 1 : 1, // 1 worker (flujo secuencial)
  
  // Reporter
  reporter: [
    ['list'],
    ['html', { outputFolder: 'playwright-report' }],
    ['junit', { outputFile: 'test-results/junit.xml' }],
  ],
  
  // Uso compartido de setup (autenticación)
  use: {
    // Base URL
    baseURL: process.env.E2E_BASE_URL || 'http://localhost:3000',
    
    // Trace on failure
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    
    // Headless
    headless: process.env.CI ? true : false,
  },
  
  // Projects (browsers)
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    // Opcional: multi-browser
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] },
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] },
    // },
  ],
  
  // Web Server (auto-start)
  webServer: process.env.CI ? undefined : {
    command: 'npm run dev',
    port: 3000,
    timeout: 120 * 1000,
    reuseExistingServer: !process.env.CI,
  },
});
```

### 3.2 Estructura de Directorios

```
frontend/
├── e2e/
│   ├── tests/
│   │   └── main-flow.spec.ts        # Test E2E prioritario
│   ├── fixtures/
│   │   ├── auth.setup.ts            # Setup de autenticación
│   │   └── seed-data.ts             # Seed data para tests
│   ├── page-objects/
│   │   ├── BasePage.ts
│   │   ├── RegisterPage.ts
│   │   ├── LoginPage.ts
│   │   ├── ExplorePage.ts
│   │   ├── ResourceDetailPage.ts
│   │   ├── PublishPage.ts
│   │   └── NotificationsPage.ts
│   └── helpers/
│       ├── db-helper.ts             # Acceso a DB de test
│       └── api-helper.ts            # Llamadas directas a API
├── playwright.config.ts
└── package.json
```

---

## 4. TEST E2E PRIORITARIO (14 Pasos)

### 4.1 Flujo Completo

**Duración esperada:** 8-10 minutos  
**Browser:** Chromium (Desktop Chrome)  
**Precondiciones:**
- Base de datos de test limpia (reset antes del test)
- Backend y frontend corriendo (localhost:8000 y localhost:3000)
- Usuario Admin seed disponible (`admin@ccg.unam.mx`)

**Postcondiciones:**
- Usuario test creado, verificado, publicó recurso, recibió validación y notificación

### 4.2 Page Objects

**Principio:** Evitar selectores hardcoded en tests. Usar Page Objects.

```typescript
// e2e/page-objects/RegisterPage.ts

import { Page, Locator } from '@playwright/test';

export class RegisterPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly nameInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly successMessage: Locator;
  
  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('input[name="email"]');
    this.nameInput = page.locator('input[name="name"]');
    this.passwordInput = page.locator('input[name="password"]');
    this.submitButton = page.locator('button:has-text("Registrarse")');
    this.successMessage = page.locator('text=Verifica tu email');
  }
  
  async goto() {
    await this.page.goto('/register');
  }
  
  async register(email: string, name: string, password: string) {
    await this.emailInput.fill(email);
    await this.nameInput.fill(name);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }
  
  async waitForSuccess() {
    await this.successMessage.waitFor({ state: 'visible' });
  }
}
```

```typescript
// e2e/page-objects/LoginPage.ts

import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly page: Page;
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  
  constructor(page: Page) {
    this.page = page;
    this.emailInput = page.locator('input[name="email"]');
    this.passwordInput = page.locator('input[name="password"]');
    this.submitButton = page.locator('button:has-text("Iniciar sesión")');
  }
  
  async goto() {
    await this.page.goto('/login');
  }
  
  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
    
    // Auto-wait para redirección
    await this.page.waitForURL('/');
  }
}
```

```typescript
// e2e/page-objects/PublishPage.ts

import { Page, Locator } from '@playwright/test';

export class PublishPage {
  readonly page: Page;
  readonly titleInput: Locator;
  readonly descriptionTextarea: Locator;
  readonly typeSelect: Locator;
  readonly sourceTypeRadio: (type: string) => Locator;
  readonly tagsInput: Locator;
  readonly contentTextarea: Locator;
  readonly submitButton: Locator;
  
  constructor(page: Page) {
    this.page = page;
    this.titleInput = page.locator('input[name="title"]');
    this.descriptionTextarea = page.locator('textarea[name="description"]');
    this.typeSelect = page.locator('select[name="type"]');
    this.sourceTypeRadio = (type: string) => page.locator(`input[value="${type}"]`);
    this.tagsInput = page.locator('input[name="tags"]');
    this.contentTextarea = page.locator('textarea[name="content"]');
    this.submitButton = page.locator('button:has-text("Publish")');
  }
  
  async goto() {
    await this.page.goto('/publish');
  }
  
  async publishResource(data: {
    title: string;
    description: string;
    type: string;
    sourceType: string;
    tags: string;
    content: string;
  }) {
    await this.titleInput.fill(data.title);
    await this.descriptionTextarea.fill(data.description);
    await this.typeSelect.selectOption(data.type);
    await this.sourceTypeRadio(data.sourceType).click();
    await this.tagsInput.fill(data.tags);
    await this.contentTextarea.fill(data.content);
    await this.submitButton.click();
    
    // Auto-wait para redirección a detalle
    await this.page.waitForURL(/\/resources\/.+/);
  }
}
```

---

### 4.3 Test Principal

```typescript
// e2e/tests/main-flow.spec.ts

import { test, expect } from '@playwright/test';
import { RegisterPage } from '../page-objects/RegisterPage';
import { LoginPage } from '../page-objects/LoginPage';
import { ExplorePage } from '../page-objects/ExplorePage';
import { ResourceDetailPage } from '../page-objects/ResourceDetailPage';
import { PublishPage } from '../page-objects/PublishPage';
import { NotificationsPage } from '../page-objects/NotificationsPage';
import { getVerificationToken, seedAdminUser, resetDatabase } from '../helpers/db-helper';

test.describe('Flujo E2E Prioritario — BioAI Hub MVP', () => {
  
  test.beforeAll(async () => {
    // Reset DB de test
    await resetDatabase();
    
    // Seed: crear usuario Admin
    await seedAdminUser({
      email: 'admin@ccg.unam.mx',
      name: 'Admin CCG',
      password: 'AdminPass123!',
    });
  });
  
  test('Usuario completa flujo: Registro → Explorar → Publicar → Validación → Notificación', async ({ page }) => {
    
    // =====================================================================
    // PASO 1-2: REGISTRO Y VERIFICACIÓN EMAIL
    // =====================================================================
    const registerPage = new RegisterPage(page);
    await registerPage.goto();
    
    const testEmail = `test-${Date.now()}@example.com`;
    await registerPage.register(testEmail, 'Test User', 'SecurePass123!');
    await registerPage.waitForSuccess();
    
    // Verificar email (obtener token desde DB)
    const verificationToken = await getVerificationToken(testEmail);
    expect(verificationToken).toBeTruthy();
    
    await page.goto(`/auth/verify-email/${verificationToken}`);
    await expect(page.locator('text=Email verificado')).toBeVisible();
    
    // =====================================================================
    // PASO 3: LOGIN
    // =====================================================================
    const loginPage = new LoginPage(page);
    await loginPage.goto();
    await loginPage.login(testEmail, 'SecurePass123!');
    
    // Verificar que estamos en Home y usuario está autenticado
    await expect(page).toHaveURL('/');
    await expect(page.locator('text=Test User')).toBeVisible(); // Sidebar
    
    // =====================================================================
    // PASO 5: EXPLORAR RECURSOS
    // =====================================================================
    const explorePage = new ExplorePage(page);
    await explorePage.goto();
    
    // Verificar que carga lista (puede estar vacía al inicio)
    await expect(page.locator('[data-testid="resource-list"]')).toBeVisible();
    
    // =====================================================================
    // PASO 10: PUBLICAR NUEVO RECURSO
    // =====================================================================
    const publishPage = new PublishPage(page);
    await publishPage.goto();
    
    await publishPage.publishResource({
      title: 'E2E Test Resource — Protein Folding',
      description: 'This is a test resource created by Playwright E2E test for validation purposes.',
      type: 'Prompt',
      sourceType: 'Internal',
      tags: 'test, e2e, protein',
      content: 'Write a prompt for AlphaFold 3 to predict protein structure with high accuracy.',
    });
    
    // Verificar redirección a detalle del recurso
    await expect(page).toHaveURL(/\/resources\/.+/);
    await expect(page.locator('text=E2E Test Resource')).toBeVisible();
    
    // Verificar badge inicial: Sandbox
    const detailPage = new ResourceDetailPage(page);
    await expect(detailPage.statusBadge).toHaveText('Sandbox');
    
    // Extraer ID del recurso desde URL
    const resourceUrl = page.url();
    const resourceId = resourceUrl.split('/').pop()!;
    
    // =====================================================================
    // PASO 6-7: EXPLORAR OTROS RECURSOS Y VOTAR (si existen)
    // =====================================================================
    // Seed: crear 1 recurso de ejemplo para votar
    // (alternativa: hacerlo en beforeAll o usar fixture)
    // Por simplicidad, lo omitimos si no hay otros recursos disponibles
    
    // =====================================================================
    // PASO 11: LOGOUT Y LOGIN COMO ADMIN
    // =====================================================================
    await page.locator('[data-testid="user-menu"]').click();
    await page.locator('text=Cerrar sesión').click();
    await expect(page).toHaveURL('/login');
    
    // Login como Admin
    await loginPage.login('admin@ccg.unam.mx', 'AdminPass123!');
    await expect(page).toHaveURL('/');
    
    // =====================================================================
    // PASO 13-14: ADMIN VALIDA EL RECURSO
    // =====================================================================
    // Navegar al recurso creado por el usuario test
    await page.goto(`/resources/${resourceId}`);
    
    // Verificar que el botón de Validar está visible (solo para Admin)
    const validateButton = page.locator('button:has-text("Validate")');
    await expect(validateButton).toBeVisible();
    
    // Click en Validate (puede abrir modal de confirmación)
    await validateButton.click();
    
    // Confirmación en modal
    const confirmButton = page.locator('button:has-text("Confirm")');
    if (await confirmButton.isVisible()) {
      await confirmButton.click();
    }
    
    // Verificar que el badge cambió a Validated
    await expect(detailPage.statusBadge).toHaveText('Validated', { timeout: 10000 });
    
    // Verificar toast de éxito
    await expect(page.locator('text=Recurso validado exitosamente')).toBeVisible();
    
    // =====================================================================
    // PASO 12: LOGOUT Y LOGIN COMO USER ORIGINAL (VERIFICAR NOTIFICACIÓN)
    // =====================================================================
    await page.locator('[data-testid="user-menu"]').click();
    await page.locator('text=Cerrar sesión').click();
    
    // Login como usuario test original
    await loginPage.login(testEmail, 'SecurePass123!');
    await expect(page).toHaveURL('/');
    
    // Verificar badge de notificaciones no leídas
    const notificationBadge = page.locator('[data-testid="notification-badge"]');
    await expect(notificationBadge).toBeVisible();
    await expect(notificationBadge).toHaveText('1'); // 1 notificación no leída
    
    // Abrir panel de notificaciones
    await page.locator('[data-testid="notification-bell"]').click();
    
    // Verificar que existe notificación de validación
    const notificationMessage = page.locator('text=ha sido validado');
    await expect(notificationMessage).toBeVisible();
    
    // Click en notificación (marca como leída)
    await notificationMessage.click();
    
    // Verificar que el badge desaparece o muestra 0
    await expect(notificationBadge).toHaveText('0', { timeout: 5000 });
    
    // =====================================================================
    // PASO 8-9: REUSE (FORK) — EXTRA
    // =====================================================================
    // Navegar nuevamente al recurso validado
    await page.goto(`/resources/${resourceId}`);
    
    // Click en botón Reuse
    const reuseButton = page.locator('button:has-text("Reuse")');
    await expect(reuseButton).toBeVisible();
    await reuseButton.click();
    
    // Verificar redirección a /publish con datos pre-cargados
    await expect(page).toHaveURL('/publish');
    
    // Verificar que el título está pre-cargado
    const titleInput = page.locator('input[name="title"]');
    await expect(titleInput).toHaveValue(/E2E Test Resource/);
    
    // Verificar derived_from_resource_id (oculto en form)
    const derivedFromInput = page.locator('input[name="derived_from_resource_id"]');
    await expect(derivedFromInput).toHaveValue(resourceId);
    
    // (No publicamos, solo verificamos que el flujo funciona)
  });
});
```

---

## 5. HELPERS Y FIXTURES

### 5.1 DB Helper (acceso directo a base de datos)

```typescript
// e2e/helpers/db-helper.ts

import { Pool } from 'pg';

const pool = new Pool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '5432'),
  database: process.env.DB_NAME || 'bioai_test',
  user: process.env.DB_USER || 'postgres',
  password: process.env.DB_PASSWORD || 'postgres',
});

/**
 * Reset database (limpiar todas las tablas)
 */
export async function resetDatabase() {
  await pool.query('TRUNCATE TABLE notifications, votes, resource_versions, resources, user_roles, users, roles RESTART IDENTITY CASCADE');
  console.log('✓ Database reset');
}

/**
 * Seed usuario Admin
 */
export async function seedAdminUser(data: { email: string; name: string; password: string }) {
  // 1. Crear usuario
  const userResult = await pool.query(
    `INSERT INTO users (id, email, name, password_hash, email_verified_at, is_active)
     VALUES (gen_random_uuid(), $1, $2, crypt($3, gen_salt('bf')), NOW(), true)
     RETURNING id`,
    [data.email, data.name, data.password]
  );
  
  const userId = userResult.rows[0].id;
  
  // 2. Crear role Admin (si no existe)
  await pool.query(
    `INSERT INTO roles (id, name, description, created_at, updated_at)
     VALUES (gen_random_uuid(), 'Admin', 'Administrator', NOW(), NOW())
     ON CONFLICT (name) DO NOTHING`
  );
  
  // 3. Asignar role Admin al usuario
  const roleResult = await pool.query(`SELECT id FROM roles WHERE name = 'Admin'`);
  const roleId = roleResult.rows[0].id;
  
  await pool.query(
    `INSERT INTO user_roles (user_id, role_id, assigned_at)
     VALUES ($1, $2, NOW())`,
    [userId, roleId]
  );
  
  console.log(`✓ Admin user seeded: ${data.email}`);
}

/**
 * Obtener token de verificación de email desde DB
 */
export async function getVerificationToken(email: string): Promise<string | null> {
  const result = await pool.query(
    `SELECT verification_token FROM users WHERE email = $1`,
    [email]
  );
  
  return result.rows[0]?.verification_token || null;
}

/**
 * Cerrar pool al finalizar tests
 */
export async function closePool() {
  await pool.end();
}
```

### 5.2 API Helper (llamadas directas a API)

```typescript
// e2e/helpers/api-helper.ts

import axios, { AxiosInstance } from 'axios';

const BASE_URL = process.env.E2E_API_URL || 'http://localhost:8000/api';

/**
 * Cliente HTTP para llamadas directas a API (bypass frontend)
 */
export class APIHelper {
  private client: AxiosInstance;
  
  constructor() {
    this.client = axios.create({
      baseURL: BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });
  }
  
  /**
   * Login y obtener token JWT
   */
  async login(email: string, password: string): Promise<string> {
    const response = await this.client.post('/auth/login/', { email, password });
    return response.data.access;
  }
  
  /**
   * Publicar recurso directamente (bypass UI)
   */
  async publishResource(token: string, data: any) {
    const response = await this.client.post('/resources/', data, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  }
  
  /**
   * Validar recurso (Admin)
   */
  async validateResource(token: string, resourceId: string) {
    const response = await this.client.post(`/resources/${resourceId}/validate/`, {}, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  }
}
```

---

## 6. ESTRATEGIA DE DATOS DE PRUEBA

### 6.1 Seed Data

**Opción A: Reset + Seed en beforeAll()**
- Ventaja: DB limpia y predecible
- Desventaja: Tests lentos si hay muchos seeds

**Opción B: Factory Fixtures en código**
- Ventaja: Flexibilidad por test
- Desventaja: Más código de setup

**MVP:** Opción A (reset + seed básico)

### 6.2 Usuarios Seed

```typescript
// e2e/fixtures/seed-data.ts

export const SEED_USERS = [
  {
    email: 'admin@ccg.unam.mx',
    name: 'Admin CCG',
    password: 'AdminPass123!',
    role: 'Admin',
  },
  {
    email: 'user1@example.com',
    name: 'User 1',
    password: 'UserPass123!',
    role: 'User',
  },
];

export const SEED_RESOURCES = [
  {
    title: 'Protein Folding Prompt',
    description: 'Guide for AlphaFold 3 predictions',
    type: 'Prompt',
    source_type: 'Internal',
    tags: ['protein', 'AlphaFold'],
    content: 'Detailed prompt...',
    status: 'Validated',
    owner: 'user1@example.com',
  },
  // ... más recursos
];
```

---

## 7. ESTADOS UI A VALIDAR EN E2E

Basado en [`UI_STATES.md`](../ux/UI_STATES.md):

| Estado | Validación en E2E |
|---|---|
| **Loading** | Verificar skeleton loader visible durante carga |
| **Success** | Verificar contenido renderizado correctamente |
| **Empty** | Verificar mensaje "No hay recursos disponibles" |
| **Validation Error** | Intentar submit con campos vacíos → error inline |
| **Backend Error** | Mock API 500 → verificar mensaje "Error al cargar" |
| **Permissions** | Usuario NO Admin intenta validar → botón oculto o deshabilitado |

**Ejemplo:**
```typescript
test('should show validation error on empty form submit', async ({ page }) => {
  const publishPage = new PublishPage(page);
  await publishPage.goto();
  
  // Submit sin llenar campos
  await publishPage.submitButton.click();
  
  // Verificar error inline
  await expect(page.locator('text=El título es obligatorio')).toBeVisible();
});
```

---

## 8. CI/CD INTEGRACIÓN

### 8.1 GitHub Actions Job

```yaml
# .github/workflows/e2e.yml

name: E2E Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  e2e-test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_DB: bioai_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
        ports:
          - 5432:5432
    
    steps:
      - uses: actions/checkout@v3
      
      # Backend
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install backend dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      
      - name: Run Django migrations
        run: |
          cd backend
          python manage.py migrate --settings=config.settings.test
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/bioai_test
      
      - name: Start Django server (background)
        run: |
          cd backend
          python manage.py runserver 8000 --settings=config.settings.test &
          sleep 10  # Esperar que el server inicie
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/bioai_test
      
      # Frontend
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci
      
      - name: Build frontend
        run: |
          cd frontend
          npm run build
      
      - name: Start Next.js server (background)
        run: |
          cd frontend
          npm start &
          sleep 10  # Esperar que el server inicie
      
      # Playwright
      - name: Install Playwright
        run: |
          cd frontend
          npx playwright install --with-deps
      
      - name: Run E2E tests
        run: |
          cd frontend
          npm run test:e2e
        env:
          E2E_BASE_URL: http://localhost:3000
          E2E_API_URL: http://localhost:8000/api
          DB_HOST: localhost
          DB_PORT: 5432
          DB_NAME: bioai_test
          DB_USER: postgres
          DB_PASSWORD: postgres
      
      # Artifacts
      - name: Upload Playwright report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
      
      - name: Upload screenshots on failure
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-screenshots
          path: frontend/e2e/screenshots/
```

---

## 9. DEBUGGING Y TROUBLESHOOTING

### 9.1 Playwright Inspector (Debugging Visual)

```bash
# Modo debug (step-by-step)
PWDEBUG=1 npx playwright test

# Codegen (grabar acciones manualmente)
npx playwright codegen http://localhost:3000
```

### 9.2 Trace Viewer

```bash
# Ejecutar test con trace
npx playwright test --trace on

# Ver trace
npx playwright show-trace trace.zip
```

### 9.3 Screenshots y Videos

- **On Failure:** `screenshot: 'only-on-failure'`
- **Always:** `screenshot: 'on'`
- **Videos:** `video: 'retain-on-failure'`

Archivos guardados en `test-results/`.

---

## 10. MÉTRICAS DE E2E

### 10.1 KPIs

| Métrica | Target MVP | Cómo Medir |
|---|---|---|
| **E2E Test Success Rate** | 100% (1 test, 0 fallos) | Playwright report |
| **Duración E2E** | <10 minutos | CI logs |
| **Flakiness Rate** | 0% (no flaky) | Re-runs analysis |
| **Coverage del Flujo** | 100% (14 pasos) | Manual checklist |

### 10.2 Checklist de Cobertura del Flujo E2E

✅ Paso 1: Landing → Registro  
✅ Paso 2: Verificación de email  
✅ Paso 3: Login  
✅ Paso 4: Dashboard  
✅ Paso 5: Explore (listar recursos)  
✅ Paso 6: Ver detalle  
✅ Paso 7: Votar  
✅ Paso 8: Reuse (Fork)  
✅ Paso 9: Fork → Edición  
✅ Paso 10: Publicar nuevo recurso  
✅ Paso 11: Dashboard (ver recurso publicado)  
✅ Paso 12: Notificación recibida  
✅ Paso 13: Admin valida recurso  
✅ Paso 14: Badge cambia a Validated  

---

## 11. TESTS E2E ADICIONALES (Post-MVP)

### 11.1 Flujos Alternativos

- **Flujo de error:** Login con credenciales incorrectas
- **Flujo de permisos:** Usuario NO Admin intenta validar
- **Flujo de edición:** Editar recurso Sandbox (update in-place) vs Validated (nueva versión)

### 11.2 Pruebas de Dispositivos

- **Mobile:** iPhone 13 Pro, Pixel 5
- **Tablet:** iPad Pro
- **Desktop:** 1920x1080, 2560x1440

### 11.3 Pruebas de Accesibilidad

```typescript
import { injectAxe, checkA11y } from 'axe-playwright';

test('should have no accessibility violations', async ({ page }) => {
  await page.goto('/explore');
  await injectAxe(page);
  await checkA11y(page);
});
```

---

## 12. COMANDOS NPM

```json
// package.json

{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:debug": "PWDEBUG=1 playwright test",
    "test:e2e:report": "playwright show-report",
    "test:e2e:codegen": "playwright codegen http://localhost:3000"
  }
}
```

---

## 13. DEPENDENCIAS

```bash
# Playwright
npm install -D @playwright/test

# (Opcional) Axe para accesibilidad
npm install -D axe-playwright

# (Opcional) pg para acceso directo a DB
npm install -D pg @types/pg
```

---

## 14. LIMITACIONES Y CONSIDERACIONES

### 14.1 Limitaciones del E2E

1. **Lentitud:** E2E es más lento que unit/integration → minimizar cantidad
2. **Fragilidad:** Cambios en UI rompen tests → usar data-testid y Page Objects
3. **Dependencias externas:** Email verification requiere mock o acceso a DB

### 14.2 Mitigaciones

- **data-testid:** Atributos estables para selectores
- **Auto-wait:** Playwright espera automáticamente elementos
- **Retries:** Configurar retries en CI para flakiness transitorio

---

## 15. ROADMAP DE TESTS E2E

### v1.0 (MVP)
- ✅ 1 test E2E completo (flujo prioritario 14 pasos)
- ✅ Page Objects para 6 pantallas principales
- ✅ Integración en CI/CD

### v1.1 (Post-MVP)
- Tests E2E adicionales para flujos alternativos (3-5 tests)
- Pruebas en múltiples browsers (Firefox, WebKit)
- Pruebas de accesibilidad (axe-playwright)

### v2.0 (Expansión)
- Tests de responsive (mobile, tablet)
- Visual regression testing (Percy, Chromatic)
- Performance testing (Lighthouse CI)

---

## 16. CHANGELOG

### v1.0 (2026-02-16)
- Plan E2E inicial
- 1 test completo del flujo prioritario
- Page Objects para 6 pantallas
- Helpers para DB y API
- Integración en GitHub Actions
- Duración target: <10 minutos

---

**Documento completado:** 2026-02-16  
**Siguiente fase:** FASE 7 — Implementación (Setup + TDD)  
**Rol siguiente:** Backend Engineer + Frontend Engineer
