# Usamos Python sobre una versión de Linux (Debian)
FROM python:3.11-slim

# 1. Instalar herramientas del sistema y el Driver de Microsoft SQL Server
RUN apt-get update && apt-get install -y curl gnupg2 build-essential unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# 2. Configurar la carpeta de trabajo
WORKDIR /app

# 3. Copiar tus archivos al servidor
COPY . .

# 4. Instalar tus librerías (Django, etc.)
RUN pip install --no-cache-dir -r requirements.txt

# 5. Recolectar archivos estáticos (CSS/Imágenes)
RUN python manage.py collectstatic --no-input

# 6. Comando de inicio: Migrar base de datos y prender el servidor
# Usamos 'sh -c' para poder ejecutar dos comandos seguidos
CMD sh -c "python manage.py migrate && gunicorn pagina.wsgi:application --bind 0.0.0.0:10000"