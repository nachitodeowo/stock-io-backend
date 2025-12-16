#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Instalar las dependencias
pip install -r requirements.txt

# 2. Recolectar archivos estáticos (CSS, JS, imágenes)
python manage.py collectstatic --no-input

# 3. Migrar la base de datos (crear tablas si faltan)
python manage.py migrate