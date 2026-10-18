from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ⚠️ Production-la ithu environment variable-la vaikkanum
SECRET_KEY = 'django-insecure-smart-expense-tracker-change-me-2024'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',      # intcomma filter-ku
    'expenses',                     # our app
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

ROOT_URLCONF = 'smart_expense_tracker.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'expenses.context_processors.site_globals',
            ],
        },
    },
]

WSGI_APPLICATION = 'smart_expense_tracker.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ---------- Auth redirects ----------
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'login'

MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# ---------- Custom project settings ----------
CURRENCY_SYMBOL = '₹'
SITE_NAME = 'SpendWise'

# ============================================================
# EMAIL (Console backend for dev)
# ============================================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'SpendWise <noreply@spendwise.app>'

# Production-la ithu use pannunga (Gmail example):
# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.gmail.com'
# EMAIL_PORT = 587
# EMAIL_USE_TLS = True
# EMAIL_HOST_USER = 'your.email@gmail.com'
# EMAIL_HOST_PASSWORD = 'your-app-password'   # Gmail app password

# ============================================================
# ⭐ BATCH 3: TWILIO SMS (Optional — console fallback OK)
# ============================================================
TWILIO_ACCOUNT_SID = ''   # Fill from twilio.com/console
TWILIO_AUTH_TOKEN = ''
TWILIO_FROM_NUMBER = ''   # e.g. '+1234567890'

# ============================================================
# ⭐ PWA settings
# ============================================================
PWA_APP_NAME = 'SpendWise'
PWA_THEME_COLOR = '#6366f1'