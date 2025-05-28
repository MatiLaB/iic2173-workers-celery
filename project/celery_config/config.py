# celery
from celery.schedules import crontab

# https://docs.celeryq.dev/en/3.1/configuration.html
accept_content = ['application/json']
CELERY_SERIALIZER = 'json'
result_serializer = 'json'

broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

# Configure Celery to use a custom time zone.
timezone = 'America/Santiago'
# A sequence of modules to import when the worker starts
imports = ('celery_config.tasks', )
# beat scheduler
CELERY_BEAT_SCHEDULE = {
    'every-1-minutes_add': {
        'task': 'celery_config.tasks.add',
        'schedule': crontab(minute='*/1'), # every 1 minute
        'args': (16, 16),
    },
}
