import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASES = {
    'default': {
        'ENGINE': 'django_db_pool.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'mp_inscripcion'),
        'USER': os.getenv('DB_USER', 'mp'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'mp'),
        'HOST': os.getenv('DB_HOST', '127.0.0.1'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'POOL_OPTIONS': {
            'POOL_SIZE': int(os.getenv('DB_POOL_SIZE', 20)),
            'MAX_OVERFLOW': 10,
            'RECYCLE': 300,  # Connection recycle time in seconds
            'TIMEOUT': int(os.getenv('DB_POOL_TIMEOUT', 30))  # Pool timeout in seconds
        },
    }
}

# Cache settings
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': int(os.getenv('CACHE_TIMEOUT', 3600)),
    }
} 