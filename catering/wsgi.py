"""
WSGI config for catering project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv
load_dotenv(override=True)

environment_name = os.getenv("APP_ENVIRONMENT", "dev")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", f"catering.settings.{environment_name}")

application = get_wsgi_application()
