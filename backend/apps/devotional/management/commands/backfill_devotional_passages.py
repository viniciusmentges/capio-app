from django.core.management.base import BaseCommand
from apps.devotional.models import DevotionalContent
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "✨ Realiza o backfill de passagens bíblicas associando 'passage' a devocionais antigos baseados em 'scripture_reference'"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("[BUSCA] Localizando devocionais sem associacao relacional 'passage'..."))

        # Selecionar todos os devocionais que não possuem passage
        queryset = DevotionalContent.objects.filter(passage__isnull=True)
        total_found = queryset.count()

        if total_found == 0:
            self.stdout.write(self.style.SUCCESS("[SUCESSO] Nenhum devocional orfao de passage encontrado!"))
            return

        self.stdout.write(self.style.NOTICE(f"Foram encontrados {total_found} devocionais pendentes de correcao."))

        success_count = 0
        failure_count = 0

        for dev in queryset:
            self.stdout.write(f"-> Processando ID {dev.id}: '{dev.title}' (Ref: '{dev.scripture_reference}')")
            try:
                # O método resolve_passage() foi modularizado no modelo e normaliza a referência de forma consistente
                dev.resolve_passage()
                if dev.passage:
                    dev.save(update_fields=['passage'])
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  [OK] Sucesso! Vinculado a {dev.passage.canonical_id}"))
                else:
                    failure_count += 1
                    self.stdout.write(self.style.ERROR(f"  [ERRO] Falha: Referencia vazia ou impossivel de normalizar."))
            except Exception as e:
                failure_count += 1
                logger.error(f"Erro ao resolver passagem para devocional {dev.id}: {str(e)}", exc_info=True)
                self.stdout.write(self.style.ERROR(f"  [ERRO] Falha: {str(e)}"))

        self.stdout.write("\n" + "=" * 40)
        self.stdout.write(self.style.SUCCESS(f"Backfill finalizado!"))
        self.stdout.write(self.style.SUCCESS(f"  [OK] Corrigidos com sucesso: {success_count}"))
        if failure_count > 0:
            self.stdout.write(self.style.ERROR(f"  [ERRO] Falhas ou erros tolerados: {failure_count}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"  [OK] Nenhuma falha ocorrida!"))
        self.stdout.write("=" * 40)
