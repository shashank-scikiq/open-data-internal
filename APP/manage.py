#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from dotenv import load_dotenv
from os.path import join, dirname
from apps.src.database_utils.landing_page_json_update import load_landing_page_data
from django.core.management import execute_from_command_line

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_setup.settings')
    try:
        dotenv_path = join(dirname(__file__), '.env')

        load_dotenv(dotenv_path)
        
        # load_landing_page_data()
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
 
 
if __name__ == '__main__':
    main()
