# TEST STRATEGY — BioAI Hub

**Proyecto:** BioAI Hub — Institutional AI Repository  
**Versión:** 1.0  
**Fecha:** 2026-02-16  
**Fase:** FASE 6 — Estrategia de Calidad  
**Rol activo:** QA / Testing Engineer

---

## 1. VISIÓN GENERAL

### 1.1 Objetivo
Garantizar calidad, funcionalidad y seguridad del MVP mediante una estrategia de testing integral basada en la **pirámide de tests**.

### 1.2 Principios
1. **TDD (Test-Driven Development):** Tests antes o junto al código para lógica crítica
2. **Cobertura mínima:** ≥70% backend, ≥60% frontend (componentes críticos)
3. **Tests automatizados:** Integrados en CI/CD (pre-commit y pre-deploy)
4. **BDD para historias Must-Have:** Criterios Given/When/Then ejecutables
5. **1 test E2E mínimo:** Flujo E2E prioritario completo

---

## 2. PIRÁMIDE DE TESTS

```
         /\
        /  \        E2E (1 test flujo principal)
       / E2E\       - Playwright / Cypress
      /______\      - Navegador real
     /        \
    /  INTEG   \    Integration (API + DB)
   /            \   - pytest + DRF test client
  /______________\  - DB test (SQLite o Postgres)
 /                \
/      UNIT        \ Unit (lógica de negocio)
/____________________\ - pytest (backend)
                      - Jest (frontend)
```

### 2.1 Distribución de Esfuerzo
- **Unit Tests:** 70% de los tests
- **Integration Tests:** 25% de los tests
- **E2E Tests:** 5% de los tests (pero críticos)

### 2.2 Tiempo de Ejecución Objetivo
- Unit: <30s (total)
- Integration: <3min (total)
- E2E: <10min (1 test completo)

---

## 3. BACKEND TESTING (Django + DRF)

### 3.1 Herramientas

| Herramienta | Uso | Versión |
|---|---|---|
| **pytest** | Test runner | 7.4+ |
| **pytest-django** | Django integration | 4.5+ |
| **pytest-cov** | Code coverage | 4.1+ |
| **factory-boy** | Test fixtures | 3.3+ |
| **faker** | Fake data | 20.0+ |
| **freezegun** | Mock datetime | 1.2+ |

### 3.2 Unit Tests (Backend)

**Objetivo:** Testar lógica de negocio en Service Layer de forma aislada

**Scope:**
- Services (AuthService, ResourceService, VersioningService, etc.)
- Validators
- Utilities
- Model methods

**Estrategia:**
- Mock de dependencies (DB, external APIs)
- Fixtures con factory-boy
- Parametrized tests para múltiples casos

**Ejemplo:**
```python
# apps/resources/tests/test_versioning_service.py

import pytest
from apps.resources.services import VersioningService
from apps.resources.tests.factories import ResourceFactory, ResourceVersionFactory

class TestVersioningService:
    
    @pytest.mark.django_db
    def test_update_sandbox_resource_updates_in_place(self):
        """
        Given un recurso con última versión en Sandbox
        When se actualiza el recurso
        Then se actualiza la versión existente (NO crea nueva versión)
        """
        # Arrange
        resource = ResourceFactory()
        version = ResourceVersionFactory(
            resource=resource,
            version_number='1.0.0',
            status='Sandbox',
            is_latest=True
        )
        
        # Act
        updated_version = VersioningService.update_resource(
            resource=resource,
            user=resource.owner,
            data={'title': 'Updated Title'}
        )
        
        # Assert
        assert updated_version.id == version.id  # Mismo ID (in-place)
        assert updated_version.title == 'Updated Title'
        assert updated_version.version_number == '1.0.0'  # Mismo número
        assert resource.versions.count() == 1  # NO creó nueva versión
    
    @pytest.mark.django_db
    def test_update_validated_resource_creates_new_version(self):
        """
        Given un recurso con última versión Validated
        When se actualiza el recurso
        Then se crea nueva versión (vNext) en Sandbox
        And la versión anterior permanece Validated
        """
        # Arrange
        resource = ResourceFactory()
        old_version = ResourceVersionFactory(
            resource=resource,
            version_number='1.0.0',
            status='Validated',
            is_latest=True
        )
        
        # Act
        new_version = VersioningService.update_resource(
            resource=resource,
            user=resource.owner,
            data={'title': 'Updated Title'}
        )
        
        # Assert
        assert new_version.id != old_version.id  # Nuevo ID
        assert new_version.version_number == '1.1.0'  # Incrementado
        assert new_version.status == 'Sandbox'
        assert new_version.is_latest is True
        
        # Versión anterior NO cambió
        old_version.refresh_from_db()
        assert old_version.status == 'Validated'  # Sigue Validated
        assert old_version.is_latest is False  # Ya no es latest
        
        assert resource.versions.count() == 2  # Ahora hay 2 versiones
```

