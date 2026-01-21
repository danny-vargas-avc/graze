"""
WSGI config for Graze API.
"""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'graze_api.settings')
application = get_wsgi_application()
