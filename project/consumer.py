import os
from celery import Celery
from celery_config import config 

celery_app = Celery(
    'worker',
    broker=config.broker_url,
    backend=config.result_backend
)

celery_app.config_from_object('celery_config.config', namespace='CELERY')