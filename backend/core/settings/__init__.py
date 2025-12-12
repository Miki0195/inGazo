# Settings package
# Import the appropriate settings based on environment
import os

environment = os.getenv('DJANGO_ENVIRONMENT', 'dev')

if environment == 'prod':
    from .prod import *  # noqa
else:
    from .dev import *  # noqa

