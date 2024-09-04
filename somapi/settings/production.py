import os
import sys


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


DEBUG = os.getenv("DEBUG","False").lower()=="true" 

print("DEBUG==>",DEBUG)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",  # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        "NAME": os.getenv("DB_NAME"),# "tzapi",  # Or path to database file if using sqlite3.
        "USER": os.getenv("DB_USER"),# "moeke",  # Not used with sqlite3.
        "PASSWORD":os.getenv("DB_PASSWORD"),# "VKMCrEDlMGYjSe3",  # Not used with sqlite3.
        "HOST":os.getenv("DB_HOST"),# "127.0.0.1",  # Set to empty string for localhost. Not used with sqlite3.
        "PORT": os.getenv("DB_PORT"),# "5432" if "process_tasks" not in sys.argv else "5432",  # Set to empty string for default. Not used with sqlite3.
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "memcached:11211",
    }
}
CACHE_TIMEOUT = 60 * 8




# pg_dump -U nzmewqyrvjyhpl -h ec2-107-22-173-160.compute-1.amazonaws.com dcoimmfelmkfbc > winda_backup

# Update database configuration with $DATABASE_URL.
# Honor the 'X-Forwarded-Proto' header for request.is_secure()
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


STATICFILES_DIRS = (os.path.join(PROJECT_ROOT, "../../templates"),)
CORS_ORIGIN_ALLOW_ALL = True

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/
# STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
# DEBUG=True


EMAIL_HOST = os.getenv("EMAIL_HOST","")# "sisitech.com"
EMAIL_HOST_USER =  os.getenv("EMAIL_HOST_USER","")# "apitz@sisitech.com"
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD","")# "tatawauwzniurpsh"

SMTP_PORT = int(os.getenv("SMTP_PORT","587"))

DEFAULT_FROM_EMAIL =  os.getenv("DEFAULT_FROM_EMAIL","Daa Somalia <somaliadaa@gmail.com>") 


