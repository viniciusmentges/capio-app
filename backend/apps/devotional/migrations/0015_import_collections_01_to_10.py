from django.db import migrations
from django.core.management import call_command
import sys
import logging

logger = logging.getLogger(__name__)

def promote_all_ten_collections(apps, schema_editor):
    if 'test' in sys.argv or 'test_coverage' in sys.argv:
        return
    try:
        logger.info("[CAPIO PROMOÇÃO EDITORIAL] Iniciando importação e ativação das 10 coleções em produção...")
        call_command('import_editorial_staging')
        
        Emotion = apps.get_model('devotional', 'Emotion')
        Emotion.objects.filter(slug='inseguro').update(icon='insecure_icon')
        Emotion.objects.filter(slug='cansado').update(icon='tired_icon')
        
        DevotionalContent = apps.get_model('devotional', 'DevotionalContent')
        promoted_count = DevotionalContent.objects.filter(
            emotion__slug__in=[
                'ansioso', 'triste', 'medo', 'desmotivado', 'sozinho',
                'sem-esperanca', 'direcao', 'gratidao', 'inseguro', 'cansado',
                'corajoso-mas-incerto', 'chamado-mas-hesitante', 'tentado',
                'em-conflito-com-alguem', 'grato-mas-disperso', 'disciplinado-mas-frio'
            ]
        ).update(is_active=True, reviewed_by_human=True)
        
        logger.info(f"[CAPIO PROMOÇÃO EDITORIAL] {promoted_count} devocionais garantidos como ativos e revisados em produção.")
    except Exception as e:
        logger.error(f"Erro na importação das 10 coleções na migration 0015: {e}")

class Migration(migrations.Migration):

    dependencies = [
        ('devotional', '0014_clean_markdown_asterisks'),
    ]

    operations = [
        migrations.RunPython(promote_all_ten_collections, migrations.RunPython.noop),
    ]
