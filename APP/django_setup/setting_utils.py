import os
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print("--------------")
print(BASE_DIR)


def get_env_value(env_variable, optional=False, default_value=""):
    try:
        return os.environ[env_variable]
    except KeyError:
        if optional:
            return default_value
        else:
            error_msg = 'Set the {} environment variable'.format(env_variable)
            # Commenting as creating issue in collectstatic as env for schema is not available
            # raise ImproperlyConfigured(error_msg)
            print(error_msg)