**Coverage target:** ≥80% de Service Layer

---

### 3.3 Integration Tests (Backend)

**Objetivo:** Testar endpoints de API con DB real (o test DB)

**Scope:**
- API endpoints (requests HTTP)
- Integración con BD
- Serializers
- Permissions

**Estrategia:**
- Django test client (DRF APIClient)
- Test database (PostgreSQL o SQLite)
- Transacciones rollback automático

**Ejemplo:**
```python
# apps/resources/tests/test_api.py

from rest_framework.test import APITestCase
from rest_framework import status
from apps.authentication.tests.factories import UserFactory
from apps.resources.tests.factories import ResourceFactory

class ResourceAPITest(APITestCase):
    
    def setUp(self):
        self.user = UserFactory(email_verified_at=timezone.now())
        self.admin = UserFactory(email_verified_at=timezone.now(), is_admin=True)
    
    def test_publish_resource_success(self):
        """
        Given usuario autenticado con email verificado
        When POST /api/resources con datos válidos
        Then retorna 201 Created
        And recurso es creado con versión v1.0.0
        """
        # Arrange
        self.client.force_authenticate(user=self.user)
        
        data = {
            'title': 'Test Resource',
            'description': 'Test description',
            'type': 'Prompt',
            'source_type': 'Internal',
            'tags': ['test', 'prompt'],
            'content': 'This is the content',
            'status': 'Sandbox'
        }
        
        # Act
        response = self.client.post('/api/resources/', data, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['latest_version']['version_number'] == '1.0.0'
        assert response.data['latest_version']['status'] == 'Sandbox'
        assert response.data['owner']['id'] == str(self.user.id)
    
    def test_publish_resource_email_not_verified(self):
        """
        Given usuario con email NO verificado
        When intenta publicar recurso
        Then retorna 403 Forbidden
        """
        # Arrange
        user_unverified = UserFactory(email_verified_at=None)
        self.client.force_authenticate(user=user_unverified)
        
        # Act
        response = self.client.post('/api/resources/', {
            'title': 'Test',
            'description': 'Test',
            'type': 'Prompt',
            'source_type': 'Internal',
            'content': 'Test'
        }, format='json')
        
        # Assert
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'email' in response.data['error'].lower()
```

**Coverage target:** ≥70% de Views y Serializers

---

### 3.4 Fixtures y Factories

**factory-boy para generar datos de test:**

```python
# apps/authentication/tests/factories.py

import factory
from apps.authentication.models import User

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    id = factory.Faker('uuid4')
    email = factory.Faker('email')
    name = factory.Faker('name')
    password_hash = factory.PostGenerationMethodCall('set_password', 'password123')
    email_verified_at = factory.Faker('date_time')
    is_active = True
    
    @factory.post_generation
    def roles(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            for role in extracted:
                self.roles.add(role)

class AdminUserFactory(UserFactory):
    @factory.post_generation
    def roles(self, create, extracted, **kwargs):
        from apps.authentication.models import Role
        admin_role, _ = Role.objects.get_or_create(name='Admin')
        self.roles.add(admin_role)
```

---

## 4. FRONTEND TESTING (Next.js + React)

### 4.1 Herramientas

| Herramienta | Uso | Versión |
|---|---|---|
| **Jest** | Test runner | 29.7+ |
| **React Testing Library** | Component testing | 14.0+ |
| **@testing-library/user-event** | Simular interacciones | 14.5+ |
| **MSW (Mock Service Worker)** | Mock API calls | 2.0+ |
| **@testing-library/jest-dom** | Custom matchers | 6.1+ |

