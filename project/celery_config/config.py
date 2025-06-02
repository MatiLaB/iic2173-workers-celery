from celery.schedules import crontab

from . import database

# https://docs.celeryq.dev/en/3.1/configuration.html
accept_content = ['application/json']
CELERY_SERIALIZER = 'json'
result_serializer = 'json'

# --- Usa las variables importadas de database.py ---
broker_url = f'redis://{database.REDIS_HOST}:{database.REDIS_PORT}/{database.REDIS_DB}'
result_backend = f'redis://{database.REDIS_HOST}:{database.REDIS_PORT}/{database.REDIS_DB}'
# ----------------------------------------------------

# Configure Celery to use a custom time zone.
timezone = 'America/Santiago'
# A sequence of modules to import when the worker starts
imports = ('celery_config.tasks', )


broker_connection_retry_on_startup = True
broker_connection_max_retries = 30
broker_connection_timeout = 300
broker_pool_limit = 10
task_acks_late = True
worker_prefetch_multiplier = 1


# beat scheduler
CELERY_BEAT_SCHEDULE = {
    'every-1-minutes_add': {
        'task': 'celery_config.tasks.add',
        'schedule': crontab(minute='*/1a'), # every 1 minute
        'args': (16, 16),
    },
}