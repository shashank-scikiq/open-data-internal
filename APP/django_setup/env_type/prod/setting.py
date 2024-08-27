import os
from django_setup.setting_utils import get_env_value, BASE_DIR

INSTALL_APP = [
    'apps.retail_all.retail_all_app',
    'apps.logistics_all.logistics_all_app',
    'apps.retail_b2b',
    'apps.retail_b2c',
]


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': get_env_value("POSTGRES_DB"),
        'USER':  get_env_value("POSTGRES_USER"),
        'PASSWORD':  get_env_value("POSTGRES_PASSWORD"),
        'HOST':  get_env_value("POSTGRES_HOST"),
        'PORT':  get_env_value("POSTGRES_PORT"),
        'OPTIONS':
            {
                'options': f'-c search_path={get_env_value("POSTGRES_SCHEMA")}',
            },
    }
}

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'common', 'web'),

]