### 4.2 Unit Tests (Frontend)

**Objetivo:** Testar componentes, hooks y utils de forma aislada

**Scope:**
- Componentes (ResourceCard, VoteButton, Badge)
- Hooks custom (useAuth, useResource)
- Utilities (validation, formatting)

**Estrategia:**
- Mock de API calls con MSW
- Render con React Testing Library
- User interactions con userEvent

**Ejemplo:**
```typescript
// components/resource/VoteButton.test.tsx

import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { VoteButton } from './VoteButton';
import { server } from '@/test/mocks/server';
import { http, HttpResponse } from 'msw';

describe('VoteButton', () => {
  it('should toggle vote on click', async () => {
    // Arrange
    const user = userEvent.setup();
    const mockToggle = jest.fn();
    
    // Mock API response
    server.use(
      http.post('/api/resources/:id/vote', () => {
        return HttpResponse.json({ voted: true, votes_count: 26 });
      })
    );
    
    render(
      <VoteButton 
        resourceId="123" 
        initialVoted={false} 
        initialCount={25}
      />
    );
    
    // Act
    const button = screen.getByRole('button', { name: /upvote/i });
    await user.click(button);
    
    // Assert
    expect(await screen.findByText('26')).toBeInTheDocument();
    expect(button).toHaveClass('voted'); // Estado visual cambia
  });
  
  it('should show tooltip for anonymous users', () => {
    render(
      <VoteButton 
        resourceId="123" 
        initialVoted={false} 
        initialCount={25}
        isAuthenticated={false}
      />
    );
    
    const button = screen.getByRole('button', { name: /upvote/i });
    expect(button).toBeDisabled();
    expect(screen.getByText(/inicia sesión para votar/i)).toBeInTheDocument();
  });
});
```

**Coverage target:** ≥60% de componentes críticos

---

## 5. BDD (BEHAVIOR-DRIVEN DEVELOPMENT)

### 5.1 Herramientas

**Backend:** pytest-bdd (Python)

```bash
pip install pytest-bdd
```

**Features:** Gherkin files (`.feature`) basados en historias Must-Have

Ver [`BDD_FEATURES.feature`](BDD_FEATURES.feature) para features completas.

### 5.2 Estructura BDD

```
backend/
├── features/
│   ├── authentication.feature
│   ├── resources.feature
│   ├── validation.feature
│   └── interactions.feature
└── step_defs/
    ├── test_authentication.py
    ├── test_resources.py
    ├── test_validation.py
    └── test_interactions.py
```

### 5.3 Ejemplo BDD

**Feature:**
```gherkin
# features/authentication.feature

Feature: User Registration
  Como usuario nuevo
  Quiero registrarme con mi email
  Para poder publicar recursos en la plataforma

  Background:
    Given la base de datos está limpia

  Scenario: Successful registration
    Given que no estoy registrado
    When envío POST /api/auth/register con:
      | email              | nombre      | contraseña     |
      | juan@example.com   | Juan Pérez  | SecurePass123! |
    Then recibo código 201
    And el usuario es creado con email_verified_at NULL
    And se envía email de verificación

  Scenario: Duplicate email
    Given que existe usuario con email "juan@example.com"
    When intento registrarme con el mismo email
    Then recibo código 409
    And el mensaje es "Email already registered"
```

**Step definitions:**
```python
# step_defs/test_authentication.py

from pytest_bdd import scenarios, given, when, then, parsers
from rest_framework.test import APIClient

scenarios('../features/authentication.feature')

@given('que no estoy registrado')
def not_registered():
    pass  # DB limpia en background

@when(parsers.parse('envío POST /api/auth/register con:\n{table}'))
def register_user(table, api_client):
    # Parse table y enviar request
    data = parse_gherkin_table(table)
    response = api_client.post('/api/auth/register/', data)
    api_client.last_response = response

@then(parsers.parse('recibo código {status_code:d}'))
def check_status_code(api_client, status_code):
    assert api_client.last_response.status_code == status_code
```

---

## 6. E2E TESTING

### 6.1 Herramienta: Playwright

