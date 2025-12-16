"""
Django settings for pagina project.
"""

from pathlib import Path
import os  # <--- IMPORTANTE: Necesario para leer las variables de Render

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
# En produccion intenta leer la llave segura, si no hay, usa esta por defecto para local
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-5bmrr%(%20-4i9(mujzm5qs%=%#u-f8l+6w(5%8(unk)0ze%k+')

# SECURITY WARNING: don't run with debug turned on in production!
# Si estamos en Render, DEBUG se apaga automágicamente (False). En tu PC será True.
DEBUG = 'RENDER' not in os.environ

# Permitimos todos los hosts para evitar errores en la nube
ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'api',
    'corsheaders',
    'rest_framework_simplejwt'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware", # <--- AGREGA ESTO AQUÍ (Vital para los estilos)
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'pagina.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'pagina.wsgi.application'


# --- CONFIGURACIÓN DE BASE DE DATOS HÍBRIDA ---
# Si Render está activo, usa las variables secretas.
# Si estás en tu PC, usa tu configuración actual.

if 'RENDER' in os.environ:
    # CONFIGURACIÓN PARA PRODUCCIÓN (RENDER)
    DATABASES = {
        'default': {
            'ENGINE': 'mssql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': '1433',
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
            },
        }
    }
else:
    # CONFIGURACIÓN LOCAL (TU PC)
    # Aquí dejamos tus datos para que te siga funcionando en VS Code
    DATABASES = {
        'default': {
            'ENGINE': 'mssql',
            'NAME': 'bd_proyecto',
            'USER': 'usuario', 
            'PASSWORD': 'Nacho0417', # <--- OJO: En el futuro intenta no subir esto a GitHub
            'HOST': 'tcp:sqlproyect.database.windows.net',
            'PORT': '1433',
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server',
            },
        }
    }


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', },
]


# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- CONFIGURACIÓN DE ARCHIVOS ESTÁTICOS (WHITENOISE) ---
STATIC_URL = 'static/'

if not DEBUG:
    # Esto le dice a Render dónde juntar los estilos
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}