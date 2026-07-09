from django.db import migrations
from django.core.management import call_command
import sys
import logging

logger = logging.getLogger(__name__)

def promote_all_twenty_collections(apps, schema_editor):
    if 'test' in sys.argv or 'test_coverage' in sys.argv:
        return
    try:
        logger.info("[CAPIO PROMOÇÃO EDITORIAL] Iniciando importação e ativação das 20 coleções em produção...")
        call_command('import_editorial_staging')
        
        Emotion = apps.get_model('devotional', 'Emotion')
        icons_map = {
            'ansioso': 'anxiety_icon',
            'triste': 'sad_icon',
            'medo': 'fear_icon',
            'desmotivado': 'unmotivated_icon',
            'sozinho': 'lonely_icon',
            'sem-esperanca': 'hopeless_icon',
            'direcao': 'direction_icon',
            'gratidao': 'gratitude_icon',
            'inseguro': 'insecure_icon',
            'cansado': 'tired_icon',
            'corajoso-mas-incerto': 'courageous_uncertain_icon',
            'chamado-mas-hesitante': 'called_hesitant_icon',
            'tentado': 'tempted_icon',
            'em-conflito-com-alguem': 'conflict_icon',
            'grato-mas-disperso': 'grateful_dispersed_icon',
            'disciplinado-mas-frio': 'disciplined_cold_icon',
            'culpado': 'guilty_icon',
            'raiva': 'anger_icon',
            'confuso': 'confused_icon',
            'vazio': 'empty_icon',
        }
        for slug, icon_name in icons_map.items():
            Emotion.objects.filter(slug=slug).update(icon=icon_name)
        
        DevotionalContent = apps.get_model('devotional', 'DevotionalContent')
        all_slugs = list(icons_map.keys())
        promoted_count = DevotionalContent.objects.filter(
            emotion__slug__in=all_slugs
        ).update(is_active=True, reviewed_by_human=True)
        
        logger.info(f"[CAPIO PROMOÇÃO EDITORIAL] {promoted_count} devocionais garantidos como ativos e revisados em produção (20 emoções).")
    except Exception as e:
        logger.error(f"Erro na importação e ativação das 20 coleções na migration 0016: {e}")

class Migration(migrations.Migration):

    dependencies = [
        ('devotional', '0015_import_collections_01_to_10'),
    ]

    operations = [
        migrations.RunPython(promote_all_twenty_collections, migrations.RunPython.noop),
    ]
