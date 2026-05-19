from django.core.management.base import BaseCommand
from django.db.models import Q
from apps.devotional.models import DevotionalContent
from services.ai import get_ai_service
import time

class Command(BaseCommand):
    help = 'Gera automaticamente em lote os share_quotes ausentes nos devocionais antigos usando Claude'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("[BUSCA] Buscando devocionais sem 'share_quote' no banco de dados..."))

        # Selecionar devocionais que tenham a frase nula, vazia ou apenas com espaços
        query = Q(share_quote__isnull=True) | Q(share_quote="") | Q(share_quote=" ") | Q(share_quote="None")
        devotionals = DevotionalContent.objects.filter(query)
        total = devotionals.count()

        if total == 0:
            self.stdout.write(self.style.SUCCESS("[OK] Nenhum devocional antigo sem 'share_quote' foi encontrado! Tudo impecável."))
            return

        self.stdout.write(self.style.WARNING(f"[ALERTA] Encontrados {total} devocionais necessitando de curadoria de frase compartilhável."))

        ai_service = get_ai_service()
        success_count = 0

        for index, dev in enumerate(devotionals, 1):
            self.stdout.write(f"[{index}/{total}] Processando devocional ID {dev.id}: '{dev.title}'...")
            
            if not dev.reflection:
                self.stdout.write(self.style.ERROR(f"[-] Devocional ID {dev.id} não possui texto de reflexão. Pulando..."))
                continue

            try:
                # Chamar Claude para extrair a frase contemplativa
                self.stdout.write("[Claude] Sintonizando Claude para formular fragmento contemplativo...")
                share_quote = ai_service.generate_share_quote(dev.reflection)
                
                # Fazer um pequeno clean de aspas extras que o Claude possa retornar
                share_quote = share_quote.strip().strip('"').strip("'").strip('“').strip('”')

                if share_quote:
                    dev.share_quote = share_quote
                    # Ignorar temporariamente a validação completa de outros campos antigos caso estejam vazios
                    dev.save(update_fields=['share_quote'])
                    
                    self.stdout.write(self.style.SUCCESS(f"[SUCESSO] Share Quote gerado: \"{share_quote}\""))
                    success_count += 1
                else:
                    self.stdout.write(self.style.ERROR(f"[-] IA retornou frase vazia para ID {dev.id}"))
                
                # Evitar throttling ou sobrecarga na API em lotes grandes
                time.sleep(1.0)

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[ERRO] Erro ao processar ID {dev.id}: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"\n[FIM] Processamento concluído! {success_count} de {total} devocionais foram atualizados com sucesso."))