**Justificación:**
- Más rápido que Selenium
- Mejor DX (Developer Experience)
- Auto-wait (no sleeps manuales)
- Multi-browser (Chromium, Firefox, WebKit)
- Screenshots y videos en failures

**Instalación:**
```bash
npm install -D @playwright/test
npx playwright install
```

### 6.2 Test E2E Prioritario

Ver [`E2E_PLAN.md`](E2E_PLAN.md) para plan completo.

**Test único (flujo completo):**

```typescript
// e2e/tests/main-flow.spec.ts

import { test, expect } from '@playwright/test';

test.describe('Flujo E2E Prioritario', () => {
  test('Usuario puede registrarse, explorar, publicar, y recibir validación', async ({ page }) => {
    // PASO 1-2: Registro y verificación
    await page.goto('https://bioai.ccg.unam.mx/register');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="name"]', 'Test User');
    await page.fill('input[name="password"]', 'SecurePass123!');
    await page.click('button:has-text("Registrarse")');
    
    await expect(page).toHaveURL(/verify-email/);
    await expect(page.locator('text=Verifica tu email')).toBeVisible();
    
    // Mock: Obtener token de verificación desde DB de test
    const verificationToken = await getVerificationTokenFromDB('test@example.com');
    await page.goto(`https://bioai.ccg.unam.mx/auth/verify-email/${verificationToken}`);
    
    await expect(page.locator('text=Email verificado')).toBeVisible();
    
    // PASO 3: Login
    await page.goto('https://bioai.ccg.unam.mx/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'SecurePass123!');
    await page.click('button:has-text("Iniciar sesión")');
    
    await expect(page).toHaveURL('/');
    await expect(page.locator('text=Test User')).toBeVisible(); // Sidebar
    
    // PASO 5: Explorar
    await page.click('a:has-text("Explore")');
    await expect(page).toHaveURL('/explore');
    
    // Seed data: Asegurar que existe al menos 1 recurso
    await expect(page.locator('[data-testid="resource-card"]').first()).toBeVisible();
    
    // PASO 6-7: Ver detalle y votar
    await page.click('[data-testid="resource-card"]').first();
    await expect(page).toHaveURL(/\/resources\/.+/);
    
    const voteButton = page.locator('[data-testid="vote-button"]');
    await voteButton.click();
    await expect(voteButton).toHaveClass(/voted/);
    
    // PASO 10: Publicar nuevo recurso
    await page.click('a:has-text("Publish")');
    await expect(page).toHaveURL('/publish');
    
    await page.fill('input[name="title"]', 'E2E Test Resource');
    await page.fill('textarea[name="description"]', 'This is a test resource created by E2E test');
    await page.selectOption('select[name="type"]', 'Prompt');
    await page.click('input[value="Internal"]'); // Source type radio
    await page.fill('textarea[name="content"]', 'Test prompt content');
    await page.fill('input[name="tags"]', 'test, e2e');
    
    await page.click('button:has-text("Publish")');
    
    await expect(page).toHaveURL(/\/resources\/.+/);
    await expect(page.locator('text=Recurso publicado exitosamente')).toBeVisible();
    await expect(page.locator('[data-testid="badge"]')).toHaveText('Sandbox');
    
    // PASO 13-14: Validación Admin (cambiar a usuario admin)
    const resourceId = page.url().split('/').pop();
    
    await page.goto('https://bioai.ccg.unam.mx/logout');
    await page.goto('https://bioai.ccg.unam.mx/login');
    await page.fill('input[name="email"]', 'admin@ccg.unam.mx'); // Usuario admin seed
    await page.fill('input[name="password"]', 'AdminPass123!');
    await page.click('button:has-text("Iniciar sesión")');
    
    await page.goto(`https://bioai.ccg.unam.mx/resources/${resourceId}`);
    
    const validateButton = page.locator('button:has-text("Validate")');
    await expect(validateButton).toBeVisible(); // Solo Admin ve este botón
    await validateButton.click();
    
    // Modal de confirmación
    await page.click('button:has-text("Confirm")');
    
    await expect(page.locator('[data-testid="badge"]')).toHaveText('Validated');
    await expect(page.locator('text=Recurso validado exitosamente')).toBeVisible();
    
    // PASO 12: Usuario original recibe notificación (volver a login como test user)
    await page.goto('https://bioai.ccg.unam.mx/logout');
    await page.goto('https://bioai.ccg.unam.mx/login');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'SecurePass123!');
    await page.click('button:has-text("Iniciar sesión")');
    
    // Verificar badge de notificaciones
    const notificationBadge = page.locator('[data-testid="notification-badge"]');
    await expect(notificationBadge).toHaveText('1'); // 1 notificación no leída
    
    await page.click('[data-testid="notification-bell"]');
    await expect(page.locator('text=ha sido validado')).toBeVisible();
  });
});
```

**Duración esperada:** ~8-10 minutos

---

## 7. ESTRATEGIA DE COBERTURA

### 7.1 Cobertura por Módulo (Backend)

| Módulo | Target Coverage | Enfoque |
|---|---|---|
| **authentication/** | ≥85% | Crítico (seguridad) |
| **resources/** | ≥80% | Core domain |
| **interactions/** | ≥75% | Votos, forks |
| **validation/** | ≥85% | Crítico (calidad) |
| **notifications/** | ≥70% | Secundario |
| **core/** | ≥80% | Utilities |

### 7.2 Cobertura por Tipo de Test (Backend)

```
Unit Tests:        ≥70% de Service Layer
Integration Tests: ≥60% de Views/Serializers
Total:             ≥70% código backend
```

**Comandos:**
```bash
# Ejecutar tests con cobertura
pytest --cov=apps --cov-report=html --cov-report=term

