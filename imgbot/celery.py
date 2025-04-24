import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'imgbot.settings')
app = Celery('imgbot')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()