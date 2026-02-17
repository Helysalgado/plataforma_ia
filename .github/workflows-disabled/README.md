# CI/CD Workflows - Temporalmente Deshabilitados

Los workflows de CI/CD han sido movidos a esta carpeta para la entrega académica.

## Workflows Disponibles

- `ci.yml` - Continuous Integration (Lint & Test)
- `cd.yml` - Continuous Deployment (Deploy to Production)

## Por Qué Están Deshabilitados

Para la entrega parcial del MVP, los workflows están deshabilitados porque:

1. **Backend Tests**: El proyecto no tiene tests unitarios completos aún
2. **Frontend Lint**: Hay algunos warnings de linting que no afectan funcionalidad
3. **Deploy Secrets**: No están configurados los secrets en GitHub (DEPLOY_SSH_KEY, etc.)
4. **Docker Build**: Requiere variables de entorno que no están en el repo

## Cómo Reactivarlos

Cuando estés listo para producción:

```bash
# Mover de vuelta a workflows/
mv .github/workflows-disabled/*.yml .github/workflows/

# Configurar secrets en GitHub:
# Settings → Secrets and variables → Actions → New repository secret

# Secrets necesarios:
# - DEPLOY_SSH_KEY
# - DEPLOY_HOST
# - DEPLOY_USER
# - DEPLOY_PATH
# - SLACK_WEBHOOK (opcional)
```

## Próximos Pasos

Ver `docs/delivery/NEXT_STEPS.md` para el roadmap completo, incluyendo:
- Implementar tests unitarios (pytest, jest)
- Configurar linter y pre-commit hooks
- Setup de CI/CD con secrets
- Deploy automatizado