# Ver reporte
open htmlcov/index.html
```

### 7.3 Cobertura Frontend

```
Components:  ≥60% (críticos: ResourceCard, VoteButton, Forms)
Hooks:       ≥70% (useAuth, useResource)
Utils:       ≥80% (validación, formatting)
Total:       ≥60% código frontend
```

**Comandos:**
```bash
# Ejecutar tests con cobertura
npm test -- --coverage

# Ver reporte
open coverage/lcov-report/index.html
```

---

## 8. TESTING DE SEGURIDAD

### 8.1 Tests de Autorización

**Críticos:**
- Usuario anónimo NO puede acceder a rutas protegidas
- Usuario NO puede editar recursos ajenos
- Usuario NO puede validar recursos (solo Admin)
- Usuario suspendido NO puede login

**Ejemplo:**
```python
def test_user_cannot_edit_other_user_resource(self):
    """Usuario NO puede editar recurso de otro usuario"""
    user1 = UserFactory()
    user2 = UserFactory()
    resource = ResourceFactory(owner=user1)
    
    self.client.force_authenticate(user=user2)
    response = self.client.patch(f'/api/resources/{resource.id}/', {
        'title': 'Hacked Title'
    })
    
    assert response.status_code == 403
```

### 8.2 Tests de Validación

**Críticos:**
- Contraseñas débiles rechazadas
- Emails duplicados rechazados
- Contenido vacío rechazado (si Internal)
- XSS en inputs no se ejecuta

**Ejemplo:**
```python
def test_weak_password_rejected(self):
    response = self.client.post('/api/auth/register/', {
        'email': 'test@example.com',
        'name': 'Test',
        'password': '12345'  # Débil
    })
    
    assert response.status_code == 400
    assert 'password' in response.data['details']
```

### 8.3 Tests de Rate Limiting

**Críticos:**
- 5 intentos fallidos de login → bloqueado 15 min
- 10 publicaciones / hora → bloqueado temporalmente

**Ejemplo:**
```python
def test_login_rate_limit(self):
    # 5 intentos fallidos
    for i in range(5):
        response = self.client.post('/api/auth/login/', {
            'email': 'test@example.com',
            'password': 'wrong'
        })
        assert response.status_code == 401
    
    # 6to intento → rate limited
    response = self.client.post('/api/auth/login/', {
        'email': 'test@example.com',
        'password': 'wrong'
    })
    assert response.status_code == 429
