import os
from celery import Celery

# Define as configurações do Django como o módulo padrão para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

app = Celery('capio')

# Configura o Celery usando as chaves prefixadas com 'CELERY_' no Django Settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescobre automaticamente tasks.py dentro das pastas de aplicativos instalados no Django
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
