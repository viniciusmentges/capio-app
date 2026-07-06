from django.db import migrations
from django.core.management import call_command
import logging

logger = logging.getLogger(__name__)

def import_editorial_data(apps, schema_editor):
    try:
        call_command('import_editorial_staging')
    except Exception as e:
        logger.error(f"Erro ao importar dados editoriais em staging na migration: {e}")

class Migration(migrations.Migration):

    dependencies = [
        ('devotional', '0011_devotionalcontent_daily_companion_and_more'),
    ]

    operations = [
        migrations.RunPython(import_editorial_data, migrations.RunPython.noop),
    ]