```

---

## 9. TESTING DE ESTADOS UI

Basado en [`UI_STATES.md`](../ux/UI_STATES.md).

### 9.1 Estados Críticos a Testar

Por cada pantalla, asegurar tests para:
- ✅ Loading
- ✅ Success (happy path)
- ✅ Empty state
- ✅ Validation error (frontend)
- ✅ Backend error (401, 403, 404, 500)

**Ejemplo:**
```typescript
// app/explore/page.test.tsx

describe('Explore Page States', () => {
  it('should show loading state', () => {
    render(<ExplorePage />);
    expect(screen.getByTestId('skeleton-loader')).toBeInTheDocument();
  });
  
  it('should show empty state when no resources', async () => {
    server.use(
      http.get('/api/resources', () => {
        return HttpResponse.json({ count: 0, results: [] });
      })
    );
    
    render(<ExplorePage />);
    
    await waitFor(() => {
      expect(screen.getByText(/no hay recursos disponibles/i)).toBeInTheDocument();
    });
  });
  
  it('should show error state on API failure', async () => {
    server.use(
      http.get('/api/resources', () => {
        return new HttpResponse(null, { status: 500 });
      })
    );
    
    render(<ExplorePage />);
    
    await waitFor(() => {
      expect(screen.getByText(/error al cargar recursos/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /reintentar/i })).toBeInTheDocument();
    });
  });
});
```

---

## 10. CONTINUOUS INTEGRATION (CI)

### 10.1 GitHub Actions Pipeline

```yaml
# .github/workflows/ci.yml

name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install black flake8
      - run: black --check backend/
      - run: flake8 backend/

  backend-test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15-alpine
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r backend/requirements.txt
      - run: pytest backend/ --cov=apps --cov-report=xml
      - uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  frontend-lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      - run: npm ci
        working-directory: frontend
      - run: npm run lint
        working-directory: frontend

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
        working-directory: frontend
      - run: npm test -- --coverage
        working-directory: frontend

  e2e-test:
    runs-on: ubuntu-latest
    needs: [backend-test, frontend-test]
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npx playwright install
      - run: docker-compose up -d
      - run: npm run test:e2e
      - uses: actions/upload-artifact@v3
        if: failure()
        with:
          name: playwright-screenshots
          path: e2e/screenshots/
```

---

## 11. PRE-COMMIT HOOKS

**Herramienta:** pre-commit

```yaml
# .pre-commit-config.yaml

repos:
  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11
        files: ^backend/

  - repo: https://github.com/PyCQA/flake8
    rev: 6.1.0
    hooks:
      - id: flake8
        files: ^backend/

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: ^frontend/
        types: [javascript, jsx, ts, tsx]

  - repo: local
    hooks:
      - id: pytest-quick
        name: pytest-quick
        entry: pytest backend/ -x --tb=short
        language: system
        pass_filenames: false
        always_run: true
```

**Instalación:**
```bash
pip install pre-commit
pre-commit install
```

---

## 12. TESTS OBLIGATORIOS POR HISTORIA

Según AGENTS.md (línea 60-67), cada historia Must-Have debe incluir tests.

**Mapeo:**

| Historia | Unit Tests | Integration Tests | E2E Test |
|---|---|---|---|
| US-01 (Registro) | AuthService.register | POST /auth/register | ✅ Incluido en flujo E2E |
| US-02 (Login) | AuthService.login | POST /auth/login | ✅ Incluido en flujo E2E |
| US-05 (Explorar) | - | GET /resources | ✅ Incluido en flujo E2E |
| US-06 (Buscar/Filtrar) | - | GET /resources?search=X | - |
| US-07 (Detalle) | - | GET /resources/:id | ✅ Incluido en flujo E2E |
| US-08 (Publicar) | ResourceService.create | POST /resources | ✅ Incluido en flujo E2E |
| US-13 (Validar Admin) | ValidationService.validate | POST /resources/:id/validate | ✅ Incluido en flujo E2E |
| US-16 (Votar) | VoteService.toggle_vote | POST /resources/:id/vote | ✅ Incluido en flujo E2E |
| US-17 (Fork) | ForkService.fork_resource | POST /resources/:id/fork | - |
| US-18 (Notificaciones) | NotificationService.create | GET /notifications | ✅ Incluido en flujo E2E |

**Total estimado:**
- Unit: ~50 tests
- Integration: ~40 tests
- E2E: 1 test completo (~15 steps)

---

## 13. AMBIENTE DE TESTING

### 13.1 Backend Test Environment

```python
# config/settings/test.py

