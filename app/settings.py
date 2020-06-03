import os
from pathlib import Path

from starlette.config import Config

ROOT_DIR = Path(__file__).parents[1]

READ_DOT_ENV_FILE = bool(os.environ.get('READ_DOT_ENV_FILE', default=False))

if READ_DOT_ENV_FILE:
    config = Config(str(ROOT_DIR / '.env'))
else:
    config = Config()

GRAPHQL_SCHEMA_FILE = config(
    'GRAPHQL_SCHEMA_FILE', cast=str, default=str(ROOT_DIR / 'schema.graphql')
)
GRAPHQL_PATH = config('GRAPHQL_PATH', default='/graphql/')

DEBUG = config('DEBUG', cast=bool, default=False)

TESTING = config('TESTING', cast=bool, default=False)

DATABASE_URL = config(
    'DATABASE_URL', default='postgresql://postgres:postgres@postgres:5432/interagent'
)
# REDIS_URL = config('REDIS_URL', default='redis://redis:6379')

if DEBUG:
    LOG_LEVEL = config('LOG_LEVEL', default='DEBUG')
else:
    LOG_LEVEL = config('LOG_LEVEL', default='INFO')


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s] [%(process)s] [%(name)s:%(module)s:%(lineno)d] [%(levelname)s] [%(message)s]',
        }
    },
    'handlers': {'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'}},
    'root': {'level': LOG_LEVEL, 'handlers': ['console']},
}
