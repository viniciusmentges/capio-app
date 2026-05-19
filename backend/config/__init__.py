# Garante que o celery_app é carregado quando o Django inicia para registro de tarefas.
from .celery import app as celery_app

__all__ = ('celery_app',)
