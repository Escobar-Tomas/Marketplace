"""
Django settings for Marketplace_Django project.
...
"""

from pathlib import Path
import os
from dotenv import load_dotenv # Importar librería

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CORRECCIÓN CRÍTICA: Cargar .env con ruta explícita ---
# Esto asegura que PythonAnywhere encuentre el archivo sí o sí.
env_path = os.path.join(BASE_DIR, '.env')
load_dotenv(env_path)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-w))1*jw=2aejr92x=w1mu%#k*ty9a%zay2=ans^4a&&r207dol'

# SECURITY WARNING: don't run with debug turned on in production!
# En producción DEBUG será False, en tu PC será True
DEBUG = os.getenv('DEBUG', 'True') == 'True'

# DOMINIOS: Permitimos tu PC y los servidores de PythonAnywhere
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '.pythonanywhere.com']


# Application definition

INSTALLED_APPS = [
    'Marketplace_App',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'Marketplace_Django.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['Marketplace_App/templates'],
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

WSGI_APPLICATION = 'Marketplace_Django.wsgi.application'


# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'Marketplace_App/static'),
]

# Aquí es donde el servidor juntará todos los archivos (admin + app)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'

# URL base para servir archivos multimedia
MEDIA_URL = '/media/'
# Ruta en el sistema de archivos donde se guardarán
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# --- CONFIGURACIÓN DE EMAIL (GMAIL SMTP) ---
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True

# Leemos los valores del archivo .env
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

# IMPORTANTE: Definir el remitente por defecto igual que el usuario host
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
SERVER_EMAIL = EMAIL_HOST_USER

# Para debugging en consola si no hay credenciales (opcional)
if not EMAIL_HOST_USER or not EMAIL_HOST_PASSWORD:
    print("ADVERTENCIA: Credenciales de email no encontradas en .env. Los correos fallarán.")