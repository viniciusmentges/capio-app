from django.core.management.base import BaseCommand
from apps.devotional.models import Emotion

class Command(BaseCommand):
    help = "Define a ordem oficial das 31 emocoes"

    def handle(self, *args, **options):
        ordered_slugs = [
            "ansioso", "em-paz", "triste", "esperancoso", "medo", "confiante", 
            "desmotivado", "animado", "sozinho", "amado", "sem-esperanca", 
            "feliz", "direcao", "inspirado", "gratidao", "realizado", 
            "corajoso-mas-incerto", "pronto-para-servir", "chamado-mas-hesitante", 
            "encantado", "tentado", "em-conflito-com-alguem", "grato-mas-disperso", 
            "disciplinado-mas-frio", "inseguro", "cansado", "culpado", 
            "envergonhado", "raiva", "confuso", "vazio"
        ]
        
        missing = []
        for idx, slug in enumerate(ordered_slugs, start=1):
            emotion = Emotion.objects.filter(slug=slug).first()
            if emotion:
                emotion.display_order = idx
                emotion.save(update_fields=['display_order'])
                self.stdout.write(self.style.SUCCESS(f"[{idx}] {slug} -> OK"))
            else:
                self.stdout.write(self.style.ERROR(f"[{idx}] {slug} -> NAO ENCONTRADO"))
                missing.append(slug)
        
        if missing:
            self.stdout.write(self.style.WARNING("Emocoes ausentes: " + ", ".join(missing)))
        else:
            self.stdout.write(self.style.SUCCESS("Todas as emocoes ordenadas com sucesso!"))
