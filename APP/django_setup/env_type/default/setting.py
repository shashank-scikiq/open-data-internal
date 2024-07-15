import os
from django_setup.setting_utils import get_env_value, BASE_DIR

INSTALL_APP = [
    'apps.retail_b2b.retail_b2b_app',
    'apps.dashboard.dashboard_app',
    'apps.summary.summary_app',
    'apps.logistics.logistics_app',
    'apps.retail_all.retail_all_app',
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
    os.path.join(BASE_DIR, 'apps', 'dashboard', 'web'),
    os.path.join(BASE_DIR, 'apps', 'logistics', 'web'),
    os.path.join(BASE_DIR, 'apps', 'summary', 'web'),
    os.path.join(BASE_DIR, 'apps', 'retail_all', 'web'),
    # Enable when required
    # os.path.join(BASE_DIR, 'apps', 'mobility', 'web'),
    # os.path.join(BASE_DIR, 'apps', 'finance', 'web'),
    os.path.join(BASE_DIR, 'apps', 'retail_b2b', 'web'),
    os.path.join(BASE_DIR, 'apps', 'misc', 'web'),
    os.path.join(BASE_DIR, 'common', 'web'),

]


