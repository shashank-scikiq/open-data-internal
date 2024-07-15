import os

from django.core.wsgi import get_wsgi_application
from dotenv import load_dotenv
from os.path import join, dirname
from dj_static import Cling

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_setup.settings")

dotenv_path = '../.env'
load_dotenv(dotenv_path)

application = Cling(get_wsgi_application())
