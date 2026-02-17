#!/bin/bash

# Script para ejecutar y verificar US-01 y US-02
# Sin Docker (desarrollo local)

set -e

echo "========================================="
echo "  Testing US-01 y US-02 (Local)"
echo "========================================="
echo ""

cd backend

echo "📦 1. Instalando dependencias..."
pip install -q -r requirements.txt

echo ""
echo "🗄️  2. Ejecutando migraciones..."
export DJANGO_SETTINGS_MODULE=config.settings.test
python manage.py makemigrations
python manage.py migrate

echo ""
echo "🌱 3. Seeding roles..."
python manage.py seed_roles

echo ""
echo "🧪 4. Ejecutando tests..."
pytest apps/authentication/tests/ -v --tb=short

echo ""
echo "📊 5. Generando reporte de cobertura..."
pytest apps/authentication/tests/ --cov=apps.authentication --cov-report=term --cov-report=html

echo ""
echo "✅ ¡Tests completados!"
echo "   Ver reporte de cobertura en: htmlcov/index.html"