from .base import *

# BD en memoria (SQLite) o PostgreSQL test
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Email: No enviar realmente
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Deshabilitar rate limiting en tests
RATELIMIT_ENABLE = False

# Simplificar hashing de contraseñas (más rápido)
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
```

### 13.2 Frontend Test Environment

```typescript
// jest.config.js

module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/jest.setup.ts'],
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/$1',
  },
  collectCoverageFrom: [
    'app/**/*.{ts,tsx}',
    'components/**/*.{ts,tsx}',
    'lib/**/*.{ts,tsx}',
    '!**/*.d.ts',
    '!**/node_modules/**',
  ],
};
```

---

## 14. DEFINITION OF DONE (DoD) — TESTING

Una historia se considera "Done" cuando:

- ✅ Unit tests escritos y pasando (coverage ≥70%)
- ✅ Integration tests escritos y pasando
- ✅ Tests de seguridad (autorización) pasando
- ✅ BDD feature ejecutable (si historia Must-Have)
- ✅ E2E test actualizado (si aplica al flujo principal)
- ✅ No rompe tests existentes (regresión)
- ✅ Coverage total no disminuye

---

## 15. MÉTRICAS DE CALIDAD

### 15.1 KPIs de Testing

| Métrica | Target MVP | Cómo Medir |
|---|---|---|
| **Code Coverage (Backend)** | ≥70% | pytest-cov |
| **Code Coverage (Frontend)** | ≥60% | Jest coverage |
| **Tests Passing Rate** | 100% | CI pipeline |
| **E2E Test Success** | 100% (1 test) | Playwright report |
| **Flaky Tests** | 0 | Re-runs analysis |
| **Test Execution Time** | <5min total | CI logs |

### 15.2 Quality Gates (CI/CD)

**No merge a main sin:**
- ✅ Lint passing (Black, Flake8, ESLint)
- ✅ Tests passing (unit + integration)
- ✅ Coverage ≥70% backend, ≥60% frontend
- ✅ E2E test passing (before deploy)

---

## 16. TESTING DE PERFORMANCE (Post-MVP)

### 16.1 Load Testing

**Herramienta:** Locust o k6

**Escenarios:**
- 50 usuarios concurrentes navegando /explore
- 10 usuarios publicando recursos simultáneamente
- 100 req/s a API /resources

**Target:** p95 <500ms

### 16.2 Stress Testing

- Encontrar breaking point (cuántos usuarios hasta degradación)
- Validar escalabilidad horizontal

---

## 17. TESTING DE VERSIONADO (Crítico)

**Casos especiales a testar exhaustivamente:**

```python
class TestVersioningEdgeCases:
    def test_concurrent_edits_on_validated_resource(self):
        """
        Given 2 usuarios intentan editar recurso Validated simultáneamente
        When ambos crean nueva versión
        Then solo 1 versión debe tener is_latest=True
        And NO debe haber race condition
        """
        # Test con threading o transaction.atomic
    
    def test_fork_of_fork_maintains_traceability(self):
        """
        Given recurso A es forkeado como B
        And recurso B es forkeado como C
        When consulto derived_from de C
        Then muestra B (no A)
        And cadena completa es A → B → C
        """
    
    def test_delete_original_does_not_delete_forks(self):
        """
        Given recurso A tiene 3 forks
        When owner elimina A (soft delete)
        Then forks siguen existiendo
        And derived_from_resource_id sigue apuntando a A (no NULL)
        """
```

---

## 18. CHANGELOG

### v1.0 (2026-02-16)
- Estrategia de testing inicial
- Pirámide de tests definida (70% unit, 25% integration, 5% E2E)
- Herramientas seleccionadas (pytest, Jest, Playwright)
- Coverage targets establecidos (≥70% backend, ≥60% frontend)
- BDD con pytest-bdd
- 1 test E2E del flujo completo
- Quality gates en CI/CD

---

**Documento completado:** 2026-02-16  
**Siguiente artefacto:** BDD_FEATURES.feature  
**Rol siguiente:** QA Engineer
