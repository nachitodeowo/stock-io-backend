# Usamos Debian 11 (Bullseye) para compatibilidad con SQL Server
FROM python:3.11-bullseye

WORKDIR /app

# 1. Instalar dependencias del sistema y el Driver ODBC 17
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# 2. Copiar archivos
COPY . .

# 3. Instalar librerías
RUN pip install --no-cache-dir -r requirements.txt

# --- IMPORTANTE: Quitamos el collectstatic de aquí ---

# 4. Comando de inicio (Todo junto al final)
# Primero recolecta estáticos, luego migra la BD, y finalmente prende el servidor
CMD sh -c "python manage.py collectstatic --no-input && python manage.py migrate && gunicorn pagina.wsgi:application --bind 0.0.0.0:10000"