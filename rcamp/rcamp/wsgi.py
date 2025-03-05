"""
WSGI config for rcamp project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
import debugpy
import logging

from django.core.wsgi import get_wsgi_application

debugpy.listen(('0.0.0.0', 5678))  # 5678 is the default debug port
logger = logging.getLogger('admin')
logger.info("Debugger is listening on port 5678...")

# Optionally, you can make the process wait for a debugger to attach
debugpy.wait_for_client()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rcamp.settings")

application = get_wsgi_application()
