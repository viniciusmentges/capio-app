from django.core.management.base import BaseCommand
from services.reflection.reflection_service import ReflectionService
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Gera e persiste a reflexão diária da CAPIO antes do primeiro acesso.'

    def handle(self, *args, **options):
        today = timezone.localtime().date()
        self.stdout.write(f"Iniciando ritual de aquecimento para {today}...")
        
        try:
            reflection = ReflectionService.warmup_reflection(today)
            self.stdout.write(self.style.SUCCESS(
                f"Sucesso: Reflexão '{reflection.title}' preparada para {today}."
            ))
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f"Erro no ritual: {str(e)}"
            ))
            logger.error(f"Warmup failed: {str(e)}")
