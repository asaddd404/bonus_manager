from pathlib import Path

# Базовая директория
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ (сгенерируй новый!)
SECRET_KEY = '6=z!9v1q2tr($yk*^)-8w=da@7w7az+o2uto8@wx(v@tpc%y$k'  # python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

# Отладка отключена для продакшена
DEBUG = False

# Разрешённые хосты
ALLOWED_HOSTS = ['109.235.119.125', 'cash.inbrain.kz','bonus.inbrain.kz', 'localhost', '127.0.0.1']

# Установленные приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',  # Замени на 'manager_app', если используешь manager_app
    'crispy_forms',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bonus_manager.urls'

# Настройка шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],  # Если есть общие шаблоны
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bonus_manager.wsgi.application'

# База данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Валидаторы паролей
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Локализация
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Статические файлы
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# STATICFILES_DIRS = [BASE_DIR / 'static']  # Если есть кастомные файлы

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Авторизация
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

AUTH_USER_MODEL = 'core.User'  # Проверь, что модель User определена в core/models.py

# Логирование
LOGGING = {    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'debug.log',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
