# Usamos una versión específica (Debian 11 Bullseye) que es compatible con el driver MS SQL
FROM python:3.11-bullseye

WORKDIR /app

# 1. Instalar dependencias del sistema y el Driver ODBC 17
# Nota: Usamos bullseye para asegurar compatibilidad con las llaves de Microsoft
RUN apt-get update && apt-get install -y \
    curl \
    gnupg2 \
    unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# 2. Copiar el resto de los archivos
COPY . .

# 3. Instalar librerías de Python
RUN pip install --no-cache-dir -r requirements.txt

# 4. Recolectar archivos estáticos
RUN python manage.py collectstatic --no-input

# 5. Comando para arrancar
CMD sh -c "python manage.py migrate && gunicorn pagina.wsgi:application --bind 0.0.0.0:10000"