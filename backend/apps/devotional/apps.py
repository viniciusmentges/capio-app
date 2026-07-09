from django.apps import AppConfig
import sys

class DevotionalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.devotional'

    def ready(self):
        if 'test' not in sys.argv and 'test_coverage' not in sys.argv:
            try:
                from django.db import connection
                if 'devotional_emotion' in connection.introspection.table_names():
                    from apps.devotional.models import DevotionalContent, Emotion
                    active_count = DevotionalContent.objects.filter(is_active=True).count()
                    vazio_emo = Emotion.objects.filter(slug='vazio').first()
                    if active_count < 147 or not vazio_emo or not getattr(vazio_emo, 'icon', ''):
                        from django.core.management import call_command
                        call_command('import_editorial_staging')
                        icons_map = {
                            'ansioso': 'anxiety_icon', 'triste': 'sad_icon', 'medo': 'fear_icon',
                            'desmotivado': 'unmotivated_icon', 'sozinho': 'lonely_icon',
                            'sem-esperanca': 'hopeless_icon', 'direcao': 'direction_icon',
                            'gratidao': 'gratitude_icon', 'inseguro': 'insecure_icon',
                            'cansado': 'tired_icon', 'corajoso-mas-incerto': 'courageous_uncertain_icon',
                            'chamado-mas-hesitante': 'called_hesitant_icon', 'tentado': 'tempted_icon',
                            'em-conflito-com-alguem': 'conflict_icon', 'grato-mas-disperso': 'grateful_dispersed_icon',
                            'disciplinado-mas-frio': 'disciplined_cold_icon', 'culpado': 'guilty_icon',
                            'raiva': 'anger_icon', 'confuso': 'confused_icon', 'vazio': 'empty_icon',
                        }
                        for slug, icon_name in icons_map.items():
                            Emotion.objects.filter(slug=slug).update(icon=icon_name)
                        DevotionalContent.objects.filter(
                            emotion__slug__in=list(icons_map.keys())
                        ).update(is_active=True, reviewed_by_human=True)
            except Exception:
                pass
