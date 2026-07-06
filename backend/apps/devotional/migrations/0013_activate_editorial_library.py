from django.db import migrations
import logging

import sys

logger = logging.getLogger(__name__)

def activate_editorial_data(apps, schema_editor):
    if 'test' in sys.argv or 'test_coverage' in sys.argv:
        return
    try:
        DevotionalContent = apps.get_model('devotional', 'DevotionalContent')
        updated_count = DevotionalContent.objects.filter(
            reviewed_by_human=True,
            emotion__slug__in=['ansioso', 'triste', 'medo', 'desmotivado']
        ).update(is_active=True)
        logger.info(f"[CAPIO EDITORIAL] {updated_count} devocionais promovidos para produção (is_active=True).")
    except Exception as e:
        logger.error(f"Erro ao ativar biblioteca editorial na migration 0013: {e}")

class Migration(migrations.Migration):

    dependencies = [
        ('devotional', '0012_import_editorial_staging_data'),
    ]

    operations = [
        migrations.RunPython(activate_editorial_data, migrations.RunPython.noop),
    ]
